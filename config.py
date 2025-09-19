"""
Конфигурация приложения для Admin Panel
Поддерживает загрузку из .env файла и переменных окружения
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (если существует)
load_dotenv()


class Config:
    """Базовая конфигурация"""
    
    @classmethod
    def get_secret_key(cls):
        """Получить SECRET_KEY из переменных окружения"""
        return os.environ.get('SECRET_KEY')
    
    @classmethod
    def validate_secret_key(cls):
        """Валидация SECRET_KEY"""
        secret_key = cls.get_secret_key()
        if not secret_key:
            raise ValueError("SECRET_KEY environment variable is required")
        return secret_key
    
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    # SQLAlchemy Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Application Configuration
    PORT = int(os.environ.get('PORT', 8000))
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def get_profiles_database_uri():
        """
        Получить URI для базы данных профилей (только чтение)
        """
        # Сначала проверяем полную строку подключения
        profiles_url = os.environ.get('PROFILES_DATABASE_URL')
        if profiles_url:
            return profiles_url
        
        # Если нет, собираем из отдельных переменных
        host = os.environ.get('PROFILES_DB_HOST')
        port = os.environ.get('PROFILES_DB_PORT', '5432')
        name = os.environ.get('PROFILES_DB_NAME')
        user = os.environ.get('PROFILES_DB_USER')
        password = os.environ.get('PROFILES_DB_PASSWORD')
        
        if not all([host, name, user, password]):
            raise ValueError(
                "Profiles database configuration is incomplete. "
                "Either set PROFILES_DATABASE_URL or all of: "
                "PROFILES_DB_HOST, PROFILES_DB_NAME, PROFILES_DB_USER, PROFILES_DB_PASSWORD"
            )
        
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    @staticmethod
    def get_admin_database_uri():
        """
        Получить URI для базы данных админов (полные права)
        """
        # Сначала проверяем полную строку подключения
        admin_url = os.environ.get('ADMIN_DATABASE_URL')
        if admin_url:
            return admin_url
        
        # Railway автоматически создает DATABASE_URL, можем использовать его для админов
        railway_url = os.environ.get('DATABASE_URL')
        if railway_url:
            return railway_url
        
        # Если нет, собираем из отдельных переменных
        host = os.environ.get('ADMIN_DB_HOST')
        port = os.environ.get('ADMIN_DB_PORT', '5432')
        name = os.environ.get('ADMIN_DB_NAME')
        user = os.environ.get('ADMIN_DB_USER')
        password = os.environ.get('ADMIN_DB_PASSWORD')
        
        if not all([host, name, user, password]):
            raise ValueError(
                "Admin database configuration is incomplete. "
                "Either set ADMIN_DATABASE_URL, DATABASE_URL or all of: "
                "ADMIN_DB_HOST, ADMIN_DB_NAME, ADMIN_DB_USER, ADMIN_DB_PASSWORD"
            )
        
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    @classmethod
    def init_app(cls, app):
        """Инициализация конфигурации для Flask приложения"""
        
        # Основные настройки Flask
        app.config['SECRET_KEY'] = cls.validate_secret_key()
        app.config['DEBUG'] = cls.DEBUG
        
        # Настройки SQLAlchemy
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = cls.SQLALCHEMY_TRACK_MODIFICATIONS
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = cls.SQLALCHEMY_ENGINE_OPTIONS
        
        # Получаем URI для баз данных
        try:
            profiles_db_uri = cls.get_profiles_database_uri()
            admin_db_uri = cls.get_admin_database_uri()
        except ValueError as e:
            raise ValueError(f"Database configuration error: {e}")
        
        # Конфигурация для двух баз данных
        app.config['SQLALCHEMY_DATABASE_URI'] = admin_db_uri  # Основная БД для админов
        app.config['SQLALCHEMY_BINDS'] = {
            'admin': admin_db_uri,      # PostgreSQL для админов (полные права)
            'profiles': profiles_db_uri  # PostgreSQL для профилей (только чтение)
        }
        
        # Сохраняем URI для отладки (без паролей)
        app.config['_ADMIN_DB_URI'] = cls._hide_password(admin_db_uri)
        app.config['_PROFILES_DB_URI'] = cls._hide_password(profiles_db_uri)
    
    @staticmethod
    def _hide_password(uri):
        """Скрыть пароль в URI для безопасного логирования"""
        if '://' in uri and '@' in uri:
            scheme, rest = uri.split('://', 1)
            if '@' in rest:
                creds, host_part = rest.split('@', 1)
                if ':' in creds:
                    user, _ = creds.split(':', 1)
                    return f"{scheme}://{user}:***@{host_part}"
        return uri


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Дополнительные настройки безопасности для продакшена
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': 10,
        'max_overflow': 20,
    }


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    DEBUG = True
    
    @classmethod
    def get_secret_key(cls):
        """Получить SECRET_KEY для тестов"""
        return 'test_secret_key'
    
    @classmethod
    def validate_secret_key(cls):
        """Валидация SECRET_KEY для тестов"""
        return cls.get_secret_key()
    
    # Для тестов используем SQLite в памяти
    @classmethod
    def init_app(cls, app):
        # Переопределяем для использования SQLite в тестах
        app.config['SECRET_KEY'] = cls.validate_secret_key()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_BINDS'] = {
            'admin': 'sqlite:///:memory:',
            'profiles': 'sqlite:///:memory:'
        }
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Получить конфигурацию по имени
    
    Args:
        config_name: Имя конфигурации ('development', 'production', 'testing')
                    Если не указано, берется из FLASK_ENV
    
    Returns:
        Класс конфигурации
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])


def validate_config():
    """
    Валидация конфигурации - проверка всех обязательных переменных
    
    Raises:
        ValueError: Если отсутствуют обязательные переменные
    """
    # Проверяем SECRET_KEY
    if not os.environ.get('SECRET_KEY'):
        raise ValueError(
            "Missing required environment variables: SECRET_KEY\n"
            "Please set them in your .env file or environment"
        )
    
    # Проверяем конфигурацию БД только если не в режиме тестирования
    if os.environ.get('FLASK_ENV') != 'testing':
        try:
            Config.get_admin_database_uri()
            Config.get_profiles_database_uri()
        except ValueError as e:
            raise ValueError(f"Database configuration error: {e}")
    
    print("✅ Configuration validation passed")
