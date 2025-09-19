#!/usr/bin/env python3
"""
Файл запуска Flask приложения для админ панели фермы

Использование:
    python run.py

Переменные окружения для PostgreSQL:
    DB_HOST - хост PostgreSQL (по умолчанию: localhost)
    DB_PORT - порт PostgreSQL (по умолчанию: 5432)
    DB_NAME - имя базы данных (по умолчанию: farm_profiles)
    DB_USER - пользователь PostgreSQL (по умолчанию: postgres)
    DB_PASSWORD - пароль PostgreSQL (по умолчанию: password)

Переменные окружения для приложения:
    SECRET_KEY - секретный ключ Flask (по умолчанию: dev_secret_key_change_in_production)
    FLASK_ENV - окружение Flask (по умолчанию: development)
"""

import os
import sys

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем приложение
from app import app, init_db

def setup_environment():
    """Настройка переменных окружения для разработки"""
    
    # Переменные для PostgreSQL (если не установлены)
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_PORT', '5432')
    os.environ.setdefault('DB_NAME', 'farm_profiles')
    os.environ.setdefault('DB_USER', 'postgres')
    os.environ.setdefault('DB_PASSWORD', 'password')
    
    # Переменные для Flask
    os.environ.setdefault('SECRET_KEY', 'dev_secret_key_change_in_production')
    os.environ.setdefault('FLASK_ENV', 'development')
    
    print("🔧 Переменные окружения:")
    print(f"   DB_HOST: {os.environ.get('DB_HOST')}")
    print(f"   DB_PORT: {os.environ.get('DB_PORT')}")
    print(f"   DB_NAME: {os.environ.get('DB_NAME')}")
    print(f"   DB_USER: {os.environ.get('DB_USER')}")
    print(f"   SECRET_KEY: {'***' if os.environ.get('SECRET_KEY') else 'не установлен'}")
    print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print()

def main():
    """Основная функция запуска приложения"""
    
    print("🚀 Запуск админ панели фермы...")
    print("=" * 50)
    
    # Настраиваем окружение
    setup_environment()
    
    # Инициализируем базу данных
    print("📁 Инициализация SQLite базы данных...")
    try:
        init_db()
        print("✅ SQLite база данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return 1
    
    print()
    print("🌐 Запуск веб-сервера...")
    print("   URL: http://localhost:8000")
    print("   Логин: admin")
    print("   Пароль: admin")
    print()
    print("🔍 Для подключения к PostgreSQL убедитесь что:")
    print("   • PostgreSQL сервер запущен")
    print("   • База данных 'farm_profiles' существует")
    print("   • Пользователь имеет права доступа")
    print()
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        # Запуск приложения в режиме разработки
        app.run(
            debug=True,
            host='127.0.0.1',
            port=8000,
            use_reloader=True,
            use_debugger=True
        )
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка запуска приложения: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
