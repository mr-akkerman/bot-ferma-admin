import pytest
import os
from bs4 import BeautifulSoup
from app import app


@pytest.fixture
def client():
    """Создает тестовый клиент Flask"""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_dashboard_template_exists():
    """Тест существования шаблона dashboard.html"""
    template_path = os.path.join('templates', 'dashboard.html')
    assert os.path.exists(template_path), "Шаблон dashboard.html не найден"


def test_admins_template_exists():
    """Тест существования шаблона admins.html"""
    template_path = os.path.join('templates', 'admins.html')
    assert os.path.exists(template_path), "Шаблон admins.html не найден"


def test_tools_template_exists():
    """Тест существования шаблона tools.html"""
    template_path = os.path.join('templates', 'tools.html')
    assert os.path.exists(template_path), "Шаблон tools.html не найден"


def test_base_template_has_navigation_menu():
    """Тест наличия навигационного меню в базовом шаблоне"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Проверяем наличие сайдбара
    sidebar = soup.find('aside', class_='sidebar')
    assert sidebar is not None, "Сайдбар не найден в base.html"
    
    # Проверяем наличие навигации в сайдбаре
    sidebar_nav = sidebar.find('nav', class_='sidebar-nav')
    assert sidebar_nav is not None, "Навигация в сайдбаре не найдена"
    
    # Проверяем наличие списка ссылок
    nav_list = sidebar_nav.find('ul')
    assert nav_list is not None, "Список навигации не найден"
    
    # Проверяем наличие ссылок на все страницы
    links = nav_list.find_all('a')
    link_texts = [link.get_text().strip() for link in links]
    
    expected_links = ['Дашборд', 'Управление админами', 'Инструменты']
    for expected_link in expected_links:
        assert expected_link in link_texts, f"Ссылка '{expected_link}' не найдена в навигации"


def test_dashboard_template_extends_base():
    """Тест наследования dashboard.html от base.html"""
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '{% extends "base.html" %}' in content, "dashboard.html не наследуется от base.html"


def test_admins_template_extends_base():
    """Тест наследования admins.html от base.html"""
    with open('templates/admins.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '{% extends "base.html" %}' in content, "admins.html не наследуется от base.html"


def test_tools_template_extends_base():
    """Тест наследования tools.html от base.html"""
    with open('templates/tools.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '{% extends "base.html" %}' in content, "tools.html не наследуется от base.html"


def test_dashboard_template_has_correct_title():
    """Тест корректности заголовка в dashboard.html"""
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Проверяем блок title
    assert 'Дашборд - Admin Panel' in content, "Неверный заголовок страницы в dashboard.html"
    
    # Проверяем заголовок h1
    assert '<h1>Дашборд</h1>' in content, "Заголовок h1 'Дашборд' не найден в dashboard.html"


def test_admins_template_has_correct_title():
    """Тест корректности заголовка в admins.html"""
    with open('templates/admins.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем блок title
    assert 'Управление админами - Admin Panel' in content, "Неверный заголовок страницы в admins.html"
    
    # Проверяем заголовок h1
    assert '<h1>Управление админами</h1>' in content, "Заголовок h1 'Управление админами' не найден в admins.html"


def test_tools_template_has_correct_title():
    """Тест корректности заголовка в tools.html"""
    with open('templates/tools.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем блок title
    assert 'Инструменты - Admin Panel' in content, "Неверный заголовок страницы в tools.html"
    
    # Проверяем заголовок h1
    assert '<h1>Инструменты</h1>' in content, "Заголовок h1 'Инструменты' не найден в tools.html"


def test_dashboard_template_has_statistics_placeholder():
    """Тест наличия секций статистики в dashboard.html"""
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'global-statistics' in content, "Секция глобальной статистики не найдена в dashboard.html"
    assert 'Общая статистика' in content, "Заголовок 'Общая статистика' не найден"
    assert 'groups-statistics' in content, "Секция статистики по группам не найдена в dashboard.html"


def test_admins_template_has_admins_placeholder():
    """Тест наличия плейсхолдера для списка админов в admins.html"""
    with open('templates/admins.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'admins-placeholder' in content, "Плейсхолдер для админов не найден в admins.html"
    assert 'список администраторов' in content, "Текст плейсхолдера админов не найден"


def test_tools_template_has_development_message():
    """Тест наличия сообщения о разработке в tools.html"""
    with open('templates/tools.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'Инструменты в разработке' in content, "Сообщение 'Инструменты в разработке' не найдено в tools.html"


def test_navigation_links_structure():
    """Тест структуры ссылок навигации"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Находим все ссылки в навигации
    nav_links = soup.find('nav', class_='sidebar-nav').find_all('a')
    
    # Проверяем, что есть 3 ссылки
    assert len(nav_links) == 3, f"Ожидается 3 ссылки в навигации, найдено {len(nav_links)}"
    
    # Проверяем href атрибуты ссылок
    expected_hrefs = [
        "{{ url_for('dashboard') }}",
        "{{ url_for('admins') }}",
        "{{ url_for('tools') }}"
    ]
    
    for i, link in enumerate(nav_links):
        href = link.get('href')
        assert href == expected_hrefs[i], f"Неверный href для ссылки {i+1}: ожидается {expected_hrefs[i]}, получено {href}"
