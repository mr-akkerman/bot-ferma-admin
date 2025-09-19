from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

# Инициализация SQLAlchemy
db = SQLAlchemy()

# Модель User для SQLite БД админов
class User(db.Model):
    __bind_key__ = 'sqlite'
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Модель Profile для чтения из PostgreSQL
class Profile(db.Model):
    __bind_key__ = 'postgres'
    __tablename__ = 'profiles'
    
    pid = db.Column(db.Integer, primary_key=True)
    data_create = db.Column(db.DateTime)
    party = db.Column(db.String)
    domaincount = db.Column(db.Integer)
    
    @staticmethod
    def get_total_count():
        """Общее количество профилей"""
        return db.session.query(func.count(Profile.pid)).scalar()
    
    @staticmethod
    def get_average_age_days():
        """Средний возраст профилей в днях от data_create до сегодня"""
        return db.session.query(
            func.avg(func.extract('epoch', func.now() - Profile.data_create) / 86400)
        ).scalar()
    
    @staticmethod
    def get_average_domain_count():
        """Среднее количество доменов по всем профилям"""
        return db.session.query(func.avg(Profile.domaincount)).scalar()
    
    @staticmethod
    def get_groups_stats():
        """Список групп с количеством профилей, средним возрастом и средними доменами в каждой"""
        return db.session.query(
            Profile.party,
            func.count(Profile.pid).label('count'),
            func.avg(func.extract('epoch', func.now() - Profile.data_create) / 86400).label('avg_age_days'),
            func.avg(Profile.domaincount).label('avg_domains')
        ).group_by(Profile.party).all()
