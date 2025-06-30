"""
Database Service Layer - Abstrahiert Datenbankoperationen
Verwendet SQLAlchemy-Modelle und Mock-Database
"""

from .models import User, Note
from .db import mock_db
from datetime import datetime

class DatabaseService:
    """Service-Klasse für alle Datenbankoperationen"""
    
    def __init__(self):
        self.db = mock_db
    
    # User-Operationen
    
    def create_user(self, name, email, password, admin=False):
        """Neuen User erstellen"""
        session = self.db.create_session()
        try:
            user = User(name=name, email=email, password=password, admin=admin)
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
    
    def get_user_by_id(self, user_id):
        """User by ID finden"""
        session = self.db.create_session()
        return session.query(User).filter_by(id=user_id).first()
    
    def get_user_by_email(self, email):
        """User by Email finden"""
        session = self.db.create_session()
        return session.query(User).filter_by(email=email).first()
    
    def get_user_by_name(self, name):
        """User by Name finden"""
        session = self.db.create_session()
        return session.query(User).filter_by(name=name).first()
    
    def get_all_users(self):
        """Alle User abrufen"""
        session = self.db.create_session()
        return session.query(User).all()
    
    def delete_user(self, user_id):
        """User löschen (mit Cascade Delete für Notes)"""
        session = self.db.create_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
    
    def authenticate_user(self, email, password):
        """User authentifizieren"""
        user = self.get_user_by_email(email)
        if user and user.check_password(password):
            return user
        return None
    
    def user_exists(self, name=None, email=None):
        """Prüfen ob User bereits existiert"""
        if name and self.get_user_by_name(name):
            return True
        if email and self.get_user_by_email(email):
            return True
        return False
    
    def get_user_count(self):
        """Anzahl aller User"""
        return len(self.db.users)
    
    # Note-Operationen
    
    def create_note(self, title, content, user_id):
        """Créer une nouvelle note - paramètre changé de owner_id à user_id"""
        session = self.db.create_session()
        try:
            note = Note(title=title, content=content, user_id=user_id)
            session.add(note)
            session.commit()
            return note
        except Exception as e:
            session.rollback()
            raise e
    
    def get_note_by_id(self, note_id):
        """Note by ID finden"""
        session = self.db.create_session()
        return session.query(Note).filter_by(id=note_id).first()
    
    def get_notes_by_user(self, user_id):
        """Récupérer toutes les notes d'un utilisateur - utilise user_id"""
        session = self.db.create_session()
        return session.query(Note).filter_by(user_id=user_id).all()
    
    def get_all_notes(self):
        """Alle Notes abrufen"""
        session = self.db.create_session()
        return session.query(Note).all()
    
    def update_note(self, note_id, title=None, content=None):
        """Note aktualisieren"""
        session = self.db.create_session()
        try:
            note = session.query(Note).filter_by(id=note_id).first()
            if note:
                if title is not None:
                    note.title = title
                if content is not None:
                    note.content = content
                note.updated_at = datetime.utcnow()
                session.commit()
                return note
            return None
        except Exception as e:
            session.rollback()
            raise e
    
    def delete_note(self, note_id):
        """Note löschen"""
        session = self.db.create_session()
        try:
            note = session.query(Note).filter_by(id=note_id).first()
            if note:
                session.delete(note)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
    
    def note_belongs_to_user(self, note_id, user_id):
        """Vérifier si la note appartient à l'utilisateur - utilise user_id"""
        note = self.get_note_by_id(note_id)
        return note and note.user_id == user_id
    
    def get_note_count(self):
        """Anzahl aller Notes"""
        return len(self.db.notes)
    
    def get_notes_count_by_user(self, user_id):
        """Compter les notes d'un utilisateur - utilise user_id"""
        return len([note for note in self.db.notes if note.user_id == user_id])
    
    # Statistik-Operationen
    
    def get_stats(self):
        """Basis-Statistiken abrufen"""
        return {
            'total_users': self.get_user_count(),
            'total_notes': self.get_note_count()
        }
    
    def get_detailed_stats(self):
        """Detaillierte Statistiken mit User-Details"""
        users = self.get_all_users()
        users_detail = []
        
        for user in users:
            notes_count = self.get_notes_count_by_user(user.id)
            users_detail.append({
                'user': user.to_dict(),
                'notes_count': notes_count
            })
        
        return {
            'total_users': len(users),
            'total_notes': self.get_note_count(),
            'users_detail': users_detail
        }

# Globale Service-Instanz
db_service = DatabaseService()