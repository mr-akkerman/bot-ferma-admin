import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models import db, User
from auth import login_user, logout_user, is_authenticated
from dashboard import get_dashboard_data
from admin_management import get_admins_list, add_admin, remove_admin
from config import get_config, validate_config

# Валидация конфигурации при импорте
try:
    validate_config()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    exit(1)

# Создание Flask приложения
app = Flask(__name__, instance_relative_config=True)

# Получаем и применяем конфигурацию
config_class = get_config()
config_class.init_app(app)

print(f"🔧 Using configuration: {config_class.__name__}")
print(f"🔒 Admin DB: {app.config.get('_ADMIN_DB_URI', 'Not configured')}")
print(f"📊 Profiles DB: {app.config.get('_PROFILES_DB_URI', 'Not configured')}")

# Инициализация SQLAlchemy
db.init_app(app)

# Функция для проверки авторизации
def require_auth():
    """Проверяет авторизацию пользователя"""
    return is_authenticated()

# Обработчик before_request для защиты роутов
@app.before_request
def check_auth():
    """Проверяет авторизацию перед каждым запросом"""
    # Пропускаем проверку для /login, /logout и статических файлов
    if request.endpoint in ['login', 'logout', 'static']:
        return
    
    # Для всех остальных роутов проверяем авторизацию
    if not require_auth():
        return redirect(url_for('login'))

# Функция инициализации базы данных
def init_db():
    """Инициализация PostgreSQL базы данных админов и создание дефолтного админа"""
    with app.app_context():
        try:
            # Создаем таблицы для админской PostgreSQL БД
            db.create_all(bind_key='admin')
            print("✅ Admin database tables created/verified")
            
            # Проверяем существование дефолтного админа
            admin_exists = User.query.filter_by(username='admin').first()
            
            if not admin_exists:
                # Создаем дефолтного админа с хешированным паролем
                password_hash = generate_password_hash('admin')
                default_admin = User(
                    username='admin',
                    password_hash=password_hash
                )
                db.session.add(default_admin)
                db.session.commit()
                print("✅ Создан дефолтный админ: admin/admin")
                print("⚠️  ВАЖНО: Измените пароль админа после первого входа!")
            else:
                print("ℹ️  Дефолтный админ уже существует")
                
        except Exception as e:
            print(f"❌ Ошибка инициализации базы данных админов: {e}")
            print("🔍 Проверьте настройки подключения к PostgreSQL для админов")
            raise

# Роуты авторизации
@app.route('/')
def index():
    """Главная страница - редирект на dashboard если авторизован, иначе на login"""
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в систему"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST запрос - обработка входа
    username = request.form.get('username')
    password = request.form.get('password')
    
    if login_user(username, password):
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    """Выход из системы"""
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """Дашборд админки"""
    try:
        # Получаем статистику для дашборда
        dashboard_data = get_dashboard_data()
        return render_template('dashboard.html', data=dashboard_data)
    except Exception as e:
        # Обрабатываем ошибки подключения к PostgreSQL профилей
        error_message = "Ошибка подключения к базе данных профилей. Проверьте настройки PROFILES_DB_*"
        print(f"❌ Dashboard error: {e}")
        return render_template('dashboard.html', error=error_message)


@app.route('/admins')
def admins():
    """Управление админами"""
    # Получаем список всех админов
    result = get_admins_list()
    if result['success']:
        return render_template('admins.html', admins=result['admins'])
    else:
        return render_template('admins.html', error=result['error'])


@app.route('/admins/add', methods=['POST'])
def add_admin_route():
    """Добавление нового админа"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template('admins.html', error='Имя пользователя и пароль обязательны')
    
    result = add_admin(username, password)
    if result['success']:
        return redirect(url_for('admins'))
    else:
        # Получаем список админов для отображения с ошибкой
        admins_result = get_admins_list()
        admins = admins_result['admins'] if admins_result['success'] else []
        return render_template('admins.html', error=result['error'], admins=admins)


@app.route('/admins/delete/<int:user_id>', methods=['POST'])
def delete_admin_route(user_id):
    """Удаление админа"""
    result = remove_admin(user_id)
    if result['success']:
        return redirect(url_for('admins'))
    else:
        # Получаем список админов для отображения с ошибкой
        admins_result = get_admins_list()
        admins = admins_result['admins'] if admins_result['success'] else []
        return render_template('admins.html', error=result['error'], admins=admins)


@app.route('/tools')
def tools():
    """Инструменты"""
    return render_template('tools.html')

if __name__ == '__main__':
    # Инициализация базы данных при запуске
    init_db()
    
    # Получаем порт от Railway или используем 8000 для локальной разработки
    port = int(os.environ.get('PORT', 8000))
    
    # Определяем режим на основе переменной окружения
    is_production = os.environ.get('RAILWAY_ENVIRONMENT_NAME') is not None
    
    print(f"🚀 Starting app on port {port}")
    print(f"🔧 Environment: {'Production (Railway)' if is_production else 'Development'}")
    
    app.run(
        host='0.0.0.0',  # ОБЯЗАТЕЛЬНО для Railway!
        port=port,       # Порт от Railway
        debug=not is_production  # debug=False в продакшене
    )
