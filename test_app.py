import pytest
from app import app

class TestFlaskApp:
    """Тесты для Flask приложения админки фермы профилей"""
    
    @pytest.fixture
    def client(self):
        """Создание тестового клиента"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_app_creation(self):
        """Тест создания Flask приложения"""
        assert app is not None
        assert app.name == 'app'
    
    def test_main_route(self, client):
        """Тест доступности главного роута"""
        response = client.get('/')
        assert response.status_code == 200
        assert response.data.decode() == "Admin Panel"
    
    def test_database_config(self):
        """Тест наличия конфигурации баз данных"""
        # Проверка наличия секретного ключа
        assert 'SECRET_KEY' in app.config
        assert app.config['SECRET_KEY'] is not None
        
        # Проверка конфигурации SQLite для админов
        assert 'ADMIN_DATABASE_URI' in app.config
        assert 'sqlite:///admin.db' in app.config['ADMIN_DATABASE_URI']
        
        # Проверка конфигурации PostgreSQL для профилей
        assert 'PROFILES_DATABASE_URI' in app.config
        assert app.config['PROFILES_DATABASE_URI'] is not None
        # Проверяем что конфигурация содержит postgresql
        assert 'postgresql://' in app.config['PROFILES_DATABASE_URI']

if __name__ == '__main__':
    # Запуск тестов без pytest (базовая проверка)
    test_instance = TestFlaskApp()
    
    print("Запуск базовых тестов Flask приложения...")
    
    # Тест создания приложения
    try:
        test_instance.test_app_creation()
        print("✓ Тест создания приложения - ПРОЙДЕН")
    except Exception as e:
        print(f"✗ Тест создания приложения - ПРОВАЛЕН: {e}")
    
    # Тест конфигурации БД
    try:
        test_instance.test_database_config()
        print("✓ Тест конфигурации БД - ПРОЙДЕН")
    except Exception as e:
        print(f"✗ Тест конфигурации БД - ПРОВАЛЕН: {e}")
    
    # Тест главного роута
    try:
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            assert response.data.decode() == "Admin Panel"
        print("✓ Тест главного роута - ПРОЙДЕН")
    except Exception as e:
        print(f"✗ Тест главного роута - ПРОВАЛЕН: {e}")
    
    print("\nВсе базовые тесты завершены!")
