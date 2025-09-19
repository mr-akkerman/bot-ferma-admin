from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
