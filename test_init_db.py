import os
import tempfile
import pytest
from werkzeug.security import check_password_hash
from app import app, init_db
from models import db, User

class TestInitDB:
    """Тесты для функции инициализации базы данных"""
    
    @pytest.fixture
    def temp_db(self):
        """Создание временной БД для тестов"""
        # Создаем временный файл для БД
        db_fd, db_path = tempfile.mkstemp()
        app.config['ADMIN_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['ADMIN_DATABASE_URI']
        app.config['SQLALCHEMY_BINDS'] = {
            'sqlite': app.config['ADMIN_DATABASE_URI'],
            'postgres': app.config['PROFILES_DATABASE_URI']
        }
        app.config['TESTING'] = True
        
        yield db_path
        
        # Очистка после теста
        os.close(db_fd)
        os.unlink(db_path)
    
    def test_init_db_creates_sqlite_tables(self, temp_db):
        """Тест создания SQLite таблиц"""
        with app.app_context():
            # Вызываем функцию инициализации
            init_db()
            
            # Проверяем что таблица users создана
            from sqlalchemy import inspect
            inspector = inspect(db.get_engine(bind='sqlite'))
            tables = inspector.get_table_names()
            
            assert 'users' in tables
    
    def test_init_db_creates_default_admin(self, temp_db):
        """Тест создания дефолтного админа"""
        with app.app_context():
            # Очищаем таблицу перед тестом
            db.session.query(User).delete()
            db.session.commit()
            
            # Проверяем что админов нет
            admin_count_before = User.query.count()
            assert admin_count_before == 0
            
            # Вызываем функцию инициализации
            init_db()
            
            # Проверяем что админ создан
            admin_count_after = User.query.count()
            assert admin_count_after == 1
            
            # Проверяем данные админа
            admin = User.query.filter_by(username='admin').first()
            assert admin is not None
            assert admin.username == 'admin'
            assert admin.password_hash is not None
    
    def test_init_db_password_hashing(self, temp_db):
        """Тест хеширования пароля"""
        with app.app_context():
            # Вызываем функцию инициализации
            init_db()
            
            # Получаем созданного админа
            admin = User.query.filter_by(username='admin').first()
            
            # Проверяем что пароль захеширован
            assert admin.password_hash != 'admin'  # Пароль не в открытом виде
            assert len(admin.password_hash) > 20   # Хеш должен быть длинным
            
            # Проверяем что хеш корректный
            assert check_password_hash(admin.password_hash, 'admin')
            assert not check_password_hash(admin.password_hash, 'wrong_password')
    
    def test_init_db_does_not_create_duplicate_admin(self, temp_db):
        """Тест что дублирующий админ не создается"""
        with app.app_context():
            # Первый вызов инициализации
            init_db()
            admin_count_first = User.query.count()
            assert admin_count_first == 1
            
            # Второй вызов инициализации
            init_db()
            admin_count_second = User.query.count()
            assert admin_count_second == 1  # Должен остаться один админ
            
            # Проверяем что это тот же админ
            admins = User.query.filter_by(username='admin').all()
            assert len(admins) == 1
    
    def test_admin_fields_are_correct(self, temp_db):
        """Тест корректности полей созданного админа"""
        with app.app_context():
            init_db()
            
            admin = User.query.filter_by(username='admin').first()
            
            # Проверяем все поля
            assert admin.id is not None
            assert isinstance(admin.id, int)
            assert admin.username == 'admin'
            assert admin.password_hash is not None
            assert admin.created_at is not None

if __name__ == '__main__':
    # Запуск тестов без pytest (базовая проверка)
    print("Запуск базовых тестов инициализации БД...")
    
    # Создаем временную БД для тестов
    import tempfile
    db_fd, db_path = tempfile.mkstemp()
    
    try:
        # Настраиваем приложение для тестов
        app.config['ADMIN_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['ADMIN_DATABASE_URI']
        app.config['SQLALCHEMY_BINDS'] = {
            'sqlite': app.config['ADMIN_DATABASE_URI'],
            'postgres': app.config.get('PROFILES_DATABASE_URI', 'postgresql://test')
        }
        app.config['TESTING'] = True
        
        with app.app_context():
            # Тест создания таблиц
            try:
                init_db()
                from sqlalchemy import inspect
                inspector = inspect(db.get_engine(bind='sqlite'))
                tables = inspector.get_table_names()
                assert 'users' in tables
                print("✓ Тест создания SQLite таблиц - ПРОЙДЕН")
            except Exception as e:
                print(f"✗ Тест создания SQLite таблиц - ПРОВАЛЕН: {e}")
            
            # Тест создания админа
            try:
                admin = User.query.filter_by(username='admin').first()
                assert admin is not None
                assert admin.username == 'admin'
                print("✓ Тест создания дефолтного админа - ПРОЙДЕН")
            except Exception as e:
                print(f"✗ Тест создания дефолтного админа - ПРОВАЛЕН: {e}")
            
            # Тест хеширования пароля
            try:
                admin = User.query.filter_by(username='admin').first()
                assert admin.password_hash != 'admin'
                assert check_password_hash(admin.password_hash, 'admin')
                print("✓ Тест хеширования пароля - ПРОЙДЕН")
            except Exception as e:
                print(f"✗ Тест хеширования пароля - ПРОВАЛЕН: {e}")
        
    finally:
        # Очистка
        os.close(db_fd)
        os.unlink(db_path)
    
    print("\nВсе тесты инициализации БД завершены!")
