"""
Mock-Database-Layer der SQLite-Datenbank mit SQLAlchemy-Modellen simuliert
Verhält sich wie eine echte SQLite-Datenbank mit SQLAlchemy ORM
"""

from .models import User, Note, db
from datetime import datetime
import copy

class MockSession:
    """Mock SQLAlchemy Session"""
    
    def __init__(self, mock_db):
        self.mock_db = mock_db
        self._new_objects = []
        self._dirty_objects = []
        self._deleted_objects = []
    
    def add(self, obj):
        """Objekt zur Session hinzufügen"""
        self._new_objects.append(obj)
    
    def delete(self, obj):
        """Objekt zum Löschen markieren"""
        self._deleted_objects.append(obj)
    
    def commit(self):
        """Änderungen committen"""
        # Neue Objekte hinzufügen
        for obj in self._new_objects:
            if isinstance(obj, User):
                obj.id = self.mock_db._get_next_user_id()
                obj.created_at = datetime.utcnow()
                self.mock_db.users.append(obj)
            elif isinstance(obj, Note):
                obj.id = self.mock_db._get_next_note_id()
                obj.created_at = datetime.utcnow()
                obj.updated_at = datetime.utcnow()
                self.mock_db.notes.append(obj)
        
        # Gelöschte Objekte entfernen
        for obj in self._deleted_objects:
            if isinstance(obj, User):
                self.mock_db.users = [u for u in self.mock_db.users if u.id != obj.id]
                # Suppression en cascade : supprimer toutes les notes de l'utilisateur
                self.mock_db.notes = [n for n in self.mock_db.notes if n.user_id != obj.id]
            elif isinstance(obj, Note):
                self.mock_db.notes = [n for n in self.mock_db.notes if n.id != obj.id]
        
        # Listen leeren
        self._new_objects.clear()
        self._dirty_objects.clear()
        self._deleted_objects.clear()
    
    def rollback(self):
        """Änderungen rückgängig machen"""
        self._new_objects.clear()
        self._dirty_objects.clear()
        self._deleted_objects.clear()
    
    def query(self, model_class):
        """Query-Objekt erstellen"""
        return MockQuery(self.mock_db, model_class)

class MockQuery:
    """Mock SQLAlchemy Query"""
    
    def __init__(self, mock_db, model_class):
        self.mock_db = mock_db
        self.model_class = model_class
        self._filters = []
    
    def filter(self, condition):
        """Filter hinzufügen (vereinfacht)"""
        new_query = MockQuery(self.mock_db, self.model_class)
        new_query._filters = self._filters + [condition]
        return new_query
    
    def filter_by(self, **kwargs):
        """Filter by Attributen"""
        new_query = MockQuery(self.mock_db, self.model_class)
        new_query._filters = self._filters + [('filter_by', kwargs)]
        return new_query
    
    def first(self):
        """Erstes Ergebnis zurückgeben"""
        results = self._get_results()
        return results[0] if results else None
    
    def all(self):
        """Alle Ergebnisse zurückgeben"""
        return self._get_results()
    
    def count(self):
        """Anzahl der Ergebnisse"""
        return len(self._get_results())
    
    def _get_results(self):
        """Ergebnisse basierend auf Filtern abrufen"""
        if self.model_class == User:
            data = self.mock_db.users
        elif self.model_class == Note:
            data = self.mock_db.notes
        else:
            return []
        
        # Filter anwenden
        for filter_item in self._filters:
            if isinstance(filter_item, tuple) and filter_item[0] == 'filter_by':
                kwargs = filter_item[1]
                data = [item for item in data if all(
                    self._compare_values(getattr(item, key, None), value, key) for key, value in kwargs.items()
                )]
        
        return data
    
    def _compare_values(self, item_value, filter_value, key):
        """Vergleiche Werte, E-Mail case-insensitive"""
        if key == 'email' and isinstance(item_value, str) and isinstance(filter_value, str):
            return item_value.lower() == filter_value.lower()
        return item_value == filter_value

class MockDatabase:
    """Mock-Datenbank die SQLite-Verhalten simuliert"""
    
    def __init__(self):
        self.users = []
        self.notes = []
        self._user_id_counter = 1
        self._note_id_counter = 1
        self._initialize_dummy_data()
    
    def _get_next_user_id(self):
        """Nächste User-ID generieren"""
        current_id = self._user_id_counter
        self._user_id_counter += 1
        return current_id
    
    def _get_next_note_id(self):
        """Nächste Note-ID generieren"""
        current_id = self._note_id_counter
        self._note_id_counter += 1
        return current_id
    
    def create_session(self):
        """Neue Session erstellen"""
        return MockSession(self)
    
    def reset_database(self):
        """Datenbank zurücksetzen für Tests"""
        self.users.clear()
        self.notes.clear()
        self._user_id_counter = 1
        self._note_id_counter = 1
        self._initialize_dummy_data()
    
    def get_user_by_email(self, email):
        """Benutzer nach E-Mail suchen"""
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    def get_user_by_id(self, user_id):
        """Benutzer nach ID suchen"""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def _initialize_dummy_data(self):
        """Dummy-Daten initialisieren"""
        # Admin-Benutzer
        admin = User(name="admin", email="admin@example.com", password="admin123", admin=True)
        admin.id = self._get_next_user_id()
        admin.created_at = datetime.utcnow()
        self.users.append(admin)
        
        # Normaler Benutzer
        user = User(name="john_doe", email="john@example.com", password="password123")
        user.id = self._get_next_user_id()
        user.created_at = datetime.utcnow()
        self.users.append(user)
        
        # Notes de démonstration - utilisation de user_id au lieu de owner_id
        note1 = Note(title="Admin Notiz", content="Das ist eine Admin-Notiz.", user_id=admin.id)
        note1.id = self._get_next_note_id()
        note1.created_at = datetime.utcnow()
        note1.updated_at = datetime.utcnow()
        self.notes.append(note1)
        
        note2 = Note(title="Erste Notiz", content="Das ist meine erste Notiz im System.", user_id=user.id)
        note2.id = self._get_next_note_id()
        note2.created_at = datetime.utcnow()
        note2.updated_at = datetime.utcnow()
        self.notes.append(note2)
        
        note3 = Note(title="Einkaufsliste", content="Milch, Brot, Eier, Käse", user_id=user.id)
        note3.id = self._get_next_note_id()
        note3.created_at = datetime.utcnow()
        note3.updated_at = datetime.utcnow()
        self.notes.append(note3)

# Globale Mock-Database-Instanz
mock_db = MockDatabase()

def init_db(app):
    """Datenbank initialisieren"""
    # SQLAlchemy ist bereits in main.py initialisiert
    # Mock-Database ist bereits initialisiert
    print("Mock-Database initialisiert mit Dummy-Daten")
    return mock_db