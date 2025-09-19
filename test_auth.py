"""Тесты системы авторизации для админки"""
import tempfile
import os
from werkzeug.security import generate_password_hash
from app import app, db
from models import User
from auth import login_user, logout_user, is_authenticated


def test_auth_functionality():
    """Основной тест функциональности авторизации"""
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
                
                # Тест 1: Проверяем, что пользователь не аутентифицирован без входа
                response = client.get('/')
                assert is_authenticated() is False, "Пользователь не должен быть аутентифицирован без входа"
                
                # Тест 2: Успешная авторизация с правильными данными
                result = login_user('testuser', 'testpass')
                assert result is True, "Авторизация с правильными данными должна быть успешной"
                assert is_authenticated() is True, "Пользователь должен быть аутентифицирован после успешного входа"
                
                # Тест 3: Выход из системы
                logout_user()
                assert is_authenticated() is False, "Пользователь не должен быть аутентифицирован после выхода"
                
                # Тест 4: Неправильный username
                result = login_user('wronguser', 'testpass')
                assert result is False, "Авторизация с неправильным username должна быть отклонена"
                assert is_authenticated() is False, "Пользователь не должен быть аутентифицирован после неудачного входа"
                
                # Тест 5: Неправильный пароль
                result = login_user('testuser', 'wrongpass')
                assert result is False, "Авторизация с неправильным паролем должна быть отклонена"
                assert is_authenticated() is False, "Пользователь не должен быть аутентифицирован после неудачного входа"
                
                # Тест 6: Работа с админом
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin')
                )
                db.session.add(admin_user)
                db.session.commit()
                
                result = login_user('admin', 'admin')
                assert result is True, "Авторизация администратора должна быть успешной"
                assert is_authenticated() is True, "Администратор должен быть аутентифицирован"
                
                logout_user()
                assert is_authenticated() is False, "Администратор должен быть деаутентифицирован после выхода"
                
                print("✅ Все тесты авторизации пройдены успешно!")
                
    finally:
        # Очистка
        os.close(db_fd)
        os.unlink(db_path)


def test_session_functionality():
    """Тест работы с сессиями"""
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
                    username='sessionuser',
                    password_hash=generate_password_hash('sessionpass')
                )
                db.session.add(test_user)
                db.session.commit()
                
                # Проверяем, что изначально user_id отсутствует в сессии
                with client.session_transaction() as sess:
                    assert 'user_id' not in sess, "Сессия должна быть пустой изначально"
                
                # Тестируем авторизацию и проверку сессии
                # Выполняем запрос для создания контекста сессии
                response = client.get('/')
                
                # Авторизуемся
                login_user('sessionuser', 'sessionpass')
                
                # Проверяем статус авторизации
                assert is_authenticated() is True, "Пользователь должен быть аутентифицирован"
                
                # Выходим из системы
                logout_user()
                
                # Проверяем статус после выхода
                assert is_authenticated() is False, "Пользователь не должен быть аутентифицирован после выхода"
                
                # Дополнительный тест работы с сессией напрямую
                with client.session_transaction() as sess:
                    # Устанавливаем user_id вручную для тестирования логики is_authenticated
                    sess['user_id'] = test_user.id
                
                # Проверяем, что is_authenticated работает с установленным user_id
                response = client.get('/')
                assert is_authenticated() is True, "is_authenticated должен возвращать True при наличии user_id в сессии"
                
                print("✅ Все тесты сессий пройдены успешно!")
                
    finally:
        # Очистка
        os.close(db_fd)
        os.unlink(db_path)


if __name__ == '__main__':
    test_auth_functionality()
    test_session_functionality()
    print("🎉 Все тесты авторизации завершены успешно!")
