#!/usr/bin/env python3
"""
Тесты для проверки новой конфигурации с PostgreSQL
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from config import Config, get_config, validate_config, DevelopmentConfig, ProductionConfig, TestingConfig


class TestConfig:
    """Тесты для системы конфигурации"""
    
    def test_config_classes_exist(self):
        """Проверка существования классов конфигурации"""
        assert Config is not None
        assert DevelopmentConfig is not None
        assert ProductionConfig is not None
        assert TestingConfig is not None
    
    def test_get_config_default(self):
        """Проверка получения конфигурации по умолчанию"""
        with patch.dict('os.environ', {}, clear=True):
            config_class = get_config()
            assert config_class == DevelopmentConfig
    
    def test_get_config_by_name(self):
        """Проверка получения конфигурации по имени"""
        assert get_config('development') == DevelopmentConfig
        assert get_config('production') == ProductionConfig
        assert get_config('testing') == TestingConfig
        assert get_config('unknown') == DevelopmentConfig  # fallback
    
    def test_get_config_from_env(self):
        """Проверка получения конфигурации из переменной окружения"""
        with patch.dict('os.environ', {'FLASK_ENV': 'production'}):
            config_class = get_config()
            assert config_class == ProductionConfig
    
    def test_profiles_database_uri_from_url(self):
        """Проверка получения URI профилей из полной строки"""
        test_url = "postgresql://user:pass@host:5432/db"
        with patch.dict('os.environ', {'PROFILES_DATABASE_URL': test_url}):
            uri = Config.get_profiles_database_uri()
            assert uri == test_url
    
    def test_profiles_database_uri_from_parts(self):
        """Проверка получения URI профилей из отдельных переменных"""
        env_vars = {
            'PROFILES_DB_HOST': 'localhost',
            'PROFILES_DB_PORT': '5432',
            'PROFILES_DB_NAME': 'testdb',
            'PROFILES_DB_USER': 'testuser',
            'PROFILES_DB_PASSWORD': 'testpass'
        }
        with patch.dict('os.environ', env_vars):
            uri = Config.get_profiles_database_uri()
            expected = "postgresql://testuser:testpass@localhost:5432/testdb"
            assert uri == expected
    
    def test_profiles_database_uri_missing_vars(self):
        """Проверка ошибки при отсутствии переменных профилей"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Profiles database configuration is incomplete"):
                Config.get_profiles_database_uri()
    
    def test_admin_database_uri_from_database_url(self):
        """Проверка получения URI админов из DATABASE_URL (Railway)"""
        test_url = "postgresql://admin:pass@railwayhost:5432/admindb"
        with patch.dict('os.environ', {'DATABASE_URL': test_url}):
            uri = Config.get_admin_database_uri()
            assert uri == test_url
    
    def test_admin_database_uri_from_admin_url(self):
        """Проверка получения URI админов из ADMIN_DATABASE_URL"""
        test_url = "postgresql://admin:pass@host:5432/admindb"
        with patch.dict('os.environ', {'ADMIN_DATABASE_URL': test_url}):
            uri = Config.get_admin_database_uri()
            assert uri == test_url
    
    def test_admin_database_uri_from_parts(self):
        """Проверка получения URI админов из отдельных переменных"""
        env_vars = {
            'ADMIN_DB_HOST': 'localhost',
            'ADMIN_DB_PORT': '5432',
            'ADMIN_DB_NAME': 'admindb',
            'ADMIN_DB_USER': 'adminuser',
            'ADMIN_DB_PASSWORD': 'adminpass'
        }
        with patch.dict('os.environ', env_vars):
            uri = Config.get_admin_database_uri()
            expected = "postgresql://adminuser:adminpass@localhost:5432/admindb"
            assert uri == expected
    
    def test_admin_database_uri_missing_vars(self):
        """Проверка ошибки при отсутствии переменных админов"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Admin database configuration is incomplete"):
                Config.get_admin_database_uri()
    
    def test_hide_password(self):
        """Проверка сокрытия пароля в URI"""
        uri = "postgresql://user:secretpass@host:5432/db"
        hidden = Config._hide_password(uri)
        assert "secretpass" not in hidden
        assert "user:***@host:5432/db" in hidden
    
    def test_validate_config_missing_secret_key(self):
        """Проверка валидации с отсутствующим SECRET_KEY"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: SECRET_KEY"):
                validate_config()
    
    def test_validate_config_success(self):
        """Проверка успешной валидации"""
        env_vars = {
            'SECRET_KEY': 'test-secret-key',
            'FLASK_ENV': 'testing'  # для тестирования пропускаем проверку БД
        }
        with patch.dict('os.environ', env_vars):
            # Не должно вызвать исключение
            validate_config()


class TestConfigIntegration:
    """Интеграционные тесты конфигурации"""
    
    def test_config_init_app(self):
        """Проверка инициализации конфигурации в Flask приложении"""
        from flask import Flask
        
        app = Flask(__name__)
        
        env_vars = {
            'SECRET_KEY': 'test-secret-key',
            'PROFILES_DATABASE_URL': 'postgresql://user:pass@host:5432/profiles',
            'ADMIN_DATABASE_URL': 'postgresql://admin:pass@host:5432/admin'
        }
        
        with patch.dict('os.environ', env_vars):
            Config.init_app(app)
            
            # Проверяем основные настройки
            assert app.config['SECRET_KEY'] == 'test-secret-key'
            assert 'SQLALCHEMY_DATABASE_URI' in app.config
            assert 'SQLALCHEMY_BINDS' in app.config
            
            # Проверяем binds
            binds = app.config['SQLALCHEMY_BINDS']
            assert 'admin' in binds
            assert 'profiles' in binds
            assert binds['profiles'] == 'postgresql://user:pass@host:5432/profiles'
            assert binds['admin'] == 'postgresql://admin:pass@host:5432/admin'
    
    def test_testing_config_init_app(self):
        """Проверка инициализации тестовой конфигурации"""
        from flask import Flask
        
        app = Flask(__name__)
        TestingConfig.init_app(app)
        
        # Тестовая конфигурация должна использовать SQLite в памяти
        assert app.config['TESTING'] is True
        assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_DATABASE_URI']
        assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_BINDS']['admin']
        assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_BINDS']['profiles']


class TestModelChanges:
    """Проверка изменений в моделях"""
    
    def test_user_model_bind_key(self):
        """Проверка правильного bind_key для модели User"""
        from models import User
        assert User.__bind_key__ == 'admin'
    
    def test_profile_model_bind_key(self):
        """Проверка правильного bind_key для модели Profile"""
        from models import Profile
        assert Profile.__bind_key__ == 'profiles'


class TestDotenvIntegration:
    """Тесты интеграции с python-dotenv"""
    
    def test_dotenv_loading(self):
        """Проверка загрузки переменных из .env файла"""
        # Создаем временный .env файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_VAR=test_value\n')
            f.write('SECRET_KEY=dotenv_secret\n')
            env_file = f.name
        
        try:
            # Импортируем dotenv и загружаем файл
            from dotenv import load_dotenv
            load_dotenv(env_file)
            
            # Проверяем что переменные загрузились
            assert os.environ.get('TEST_VAR') == 'test_value'
            assert os.environ.get('SECRET_KEY') == 'dotenv_secret'
            
        finally:
            # Очищаем
            os.unlink(env_file)
            if 'TEST_VAR' in os.environ:
                del os.environ['TEST_VAR']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
