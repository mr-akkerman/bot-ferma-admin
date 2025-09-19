import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from models import db, User
from auth import login_user, logout_user, is_authenticated

# Создание Flask приложения
app = Flask(__name__, instance_relative_config=True)

# Конфигурация приложения
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')

# Конфигурация базы данных для админов (SQLite)
app.config['ADMIN_DATABASE_URI'] = 'sqlite:///admin.db'

# Конфигурация базы данных для профилей (PostgreSQL)
app.config['PROFILES_DATABASE_URI'] = os.environ.get(
    'PROFILES_DATABASE_URL',
    'postgresql://{}:{}@{}:{}/{}'.format(
        os.environ.get('DB_USER', 'postgres'),
        os.environ.get('DB_PASSWORD', 'password'),
        os.environ.get('DB_HOST', 'localhost'),
        os.environ.get('DB_PORT', '5432'),
        os.environ.get('DB_NAME', 'farm_profiles')
    )
)

# Конфигурация SQLAlchemy для двух БД
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['ADMIN_DATABASE_URI']
app.config['SQLALCHEMY_BINDS'] = {
    'sqlite': app.config['ADMIN_DATABASE_URI'],
    'postgres': app.config['PROFILES_DATABASE_URI']
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy
db.init_app(app)

# Функция инициализации базы данных
def init_db():
    """Инициализация SQLite базы данных и создание дефолтного админа"""
    with app.app_context():
        # Создаем таблицы для SQLite БД
        db.create_all(bind_key='sqlite')
        
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
            print("Создан дефолтный админ: admin/admin")
        else:
            print("Дефолтный админ уже существует")

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
    """Дашборд админки (заглушка)"""
    return "Dashboard - Admin Panel"

if __name__ == '__main__':
    # Инициализация базы данных при запуске
    init_db()
    app.run(debug=True)
