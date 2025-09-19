#!/usr/bin/env python3
"""
Тестирование дашборда
"""

import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from dashboard import get_dashboard_data

def test_dashboard():
    """Тестирует получение данных дашборда"""
    print("============================================================")
    print("  ТЕСТИРОВАНИЕ ДАШБОРДА")
    print("============================================================")
    
    with app.app_context():
        print("📊 Тестируем функцию get_dashboard_data()...")
        
        try:
            data = get_dashboard_data()
            
            print("\n✅ Результат:")
            print(f"  - Общее количество профилей: {data['total_count']}")
            print(f"  - Средний возраст (дни): {data['avg_age_days']}")
            print(f"  - Среднее количество доменов: {data['avg_domain_count']}")
            print(f"  - Количество групп: {len(data['groups_stats'])}")
            
            if data['groups_stats']:
                print("\n📊 Группы:")
                for group in data['groups_stats']:
                    print(f"  - {group['party']}: {group['count']} профилей, "
                          f"ср.возраст {group['avg_age_days']} дней, "
                          f"ср.домены {group['avg_domains']}")
            
            if data['total_count'] > 0:
                print("\n✅ Дашборд работает корректно!")
                return True
            else:
                print("\n⚠️  Дашборд возвращает нулевые данные")
                return False
                
        except Exception as e:
            print(f"\n❌ Ошибка при тестировании дашборда: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False

if __name__ == '__main__':
    success = test_dashboard()
    if success:
        print("\n🎉 Тест дашборда успешно пройден!")
        sys.exit(0)
    else:
        print("\n💥 Тест дашборда провален!")
        sys.exit(1)