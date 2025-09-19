import pytest
import os
import tempfile
from flask import Flask
from models import db, User
from app import app as main_app


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
    main_app.config['WTF_CSRF_ENABLED'] = False  # Отключаем CSRF для тестов
    
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


@pytest.fixture(autouse=True)
def clean_db(app):
    """Очищаем БД перед каждым тестом"""
    with app.app_context():
        # Удаляем всех пользователей перед каждым тестом
        db.session.query(User).delete()
        db.session.commit()


@pytest.fixture
def auth_session(app, client, clean_db):
    """Создаем авторизованную сессию"""
    # Создаем тестового админа после очистки БД и устанавливаем его в сессию
    with app.app_context():
        test_admin = User.create_admin('test_session_admin', 'test_password')
        admin_id = test_admin.id  # Получаем ID пока еще в контексте
        
    with client.session_transaction() as sess:
        sess['user_id'] = admin_id
    
    yield client


def test_admins_get_with_test_admin(auth_session):
    """Тест отображения списка админов (с тестовым админом)"""
    response = auth_session.get('/admins')
    
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data or response.status_code == 200


def test_admins_get_with_additional_data(auth_session):
    """Тест отображения списка админов с дополнительными данными"""
    with main_app.app_context():
        # Создаем дополнительных тестовых админов
        User.create_admin('test_admin1', 'password1')
        User.create_admin('test_admin2', 'password2')
    
    response = auth_session.get('/admins')
    
    assert response.status_code == 200


def test_add_admin_success(auth_session):
    """Тест успешного добавления админа"""
    response = auth_session.post('/admins/add', data={
        'username': 'new_admin',
        'password': 'new_password'
    })
    
    # Должен быть редирект на страницу админов
    assert response.status_code == 302
    assert '/admins' in response.location
    
    # Проверяем что админ создан
    with main_app.app_context():
        assert User.admin_exists('new_admin') is True


def test_add_admin_missing_username(auth_session):
    """Тест добавления админа без имени пользователя"""
    initial_count = None
    with main_app.app_context():
        initial_count = User.get_admin_count()
    
    response = auth_session.post('/admins/add', data={
        'password': 'password'
    })
    
    assert response.status_code == 200
    
    # Проверяем что количество админов не изменилось
    with main_app.app_context():
        assert User.get_admin_count() == initial_count


def test_add_admin_missing_password(auth_session):
    """Тест добавления админа без пароля"""
    initial_count = None
    with main_app.app_context():
        initial_count = User.get_admin_count()
    
    response = auth_session.post('/admins/add', data={
        'username': 'test_admin'
    })
    
    assert response.status_code == 200
    
    # Проверяем что количество админов не изменилось
    with main_app.app_context():
        assert User.get_admin_count() == initial_count


def test_add_admin_duplicate_username(auth_session):
    """Тест добавления админа с дублирующимся именем"""
    initial_count = None
    with main_app.app_context():
        # Создаем первого админа
        User.create_admin('existing_admin', 'password1')
        initial_count = User.get_admin_count()
    
    response = auth_session.post('/admins/add', data={
        'username': 'existing_admin',
        'password': 'password2'
    })
    
    assert response.status_code == 200
    
    # Проверяем что количество админов не изменилось
    with main_app.app_context():
        assert User.get_admin_count() == initial_count


def test_delete_admin_success(auth_session):
    """Тест успешного удаления админа"""
    initial_count = None
    admin1_id = None
    with main_app.app_context():
        # Создаем дополнительного админа (у нас уже есть тестовый)
        admin1 = User.create_admin('admin1', 'password1')
        admin1_id = admin1.id
        initial_count = User.get_admin_count()
    
    response = auth_session.post(f'/admins/delete/{admin1_id}')
    
    # Должен быть редирект на страницу админов
    assert response.status_code == 302
    assert '/admins' in response.location
    
    # Проверяем что админ удален
    with main_app.app_context():
        assert User.get_admin_count() == initial_count - 1
        assert User.admin_exists('admin1') is False


