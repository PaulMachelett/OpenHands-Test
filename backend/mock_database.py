"""
Mock-Database-Layer der SQLite-Datenbank mit SQLAlchemy-Modellen simuliert
Verhält sich wie eine echte SQLite-Datenbank mit SQLAlchemy ORM
"""

from models import User, Note
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
                # Cascade delete: Alle Notizen des Users löschen
                self.mock_db.notes = [n for n in self.mock_db.notes if n.owner_id != obj.id]
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
    
    def query(self, model):
        """Query-Objekt erstellen"""
        return MockQuery(self.mock_db, model)

class MockQuery:
    """Mock SQLAlchemy Query"""
    
    def __init__(self, mock_db, model):
        self.mock_db = mock_db
        self.model = model
        self._filters = []
    
    def filter(self, condition):
        """Filter hinzufügen"""
        new_query = MockQuery(self.mock_db, self.model)
        new_query._filters = self._filters + [condition]
        return new_query
    
    def filter_by(self, **kwargs):
        """Filter by Attributen"""
        new_query = MockQuery(self.mock_db, self.model)
        new_query._filters = self._filters + [('filter_by', kwargs)]
        return new_query
    
    def first(self):
        """Erstes Ergebnis zurückgeben"""
        results = self._execute_query()
        return results[0] if results else None
    
    def all(self):
        """Alle Ergebnisse zurückgeben"""
        return self._execute_query()
    
    def get(self, id):
        """Objekt by ID"""
        if self.model == User:
            return next((u for u in self.mock_db.users if u.id == id), None)
        elif self.model == Note:
            return next((n for n in self.mock_db.notes if n.id == id), None)
        return None
    
    def _execute_query(self):
        """Query ausführen"""
        if self.model == User:
            results = copy.deepcopy(self.mock_db.users)
        elif self.model == Note:
            results = copy.deepcopy(self.mock_db.notes)
        else:
            results = []
        
        # Filter anwenden
        for filter_condition in self._filters:
            if isinstance(filter_condition, tuple) and filter_condition[0] == 'filter_by':
                kwargs = filter_condition[1]
                results = [obj for obj in results if all(
                    getattr(obj, key, None) == value for key, value in kwargs.items()
                )]
        
        return results

class MockDatabase:
    """Mock-Datenbank die SQLite mit SQLAlchemy simuliert"""
    
    def __init__(self):
        self.users = []
        self.notes = []
        self._user_id_counter = 1
        self._note_id_counter = 1
        self._init_dummy_data()
    
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
    
    def _init_dummy_data(self):
        """Dummy-Daten initialisieren"""
        # Admin-User erstellen
        admin_user = User(
            name='admin',
            email='admin@example.com',
            password='admin123',
            admin=True
        )
        admin_user.id = self._get_next_user_id()
        admin_user.created_at = datetime.utcnow()
        self.users.append(admin_user)
        
        # Normaler User erstellen
        normal_user = User(
            name='john_doe',
            email='john@example.com',
            password='password123',
            admin=False
        )
        normal_user.id = self._get_next_user_id()
        normal_user.created_at = datetime.utcnow()
        self.users.append(normal_user)
        
        # Dummy-Notizen erstellen
        note1 = Note(
            title='Erste Notiz',
            content='Das ist meine erste Notiz im System.',
            owner_id=normal_user.id
        )
        note1.id = self._get_next_note_id()
        note1.created_at = datetime.utcnow()
        note1.updated_at = datetime.utcnow()
        self.notes.append(note1)
        
        note2 = Note(
            title='Einkaufsliste',
            content='Milch, Brot, Eier, Käse',
            owner_id=normal_user.id
        )
        note2.id = self._get_next_note_id()
        note2.created_at = datetime.utcnow()
        note2.updated_at = datetime.utcnow()
        self.notes.append(note2)
        
        note3 = Note(
            title='Admin Notiz',
            content='Wichtige Admin-Informationen',
            owner_id=admin_user.id
        )
        note3.id = self._get_next_note_id()
        note3.created_at = datetime.utcnow()
        note3.updated_at = datetime.utcnow()
        self.notes.append(note3)
    
    def create_session(self):
        """Neue Session erstellen"""
        return MockSession(self)

# Globale Mock-Database-Instanz
mock_db = MockDatabase()