import pytest
from models import db, User, Profile
from sqlalchemy import inspect

class TestModels:
    """Тесты для SQLAlchemy моделей"""
    
    def test_user_model_definition(self):
        """Тест корректности определения модели User"""
        # Проверка названия таблицы
        assert User.__tablename__ == 'users'
        
        # Проверка bind key
        assert User.__bind_key__ == 'sqlite'
        
        # Проверка что это наследник db.Model
        assert issubclass(User, db.Model)
    
    def test_user_model_fields(self):
        """Тест наличия всех полей модели User"""
        # Получаем список колонок
        columns = User.__table__.columns
        
        # Проверяем наличие всех полей
        assert 'id' in columns
        assert 'username' in columns
        assert 'password_hash' in columns
        assert 'created_at' in columns
        
        # Проверяем типы полей
        assert str(columns['id'].type) == 'INTEGER'
        assert str(columns['username'].type) == 'VARCHAR(50)'
        assert str(columns['password_hash'].type) == 'VARCHAR(255)'
        assert 'DATETIME' in str(columns['created_at'].type)
        
        # Проверяем ограничения
        assert columns['id'].primary_key is True
        assert columns['id'].autoincrement is True
        assert columns['username'].unique is True
        assert columns['username'].nullable is False
        assert columns['password_hash'].nullable is False
    
    def test_profile_model_definition(self):
        """Тест корректности определения модели Profile"""
        # Проверка названия таблицы
        assert Profile.__tablename__ == 'profiles'
        
        # Проверка bind key
        assert Profile.__bind_key__ == 'postgres'
        
        # Проверка что это наследник db.Model
        assert issubclass(Profile, db.Model)
    
    def test_profile_model_fields(self):
        """Тест наличия всех полей модели Profile"""
        # Получаем список колонок
        columns = Profile.__table__.columns
        
        # Проверяем наличие всех полей
        assert 'pid' in columns
        assert 'data_create' in columns
        assert 'party' in columns
        assert 'domaincount' in columns
        
        # Проверяем типы полей
        assert str(columns['pid'].type) == 'INTEGER'
        assert 'DATETIME' in str(columns['data_create'].type)
        assert 'VARCHAR' in str(columns['party'].type)
        assert str(columns['domaincount'].type) == 'INTEGER'
        
        # Проверяем первичный ключ
        assert columns['pid'].primary_key is True
    
    def test_bind_keys_configuration(self):
        """Тест настройки bind ключей"""
        # Проверяем что модели имеют разные bind ключи
        assert User.__bind_key__ != Profile.__bind_key__
        
        # Проверяем конкретные значения
        assert User.__bind_key__ == 'sqlite'
        assert Profile.__bind_key__ == 'postgres'
    
    def test_model_instances_creation(self):
        """Тест создания экземпляров моделей"""
        # Создание экземпляра User
        user = User()
        assert isinstance(user, User)
        assert isinstance(user, db.Model)
        
        # Создание экземпляра Profile
        profile = Profile()
        assert isinstance(profile, Profile)
        assert isinstance(profile, db.Model)

if __name__ == '__main__':
    # Запуск тестов без pytest (базовая проверка)
    test_instance = TestModels()
    
    print("Запуск базовых тестов моделей...")
    
    tests = [
        ('Тест определения модели User', test_instance.test_user_model_definition),
        ('Тест полей модели User', test_instance.test_user_model_fields),
        ('Тест определения модели Profile', test_instance.test_profile_model_definition),
        ('Тест полей модели Profile', test_instance.test_profile_model_fields),
        ('Тест конфигурации bind ключей', test_instance.test_bind_keys_configuration),
        ('Тест создания экземпляров моделей', test_instance.test_model_instances_creation)
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name} - ПРОЙДЕН")
        except Exception as e:
            print(f"✗ {test_name} - ПРОВАЛЕН: {e}")
    
    print("\nВсе тесты моделей завершены!")
