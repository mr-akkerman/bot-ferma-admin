"""
Тесты для логики дашборда
"""
import unittest
from unittest.mock import patch, MagicMock
from dashboard import get_dashboard_data


class TestDashboard(unittest.TestCase):
    """Тесты для функции get_dashboard_data"""
    
    @patch('dashboard.Profile')
    def test_get_dashboard_data_with_normal_data(self, mock_profile):
        """Тест получения данных дашборда с нормальными данными"""
        # Настройка моков
        mock_profile.get_total_count.return_value = 150
        mock_profile.get_average_age_days.return_value = 45.678
        mock_profile.get_average_domain_count.return_value = 12.345
        mock_profile.get_groups_stats.return_value = [
            ('group1', 50, 30.567, 10.234),
            ('group2', 75, 45.891, 15.678),
            ('group3', 25, 20.123, 8.901)
        ]
        
        # Вызов функции
        result = get_dashboard_data()
        
        # Проверка структуры данных
        self.assertIsInstance(result, dict)
        
        # Проверка основных ключей
        expected_keys = {'total_count', 'avg_age_days', 'avg_domain_count', 'groups_stats'}
        self.assertEqual(set(result.keys()), expected_keys)
        
        # Проверка базовой статистики
        self.assertEqual(result['total_count'], 150)
        self.assertEqual(result['avg_age_days'], 45.68)  # округлено до 2 знаков
        self.assertEqual(result['avg_domain_count'], 12.35)  # округлено до 2 знаков
        
        # Проверка статистики групп
        groups = result['groups_stats']
        self.assertIsInstance(groups, list)
        self.assertEqual(len(groups), 3)
        
        # Проверка первой группы
        group1 = groups[0]
        self.assertEqual(group1['party'], 'group1')
        self.assertEqual(group1['count'], 50)
        self.assertEqual(group1['avg_age_days'], 30.57)  # округлено
        self.assertEqual(group1['avg_domains'], 10.23)  # округлено
    
    @patch('dashboard.Profile')
    def test_get_dashboard_data_with_empty_db(self, mock_profile):
        """Тест обработки пустой БД"""
        # Настройка моков для пустой БД
        mock_profile.get_total_count.return_value = 0
        mock_profile.get_average_age_days.return_value = None
        mock_profile.get_average_domain_count.return_value = None
        mock_profile.get_groups_stats.return_value = []
        
        # Вызов функции
        result = get_dashboard_data()
        
        # Проверка результата
        expected = {
            'total_count': 0,
            'avg_age_days': 0.0,
            'avg_domain_count': 0.0,
            'groups_stats': []
        }
        self.assertEqual(result, expected)
    
    @patch('dashboard.Profile')
    def test_get_dashboard_data_with_none_values(self, mock_profile):
        """Тест обработки None значений"""
        # Настройка моков с None значениями
        mock_profile.get_total_count.return_value = None
        mock_profile.get_average_age_days.return_value = None
        mock_profile.get_average_domain_count.return_value = None
        mock_profile.get_groups_stats.return_value = None
        
        # Вызов функции
        result = get_dashboard_data()
        
        # Проверка что все значения корректно обработаны
        self.assertEqual(result['total_count'], 0)
        self.assertEqual(result['avg_age_days'], 0.0)
        self.assertEqual(result['avg_domain_count'], 0.0)
        self.assertEqual(result['groups_stats'], [])
    
    @patch('dashboard.Profile')
    def test_get_dashboard_data_with_exception(self, mock_profile):
        """Тест обработки исключений"""
        # Настройка мока для генерации исключения
        mock_profile.get_total_count.side_effect = Exception("Database error")
        
        # Вызов функции
        result = get_dashboard_data()
        
        # Проверка что возвращается безопасная статистика
        expected = {
            'total_count': 0,
            'avg_age_days': 0.0,
            'avg_domain_count': 0.0,
            'groups_stats': []
        }
        self.assertEqual(result, expected)
    
    @patch('dashboard.Profile')
    def test_rounded_values_precision(self, mock_profile):
        """Тест точности округления числовых значений"""
        # Настройка моков с числами требующими округления
        mock_profile.get_total_count.return_value = 100
        mock_profile.get_average_age_days.return_value = 45.6789123
        mock_profile.get_average_domain_count.return_value = 12.3456789
        mock_profile.get_groups_stats.return_value = [
            ('test_group', 10, 99.9999, 7.7777)
        ]
        
        # Вызов функции
        result = get_dashboard_data()
        
        # Проверка округления до 2 знаков
        self.assertEqual(result['avg_age_days'], 45.68)
        self.assertEqual(result['avg_domain_count'], 12.35)
        
        # Проверка округления в группах
        group = result['groups_stats'][0]
        self.assertEqual(group['avg_age_days'], 100.0)
        self.assertEqual(group['avg_domains'], 7.78)
    
    @patch('dashboard.Profile')
    def test_groups_with_none_values(self, mock_profile):
        """Тест обработки групп с None значениями"""
        # Настройка моков с None в группах
        mock_profile.get_total_count.return_value = 50
        mock_profile.get_average_age_days.return_value = 30.0
        mock_profile.get_average_domain_count.return_value = 10.0
        mock_profile.get_groups_stats.return_value = [
            (None, 25, None, None),
            ('valid_group', None, 45.5, 12.3)
        ]
        
        # Вызов функции
        result = get_dashboard_data()
        
        # Проверка обработки None значений в группах
        groups = result['groups_stats']
        self.assertEqual(len(groups), 2)
        
        # Первая группа с None значениями
        group1 = groups[0]
        self.assertEqual(group1['party'], 'Unknown')
        self.assertEqual(group1['count'], 25)
        self.assertEqual(group1['avg_age_days'], 0.0)
        self.assertEqual(group1['avg_domains'], 0.0)
        
        # Вторая группа с частичными None значениями
        group2 = groups[1]
        self.assertEqual(group2['party'], 'valid_group')
        self.assertEqual(group2['count'], 0)
        self.assertEqual(group2['avg_age_days'], 45.5)
        self.assertEqual(group2['avg_domains'], 12.3)
    
    @patch('dashboard.Profile')
    def test_return_data_types(self, mock_profile):
        """Тест корректности типов возвращаемых данных"""
        # Настройка моков
        mock_profile.get_total_count.return_value = 100
        mock_profile.get_average_age_days.return_value = 45.5
        mock_profile.get_average_domain_count.return_value = 12.3
        mock_profile.get_groups_stats.return_value = [
            ('group1', 50, 30.5, 10.2)
        ]
        
        # Вызов функции
        result = get_dashboard_data()
        
        # Проверка типов данных
        self.assertIsInstance(result['total_count'], int)
        self.assertIsInstance(result['avg_age_days'], float)
        self.assertIsInstance(result['avg_domain_count'], float)
        self.assertIsInstance(result['groups_stats'], list)
        
        # Проверка типов в группах
        group = result['groups_stats'][0]
        self.assertIsInstance(group['party'], str)
        self.assertIsInstance(group['count'], int)
        self.assertIsInstance(group['avg_age_days'], float)
        self.assertIsInstance(group['avg_domains'], float)


if __name__ == '__main__':
    unittest.main()
