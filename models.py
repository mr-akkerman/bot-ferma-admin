from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import generate_password_hash

# Инициализация SQLAlchemy
db = SQLAlchemy()

# Модель User для PostgreSQL БД админов
class User(db.Model):
    __bind_key__ = 'admin'
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_all_admins():
        """Получить всех админов с id, username, created_at"""
        return db.session.query(User.id, User.username, User.created_at).all()
    
    @staticmethod
    def create_admin(username, password):
        """Создать нового админа с хешированным паролем"""
        password_hash = generate_password_hash(password)
        new_admin = User(
            username=username,
            password_hash=password_hash
        )
        db.session.add(new_admin)
        db.session.commit()
        return new_admin
    
    @staticmethod
    def delete_admin(user_id):
        """Удалить админа по ID с проверкой что не удаляем последнего"""
        admin = db.session.get(User, user_id)
        if not admin:
            return False
        
        # Проверяем количество админов
        admin_count = User.get_admin_count()
        if admin_count <= 1:
            raise ValueError("Нельзя удалить последнего админа")
        
        db.session.delete(admin)
        db.session.commit()
        return True
    
    @staticmethod
    def admin_exists(username):
        """Проверить существование админа по имени"""
        return User.query.filter_by(username=username).first() is not None
    
    @staticmethod
    def get_admin_count():
        """Получить количество админов"""
        return db.session.query(func.count(User.id)).scalar()

# Модель Profile для чтения из PostgreSQL (продакшен база)
class Profile(db.Model):
    __bind_key__ = 'profiles'
    __tablename__ = 'profiles'
    
    pid = db.Column(db.Integer, primary_key=True)
    data_create = db.Column(db.DateTime)
    party = db.Column(db.String)
    domaincount = db.Column(db.Integer)
    
    @staticmethod
    def get_total_count():
        """Общее количество профилей"""
        engine = db.get_engine(bind='profiles')
        with engine.connect() as conn:
            result = conn.execute(db.text('SELECT COUNT(pid) FROM profiles')).scalar()
            return result
    
    @staticmethod
    def get_average_age_days():
        """Средний возраст профилей в днях от data_create до сегодня"""
        engine = db.get_engine(bind='profiles')
        with engine.connect() as conn:
            result = conn.execute(db.text('''
                SELECT AVG(EXTRACT(epoch FROM CURRENT_TIMESTAMP - data_create) / 86400)
                FROM profiles
                WHERE data_create IS NOT NULL
            ''')).scalar()
            return result
    
    @staticmethod
    def get_average_domain_count():
        """Среднее количество доменов по всем профилям"""
        engine = db.get_engine(bind='profiles')
        with engine.connect() as conn:
            result = conn.execute(db.text('''
                SELECT AVG(domaincount)
                FROM profiles
                WHERE domaincount IS NOT NULL
            ''')).scalar()
            return result
    
    @staticmethod
    def get_groups_stats():
        """Список групп с количеством профилей, средним возрастом и средними доменами в каждой"""
        engine = db.get_engine(bind='profiles')
        with engine.connect() as conn:
            result = conn.execute(db.text('''
                SELECT 
                    party,
                    COUNT(pid) as count,
                    AVG(EXTRACT(epoch FROM CURRENT_TIMESTAMP - data_create) / 86400) as avg_age_days,
                    AVG(domaincount) as avg_domains
                FROM profiles
                WHERE data_create IS NOT NULL
                GROUP BY party
                ORDER BY count DESC
            ''')).fetchall()
            return result
