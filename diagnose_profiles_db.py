#!/usr/bin/env python3
"""
Диагностический скрипт для проверки базы данных профилей
Проверяет подключение, структуру таблицы и выполняет тестовые запросы
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from config import Config


def print_header(title):
    """Печать заголовка секции"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_success(message):
    """Печать успешного сообщения"""
    print(f"✅ {message}")


def print_error(message):
    """Печать сообщения об ошибке"""
    print(f"❌ {message}")


def print_warning(message):
    """Печать предупреждения"""
    print(f"⚠️  {message}")


def print_info(message):
    """Печать информационного сообщения"""
    print(f"ℹ️  {message}")


def check_profiles_connection():
    """Проверка подключения к базе данных профилей"""
    print_header("ПРОВЕРКА ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ ПРОФИЛЕЙ")
    
    try:
        # Получаем URI базы данных профилей
        profiles_uri = Config.get_profiles_database_uri()
        print_info(f"URI: {Config._hide_password(profiles_uri)}")
        
        # Создаем подключение
        engine = create_engine(profiles_uri)
        
        # Тестируем подключение
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            if test_value == 1:
                print_success("Подключение к базе данных профилей установлено")
                return engine
            else:
                print_error("Тест подключения не прошел")
                return None
                
    except Exception as e:
        print_error(f"Ошибка подключения к базе данных профилей: {e}")
        return None


def check_table_structure(engine):
    """Проверка структуры таблицы profiles"""
    print_header("ПРОВЕРКА СТРУКТУРЫ ТАБЛИЦЫ PROFILES")
    
    try:
        inspector = inspect(engine)
        
        # Получаем список таблиц
        tables = inspector.get_table_names()
        print_info(f"Найденные таблицы: {tables}")
        
        if 'profiles' not in tables:
            print_error("Таблица 'profiles' не найдена!")
            print_info("Возможные варианты:")
            for table in tables:
                if 'profile' in table.lower():
                    print_info(f"  - {table}")
            return False
        
        print_success("Таблица 'profiles' найдена")
        
        # Получаем структуру таблицы
        columns = inspector.get_columns('profiles')
        print_info("Структура таблицы 'profiles':")
        
        expected_columns = ['pid', 'data_create', 'party', 'domaincount']
        found_columns = [col['name'] for col in columns]
        
        for col in columns:
            status = "✅" if col['name'] in expected_columns else "⚠️"
            print_info(f"  {status} {col['name']} ({col['type']})")
        
        # Проверяем обязательные колонки
        missing_columns = [col for col in expected_columns if col not in found_columns]
        if missing_columns:
            print_error(f"Отсутствуют обязательные колонки: {missing_columns}")
            return False
        
        print_success("Все обязательные колонки присутствуют")
        return True
        
    except Exception as e:
        print_error(f"Ошибка проверки структуры таблицы: {e}")
        return False


