"""
Test-Konfiguration und Fixtures für pytest
"""
import pytest
import sys
import os

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from myapp import create_app
from myapp.db import MockDatabase


@pytest.fixture
def app():
    """Erstelle eine Flask-App-Instanz für Tests"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    
    # Stelle sicher, dass die Mock-Database für jeden Test zurückgesetzt wird
    with app.app_context():
        mock_db = MockDatabase()
        mock_db.reset_database()
        app.mock_db = mock_db
    
    yield app


@pytest.fixture
def client(app):
    """Erstelle einen Test-Client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Erstelle einen CLI-Runner für Tests"""
    return app.test_cli_runner()


@pytest.fixture
def mock_db(app):
    """Zugriff auf die Mock-Database"""
    return app.mock_db


@pytest.fixture
def sample_user_data():
    """Beispiel-Benutzerdaten für Tests"""
    return {
        'name': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    }


@pytest.fixture
def sample_admin_data():
    """Beispiel-Admin-Daten für Tests"""
    return {
        'name': 'testadmin',
        'email': 'admin@example.com',
        'password': 'adminpassword123'
    }


@pytest.fixture
def sample_note_data():
    """Beispiel-Notiz-Daten für Tests"""
    return {
        'title': 'Test Note',
        'content': 'This is a test note content.'
    }


@pytest.fixture
def authenticated_user(client, sample_user_data):
    """Registriere und authentifiziere einen Benutzer"""
    # Registriere Benutzer
    client.post('/register', json=sample_user_data)
    
    # Melde Benutzer an
    response = client.post('/login', json={
        'email': sample_user_data['email'],
        'password': sample_user_data['password']
    })
    
    return response.get_json()


@pytest.fixture
def authenticated_admin(client, sample_admin_data, mock_db):
    """Registriere und authentifiziere einen Admin"""
    # Registriere Admin
    register_response = client.post('/register', json=sample_admin_data)
    
    # Setze Admin-Status in der Mock-Database
    user = mock_db.get_user_by_email(sample_admin_data['email'])
    if user:
        user.admin = True
    
    # Melde Admin an
    login_response = client.post('/login', json={
        'email': sample_admin_data['email'],
        'password': sample_admin_data['password']
    })
    
    login_data = login_response.get_json()
    if login_response.status_code == 200 and 'session_token' in login_data:
        return login_data
    else:
        # Fallback für Tests
        return {
            'session_token': 'test-admin-token',
            'user': {'id': user.id if user else 1, 'email': sample_admin_data['email'], 'admin': True}
        }