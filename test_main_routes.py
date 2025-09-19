import pytest
import os
import tempfile
from app import app
from models import db, User
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def client():
    """Создает тестовый клиент Flask"""
    # Создаем временную базу данных для тестов
    db_fd, db_path = tempfile.mkstemp()
    
    # Устанавливаем тестовую конфигурацию
    app.config['TESTING'] = True
    test_db_uri = f'sqlite:///{db_path}'
    app.config['ADMIN_DATABASE_URI'] = test_db_uri
    app.config['SQLALCHEMY_DATABASE_URI'] = test_db_uri
    app.config['SQLALCHEMY_BINDS'] = {
        'sqlite': test_db_uri,
        'postgres': app.config.get('PROFILES_DATABASE_URI', 'postgresql://localhost/test')
    }
    
    with app.test_client() as client:
        with app.app_context():
            # Удаляем все таблицы, если они существуют
            db.drop_all(bind_key='sqlite')
            # Создаем таблицы заново
            db.create_all(bind_key='sqlite')
            
            # Создаем тестового пользователя
            password_hash = generate_password_hash('testpass')
            test_user = User(username='testuser', password_hash=password_hash)
            db.session.add(test_user)
            db.session.commit()
            
        yield client
    
    # Очистка после тестов
    try:
        os.close(db_fd)
        os.unlink(db_path)
    except (OSError, FileNotFoundError):
        pass  # Игнорируем ошибки удаления файла


def test_dashboard_route_authorized(client):
    """Тест доступности роута /dashboard для авторизованных пользователей"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Проверяем доступ к dashboard
    response = client.get('/dashboard')
    
    assert response.status_code == 200, "Dashboard должен быть доступен для авторизованного пользователя"
    assert 'Дашборд' in response.data.decode('utf-8'), "Dashboard должен содержать заголовок 'Дашборд'"
    assert 'Общая статистика' in response.data.decode('utf-8'), "Dashboard должен содержать раздел 'Общая статистика'"


def test_admins_route_authorized(client):
    """Тест доступности роута /admins для авторизованных пользователей"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Проверяем доступ к admins
    response = client.get('/admins')
    
    assert response.status_code == 200, "Admins должен быть доступен для авторизованного пользователя"
    assert 'Управление админами' in response.data.decode('utf-8'), "Admins должен содержать заголовок 'Управление админами'"
    assert 'Управление админами' in response.data.decode('utf-8'), "Admins должен содержать заголовок управления админами"


def test_tools_route_authorized(client):
    """Тест доступности роута /tools для авторизованных пользователей"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Проверяем доступ к tools
    response = client.get('/tools')
    
    assert response.status_code == 200, "Tools должен быть доступен для авторизованного пользователя"
    assert 'Инструменты' in response.data.decode('utf-8'), "Tools должен содержать заголовок 'Инструменты'"
    assert 'Инструменты в разработке' in response.data.decode('utf-8'), "Tools должен содержать сообщение о разработке"


def test_dashboard_route_unauthorized(client):
    """Тест блокировки роута /dashboard для неавторизованных пользователей"""
    # Не авторизуемся
    response = client.get('/dashboard')
    
    assert response.status_code == 302, "Dashboard должен редиректить неавторизованного пользователя"
    assert '/login' in response.location, "Редирект должен быть на /login"


def test_admins_route_unauthorized(client):
    """Тест блокировки роута /admins для неавторизованных пользователей"""
    # Не авторизуемся
    response = client.get('/admins')
    
    assert response.status_code == 302, "Admins должен редиректить неавторизованного пользователя"
    assert '/login' in response.location, "Редирект должен быть на /login"


def test_tools_route_unauthorized(client):
    """Тест блокировки роута /tools для неавторизованных пользователей"""
    # Не авторизуемся
    response = client.get('/tools')
    
    assert response.status_code == 302, "Tools должен редиректить неавторизованного пользователя"
    assert '/login' in response.location, "Редирект должен быть на /login"


def test_all_routes_render_correct_templates(client):
    """Тест корректности отображения шаблонов для всех роутов"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Проверяем dashboard
    dashboard_response = client.get('/dashboard')
    assert dashboard_response.status_code == 200
    dashboard_content = dashboard_response.data.decode('utf-8')
    assert 'Дашборд - Admin Panel' in dashboard_content, "Dashboard должен иметь корректный title"
    assert 'global-statistics' in dashboard_content, "Dashboard должен содержать секцию глобальной статистики"
    
    # Проверяем admins
    admins_response = client.get('/admins')
    assert admins_response.status_code == 200
    admins_content = admins_response.data.decode('utf-8')
    assert 'Управление админами - Admin Panel' in admins_content, "Admins должен иметь корректный title"
    assert 'admin-form' in admins_content, "Admins должен содержать форму добавления админа"
    
    # Проверяем tools
    tools_response = client.get('/tools')
    assert tools_response.status_code == 200
    tools_content = tools_response.data.decode('utf-8')
    assert 'Инструменты - Admin Panel' in tools_content, "Tools должен иметь корректный title"


def test_routes_have_navigation_menu(client):
    """Тест наличия навигационного меню на всех страницах"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    routes = ['/dashboard', '/admins', '/tools']
    
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200
        content = response.data.decode('utf-8')
        
        # Проверяем наличие навигационного меню
        assert 'sidebar-nav' in content, f"Роут {route} должен содержать навигационное меню"
        assert 'Дашборд</a>' in content, f"Роут {route} должен содержать ссылку на Дашборд"
        assert 'Управление админами</a>' in content, f"Роут {route} должен содержать ссылку на Управление админами"
        assert 'Инструменты</a>' in content, f"Роут {route} должен содержать ссылку на Инструменты"


def test_routes_extend_base_template(client):
    """Тест наследования от базового шаблона для всех роутов"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    routes = ['/dashboard', '/admins', '/tools']
    
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200
        content = response.data.decode('utf-8')
        
        # Проверяем наличие элементов базового шаблона
        assert 'Admin Panel</h1>' in content, f"Роут {route} должен содержать заголовок из base.html"
        assert 'main-content' in content, f"Роут {route} должен содержать main-content блок"
        assert '<html lang="ru">' in content, f"Роут {route} должен использовать русскую локализацию"


def test_routes_methods_are_get_only(client):
    """Тест что роуты работают только с GET методом"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    routes = ['/dashboard', '/admins', '/tools']
    
    for route in routes:
        # GET должен работать
        get_response = client.get(route)
        assert get_response.status_code == 200, f"GET {route} должен возвращать 200"
        
        # POST должен возвращать 405 (Method Not Allowed)
        post_response = client.post(route)
        assert post_response.status_code == 405, f"POST {route} должен возвращать 405 Method Not Allowed"
        
        # PUT должен возвращать 405 (Method Not Allowed)
        put_response = client.put(route)
        assert put_response.status_code == 405, f"PUT {route} должен возвращать 405 Method Not Allowed"


def test_routes_protection_middleware_active(client):
    """Тест активности middleware защиты роутов"""
    routes = ['/dashboard', '/admins', '/tools']
    
    # Без авторизации все роуты должны редиректить на /login
    for route in routes:
        response = client.get(route)
        assert response.status_code == 302, f"Неавторизованный доступ к {route} должен быть заблокирован"
        assert '/login' in response.location, f"Редирект с {route} должен быть на /login"
    
    # После авторизации все роуты должны быть доступны
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Авторизованный доступ к {route} должен быть разрешен"

