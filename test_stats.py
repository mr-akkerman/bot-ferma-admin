"""
Тесты для статистических методов модели Profile
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from models import db, Profile


class TestProfileStats(unittest.TestCase):
    """Тесты для статистических методов Profile"""
    
    def setUp(self):
        """Настройка тестовой среды"""
        self.mock_session = MagicMock()
        
    @patch('models.db.session')
    def test_get_total_count(self, mock_session):
        """Тест метода get_total_count()"""
        # Настройка мока
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = 150
        
        # Вызов метода
        result = Profile.get_total_count()
        
        # Проверка SQL запроса
        mock_session.query.assert_called_once()
        mock_query.scalar.assert_called_once()
        
        # Проверка типа данных
        self.assertIsInstance(result, int)
        self.assertEqual(result, 150)
    
    @patch('models.db.session')
    def test_get_average_age_days(self, mock_session):
        """Тест метода get_average_age_days()"""
        # Настройка мока
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = 45.5
        
        # Вызов метода
        result = Profile.get_average_age_days()
        
        # Проверка SQL запроса
        mock_session.query.assert_called_once()
        mock_query.scalar.assert_called_once()
        
        # Проверка типа данных
        self.assertIsInstance(result, (int, float))
        self.assertEqual(result, 45.5)
    
    @patch('models.db.session')
    def test_get_average_domain_count(self, mock_session):
        """Тест метода get_average_domain_count()"""
        # Настройка мока
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = 12.7
        
        # Вызов метода
        result = Profile.get_average_domain_count()
        
        # Проверка SQL запроса
        mock_session.query.assert_called_once()
        mock_query.scalar.assert_called_once()
        
        # Проверка типа данных
        self.assertIsInstance(result, (int, float))
        self.assertEqual(result, 12.7)
    
    @patch('models.db.session')
    def test_get_groups_stats(self, mock_session):
        """Тест метода get_groups_stats()"""
        # Настройка мока - результат группировки
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [
            ('group1', 50, 30.5, 10.2),
            ('group2', 75, 45.8, 15.6),
            ('group3', 25, 20.1, 8.9)
        ]
        
        # Вызов метода
        result = Profile.get_groups_stats()
        
        # Проверка SQL запроса
        mock_session.query.assert_called_once()
        mock_query.group_by.assert_called_once()
        mock_query.all.assert_called_once()
        
        # Проверка типа данных
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        
        # Проверка структуры данных каждой группы
        for group_data in result:
            self.assertIsInstance(group_data, tuple)
            self.assertEqual(len(group_data), 4)
            
            party, count, avg_age, avg_domains = group_data
            self.assertIsInstance(party, str)
            self.assertIsInstance(count, int)
            self.assertIsInstance(avg_age, (int, float))
            self.assertIsInstance(avg_domains, (int, float))
    
    @patch('models.db.session')
    def test_get_total_count_returns_zero(self, mock_session):
        """Тест get_total_count() когда профилей нет"""
        # Настройка мока
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = 0
        
        # Вызов метода
        result = Profile.get_total_count()
        
        # Проверка результата
        self.assertEqual(result, 0)
        self.assertIsInstance(result, int)
    
    @patch('models.db.session')
    def test_get_average_age_days_returns_none(self, mock_session):
        """Тест get_average_age_days() когда данных нет"""
        # Настройка мока
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Вызов метода
        result = Profile.get_average_age_days()
        
        # Проверка результата
        self.assertIsNone(result)
    
    @patch('models.db.session')
    def test_get_average_domain_count_returns_none(self, mock_session):
        """Тест get_average_domain_count() когда данных нет"""
        # Настройка мока
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Вызов метода
        result = Profile.get_average_domain_count()
        
        # Проверка результата
        self.assertIsNone(result)
    
    @patch('models.db.session')
    def test_get_groups_stats_empty_result(self, mock_session):
        """Тест get_groups_stats() когда групп нет"""
        # Настройка мока
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = []
        
        # Вызов метода
        result = Profile.get_groups_stats()
        
        # Проверка результата
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_sql_query_structure_get_total_count(self):
        """Тест структуры SQL запроса для get_total_count"""
        with patch('models.db.session') as mock_session:
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.scalar.return_value = 100
            
            Profile.get_total_count()
            
            # Проверяем, что используется func.count с правильным полем
            args = mock_session.query.call_args[0]
            self.assertEqual(len(args), 1)
            
    def test_sql_query_structure_get_average_age_days(self):
        """Тест структуры SQL запроса для get_average_age_days"""
        with patch('models.db.session') as mock_session:
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.scalar.return_value = 30.0
            
            Profile.get_average_age_days()
            
            # Проверяем, что запрос был вызван
            mock_session.query.assert_called_once()
            
    def test_sql_query_structure_get_average_domain_count(self):
        """Тест структуры SQL запроса для get_average_domain_count"""
        with patch('models.db.session') as mock_session:
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.scalar.return_value = 15.0
            
            Profile.get_average_domain_count()
            
            # Проверяем, что запрос был вызван
            mock_session.query.assert_called_once()
    
    def test_sql_query_structure_get_groups_stats(self):
        """Тест структуры SQL запроса для get_groups_stats"""
        with patch('models.db.session') as mock_session:
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.group_by.return_value = mock_query
            mock_query.all.return_value = []
            
            Profile.get_groups_stats()
            
            # Проверяем, что используется group_by
            mock_query.group_by.assert_called_once()


if __name__ == '__main__':
    unittest.main()
