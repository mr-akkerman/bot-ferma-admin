from flask import session
from werkzeug.security import check_password_hash
from models import User

def login_user(username, password):
    """
    Проверяет существование пользователя в SQLite БД и сверяет хеш пароля.
    
    Args:
        username (str): Имя пользователя
        password (str): Пароль
    
    Returns:
        bool: True если авторизация успешна, False в противном случае
    """
    # Ищем пользователя по username
    user = User.query.filter_by(username=username).first()
    
    # Если пользователь не найден, возвращаем False
    if not user:
        return False
    
    # Проверяем пароль
    if check_password_hash(user.password_hash, password):
        # Сохраняем user_id в сессии
        session['user_id'] = user.id
        return True
    
    return False

def logout_user():
    """
    Очищает сессию пользователя (выход из системы).
    """
    session.pop('user_id', None)

def is_authenticated():
    """
    Проверяет, авторизован ли пользователь.
    
    Returns:
        bool: True если пользователь авторизован, False в противном случае
    """
    return 'user_id' in session