def check_data_content(engine):
    """Проверка содержимого данных"""
    print_header("ПРОВЕРКА СОДЕРЖИМОГО ДАННЫХ")
    
    try:
        with engine.connect() as conn:
            # Общее количество записей
            result = conn.execute(text("SELECT COUNT(*) FROM profiles"))
            total_count = result.scalar()
            print_info(f"Общее количество записей: {total_count}")
            
            if total_count == 0:
                print_warning("Таблица profiles пустая!")
                return False
            
            # Пример записей
            result = conn.execute(text("SELECT * FROM profiles LIMIT 5"))
            rows = result.fetchall()
            columns = result.keys()
            
            print_info("Первые 5 записей:")
            for i, row in enumerate(rows, 1):
                print_info(f"  Запись {i}:")
                for col, val in zip(columns, row):
                    print_info(f"    {col}: {val}")
            
            # Проверка типов данных в ключевых колонках
            print_info("\nПроверка данных по колонкам:")
            
            # pid
            result = conn.execute(text("SELECT COUNT(DISTINCT pid) FROM profiles"))
            unique_pids = result.scalar()
            print_info(f"  Уникальных pid: {unique_pids}")
            
            # data_create
            result = conn.execute(text("SELECT COUNT(*) FROM profiles WHERE data_create IS NOT NULL"))
            valid_dates = result.scalar()
            print_info(f"  Записей с валидной data_create: {valid_dates}")
            
            # party
            result = conn.execute(text("SELECT COUNT(DISTINCT party) FROM profiles WHERE party IS NOT NULL"))
            unique_parties = result.scalar()
            print_info(f"  Уникальных групп (party): {unique_parties}")
            
            if unique_parties > 0:
                result = conn.execute(text("SELECT party, COUNT(*) FROM profiles WHERE party IS NOT NULL GROUP BY party LIMIT 5"))
                parties = result.fetchall()
                print_info("  Примеры групп:")
                for party, count in parties:
                    print_info(f"    {party}: {count} записей")
            
            # domaincount
            result = conn.execute(text("SELECT COUNT(*) FROM profiles WHERE domaincount IS NOT NULL AND domaincount > 0"))
            valid_domains = result.scalar()
            print_info(f"  Записей с валидным domaincount: {valid_domains}")
            
            return True
            
    except Exception as e:
        print_error(f"Ошибка проверки данных: {e}")
        return False


def test_statistics_queries(engine):
    """Тестирование запросов статистики"""
    print_header("ТЕСТИРОВАНИЕ ЗАПРОСОВ СТАТИСТИКИ")
    
    try:
        with engine.connect() as conn:
            print_info("Выполняем запросы из модели Profile...")
            
            # 1. Общее количество профилей
            print_info("\n1. Общее количество профилей:")
            result = conn.execute(text("SELECT COUNT(pid) FROM profiles"))
            total_count = result.scalar()
            print_info(f"   Результат: {total_count}")
            
            # 2. Средний возраст профилей в днях
            print_info("\n2. Средний возраст профилей (дни):")
            query = text("""
                SELECT AVG(EXTRACT('epoch' FROM (NOW() - data_create)) / 86400) 
                FROM profiles 
                WHERE data_create IS NOT NULL
            """)
            result = conn.execute(query)
            avg_age = result.scalar()
            print_info(f"   Результат: {avg_age}")
            
            # 3. Среднее количество доменов
            print_info("\n3. Среднее количество доменов:")
            result = conn.execute(text("SELECT AVG(domaincount) FROM profiles WHERE domaincount IS NOT NULL"))
            avg_domains = result.scalar()
            print_info(f"   Результат: {avg_domains}")
            
            # 4. Статистика по группам
            print_info("\n4. Статистика по группам:")
            query = text("""
                SELECT 
                    party,
                    COUNT(pid) as count,
                    AVG(EXTRACT('epoch' FROM (NOW() - data_create)) / 86400) as avg_age_days,
                    AVG(domaincount) as avg_domains
                FROM profiles 
                WHERE party IS NOT NULL 
                GROUP BY party 
                ORDER BY count DESC 
                LIMIT 10
            """)
            result = conn.execute(query)
            groups = result.fetchall()
            
            if groups:
                print_info("   Топ-10 групп:")
                for group in groups:
                    party, count, avg_age, avg_domains = group
                    print_info(f"     {party}: {count} профилей, ср.возраст {avg_age:.1f} дней, ср.домены {avg_domains:.1f}")
            else:
                print_warning("   Нет данных по группам")
            
            return True
            
    except Exception as e:
        print_error(f"Ошибка выполнения запросов статистики: {e}")
        print_info(f"Детали ошибки: {type(e).__name__}")
        return False


