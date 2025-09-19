from models import User
from sqlalchemy.exc import IntegrityError


def get_admins_list():
    """Возвращает список всех админов"""
    try:
        admins = User.get_all_admins()
        return {
            'success': True,
            'admins': [
                {
                    'id': admin.id,
                    'username': admin.username,
                    'created_at': admin.created_at.isoformat() if admin.created_at else None
                }
                for admin in admins
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка получения списка админов: {str(e)}'
        }


def add_admin(username, password):
    """
    Проверяет уникальность username и создает нового админа
    Возвращает успех/ошибку
    """
    try:
        # Проверяем что username не пустой
        if not username or not username.strip():
            return {
                'success': False,
                'error': 'Имя пользователя не может быть пустым'
            }
        
        # Проверяем уникальность username
        if User.admin_exists(username):
            return {
                'success': False,
                'error': f'Админ с именем "{username}" уже существует'
            }
        
        # Создаем нового админа
        new_admin = User.create_admin(username, password)
        
        return {
            'success': True,
            'admin': {
                'id': new_admin.id,
                'username': new_admin.username,
                'created_at': new_admin.created_at.isoformat() if new_admin.created_at else None
            }
        }
    
    except IntegrityError:
        return {
            'success': False,
            'error': f'Админ с именем "{username}" уже существует'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка создания админа: {str(e)}'
        }


def remove_admin(user_id):
    """
    Проверяет что это не последний админ и удаляет админа
    Возвращает успех/ошибку
    """
    try:
        # Пытаемся удалить админа (метод сам проверит количество админов)
        result = User.delete_admin(user_id)
        
        if result:
            return {
                'success': True,
                'message': f'Админ с ID {user_id} успешно удален'
            }
        else:
            return {
                'success': False,
                'error': f'Админ с ID {user_id} не найден'
            }
    
    except ValueError as e:
        # Ошибка защиты от удаления последнего админа
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка удаления админа: {str(e)}'
        }
