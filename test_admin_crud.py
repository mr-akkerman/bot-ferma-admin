import pytest
import os
import tempfile
from flask import Flask
from models import db, User
from werkzeug.security import check_password_hash


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


def test_admin_exists(app_context):
    """Тест проверки существования админа"""
    # Создаем тестового админа
    User.create_admin('test_admin', 'test_password')
    
    # Проверяем что админ существует
    assert User.admin_exists('test_admin') is True
    
    # Проверяем что несуществующий админ не найден
    assert User.admin_exists('nonexistent_admin') is False


def test_get_admin_count(app_context):
    """Тест подсчета количества админов"""
    # Изначально админов нет
    assert User.get_admin_count() == 0
    
    # Создаем админа
    User.create_admin('admin1', 'password1')
    assert User.get_admin_count() == 1
    
    # Создаем еще одного админа
    User.create_admin('admin2', 'password2')
    assert User.get_admin_count() == 2


def test_create_admin(app_context):
    """Тест создания админа"""
    # Создаем админа
    admin = User.create_admin('new_admin', 'secure_password')
    
    # Проверяем что админ создан
    assert admin is not None
    assert admin.username == 'new_admin'
    assert admin.id is not None
    assert admin.created_at is not None
    
    # Проверяем что пароль хеширован правильно
    assert check_password_hash(admin.password_hash, 'secure_password')
    
    # Проверяем что админ есть в базе
    assert User.admin_exists('new_admin') is True
    assert User.get_admin_count() == 1


def test_get_all_admins(app_context):
    """Тест получения всех админов"""
    # Создаем несколько админов
    User.create_admin('admin1', 'password1')
    User.create_admin('admin2', 'password2')
    User.create_admin('admin3', 'password3')
    
    # Получаем всех админов
    admins = User.get_all_admins()
    
    # Проверяем результат
    assert len(admins) == 3
    
    # Проверяем структуру данных (id, username, created_at)
    admin_usernames = [admin.username for admin in admins]
    assert 'admin1' in admin_usernames
    assert 'admin2' in admin_usernames
    assert 'admin3' in admin_usernames
    
    # Проверяем что у каждого админа есть все необходимые поля
    for admin in admins:
        assert hasattr(admin, 'id')
        assert hasattr(admin, 'username')
        assert hasattr(admin, 'created_at')


def test_delete_admin_success(app_context):
    """Тест успешного удаления админа"""
    # Создаем двух админов
    admin1 = User.create_admin('admin1', 'password1')
    admin2 = User.create_admin('admin2', 'password2')
    
    assert User.get_admin_count() == 2
    
    # Удаляем одного админа
    result = User.delete_admin(admin1.id)
    
    # Проверяем результат удаления
    assert result is True
    assert User.get_admin_count() == 1
    assert User.admin_exists('admin1') is False
    assert User.admin_exists('admin2') is True


def test_delete_admin_not_found(app_context):
    """Тест удаления несуществующего админа"""
    # Создаем одного админа
    User.create_admin('admin1', 'password1')
    
    # Пытаемся удалить несуществующего админа
    result = User.delete_admin(999)
    
    # Проверяем что удаление не удалось
    assert result is False
    assert User.get_admin_count() == 1


def test_delete_last_admin_protection(app_context):
    """Тест защиты от удаления последнего админа"""
    # Создаем только одного админа
    admin = User.create_admin('last_admin', 'password')
    
    assert User.get_admin_count() == 1
    
    # Пытаемся удалить последнего админа
    with pytest.raises(ValueError) as exc_info:
        User.delete_admin(admin.id)
    
    # Проверяем сообщение об ошибке
    assert "Нельзя удалить последнего админа" in str(exc_info.value)
    
    # Проверяем что админ не был удален
    assert User.get_admin_count() == 1
    assert User.admin_exists('last_admin') is True


def test_create_admin_with_duplicate_username(app_context):
    """Тест создания админа с дублирующимся именем"""
    # Создаем первого админа
    User.create_admin('duplicate_admin', 'password1')
    
    # Пытаемся создать админа с тем же именем
    # SQLAlchemy должна выбросить исключение из-за UNIQUE constraint
    with pytest.raises(Exception):
        User.create_admin('duplicate_admin', 'password2')


def test_admin_crud_workflow(app_context):
    """Интеграционный тест полного CRUD цикла"""
    # Начальное состояние
    assert User.get_admin_count() == 0
    assert len(User.get_all_admins()) == 0
    
    # Создаем админов
    admin1 = User.create_admin('workflow_admin1', 'password1')
    admin2 = User.create_admin('workflow_admin2', 'password2')
    admin3 = User.create_admin('workflow_admin3', 'password3')
    
    # Проверяем создание
    assert User.get_admin_count() == 3
    assert User.admin_exists('workflow_admin1') is True
    assert User.admin_exists('workflow_admin2') is True
    assert User.admin_exists('workflow_admin3') is True
    
    all_admins = User.get_all_admins()
    assert len(all_admins) == 3
    
    # Удаляем одного админа
    User.delete_admin(admin2.id)
    assert User.get_admin_count() == 2
    assert User.admin_exists('workflow_admin2') is False
    assert User.admin_exists('workflow_admin1') is True
    assert User.admin_exists('workflow_admin3') is True
    
    # Удаляем еще одного админа
    User.delete_admin(admin3.id)
    assert User.get_admin_count() == 1
    assert User.admin_exists('workflow_admin3') is False
    assert User.admin_exists('workflow_admin1') is True
    
    # Пытаемся удалить последнего админа (должно быть запрещено)
    with pytest.raises(ValueError):
        User.delete_admin(admin1.id)
    
    # Проверяем что последний админ остался
    assert User.get_admin_count() == 1
    assert User.admin_exists('workflow_admin1') is True
