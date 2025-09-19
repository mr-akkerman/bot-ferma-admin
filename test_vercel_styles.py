#!/usr/bin/env python3
"""
Тесты для проверки соответствия CSS стилей Vercel Geist Design System
"""

import os
import re
import pytest


class TestVercelStyles:
    """Тесты для проверки CSS стилей в стиле Vercel Geist Design System"""
    
    @classmethod
    def setup_class(cls):
        """Подготовка к тестам - чтение CSS файла"""
        css_path = os.path.join(os.path.dirname(__file__), 'static', 'css', 'style.css')
        
        if not os.path.exists(css_path):
            pytest.fail(f"CSS файл не найден: {css_path}")
        
        with open(css_path, 'r', encoding='utf-8') as f:
            cls.css_content = f.read()
    
    def test_css_file_exists(self):
        """Проверка существования CSS файла"""
        css_path = os.path.join(os.path.dirname(__file__), 'static', 'css', 'style.css')
        assert os.path.exists(css_path), "CSS файл должен существовать"
    
    def test_vercel_color_variables(self):
        """Проверка наличия точных цветов Vercel в CSS переменных"""
        # Основные цвета фона
        assert "--background-1: #FFFFFF" in self.css_content, "Должен быть основной фон #FFFFFF"
        assert "--background-2: #FAFAFA" in self.css_content, "Должен быть вторичный фон #FAFAFA"
        
        # Цвета для состояний
        assert "--color-1: #F5F5F5" in self.css_content, "Должен быть цвет hover #F5F5F5"
        assert "--color-2: #E5E5E5" in self.css_content, "Должен быть цвет active #E5E5E5"
        assert "--color-3: #D4D4D4" in self.css_content, "Должен быть цвет границ #D4D4D4"
        
        # Цвета текста
        assert "--foreground-1: #171717" in self.css_content, "Должен быть основной текст #171717"
        assert "--foreground-2: #737373" in self.css_content, "Должен быть вторичный текст #737373"
        
        # Акцентный цвет
        assert "--accent: #000000" in self.css_content, "Должен быть акцентный цвет #000000"
    
    def test_geist_typography(self):
        """Проверка типографики Geist"""
        # Основной шрифт Inter
        font_family_pattern = r"font-family.*Inter.*-apple-system.*BlinkMacSystemFont.*Segoe UI.*system-ui.*sans-serif"
        assert re.search(font_family_pattern, self.css_content), "Должен использоваться шрифт Inter с системными fallbacks"
        
        # Проверка основных размеров шрифтов
        assert "font-size: 14px" in self.css_content, "Должен быть размер шрифта 14px"
        assert "font-size: 32px" in self.css_content, "Должен быть размер шрифта 32px для больших значений"
        
        # Проверка font-weight
        assert "font-weight: 600" in self.css_content, "Должен быть font-weight: 600 для заголовков"
        assert "font-weight: 400" in self.css_content, "Должен быть font-weight: 400 для основного текста"
        assert "font-weight: 500" in self.css_content, "Должен быть font-weight: 500 для средних элементов"
        
        # Проверка line-height
        assert "line-height: 1.5" in self.css_content, "Должен быть line-height: 1.5"
    
    def test_spacing_grid(self):
        """Проверка использования 8px сетки"""
        # Основные отступы по 8px сетке
        spacing_variables = [
            "--spacing-1: 8px",
            "--spacing-2: 16px", 
            "--spacing-3: 24px",
            "--spacing-4: 32px",
            "--spacing-6: 48px"
        ]
        
        for spacing in spacing_variables:
            assert spacing in self.css_content, f"Должна быть переменная {spacing}"
    
    def test_sidebar_layout(self):
        """Проверка правильного макета бокового меню"""
        # Ширина бокового меню
        assert "width: 240px" in self.css_content, "Ширина sidebar должна быть 240px"
        
        # Отступ контента
        assert "margin-left: 256px" in self.css_content, "Контент должен иметь отступ 256px (240px + 16px)"
        
        # Фиксированное позиционирование
        assert "position: fixed" in self.css_content, "Sidebar должен быть зафиксирован"
    
    def test_component_styles(self):
        """Проверка стилей основных компонентов"""
        # Карточки статистики
        assert ".stat-card" in self.css_content, "Должны быть стили для .stat-card"
        
        # Таблицы
        assert ".groups-table" in self.css_content, "Должны быть стили для .groups-table"
        assert ".admins-table" in self.css_content, "Должны быть стили для .admins-table"
        
        # Формы
        assert ".admin-form" in self.css_content, "Должны быть стили для .admin-form"
        assert ".form-group" in self.css_content, "Должны быть стили для .form-group"
        
        # Кнопки
        assert ".btn" in self.css_content, "Должны быть базовые стили для .btn"
        assert ".btn-primary" in self.css_content, "Должны быть стили для .btn-primary"
        assert ".btn-danger" in self.css_content, "Должны быть стили для .btn-danger"
    
    def test_border_radius(self):
        """Проверка правильных радиусов границ"""
        # Переменные радиусов
        assert "--radius-sm: 6px" in self.css_content, "Должен быть радиус 6px"
        assert "--radius-md: 8px" in self.css_content, "Должен быть радиус 8px"
        
        # Использование border-radius
        assert "border-radius: var(--radius-sm)" in self.css_content, "Должно использоваться var(--radius-sm)"
        assert "border-radius: var(--radius-md)" in self.css_content, "Должно использоваться var(--radius-md)"
    
    def test_shadow_styles(self):
        """Проверка правильных теней"""
        # Переменная тени
        assert "--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1)" in self.css_content, "Должна быть тонкая тень"
        
        # Использование тени
        assert "box-shadow: var(--shadow-sm)" in self.css_content, "Должно использоваться var(--shadow-sm)"
    
    def test_transitions(self):
        """Проверка переходов"""
        # Переменная перехода
        assert "--transition: all 0.15s ease" in self.css_content, "Должен быть transition 0.15s ease"
        
        # Использование перехода
        assert "transition: var(--transition)" in self.css_content, "Должно использоваться var(--transition)"
    
    def test_button_styles(self):
        """Проверка стилей кнопок"""
        # Основные стили кнопок
        button_styles = [
            "padding: 8px var(--spacing-2)",
            "border-radius: var(--radius-sm)",
            "font-weight: 500",
            "font-size: 14px"
        ]
        
        for style in button_styles:
            assert style in self.css_content, f"Кнопки должны иметь стиль: {style}"
        
        # Цвета кнопок
        assert "background-color: var(--accent)" in self.css_content, "Primary кнопка должна использовать accent цвет"
        assert "background-color: var(--danger)" in self.css_content, "Danger кнопка должна использовать danger цвет"
    
    def test_table_styles(self):
        """Проверка стилей таблиц"""
        # Основные стили таблиц
        table_styles = [
            "border: 1px solid var(--color-2)",
            "border-radius: var(--radius-md)",
            "box-shadow: var(--shadow-sm)",
            "background-color: var(--background-2)"  # для заголовков
        ]
        
        for style in table_styles:
            assert style in self.css_content, f"Таблицы должны иметь стиль: {style}"
        
        # Hover эффект
        assert "background-color: var(--color-1)" in self.css_content, "Должен быть hover эффект для строк"
    
    def test_form_styles(self):
        """Проверка стилей форм"""
        # Стили input полей
        input_styles = [
            "border: 1px solid var(--color-3)",
            "border-radius: var(--radius-sm)",
            "padding: 8px 12px",
            "font-size: 14px"
        ]
        
        for style in input_styles:
            assert style in self.css_content, f"Input поля должны иметь стиль: {style}"
        
        # Focus состояние
        assert "border-color: var(--accent)" in self.css_content, "Focus должен менять цвет границы на accent"
    
    def test_responsive_design(self):
        """Проверка адаптивного дизайна"""
        # Media queries
        assert "@media (max-width: 1024px)" in self.css_content, "Должны быть стили для планшетов"
        assert "@media (max-width: 768px)" in self.css_content, "Должны быть стили для мобильных устройств"
        assert "@media (max-width: 480px)" in self.css_content, "Должны быть стили для маленьких экранов"
    
    def test_no_forbidden_styles(self):
        """Проверка отсутствия запрещенных стилей"""
        # Запрещенные градиенты
        assert "gradient" not in self.css_content.lower(), "НЕ должно быть градиентов"
        
        # Запрещенные толстые тени
        shadow_pattern = r"box-shadow:.*[5-9]\d*px"
        assert not re.search(shadow_pattern, self.css_content), "НЕ должно быть толстых теней"
        
        # Запрещенные толстые границы
        border_pattern = r"border:.*[3-9]\d*px"
        assert not re.search(border_pattern, self.css_content), "НЕ должно быть толстых границ"
    
    def test_accessibility_features(self):
        """Проверка функций доступности"""
        # Focus-visible стили
        assert ":focus-visible" in self.css_content, "Должны быть стили для focus-visible"
        
        # Outline для доступности
        assert "outline: 2px solid var(--accent)" in self.css_content, "Должен быть outline для фокуса"
        
        # Disabled состояние
        assert ":disabled" in self.css_content, "Должны быть стили для disabled элементов"
    
    def test_utility_classes(self):
        """Проверка вспомогательных классов"""
        utility_classes = [
            ".text-center",
            ".text-left", 
            ".text-right",
            ".hidden",
            ".visible",
            ".mb-1", ".mb-2", ".mb-3",
            ".mt-1", ".mt-2", ".mt-3",
            ".p-1", ".p-2", ".p-3"
        ]
        
        for class_name in utility_classes:
            assert class_name in self.css_content, f"Должен быть вспомогательный класс {class_name}"
    
    def test_header_layout(self):
        """Проверка правильного макета header"""
        # Стили header
        header_styles = [
            "position: fixed",
            "height: 64px",
            "box-sizing: border-box",
            "justify-content: space-between",
            "flex-shrink: 0"
        ]
        
        for style in header_styles:
            assert style in self.css_content, f"Header должен иметь стиль: {style}"
        
        # Стили для header actions
        assert ".header-actions form" in self.css_content, "Должны быть стили для формы в header"
        assert ".header-actions .btn" in self.css_content, "Должны быть стили для кнопок в header"

    def test_css_organization(self):
        """Проверка организации CSS кода"""
        # Проверка наличия комментариев-разделителей
        section_comments = [
            "БАЗОВЫЕ СТИЛИ И ЦВЕТОВАЯ СХЕМА",
            "HEADER",
            "SIDEBAR NAVIGATION", 
            "MAIN CONTENT AREA",
            "КАРТОЧКИ СТАТИСТИКИ",
            "ТАБЛИЦЫ",
            "ФОРМЫ",
            "КНОПКИ",
            "АДАПТИВНОСТЬ"
        ]
        
        for comment in section_comments:
            assert comment in self.css_content, f"Должен быть комментарий-раздел: {comment}"
    
    def test_login_page_styles(self):
        """Проверка стилей страницы логина"""
        login_styles = [
            ".login-page",
            ".login-container", 
            "min-height: 100vh",
            "max-width: 400px"
        ]
        
        for style in login_styles:
            assert style in self.css_content, f"Должен быть стиль для логина: {style}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
