import pytest
import os
import tempfile
from flask import Flask
from models import db, User
from app import app as main_app, init_db


@pytest.fixture
def app():
    """Создаем тестовое Flask приложение"""
    # Создаем временную базу данных для тестов
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Конфигурируем приложение для тестов
    main_app.config['TESTING'] = True
    main_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    main_app.config['SQLALCHEMY_BINDS'] = {
        'sqlite': f'sqlite:///{db_path}',
    }
    main_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    main_app.config['WTF_CSRF_ENABLED'] = False
    
    with main_app.app_context():
        # Создаем таблицы
        db.create_all(bind_key='sqlite')
        yield main_app
    
    # Очищаем после тестов
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Создаем тестовый клиент"""
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """Создаем авторизованный клиент"""
    with app.app_context():
        # Очищаем таблицу перед созданием админа
        db.session.query(User).delete()
        db.session.commit()
        
        # Создаем тестового админа
        test_admin = User.create_admin('test_admin', 'test_password')
        admin_id = test_admin.id
        
    with client.session_transaction() as sess:
        sess['user_id'] = admin_id
    
    return client


def test_app_startup(app):
    """Тест успешного запуска приложения"""
    assert app is not None
    assert app.config['TESTING'] is True
    
    # Проверяем что приложение имеет необходимые роуты
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    
    expected_routes = [
        '/',
        '/login',
        '/logout',
        '/dashboard',
        '/admins',
        '/admins/add',
        '/admins/delete/<int:user_id>',
        '/tools'
    ]
    
    for route in expected_routes:
        assert any(route in rule for rule in rules), f"Роут {route} не найден"


def test_app_configuration(app):
    """Тест корректности конфигурации приложения"""
    # Проверяем основные настройки
    assert 'SECRET_KEY' in app.config
    assert 'SQLALCHEMY_DATABASE_URI' in app.config
    assert 'SQLALCHEMY_BINDS' in app.config
    
    # Проверяем что SQLite база настроена
    assert 'sqlite' in app.config['SQLALCHEMY_BINDS']


def test_database_initialization(app):
    """Тест инициализации базы данных"""
    with app.app_context():
        # Проверяем что таблицы созданы
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        assert 'users' in tables


def test_all_routes_accessibility_unauthorized(client):
    """Тест доступности роутов без авторизации"""
    
    # Роуты, которые должны редиректить на /login
    protected_routes = [
        '/',
        '/dashboard', 
        '/admins',
        '/tools'
    ]
    
    for route in protected_routes:
        response = client.get(route)
        assert response.status_code == 302
        assert '/login' in response.location
    
    # Роут логина должен быть доступен
    response = client.get('/login')
    assert response.status_code == 200


def test_all_routes_accessibility_authorized(auth_client):
    """Тест доступности роутов с авторизацией"""
    
    # Роуты, которые должны возвращать 200
    accessible_routes = [
        '/dashboard',
        '/admins',
        '/tools'
    ]
    
    for route in accessible_routes:
        response = auth_client.get(route)
        assert response.status_code == 200, f"Роут {route} недоступен"


def test_admin_routes_post_methods(auth_client):
    """Тест POST методов админских роутов"""
    
    # Тест добавления админа
    response = auth_client.post('/admins/add', data={
        'username': 'test_new_admin',
        'password': 'test_password'
    })
    assert response.status_code == 302  # Редирект после успешного добавления
    
    # Тест удаления несуществующего админа
    response = auth_client.post('/admins/delete/999')
    assert response.status_code == 200  # Страница с ошибкой


def test_static_files_accessibility(auth_client):
    """Тест доступности статических файлов"""
    
    # Проверяем доступность CSS (статика также защищена авторизацией)
    response = auth_client.get('/static/css/style.css')
    assert response.status_code == 200
    assert 'text/css' in response.content_type
    
    # Проверяем что CSS содержит стили для админов
    css_content = response.get_data(as_text=True)
    assert '.admins-table' in css_content
    assert '.admin-form' in css_content
    assert '.btn-danger' in css_content
    assert '.alert-error' in css_content


def test_css_styles_completeness():
    """Тест полноты CSS стилей для админской панели"""
    
    css_file_path = '/Users/mr_akkerman/development/DevProjects/bot-ferma-admin/static/css/style.css'
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Проверяем наличие основных классов
    required_classes = [
        '.admins-table',
        '.admin-form', 
        '.form-group',
        '.btn',
        '.btn-primary',
        '.btn-danger',
        '.alert',
        '.alert-error',
        '.alert-success',
        '.table-actions'
    ]
    
    for css_class in required_classes:
        assert css_class in css_content, f"CSS класс {css_class} не найден"
    
    # Проверяем стиль Vercel - основные цвета и значения
    assert '#ffffff' in css_content  # Белый фон
    assert '#e1e1e1' in css_content  # Серые границы
    assert '#333333' in css_content  # Темный текст
    assert '#dc2626' in css_content  # Красный для кнопок удаления


def test_login_workflow(client):
    """Тест полного workflow авторизации"""
    
    with main_app.app_context():
        # Очищаем таблицу и создаем тестового админа
        db.session.query(User).delete()
        db.session.commit()
        User.create_admin('workflow_admin', 'workflow_password')
    
    # Проверяем редирект на login
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location
    
    # Проверяем страницу логина
    response = client.get('/login')
    assert response.status_code == 200
    
    # Пытаемся войти с корректными данными
    response = client.post('/login', data={
        'username': 'workflow_admin',
        'password': 'workflow_password'
    })
    
    # После успешного входа должен быть редирект на dashboard
    assert response.status_code == 302
    assert '/dashboard' in response.location


def test_admin_management_workflow(auth_client):
    """Тест полного workflow управления админами"""
    
    # Получаем страницу управления админами
    response = auth_client.get('/admins')
    assert response.status_code == 200
    
    # Добавляем нового админа
    response = auth_client.post('/admins/add', data={
        'username': 'workflow_test_admin',
        'password': 'test_password'
    })
    assert response.status_code == 302
    
    # Проверяем что админ создан
    with main_app.app_context():
        assert User.admin_exists('workflow_test_admin') is True
        admin = User.query.filter_by(username='workflow_test_admin').first()
        admin_id = admin.id
    
    # Пытаемся удалить админа (у нас есть тестовый + созданный = можно удалить)
    response = auth_client.post(f'/admins/delete/{admin_id}')
    assert response.status_code == 302
    
    # Проверяем что админ удален
    with main_app.app_context():
        assert User.admin_exists('workflow_test_admin') is False


def test_run_py_file_exists():
    """Тест существования и корректности файла run.py"""
    
    run_file_path = '/Users/mr_akkerman/development/DevProjects/bot-ferma-admin/run.py'
    
    # Проверяем что файл существует
    assert os.path.exists(run_file_path)
    
    # Проверяем что файл исполняемый (имеет shebang)
    with open(run_file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        assert first_line.startswith('#!/usr/bin/env python')
    
    # Проверяем что файл содержит основные функции
    with open(run_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'def setup_environment()' in content
        assert 'def main()' in content
        assert 'from app import app' in content
        assert 'DB_HOST' in content
        assert 'DB_PASSWORD' in content


def test_error_handling(auth_client):
    """Тест обработки ошибок"""
    
    # Тест добавления админа без данных
    response = auth_client.post('/admins/add', data={})
    assert response.status_code == 200  # Должна отобразиться страница с ошибкой
    
    # Тест добавления админа с дублирующимся именем
    with main_app.app_context():
        # Создаем админа с уникальным именем (тестовый админ уже существует)
        User.create_admin('duplicate_admin', 'password1')
    
    response = auth_client.post('/admins/add', data={
        'username': 'duplicate_admin',
        'password': 'password2'
    })
    assert response.status_code == 200  # Должна отобразиться страница с ошибкой


def test_security_headers(client):
    """Тест базовых заголовков безопасности"""
    
    response = client.get('/login')
    
    # Проверяем что ответ корректный
    assert response.status_code == 200
    
    # Проверяем базовые заголовки
    assert 'Content-Type' in response.headers


def test_application_integrity():
    """Финальный тест целостности всего приложения"""
    
    # Проверяем что все основные файлы существуют
    base_dir = '/Users/mr_akkerman/development/DevProjects/bot-ferma-admin'
    
    required_files = [
        'app.py',
        'models.py', 
        'auth.py',
        'dashboard.py',
        'admin_management.py',
        'run.py',
        'requirements.txt',
        'static/css/style.css'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        assert os.path.exists(full_path), f"Файл {file_path} не найден"
    
    # Проверяем что все тестовые файлы существуют
    test_files = [
        'test_admin_crud.py',
        'test_admin_management.py', 
        'test_admin_routes.py',
        'test_final.py'
    ]
    
    for test_file in test_files:
        full_path = os.path.join(base_dir, test_file)
        assert os.path.exists(full_path), f"Тестовый файл {test_file} не найден"


def test_css_vercel_style_compliance():
    """Тест соответствия стилей дизайну Vercel"""
    
    css_file_path = '/Users/mr_akkerman/development/DevProjects/bot-ferma-admin/static/css/style.css'
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Проверяем основные характеристики стиля Vercel
    vercel_characteristics = [
        'font-family: -apple-system',  # Системные шрифты
        'border-radius: 8px',          # Скругленные углы
        'border-radius: 6px',          # Меньшие скругления для элементов
        'box-shadow: 0 1px 3px',       # Тонкие тени
        'background-color: #ffffff',    # Белый фон
        'background-color: #f8f9fa',    # Светло-серый фон
        'color: #333333',              # Темно-серый текст
        'transition:',                 # Плавные переходы
        'font-weight: 600',            # Полужирные заголовки
    ]
    
    for characteristic in vercel_characteristics:
        assert characteristic in css_content, f"Характеристика Vercel стиля '{characteristic}' не найдена"