def test_orm_queries():
    """Тестирование ORM запросов через модели"""
    print_header("ТЕСТИРОВАНИЕ ORM ЗАПРОСОВ")
    
    try:
        from flask import Flask
        from models import db, Profile
        from config import get_config
        
        # Создаем тестовое приложение
        app = Flask(__name__)
        config_class = get_config()
        config_class.init_app(app)
        db.init_app(app)
        
        with app.app_context():
            print_info("Выполняем ORM запросы...")
            
            # 1. Общее количество через ORM
            try:
                total_count = Profile.get_total_count()
                print_success(f"Profile.get_total_count(): {total_count}")
            except Exception as e:
                print_error(f"Profile.get_total_count() failed: {e}")
            
            # 2. Средний возраст через ORM
            try:
                avg_age = Profile.get_average_age_days()
                print_success(f"Profile.get_average_age_days(): {avg_age}")
            except Exception as e:
                print_error(f"Profile.get_average_age_days() failed: {e}")
            
            # 3. Среднее количество доменов через ORM
            try:
                avg_domains = Profile.get_average_domain_count()
                print_success(f"Profile.get_average_domain_count(): {avg_domains}")
            except Exception as e:
                print_error(f"Profile.get_average_domain_count() failed: {e}")
            
            # 4. Статистика по группам через ORM
            try:
                groups_stats = Profile.get_groups_stats()
                print_success(f"Profile.get_groups_stats(): найдено {len(groups_stats)} групп")
                
                if groups_stats:
                    print_info("Первые 5 групп:")
                    for i, group in enumerate(groups_stats[:5], 1):
                        print_info(f"  {i}. {group.party}: {group.count} профилей")
                        
            except Exception as e:
                print_error(f"Profile.get_groups_stats() failed: {e}")
                
        return True
        
    except Exception as e:
        print_error(f"Ошибка тестирования ORM: {e}")
        return False


def test_dashboard_function():
    """Тестирование функции dashboard"""
    print_header("ТЕСТИРОВАНИЕ ФУНКЦИИ DASHBOARD")
    
    try:
        from dashboard import get_dashboard_data
        
        print_info("Вызываем get_dashboard_data()...")
        
        dashboard_data = get_dashboard_data()
        
        if dashboard_data:
            print_success("get_dashboard_data() выполнилась успешно")
            print_info("Результат:")
            
            # Проверяем структуру данных
            if hasattr(dashboard_data, 'total_count'):
                print_info(f"  total_count: {dashboard_data.total_count}")
            
            if hasattr(dashboard_data, 'avg_age_days'):
                print_info(f"  avg_age_days: {dashboard_data.avg_age_days}")
                
            if hasattr(dashboard_data, 'avg_domain_count'):
                print_info(f"  avg_domain_count: {dashboard_data.avg_domain_count}")
                
            if hasattr(dashboard_data, 'groups_stats'):
                groups_count = len(dashboard_data.groups_stats) if dashboard_data.groups_stats else 0
                print_info(f"  groups_stats: {groups_count} групп")
                
        else:
            print_warning("get_dashboard_data() вернула пустой результат")
            
        return True
        
    except Exception as e:
        print_error(f"Ошибка тестирования dashboard: {e}")
        import traceback
        print_info("Трассировка ошибки:")
        print_info(traceback.format_exc())
        return False


def main():
    """Основная функция диагностики"""
    print_header("ДИАГНОСТИКА БАЗЫ ДАННЫХ ПРОФИЛЕЙ")
    print_info(f"Время запуска: {datetime.now()}")
    
    # Проверяем конфигурацию
    try:
        from config import validate_config
        validate_config()
        print_success("Конфигурация валидна")
    except Exception as e:
        print_error(f"Ошибка конфигурации: {e}")
        return 1
    
    # 1. Проверка подключения
    engine = check_profiles_connection()
    if not engine:
        return 1
    
    # 2. Проверка структуры таблицы
    if not check_table_structure(engine):
        return 1
    
    # 3. Проверка содержимого данных
    if not check_data_content(engine):
        return 1
    
    # 4. Тестирование SQL запросов
    if not test_statistics_queries(engine):
        return 1
    
    # 5. Тестирование ORM запросов
    if not test_orm_queries():
        return 1
    
    # 6. Тестирование функции dashboard
    if not test_dashboard_function():
        return 1
    
    print_header("ДИАГНОСТИКА ЗАВЕРШЕНА УСПЕШНО")
    print_success("Все проверки пройдены!")
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
