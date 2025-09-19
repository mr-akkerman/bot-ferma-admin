"""
Тесты для CSS файла
"""
import unittest
import os
import re


class TestCSS(unittest.TestCase):
    """Тесты для static/css/style.css"""
    
    def setUp(self):
        """Настройка путей к файлам"""
        self.css_file_path = 'static/css/style.css'
        self.absolute_css_path = os.path.abspath(self.css_file_path)
    
    def test_css_file_exists(self):
        """Тест наличия CSS файла"""
        self.assertTrue(os.path.exists(self.css_file_path), 
                       f"CSS файл {self.css_file_path} не найден")
    
    def test_css_file_not_empty(self):
        """Тест что CSS файл не пустой"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        self.assertGreater(len(content), 0, "CSS файл не должен быть пустым")
    
    def test_css_syntax_basic(self):
        """Тест базового синтаксиса CSS"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Подсчет открывающих и закрывающих скобок
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        self.assertEqual(open_braces, close_braces, 
                        "Количество открывающих и закрывающих скобок должно совпадать")
    
    def test_body_styles_present(self):
        """Тест наличия стилей для body"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие селектора body
        body_pattern = r'body\s*\{'
        self.assertIsNotNone(re.search(body_pattern, content), 
                           "Стили для body не найдены")
        
        # Проверяем основные свойства body
        body_section = self._extract_css_rule(content, 'body')
        if body_section:
            self.assertIn('font-family', body_section, "font-family не найден в стилях body")
            self.assertIn('margin', body_section, "margin не найден в стилях body")
            self.assertIn('background-color', body_section, "background-color не найден в стилях body")
    
    def test_sidebar_styles_present(self):
        """Тест наличия стилей для бокового меню"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем основные классы бокового меню
        sidebar_classes = ['.sidebar', '.sidebar-nav ul', '.sidebar-nav a']
        
        for class_name in sidebar_classes:
            pattern = re.escape(class_name).replace(r'\ ', r'\s*') + r'\s*\{'
            self.assertIsNotNone(re.search(pattern, content), 
                               f"Стили для {class_name} не найдены")
    
    def test_stat_cards_styles_present(self):
        """Тест наличия стилей для карточек статистики"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем классы карточек статистики
        card_classes = ['.stats-cards', '.stat-card', '.stat-value']
        
        for class_name in card_classes:
            pattern = re.escape(class_name).replace(r'\ ', r'\s*') + r'\s*\{'
            self.assertIsNotNone(re.search(pattern, content), 
                               f"Стили для {class_name} не найдены")
        
        # Проверяем что у карточек есть тень
        stat_card_section = self._extract_css_rule(content, '.stat-card')
        if stat_card_section:
            self.assertIn('box-shadow', stat_card_section, 
                         "box-shadow не найден в стилях .stat-card")
    
    def test_table_styles_present(self):
        """Тест наличия стилей для таблицы"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем классы таблицы
        table_classes = ['.groups-table', '.groups-table th', '.groups-table td']
        
        for class_name in table_classes:
            pattern = re.escape(class_name).replace(r'\ ', r'\s*') + r'\s*\{'
            self.assertIsNotNone(re.search(pattern, content), 
                               f"Стили для {class_name} не найдены")
    
    def test_container_styles_present(self):
        """Тест наличия стилей для контейнеров"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем основные контейнеры
        container_classes = ['.container', '.main-content']
        
        for class_name in container_classes:
            pattern = re.escape(class_name).replace(r'\ ', r'\s*') + r'\s*\{'
            self.assertIsNotNone(re.search(pattern, content), 
                               f"Стили для {class_name} не найдены")
    
    def test_vercel_color_scheme(self):
        """Тест цветовой схемы в стиле Vercel"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем основные цвета Vercel
        vercel_colors = [
            '#ffffff',  # белый
            '#333333',  # темно-серый
            '#e1e1e1',  # светло-серые границы
            '#fafafa',  # очень светло-серый фон
        ]
        
        for color in vercel_colors:
            self.assertIn(color, content, f"Цвет {color} не найден в стилях")
    
    def test_error_and_no_data_styles(self):
        """Тест стилей для сообщений об ошибках и отсутствии данных"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем классы для сообщений
        message_classes = ['.error-message', '.no-data']
        
        for class_name in message_classes:
            pattern = re.escape(class_name).replace(r'\ ', r'\s*') + r'\s*\{'
            self.assertIsNotNone(re.search(pattern, content), 
                               f"Стили для {class_name} не найдены")
    
    def test_grid_layout_for_stats(self):
        """Тест использования grid для карточек статистики"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stats_cards_section = self._extract_css_rule(content, '.stats-cards')
        if stats_cards_section:
            self.assertIn('display: grid', stats_cards_section, 
                         "Grid layout не найден для .stats-cards")
            self.assertIn('grid-template-columns', stats_cards_section, 
                         "grid-template-columns не найден для .stats-cards")
    
    def test_flexbox_layout_for_container(self):
        """Тест использования flexbox для основного контейнера"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        container_section = self._extract_css_rule(content, '.container')
        if container_section:
            self.assertIn('display: flex', container_section, 
                         "Flexbox layout не найден для .container")
    
    def test_font_stack(self):
        """Тест системного шрифта в стиле Vercel"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем использование системного шрифта
        font_keywords = ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI']
        
        for keyword in font_keywords:
            self.assertIn(keyword, content, f"Шрифт {keyword} не найден")
    
    def test_border_radius_consistency(self):
        """Тест консистентности border-radius"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем что border-radius используется
        self.assertIn('border-radius', content, "border-radius не используется")
        
        # Проверяем что используется стандартное значение 8px
        self.assertIn('border-radius: 8px', content, 
                     "Стандартное значение border-radius: 8px не найдено")
    
    def _extract_css_rule(self, content, selector):
        """Вспомогательный метод для извлечения CSS правила"""
        escaped_selector = re.escape(selector).replace(r'\ ', r'\s*')
        pattern = escaped_selector + r'\s*\{([^}]*)\}'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None
    
    def test_no_animations_or_complex_effects(self):
        """Тест отсутствия анимаций и сложных эффектов"""
        with open(self.css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем отсутствие анимаций (исключая text-transform)
        animation_keywords = ['@keyframes', 'animation:', 'scale(', 'rotate(']
        
        for keyword in animation_keywords:
            self.assertNotIn(keyword, content, 
                           f"Найдена анимация или сложный эффект: {keyword}")
        
        # Проверяем transform отдельно, исключая text-transform
        transform_pattern = r'(?<!text-)transform:'
        self.assertIsNone(re.search(transform_pattern, content), 
                         "Найден запрещенный transform (не text-transform)")
        
        # Разрешаем только простой transition
        if 'transition:' in content:
            # Проверяем что это только простые transitions
            transition_pattern = r'transition:\s*[^;]*;'
            transitions = re.findall(transition_pattern, content)
            for transition in transitions:
                # Разрешаем только color transitions
                self.assertIn('color', transition, 
                             f"Найден сложный transition: {transition}")


if __name__ == '__main__':
    unittest.main()
