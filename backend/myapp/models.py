"""
SQLAlchemy Datenbankmodelle für User und Note
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib

db = SQLAlchemy()

class User(db.Model):
    """User-Modell für die Datenbank"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation vers les Notes - mise à jour pour utiliser user_id
    notes = relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name, email, password, admin=False):
        self.name = name
        self.email = email
        self.password_hash = self._hash_password(password)
        self.admin = admin
    
    def _hash_password(self, password):
        """Passwort hashen"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Passwort überprüfen"""
        return self.password_hash == self._hash_password(password)
    
    def to_dict(self, include_password=False):
        """User-Objekt zu Dictionary konvertieren"""
        result = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'admin': self.admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_password:
            result['password_hash'] = self.password_hash
        return result
    
    def __repr__(self):
        return f'<User {self.name}>'

class Note(db.Model):
    """Modèle Note pour la base de données"""
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Changé de owner_id à user_id
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, content, user_id):  # Paramètre changé de owner_id à user_id
        self.title = title
        self.content = content
        self.user_id = user_id  # Assignation changée de owner_id à user_id
    
    def to_dict(self):
        """Convertir l'objet Note en dictionnaire"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,  # Changé de owner_id à user_id
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Note {self.title}>'