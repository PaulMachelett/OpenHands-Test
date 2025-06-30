"""
Database Service Layer - Abstrahiert Datenbankoperationen
Verwendet SQLAlchemy-Modelle und Mock-Database
"""

from models import User, Note
from mock_database import mock_db
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
        return session.query(User).get(user_id)
    
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
            user = session.query(User).get(user_id)
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
    
    # Note-Operationen
    
    def create_note(self, title, content, owner_id):
        """Neue Note erstellen"""
        session = self.db.create_session()
        try:
            note = Note(title=title, content=content, owner_id=owner_id)
            session.add(note)
            session.commit()
            return note
        except Exception as e:
            session.rollback()
            raise e
    
    def get_note_by_id(self, note_id):
        """Note by ID finden"""
        session = self.db.create_session()
        return session.query(Note).get(note_id)
    
    def get_notes_by_owner(self, owner_id):
        """Alle Notes eines Users abrufen"""
        session = self.db.create_session()
        return session.query(Note).filter_by(owner_id=owner_id).all()
    
    def get_all_notes(self):
        """Alle Notes abrufen"""
        session = self.db.create_session()
        return session.query(Note).all()
    
    def update_note(self, note_id, title=None, content=None):
        """Note aktualisieren"""
        session = self.db.create_session()
        try:
            note = session.query(Note).get(note_id)
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
            note = session.query(Note).get(note_id)
            if note:
                session.delete(note)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
    
    def note_belongs_to_user(self, note_id, user_id):
        """Prüfen ob Note einem User gehört"""
        note = self.get_note_by_id(note_id)
        return note and note.owner_id == user_id
    
    # Utility-Methoden
    
    def get_user_count(self):
        """Anzahl der User"""
        return len(self.get_all_users())
    
    def get_note_count(self):
        """Anzahl der Notes"""
        return len(self.get_all_notes())
    
    def get_notes_count_by_user(self, user_id):
        """Anzahl der Notes eines Users"""
        return len(self.get_notes_by_owner(user_id))

# Globale Database-Service-Instanz
db_service = DatabaseService()