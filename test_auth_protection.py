import pytest
import os
import tempfile
from app import app, init_db
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


def test_unauthorized_access_blocked(client):
    """Тест блокировки неавторизованных запросов"""
    # Попытка доступа к защищенному роуту без авторизации
    response = client.get('/dashboard')
    
    # Должен быть редирект на /login
    assert response.status_code == 302
    assert '/login' in response.location


def test_unauthorized_access_to_index_redirects_to_login(client):
    """Тест редиректа с главной страницы на login для неавторизованного пользователя"""
    response = client.get('/')
    
    # Должен быть редирект на /login
    assert response.status_code == 302
    assert '/login' in response.location


def test_login_page_accessible_without_auth(client):
    """Тест доступности страницы логина без авторизации"""
    response = client.get('/login')
    
    # Страница логина должна быть доступна
    assert response.status_code == 200


def test_logout_accessible_without_auth(client):
    """Тест доступности роута logout без авторизации"""
    response = client.post('/logout')
    
    # Должен быть редирект на /login (logout обрабатывается без ошибок)
    assert response.status_code == 302
    assert '/login' in response.location


def test_authorized_user_access_allowed(client):
    """Тест пропуска авторизованных пользователей"""
    # Сначала авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1  # ID тестового пользователя
    
    # Теперь доступ к защищенному роуту должен быть разрешен
    response = client.get('/dashboard')
    
    # Должен быть успешный ответ (200)
    assert response.status_code == 200
    assert 'Дашборд' in response.data.decode('utf-8')


def test_authorized_user_index_redirects_to_dashboard(client):
    """Тест редиректа авторизованного пользователя с главной страницы на dashboard"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    response = client.get('/')
    
    # Должен быть редирект на /dashboard
    assert response.status_code == 302
    assert '/dashboard' in response.location


def test_login_form_submission_with_valid_credentials(client):
    """Тест успешной авторизации через форму логина"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Должен быть редирект на dashboard после успешного логина
    assert response.status_code == 302
    assert '/dashboard' in response.location


def test_login_form_submission_with_invalid_credentials(client):
    """Тест неуспешной авторизации через форму логина"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpass'
    })
    
    # Должен остаться на странице логина
    assert response.status_code == 200


def test_logout_clears_session_and_redirects(client):
    """Тест очистки сессии при logout и корректного редиректа"""
    # Авторизуемся
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Выходим из системы
    response = client.post('/logout')
    
    # Должен быть редирект на login
    assert response.status_code == 302
    assert '/login' in response.location
    
    # Проверяем, что после logout доступ к защищенным роутам заблокирован
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.location


def test_session_persistence_across_requests(client):
    """Тест сохранения сессии между запросами"""
    # Авторизуемся
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Делаем несколько запросов к защищенному роуту
    response1 = client.get('/dashboard')
    response2 = client.get('/dashboard')
    
    # Все запросы должны быть успешными
    assert response1.status_code == 200
    assert response2.status_code == 200
