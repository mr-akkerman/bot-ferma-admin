"""Тесты роутов авторизации"""
import tempfile
import os
from werkzeug.security import generate_password_hash
from app import app, db
from models import User


def test_auth_routes():
    """Основной тест роутов авторизации"""
    # Создаем временную базу данных
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Настраиваем приложение для тестов
    app.config.update({
        'TESTING': True,
        'ADMIN_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_BINDS': {
            'sqlite': f'sqlite:///{db_path}',
            'postgres': app.config.get('PROFILES_DATABASE_URI', 'sqlite:///test.db')
        },
        'SECRET_KEY': 'test_secret_key'
    })
    
    try:
        with app.test_client() as client:
            with app.app_context():
                # Удаляем и создаем таблицы заново
                db.drop_all(bind_key='sqlite')
                db.create_all(bind_key='sqlite')
                
                # Создаем тестового пользователя
                test_user = User(
                    username='testuser',
                    password_hash=generate_password_hash('testpass')
                )
                db.session.add(test_user)
                db.session.commit()
                
                # Тест 1: GET / без авторизации должен редиректить на /login
                response = client.get('/', follow_redirects=False)
                assert response.status_code == 302, "Главная страница должна редиректить неавторизованного пользователя"
                assert '/login' in response.location, "Редирект должен быть на /login"
                
                # Тест 2: GET /login должен возвращать страницу входа
                response = client.get('/login')
                assert response.status_code == 200, "Страница входа должна быть доступна"
                
                # Тест 3: POST /login с неправильными данными
                response = client.post('/login', data={'username': 'wrong', 'password': 'wrong'})
                assert response.status_code == 200, "При неправильных данных должна отображаться страница входа"
                
                # Тест 4: POST /login с правильными данными должен редиректить на /dashboard
                response = client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=False)
                assert response.status_code == 302, "Успешный вход должен редиректить"
                assert '/dashboard' in response.location, "Редирект должен быть на /dashboard"
                
                # Тест 5: GET / после авторизации должен редиректить на /dashboard
                # Сначала авторизуемся
                client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
                response = client.get('/', follow_redirects=False)
                assert response.status_code == 302, "Главная страница должна редиректить авторизованного пользователя"
                assert '/dashboard' in response.location, "Редирект должен быть на /dashboard"
                
                # Тест 6: GET /dashboard должен быть доступен после авторизации
                response = client.get('/dashboard')
                assert response.status_code == 200, "Дашборд должен быть доступен авторизованному пользователю"
                assert "Дашборд" in response.get_data(as_text=True), "Дашборд должен содержать соответствующий контент"
                
                # Тест 7: POST /logout должен выходить из системы и редиректить на /login
                response = client.post('/logout', follow_redirects=False)
                assert response.status_code == 302, "Выход должен редиректить"
                assert '/login' in response.location, "Редирект должен быть на /login"
                
                # Тест 8: После выхода GET / должен снова редиректить на /login
                response = client.get('/', follow_redirects=False)
                assert response.status_code == 302, "После выхода главная страница должна редиректить на вход"
                assert '/login' in response.location, "Редирект должен быть на /login"
                
                print("✅ Все тесты роутов авторизации пройдены успешно!")
                
    finally:
        # Очистка
        os.close(db_fd)
        os.unlink(db_path)


def test_route_methods():
    """Тест проверки методов HTTP для роутов"""
    # Создаем временную базу данных
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Настраиваем приложение для тестов
    app.config.update({
        'TESTING': True,
        'ADMIN_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_BINDS': {
            'sqlite': f'sqlite:///{db_path}',
            'postgres': app.config.get('PROFILES_DATABASE_URI', 'sqlite:///test.db')
        },
        'SECRET_KEY': 'test_secret_key'
    })
    
    try:
        with app.test_client() as client:
            with app.app_context():
                # Создаем таблицы
                db.drop_all(bind_key='sqlite')
                db.create_all(bind_key='sqlite')
                
                # Тест 1: /login поддерживает GET и POST
                get_response = client.get('/login')
                assert get_response.status_code == 200, "/login должен поддерживать GET"
                
                post_response = client.post('/login', data={'username': 'test', 'password': 'test'})
                assert post_response.status_code == 200, "/login должен поддерживать POST"
                
                # Тест 2: /logout поддерживает только POST
                post_logout = client.post('/logout')
                assert post_logout.status_code == 302, "/logout должен поддерживать POST и редиректить"
                
                # Тест 3: Несуществующий роут без авторизации должен редиректить на /login (из-за защиты роутов)
                response = client.get('/nonexistent')
                assert response.status_code == 302, "Несуществующий роут должен редиректить на логин из-за защиты роутов"
                assert '/login' in response.location, "Редирект должен быть на /login"
                
                print("✅ Все тесты методов роутов пройдены успешно!")
                
    finally:
        # Очистка
        os.close(db_fd)
        os.unlink(db_path)


def test_session_persistence_routes():
    """Тест сохранения сессии между запросами к роутам"""
    # Создаем временную базу данных
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Настраиваем приложение для тестов
    app.config.update({
        'TESTING': True,
        'ADMIN_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_BINDS': {
            'sqlite': f'sqlite:///{db_path}',
            'postgres': app.config.get('PROFILES_DATABASE_URI', 'sqlite:///test.db')
        },
        'SECRET_KEY': 'test_secret_key'
    })
    
    try:
        with app.test_client() as client:
            with app.app_context():
                # Создаем таблицы
                db.drop_all(bind_key='sqlite')
                db.create_all(bind_key='sqlite')
                
                # Создаем админа
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin')
                )
                db.session.add(admin_user)
                db.session.commit()
                
                # Тест 1: Авторизуемся как админ
                response = client.post('/login', data={'username': 'admin', 'password': 'admin'})
                assert response.status_code == 302, "Админ должен успешно авторизоваться"
                
                # Тест 2: Проверяем доступ к дашборду без повторной авторизации
                response = client.get('/dashboard')
                assert response.status_code == 200, "Дашборд должен быть доступен без повторной авторизации"
                
                # Тест 3: Главная страница должна редиректить на дашборд
                response = client.get('/', follow_redirects=False)
                assert response.status_code == 302, "Главная должна редиректить авторизованного пользователя"
                assert '/dashboard' in response.location, "Редирект должен быть на дашборд"
                
                # Тест 4: Выход должен сбросить сессию
                response = client.post('/logout')
                assert response.status_code == 302, "Выход должен работать"
                
                # Тест 5: После выхода доступ к дашборду должен быть заблокирован
                response = client.get('/')
                assert response.status_code == 302, "После выхода должен быть редирект на логин"
                
                print("✅ Все тесты сохранения сессии пройдены успешно!")
                
    finally:
        # Очистка
        os.close(db_fd)
        os.unlink(db_path)


if __name__ == '__main__':
    test_auth_routes()
    test_route_methods()
    test_session_persistence_routes()
    print("🎉 Все тесты роутов авторизации завершены успешно!")
