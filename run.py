#!/usr/bin/env python3
"""
Файл запуска Flask приложения для админ панели фермы

Использование:
    python run.py

Переменные окружения для PostgreSQL (Профили - только чтение):
    PROFILES_DB_HOST - хост PostgreSQL для профилей
    PROFILES_DB_PORT - порт PostgreSQL для профилей (по умолчанию: 5432)
    PROFILES_DB_NAME - имя базы данных профилей
    PROFILES_DB_USER - пользователь PostgreSQL для профилей
    PROFILES_DB_PASSWORD - пароль PostgreSQL для профилей
    или PROFILES_DATABASE_URL - полная строка подключения

Переменные окружения для PostgreSQL (Админы - полные права):
    ADMIN_DB_HOST - хост PostgreSQL для админов
    ADMIN_DB_PORT - порт PostgreSQL для админов (по умолчанию: 5432) 
    ADMIN_DB_NAME - имя базы данных админов
    ADMIN_DB_USER - пользователь PostgreSQL для админов
    ADMIN_DB_PASSWORD - пароль PostgreSQL для админов
    или ADMIN_DATABASE_URL - полная строка подключения
    или DATABASE_URL - автоматическая переменная Railway

Переменные окружения для приложения:
    SECRET_KEY - секретный ключ Flask (ОБЯЗАТЕЛЬНО!)
    FLASK_ENV - окружение Flask (development/production)
"""

import os
import sys

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем приложение
from app import app, init_db

def setup_environment():
    """Настройка переменных окружения для разработки"""
    
    # Переменные для Flask (ОБЯЗАТЕЛЬНЫЕ!)
    if not os.environ.get('SECRET_KEY'):
        print("⚠️  SECRET_KEY не установлен, используется тестовый ключ")
        os.environ.setdefault('SECRET_KEY', 'dev_secret_key_change_in_production')
    
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # Пример переменных для локальной разработки (если .env не используется)
    if not any([
        os.environ.get('PROFILES_DATABASE_URL'),
        all([
            os.environ.get('PROFILES_DB_HOST'),
            os.environ.get('PROFILES_DB_NAME'),
            os.environ.get('PROFILES_DB_USER'),
            os.environ.get('PROFILES_DB_PASSWORD')
        ])
    ]):
        print("⚠️  Настройки БД профилей не найдены, устанавливаем тестовые")
        os.environ.setdefault('PROFILES_DB_HOST', 'localhost')
        os.environ.setdefault('PROFILES_DB_PORT', '5432')
        os.environ.setdefault('PROFILES_DB_NAME', 'farm_profiles')
        os.environ.setdefault('PROFILES_DB_USER', 'postgres')
        os.environ.setdefault('PROFILES_DB_PASSWORD', 'password')
    
    if not any([
        os.environ.get('ADMIN_DATABASE_URL'),
        os.environ.get('DATABASE_URL'),
        all([
            os.environ.get('ADMIN_DB_HOST'),
            os.environ.get('ADMIN_DB_NAME'),
            os.environ.get('ADMIN_DB_USER'),
            os.environ.get('ADMIN_DB_PASSWORD')
        ])
    ]):
        print("⚠️  Настройки БД админов не найдены, устанавливаем тестовые")
        os.environ.setdefault('ADMIN_DB_HOST', 'localhost')
        os.environ.setdefault('ADMIN_DB_PORT', '5432')
        os.environ.setdefault('ADMIN_DB_NAME', 'admin_panel')
        os.environ.setdefault('ADMIN_DB_USER', 'postgres')
        os.environ.setdefault('ADMIN_DB_PASSWORD', 'password')
    
    print("🔧 Конфигурация:")
    print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"   SECRET_KEY: {'✅ установлен' if os.environ.get('SECRET_KEY') else '❌ не установлен'}")
    
    # Показываем статус БД профилей
    if os.environ.get('PROFILES_DATABASE_URL'):
        print(f"   Profiles DB: ✅ PROFILES_DATABASE_URL")
    elif all([os.environ.get(f'PROFILES_DB_{k}') for k in ['HOST', 'NAME', 'USER', 'PASSWORD']]):
        print(f"   Profiles DB: ✅ {os.environ.get('PROFILES_DB_HOST')}:{os.environ.get('PROFILES_DB_PORT')}/{os.environ.get('PROFILES_DB_NAME')}")
    else:
        print(f"   Profiles DB: ❌ не настроена")
    
    # Показываем статус БД админов
    if os.environ.get('DATABASE_URL'):
        print(f"   Admin DB: ✅ DATABASE_URL (Railway)")
    elif os.environ.get('ADMIN_DATABASE_URL'):
        print(f"   Admin DB: ✅ ADMIN_DATABASE_URL")
    elif all([os.environ.get(f'ADMIN_DB_{k}') for k in ['HOST', 'NAME', 'USER', 'PASSWORD']]):
        print(f"   Admin DB: ✅ {os.environ.get('ADMIN_DB_HOST')}:{os.environ.get('ADMIN_DB_PORT')}/{os.environ.get('ADMIN_DB_NAME')}")
    else:
        print(f"   Admin DB: ❌ не настроена")
    
    print()

def main():
    """Основная функция запуска приложения"""
    
    print("🚀 Запуск админ панели фермы...")
    print("=" * 50)
    
    # Настраиваем окружение
    setup_environment()
    
    # Инициализируем базу данных админов
    print("📁 Инициализация PostgreSQL базы данных админов...")
    try:
        init_db()
        print("✅ PostgreSQL база данных админов инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД админов: {e}")
        print("🔍 Проверьте настройки ADMIN_DB_* или DATABASE_URL")
        return 1
    
    print()
    print("🌐 Запуск веб-сервера...")
    print("   URL: http://localhost:8000")
    print("   Логин: admin")
    print("   Пароль: admin")
    print()
    print("📋 Требования для работы:")
    print("   • PostgreSQL сервер запущен")
    print("   • База данных для админов настроена (ADMIN_DB_* или DATABASE_URL)")
    print("   • База данных для профилей настроена (PROFILES_DB_*)")
    print("   • Установлен SECRET_KEY")
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
