import os
from bs4 import BeautifulSoup

class TestTemplates:
    """Тесты для HTML шаблонов"""
    
    def test_templates_exist(self):
        """Тест наличия всех шаблонов"""
        templates_dir = 'templates'
        
        # Проверяем что папка templates существует
        assert os.path.isdir(templates_dir), "Папка templates не найдена"
        
        # Проверяем наличие файлов шаблонов
        base_template = os.path.join(templates_dir, 'base.html')
        login_template = os.path.join(templates_dir, 'login.html')
        
        assert os.path.exists(base_template), "Шаблон base.html не найден"
        assert os.path.exists(login_template), "Шаблон login.html не найден"
    
    def test_base_template_structure(self):
        """Тест корректности HTML структуры base.html"""
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Проверяем основную HTML5 структуру
        assert soup.find('html'), "Отсутствует тег <html>"
        assert soup.find('head'), "Отсутствует тег <head>"
        assert soup.find('body'), "Отсутствует тег <body>"
        
        # Проверяем meta теги
        charset_meta = soup.find('meta', {'charset': True})
        assert charset_meta, "Отсутствует meta charset"
        assert charset_meta.get('charset') == 'UTF-8', "Некорректная кодировка"
        
        viewport_meta = soup.find('meta', {'name': 'viewport'})
        assert viewport_meta, "Отсутствует meta viewport"
        
        # Проверяем title
        title = soup.find('title')
        assert title, "Отсутствует тег <title>"
        
        # Проверяем подключение CSS
        css_link = soup.find('link', {'rel': 'stylesheet'})
        assert css_link, "Отсутствует подключение CSS"
        href = css_link.get('href')
        assert 'style.css' in href, "Некорректное подключение style.css"
    
    def test_base_template_navigation(self):
        """Тест навигации в base.html"""
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Проверяем наличие навигации
        header = soup.find('header')
        assert header, "Отсутствует тег <header>"
        
        nav = soup.find('nav')
        assert nav, "Отсутствует тег <nav>"
        
        # Проверяем заголовок Admin Panel
        h1 = soup.find('h1')
        assert h1, "Отсутствует заголовок h1"
        assert 'Admin Panel' in h1.get_text(), "Некорректный текст заголовка"
    
    def test_base_template_content_block(self):
        """Тест блока контента в base.html"""
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие блока content
        assert '{% block content %}' in content, "Отсутствует блок content"
        assert '{% endblock %}' in content, "Не закрыт блок content"
        
        # Проверяем main тег
        soup = BeautifulSoup(content, 'html.parser')
        main = soup.find('main')
        assert main, "Отсутствует тег <main>"
    
    def test_login_template_inheritance(self):
        """Тест наследования в login.html"""
        with open('templates/login.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем extends
        assert '{% extends "base.html" %}' in content, "Отсутствует наследование от base.html"
        
        # Проверяем блоки
        assert '{% block title %}' in content, "Отсутствует блок title"
        assert '{% block content %}' in content, "Отсутствует блок content"
    
    def test_login_form_structure(self):
        """Тест структуры формы в login.html"""
        with open('templates/login.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Проверяем наличие формы
        form = soup.find('form')
        assert form, "Отсутствует тег <form>"
        
        # Проверяем атрибуты формы
        assert form.get('method') == 'POST', "Некорректный метод формы"
        
        # Проверяем поля username и password
        username_input = soup.find('input', {'name': 'username'})
        assert username_input, "Отсутствует поле username"
        assert username_input.get('type') == 'text', "Некорректный тип поля username"
        assert username_input.get('required') is not None, "Поле username не обязательное"
        
        password_input = soup.find('input', {'name': 'password'})
        assert password_input, "Отсутствует поле password"
        assert password_input.get('type') == 'password', "Некорректный тип поля password"
        assert password_input.get('required') is not None, "Поле password не обязательное"
        
        # Проверяем кнопку submit
        submit_button = soup.find('button', {'type': 'submit'})
        assert submit_button, "Отсутствует кнопка отправки"
        assert 'Войти' in submit_button.get_text(), "Некорректный текст кнопки"
    
    def test_login_form_labels(self):
        """Тест меток полей в форме входа"""
        with open('templates/login.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Проверяем метки
        username_label = soup.find('label', {'for': 'username'})
        assert username_label, "Отсутствует метка для поля username"
        
        password_label = soup.find('label', {'for': 'password'})
        assert password_label, "Отсутствует метка для поля password"
        
        # Проверяем соответствие id полей
        username_input = soup.find('input', {'id': 'username'})
        assert username_input, "Поле username не имеет id"
        
        password_input = soup.find('input', {'id': 'password'})
        assert password_input, "Поле password не имеет id"

if __name__ == '__main__':
    # Запуск тестов без pytest (базовая проверка)
    test_instance = TestTemplates()
    
    print("Запуск базовых тестов шаблонов...")
    
    tests = [
        ('Тест наличия шаблонов', test_instance.test_templates_exist),
        ('Тест HTML структуры base.html', test_instance.test_base_template_structure),
        ('Тест навигации в base.html', test_instance.test_base_template_navigation),
        ('Тест блока контента в base.html', test_instance.test_base_template_content_block),
        ('Тест наследования в login.html', test_instance.test_login_template_inheritance),
        ('Тест структуры формы входа', test_instance.test_login_form_structure),
        ('Тест меток полей формы', test_instance.test_login_form_labels)
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name} - ПРОЙДЕН")
        except Exception as e:
            print(f"✗ {test_name} - ПРОВАЛЕН: {e}")
    
    print("\nВсе тесты шаблонов завершены!")
