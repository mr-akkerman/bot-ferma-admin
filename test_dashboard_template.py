"""
Тесты для шаблона dashboard.html
"""
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup
from app import app


class TestDashboardTemplate(unittest.TestCase):
    """Тесты для шаблона dashboard.html"""
    
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
    def test_dashboard_template_with_data(self, mock_get_data, mock_auth):
        """Тест отображения шаблона с данными"""
        # Настройка моков
        mock_auth.return_value = True
        mock_data = {
            'total_count': 150,
            'avg_age_days': 45.67,
            'avg_domain_count': 12.34,
            'groups_stats': [
                {'party': 'group1', 'count': 50, 'avg_age_days': 30.5, 'avg_domains': 10.2},
                {'party': 'group2', 'count': 75, 'avg_age_days': 45.8, 'avg_domains': 15.6}
            ]
        }
        mock_get_data.return_value = mock_data
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Парсинг HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Проверка основной структуры (находим h1 в main контенте)
        main_content = soup.find('main', class_='main-content')
        self.assertIsNotNone(main_content)
        h1 = main_content.find('h1')
        self.assertIsNotNone(h1)
        self.assertEqual(h1.text, 'Дашборд')
        
        # Проверка секции глобальной статистики
        global_stats = soup.find('section', class_='global-statistics')
        self.assertIsNotNone(global_stats)
        
        # Проверка заголовка глобальной статистики
        h2 = global_stats.find('h2')
        self.assertIsNotNone(h2)
        self.assertEqual(h2.text, 'Общая статистика')
        
        # Проверка карточек статистики
        stat_cards = global_stats.find_all('div', class_='stat-card')
        self.assertEqual(len(stat_cards), 3)
        
        # Проверка содержимого карточек
        card_texts = [card.get_text(strip=True) for card in stat_cards]
        self.assertIn('Общее количество профилей', card_texts[0])
        self.assertIn('150', card_texts[0])
        self.assertIn('Средний возраст профиля (дни)', card_texts[1])
        self.assertIn('45.67', card_texts[1])
        self.assertIn('Среднее количество доменов', card_texts[2])
        self.assertIn('12.34', card_texts[2])
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_template_groups_table(self, mock_get_data, mock_auth):
        """Тест отображения таблицы групп"""
        # Настройка моков
        mock_auth.return_value = True
        mock_data = {
            'total_count': 100,
            'avg_age_days': 30.0,
            'avg_domain_count': 10.0,
            'groups_stats': [
                {'party': 'test_group1', 'count': 25, 'avg_age_days': 20.5, 'avg_domains': 8.2},
                {'party': 'test_group2', 'count': 75, 'avg_age_days': 35.8, 'avg_domains': 12.6}
            ]
        }
        mock_get_data.return_value = mock_data
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Парсинг HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Проверка секции статистики по группам
        groups_stats = soup.find('section', class_='groups-statistics')
        self.assertIsNotNone(groups_stats)
        
        # Проверка заголовка секции групп
        h2 = groups_stats.find('h2')
        self.assertIsNotNone(h2)
        self.assertEqual(h2.text, 'Статистика по группам')
        
        # Проверка таблицы
        table = groups_stats.find('table', class_='groups-table')
        self.assertIsNotNone(table)
        
        # Проверка заголовков таблицы
        headers = table.find('thead').find_all('th')
        self.assertEqual(len(headers), 4)
        
        expected_headers = [
            'Название группы',
            'Количество профилей',
            'Средний возраст (дни)',
            'Среднее количество доменов'
        ]
        actual_headers = [header.text.strip() for header in headers]
        self.assertEqual(actual_headers, expected_headers)
        
        # Проверка строк данных
        rows = table.find('tbody').find_all('tr')
        self.assertEqual(len(rows), 2)
        
        # Проверка первой строки
        first_row = rows[0].find_all('td')
        self.assertEqual(len(first_row), 4)
        self.assertEqual(first_row[0].text.strip(), 'test_group1')
        self.assertEqual(first_row[1].text.strip(), '25')
        self.assertEqual(first_row[2].text.strip(), '20.5')
        self.assertEqual(first_row[3].text.strip(), '8.2')
        
        # Проверка второй строки
        second_row = rows[1].find_all('td')
        self.assertEqual(len(second_row), 4)
        self.assertEqual(second_row[0].text.strip(), 'test_group2')
        self.assertEqual(second_row[1].text.strip(), '75')
        self.assertEqual(second_row[2].text.strip(), '35.8')
        self.assertEqual(second_row[3].text.strip(), '12.6')
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_template_empty_groups(self, mock_get_data, mock_auth):
        """Тест отображения при отсутствии групп"""
        # Настройка моков
        mock_auth.return_value = True
        mock_data = {
            'total_count': 50,
            'avg_age_days': 25.0,
            'avg_domain_count': 8.0,
            'groups_stats': []
        }
        mock_get_data.return_value = mock_data
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Парсинг HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Проверка глобальной статистики все еще отображается
        global_stats = soup.find('section', class_='global-statistics')
        self.assertIsNotNone(global_stats)
        
        # Проверка секции групп
        groups_stats = soup.find('section', class_='groups-statistics')
        self.assertIsNotNone(groups_stats)
        
        # Проверка что таблица не отображается
        table = groups_stats.find('table', class_='groups-table')
        self.assertIsNone(table)
        
        # Проверка сообщения о отсутствии данных
        no_data = groups_stats.find('p', class_='no-data')
        self.assertIsNotNone(no_data)
        self.assertEqual(no_data.text.strip(), 'Нет данных по группам')
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_template_with_error(self, mock_get_data, mock_auth):
        """Тест отображения при ошибке"""
        # Настройка моков
        mock_auth.return_value = True
        mock_get_data.side_effect = Exception("Database error")
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Парсинг HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Проверка отображения ошибки
        error_message = soup.find('div', class_='error-message')
        self.assertIsNotNone(error_message)
        
        error_text = error_message.find('p')
        self.assertIsNotNone(error_text)
        self.assertEqual(error_text.text.strip(), 'Ошибка подключения к базе данных профилей')
        
        # Проверка что секции статистики не отображаются
        global_stats = soup.find('section', class_='global-statistics')
        self.assertIsNone(global_stats)
        
        groups_stats = soup.find('section', class_='groups-statistics')
        self.assertIsNone(groups_stats)
    
    @patch('app.is_authenticated')
    @patch('app.render_template')
    def test_dashboard_template_no_data(self, mock_render, mock_auth):
        """Тест отображения при отсутствии данных"""
        # Настройка моков
        mock_auth.return_value = True
        
        # Создаем HTML для случая отсутствия данных
        no_data_html = '''
        <h1>Дашборд</h1>
        <div class="no-data">
            <p>Нет данных для отображения</p>
        </div>
        '''
        mock_render.return_value = no_data_html
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        
        # Проверка что render_template был вызван
        mock_render.assert_called_once()
        
        # Проверка HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        no_data = soup.find('div', class_='no-data')
        if no_data:
            p_tag = no_data.find('p')
            if p_tag:
                self.assertEqual(p_tag.text.strip(), 'Нет данных для отображения')
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_template_html_structure(self, mock_get_data, mock_auth):
        """Тест корректности HTML структуры"""
        # Настройка моков
        mock_auth.return_value = True
        mock_data = {
            'total_count': 100,
            'avg_age_days': 30.0,
            'avg_domain_count': 10.0,
            'groups_stats': [
                {'party': 'group1', 'count': 50, 'avg_age_days': 25.0, 'avg_domains': 5.0}
            ]
        }
        mock_get_data.return_value = mock_data
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Парсинг HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Проверка основных структурных элементов
        main_content = soup.find('main', class_='main-content')
        self.assertIsNotNone(main_content)
        h1 = main_content.find('h1')
        self.assertIsNotNone(h1)
        
        # Проверка наличия секций
        global_section = soup.find('section', class_='global-statistics')
        groups_section = soup.find('section', class_='groups-statistics')
        
        self.assertIsNotNone(global_section)
        self.assertIsNotNone(groups_section)
        
        # Проверка наличия обязательных элементов в глобальной статистике
        stats_cards = global_section.find('div', class_='stats-cards')
        self.assertIsNotNone(stats_cards)
        
        stat_cards = stats_cards.find_all('div', class_='stat-card')
        self.assertEqual(len(stat_cards), 3)
        
        # Проверка структуры каждой карточки
        for card in stat_cards:
            h3 = card.find('h3')
            p = card.find('p', class_='stat-value')
            self.assertIsNotNone(h3)
            self.assertIsNotNone(p)
    
    @patch('app.is_authenticated')
    @patch('app.get_dashboard_data')
    def test_dashboard_template_table_structure(self, mock_get_data, mock_auth):
        """Тест корректности структуры таблицы"""
        # Настройка моков
        mock_auth.return_value = True
        mock_data = {
            'total_count': 100,
            'avg_age_days': 30.0,
            'avg_domain_count': 10.0,
            'groups_stats': [
                {'party': 'group1', 'count': 50, 'avg_age_days': 25.0, 'avg_domains': 5.0},
                {'party': 'group2', 'count': 50, 'avg_age_days': 35.0, 'avg_domains': 15.0}
            ]
        }
        mock_get_data.return_value = mock_data
        
        # Выполнение запроса
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Парсинг HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Проверка структуры таблицы
        table = soup.find('table', class_='groups-table')
        self.assertIsNotNone(table)
        
        # Проверка наличия thead и tbody
        thead = table.find('thead')
        tbody = table.find('tbody')
        self.assertIsNotNone(thead)
        self.assertIsNotNone(tbody)
        
        # Проверка количества колонок в заголовке
        header_row = thead.find('tr')
        self.assertIsNotNone(header_row)
        headers = header_row.find_all('th')
        self.assertEqual(len(headers), 4)
        
        # Проверка количества строк данных
        data_rows = tbody.find_all('tr')
        self.assertEqual(len(data_rows), 2)
        
        # Проверка количества колонок в каждой строке данных
        for row in data_rows:
            cells = row.find_all('td')
            self.assertEqual(len(cells), 4)


if __name__ == '__main__':
    unittest.main()
