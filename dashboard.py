"""
Логика дашборда для админ панели
"""
from models import Profile


def get_dashboard_data():
    """
    Получает статистику для дашборда
    
    Returns:
        dict: Словарь со всей статистикой
    """
    try:
        # Получаем базовую статистику
        total_count = Profile.get_total_count() or 0
        avg_age_days = Profile.get_average_age_days() or 0
        avg_domain_count = Profile.get_average_domain_count() or 0
        
        # Получаем статистику по группам
        groups_stats = Profile.get_groups_stats() or []
        
        # Форматируем данные групп
        formatted_groups = []
        for group_data in groups_stats:
            party, count, avg_age, avg_domains = group_data
            formatted_groups.append({
                'party': party or 'Unknown',
                'count': count or 0,
                'avg_age_days': round(float(avg_age or 0), 2),
                'avg_domains': round(float(avg_domains or 0), 2)
            })
        
        return {
            'total_count': total_count,
            'avg_age_days': round(float(avg_age_days), 2),
            'avg_domain_count': round(float(avg_domain_count), 2),
            'groups_stats': formatted_groups
        }
        
    except Exception:
        # В случае любой ошибки возвращаем пустую статистику
        return {
            'total_count': 0,
            'avg_age_days': 0.0,
            'avg_domain_count': 0.0,
            'groups_stats': []
        }
