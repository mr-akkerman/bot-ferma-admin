import pytest
import os
import tempfile
from flask import Flask
from models import db, User
from admin_management import get_admins_list, add_admin, remove_admin


@pytest.fixture
def app():
    """Создаем тестовое Flask приложение"""
    app = Flask(__name__)
    
    # Используем временную базу данных для тестов
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_BINDS'] = {
        'sqlite': f'sqlite:///{db_path}',
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Создаем таблицы
        db.create_all(bind_key='sqlite')
        yield app
    
    # Очищаем после тестов
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def app_context(app):
    """Создаем контекст приложения для тестов"""
    with app.app_context():
        yield app


def test_get_admins_list_empty(app_context):
    """Тест получения пустого списка админов"""
    result = get_admins_list()
    
    assert result['success'] is True
    assert result['admins'] == []


def test_get_admins_list_with_data(app_context):
    """Тест получения списка админов с данными"""
    # Создаем тестовых админов
    User.create_admin('admin1', 'password1')
    User.create_admin('admin2', 'password2')
    
    result = get_admins_list()
    
    assert result['success'] is True
    assert len(result['admins']) == 2
    
    # Проверяем структуру данных
    for admin in result['admins']:
        assert 'id' in admin
        assert 'username' in admin
        assert 'created_at' in admin
    
    # Проверяем что есть нужные админы
    usernames = [admin['username'] for admin in result['admins']]
    assert 'admin1' in usernames
    assert 'admin2' in usernames


def test_add_admin_success(app_context):
    """Тест успешного добавления админа"""
    result = add_admin('new_admin', 'secure_password')
    
    assert result['success'] is True
    assert 'admin' in result
    assert result['admin']['username'] == 'new_admin'
    assert result['admin']['id'] is not None
    assert result['admin']['created_at'] is not None
    
    # Проверяем что админ действительно создан
    assert User.admin_exists('new_admin') is True
    assert User.get_admin_count() == 1


def test_add_admin_duplicate_username(app_context):
    """Тест добавления админа с дублирующимся именем"""
    # Создаем первого админа
    User.create_admin('existing_admin', 'password1')
    
    # Пытаемся создать админа с тем же именем
    result = add_admin('existing_admin', 'password2')
    
    assert result['success'] is False
    assert 'error' in result
    assert 'уже существует' in result['error']
    
    # Проверяем что количество админов не изменилось
    assert User.get_admin_count() == 1


def test_remove_admin_success(app_context):
    """Тест успешного удаления админа"""
    # Создаем двух админов
    admin1 = User.create_admin('admin1', 'password1')
    admin2 = User.create_admin('admin2', 'password2')
    
    assert User.get_admin_count() == 2
    
    # Удаляем одного админа
    result = remove_admin(admin1.id)
    
    assert result['success'] is True
    assert 'message' in result
    assert str(admin1.id) in result['message']
    
    # Проверяем что админ удален
    assert User.get_admin_count() == 1
    assert User.admin_exists('admin1') is False
    assert User.admin_exists('admin2') is True


def test_remove_admin_not_found(app_context):
    """Тест удаления несуществующего админа"""
    # Создаем одного админа
    User.create_admin('admin1', 'password1')
    
    # Пытаемся удалить несуществующего админа
    result = remove_admin(999)
    
    assert result['success'] is False
    assert 'error' in result
    assert 'не найден' in result['error']
    
    # Проверяем что количество админов не изменилось
    assert User.get_admin_count() == 1


def test_remove_last_admin_protection(app_context):
    """Тест защиты от удаления последнего админа"""
    # Создаем только одного админа
    admin = User.create_admin('last_admin', 'password')
    
    assert User.get_admin_count() == 1
    
    # Пытаемся удалить последнего админа
    result = remove_admin(admin.id)
    
    assert result['success'] is False
    assert 'error' in result
    assert 'Нельзя удалить последнего админа' in result['error']
    
    # Проверяем что админ не был удален
    assert User.get_admin_count() == 1
    assert User.admin_exists('last_admin') is True


def test_admin_management_workflow(app_context):
    """Интеграционный тест полного workflow управления админами"""
    # Начальное состояние - пустой список
    result = get_admins_list()
    assert result['success'] is True
    assert len(result['admins']) == 0
    
    # Добавляем первого админа
    result = add_admin('workflow_admin1', 'password1')
    assert result['success'] is True
    
    # Проверяем список админов
    result = get_admins_list()
    assert result['success'] is True
    assert len(result['admins']) == 1
    assert result['admins'][0]['username'] == 'workflow_admin1'
    
    # Добавляем второго админа
    result = add_admin('workflow_admin2', 'password2')
    assert result['success'] is True
    
    # Проверяем список админов
    result = get_admins_list()
    assert result['success'] is True
    assert len(result['admins']) == 2
    
    # Получаем ID первого админа для удаления
    admin1_id = None
    for admin in result['admins']:
        if admin['username'] == 'workflow_admin1':
            admin1_id = admin['id']
            break
    
    assert admin1_id is not None
    
    # Удаляем первого админа
    result = remove_admin(admin1_id)
    assert result['success'] is True
    
    # Проверяем что остался только один админ
    result = get_admins_list()
    assert result['success'] is True
    assert len(result['admins']) == 1
    assert result['admins'][0]['username'] == 'workflow_admin2'
    
    # Пытаемся удалить последнего админа (должно быть запрещено)
    admin2_id = result['admins'][0]['id']
    result = remove_admin(admin2_id)
    assert result['success'] is False
    assert 'Нельзя удалить последнего админа' in result['error']
    
    # Проверяем что админ остался
    result = get_admins_list()
    assert result['success'] is True
    assert len(result['admins']) == 1


def test_add_admin_with_empty_username(app_context):
    """Тест добавления админа с пустым именем"""
    result = add_admin('', 'password')
    
    # Функция должна вернуть ошибку
    assert result['success'] is False
    assert 'error' in result


def test_add_admin_with_empty_password(app_context):
    """Тест добавления админа с пустым паролем"""
    result = add_admin('test_admin', '')
    
    # Функция должна создать админа (проверка сложности паролей не требуется)
    assert result['success'] is True
    assert result['admin']['username'] == 'test_admin'
