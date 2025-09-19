"""
Тесты для роута /dashboard
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestDashboardRoute(unittest.TestCase):
    """Тесты для роута /dashboard"""
    
    def setUp(self):
        """Настройка тестового клиента"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Настройка контекста приложения
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Очистка после тестов"""
        self.app_context.pop()
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_route_with_data(self, mock_get_data, mock_auth):
        """Тест роута dashboard с успешной передачей данных"""
        # Настройка моков
        mock_auth.return_value = True
        mock_data = {
            'total_count': 150,
            'avg_age_days': 45.67,
            'avg_domain_count': 12.34,
            'groups_stats': [
                {'party': 'group1', 'count': 50, 'avg_age_days': 30.5, 'avg_domains': 10.2}
            ]
        }
        mock_get_data.return_value = mock_data
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        
        # Проверки
        self.assertEqual(response.status_code, 200)
        mock_get_data.assert_called_once()
        
        # Проверяем что данные передались в шаблон
        # (В реальном тесте это сложно проверить без рендеринга шаблона,
        # но мы можем проверить что функция была вызвана)
        self.assertTrue(mock_get_data.called)
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_route_with_database_error(self, mock_get_data, mock_auth):
        """Тест роута dashboard с ошибкой подключения к БД"""
        # Настройка моков
        mock_auth.return_value = True
        mock_get_data.side_effect = Exception("Connection error")
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        
        # Проверки
        self.assertEqual(response.status_code, 200)
        mock_get_data.assert_called_once()
        
        # Проверяем что ошибка была обработана
        # (Страница должна загрузиться с сообщением об ошибке)
        self.assertTrue(mock_get_data.called)
    
    @patch('app.is_authenticated')
    def test_dashboard_route_requires_auth(self, mock_auth):
        """Тест что роут dashboard требует авторизации"""
        # Настройка мока - пользователь не авторизован
        mock_auth.return_value = False
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        
        # Проверка редиректа на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    @patch('app.render_template')
    def test_dashboard_template_context_with_data(self, mock_render, mock_get_data, mock_auth):
        """Тест передачи правильного контекста в шаблон при успешном получении данных"""
        # Настройка моков
        mock_auth.return_value = True
        mock_data = {
            'total_count': 100,
            'avg_age_days': 30.0,
            'avg_domain_count': 15.0,
            'groups_stats': []
        }
        mock_get_data.return_value = mock_data
        mock_render.return_value = "rendered template"
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        
        # Проверка что render_template был вызван с правильными параметрами
        mock_render.assert_called_once_with('dashboard.html', data=mock_data)
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    @patch('app.render_template')
    def test_dashboard_template_context_with_error(self, mock_render, mock_get_data, mock_auth):
        """Тест передачи контекста ошибки в шаблон при проблемах с БД"""
        # Настройка моков
        mock_auth.return_value = True
        mock_get_data.side_effect = Exception("Database connection failed")
        mock_render.return_value = "rendered template with error"
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        
        # Проверка что render_template был вызван с сообщением об ошибке
        mock_render.assert_called_once_with('dashboard.html', error="Ошибка подключения к базе данных профилей")
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_handles_different_exceptions(self, mock_get_data, mock_auth):
        """Тест обработки различных типов исключений"""
        # Настройка моков
        mock_auth.return_value = True
        
        # Тест с разными типами исключений
        exceptions = [
            ConnectionError("PostgreSQL connection failed"),
            TimeoutError("Database timeout"),
            ValueError("Invalid data"),
            RuntimeError("Runtime error")
        ]
        
        for exception in exceptions:
            with self.subTest(exception=type(exception).__name__):
                mock_get_data.side_effect = exception
                
                # Выполнение запроса
                response = self.client.get('/dashboard')
                
                # Проверка что ошибка обработана корректно
                self.assertEqual(response.status_code, 200)
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_function_called_once(self, mock_get_data, mock_auth):
        """Тест что get_dashboard_data вызывается ровно один раз"""
        # Настройка моков
        mock_auth.return_value = True
        mock_get_data.return_value = {'total_count': 0, 'avg_age_days': 0.0, 'avg_domain_count': 0.0, 'groups_stats': []}
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        
        # Проверка что функция вызвана ровно один раз
        self.assertEqual(mock_get_data.call_count, 1)
        self.assertEqual(response.status_code, 200)
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_route_method_get_only(self, mock_get_data, mock_auth):
        """Тест что роут поддерживает только GET запросы"""
        # Настройка моков
        mock_auth.return_value = True
        mock_get_data.return_value = {'total_count': 0, 'avg_age_days': 0.0, 'avg_domain_count': 0.0, 'groups_stats': []}
        
        # Тест GET запроса
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Тест POST запроса (должен возвращать 405 Method Not Allowed)
        response = self.client.post('/dashboard')
        self.assertEqual(response.status_code, 405)
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_route_returns_correct_content_type(self, mock_get_data, mock_auth):
        """Тест что роут возвращает правильный Content-Type"""
        # Настройка моков
        mock_auth.return_value = True
        mock_get_data.return_value = {'total_count': 0, 'avg_age_days': 0.0, 'avg_domain_count': 0.0, 'groups_stats': []}
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        
        # Проверка Content-Type
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)


if __name__ == '__main__':
    unittest.main()
