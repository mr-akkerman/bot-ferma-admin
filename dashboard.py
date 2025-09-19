"""
Логика дашборда для админ панели
"""
from models import Profile
import traceback


def get_dashboard_data():
    """
    Получает статистику для дашборда
    
    Returns:
        dict: Словарь со всей статистикой
    """
    print("📊 Начинаем получение данных для дашборда...")
    
    try:
        # Получаем базовую статистику
        print("   Получаем общее количество профилей...")
        total_count = Profile.get_total_count() or 0
        print(f"   ✅ Общее количество: {total_count}")
        
        print("   Получаем средний возраст профилей...")
        avg_age_days = Profile.get_average_age_days() or 0
        print(f"   ✅ Средний возраст: {avg_age_days}")
        
        print("   Получаем среднее количество доменов...")
        avg_domain_count = Profile.get_average_domain_count() or 0
        print(f"   ✅ Среднее количество доменов: {avg_domain_count}")
        
        # Получаем статистику по группам
        print("   Получаем статистику по группам...")
        groups_stats = Profile.get_groups_stats() or []
        print(f"   ✅ Найдено групп: {len(groups_stats)}")
        
        # Форматируем данные групп
        formatted_groups = []
        for group_data in groups_stats:
            party, count, avg_age, avg_domains = group_data
            formatted_group = {
                'party': party or 'Unknown',
                'count': count or 0,
                'avg_age_days': round(float(avg_age or 0), 2),
                'avg_domains': round(float(avg_domains or 0), 2)
            }
            formatted_groups.append(formatted_group)
            print(f"      - {formatted_group['party']}: {formatted_group['count']} профилей")
        
        result = {
            'total_count': total_count,
            'avg_age_days': round(float(avg_age_days), 2) if avg_age_days else 0.0,
            'avg_domain_count': round(float(avg_domain_count), 2) if avg_domain_count else 0.0,
            'groups_stats': formatted_groups
        }
        
        print(f"📊 ✅ Данные дашборда получены успешно: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка при получении данных дашборда: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        # В случае любой ошибки возвращаем пустую статистику
        return {
            'total_count': 0,
            'avg_age_days': 0.0,
            'avg_domain_count': 0.0,
            'groups_stats': []
        }