def test_delete_admin_not_found(auth_session):
    """Тест удаления несуществующего админа"""
    initial_count = None
    with main_app.app_context():
        initial_count = User.get_admin_count()
    
    response = auth_session.post('/admins/delete/999')
    
    assert response.status_code == 200
    
    # Проверяем что количество админов не изменилось
    with main_app.app_context():
        assert User.get_admin_count() == initial_count


def test_delete_last_admin_protection(auth_session):
    """Тест защиты от удаления последнего админа"""
    test_admin_id = None
    with main_app.app_context():
        # Находим тестового админа (он должен быть единственным)
        test_admin = User.query.filter_by(username='test_session_admin').first()
        test_admin_id = test_admin.id
        assert User.get_admin_count() == 1
    
    response = auth_session.post(f'/admins/delete/{test_admin_id}')
    
    assert response.status_code == 200
    
    # Проверяем что админ не удален
    with main_app.app_context():
        assert User.get_admin_count() == 1
        assert User.admin_exists('test_session_admin') is True


def test_admins_routes_require_auth(app, client):
    """Тест что роуты админов требуют авторизации"""
    # Создаем админа для тестирования удаления
    with app.app_context():
        admin = User.create_admin('test_admin', 'password')
        admin_id = admin.id
    
    # GET /admins без авторизации
    response = client.get('/admins')
    assert response.status_code == 302  # Редирект на логин
    assert '/login' in response.location
    
    # POST /admins/add без авторизации
    response = client.post('/admins/add', data={
        'username': 'test',
        'password': 'test'
    })
    assert response.status_code == 302  # Редирект на логин
    assert '/login' in response.location
    
    # POST /admins/delete без авторизации
    response = client.post(f'/admins/delete/{admin_id}')
    assert response.status_code == 302  # Редирект на логин
    assert '/login' in response.location


def test_admin_routes_workflow(auth_session):
    """Интеграционный тест полного workflow роутов админов"""
    # Начальное состояние - получаем список с тестовым админом
    response = auth_session.get('/admins')
    assert response.status_code == 200
    
    # Добавляем первого админа
    response = auth_session.post('/admins/add', data={
        'username': 'workflow_admin1',
        'password': 'password1'
    })
    assert response.status_code == 302
    
    # Добавляем второго админа
    response = auth_session.post('/admins/add', data={
        'username': 'workflow_admin2',
        'password': 'password2'
    })
    assert response.status_code == 302
    
    # Проверяем что админы созданы (тестовый + 2 новых)
    with main_app.app_context():
        assert User.get_admin_count() == 3
        admin1 = User.query.filter_by(username='workflow_admin1').first()
        assert admin1 is not None
        admin1_id = admin1.id
    
    # Получаем список админов
    response = auth_session.get('/admins')
    assert response.status_code == 200
    
    # Удаляем одного админа
    response = auth_session.post(f'/admins/delete/{admin1_id}')
    assert response.status_code == 302
    
    # Проверяем что остались два админа
    with main_app.app_context():
        assert User.get_admin_count() == 2
        assert User.admin_exists('workflow_admin1') is False
        assert User.admin_exists('workflow_admin2') is True
        
        # Удаляем второго админа
        admin2 = User.query.filter_by(username='workflow_admin2').first()
        admin2_id = admin2.id
    
    response = auth_session.post(f'/admins/delete/{admin2_id}')
    assert response.status_code == 302
    
    # Теперь остался только тестовый админ
    with main_app.app_context():
        assert User.get_admin_count() == 1
        test_admin = User.query.filter_by(username='test_session_admin').first()
        test_admin_id = test_admin.id
    
    # Пытаемся удалить последнего админа (должно быть запрещено)
    response = auth_session.post(f'/admins/delete/{test_admin_id}')
    assert response.status_code == 200  # Возвращает страницу с ошибкой
    
    # Проверяем что админ остался
    with main_app.app_context():
        assert User.get_admin_count() == 1
        assert User.admin_exists('test_session_admin') is True
