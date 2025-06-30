"""
Hilfsfunktionen und Utilities für das Flask-Backend
"""

import uuid
import re
from functools import wraps
from flask import request, jsonify

# Session-Management
active_sessions = {}

def generate_session_token():
    """Generiert ein eindeutiges Session-Token"""
    return str(uuid.uuid4())

def create_session(user_id):
    """Erstellt eine neue Session für einen User"""
    token = generate_session_token()
    active_sessions[token] = user_id
    return token

def get_user_from_session(token):
    """Gibt User-ID aus Session-Token zurück"""
    return active_sessions.get(token)

def remove_session(token):
    """Entfernt eine Session"""
    if token in active_sessions:
        del active_sessions[token]
        return True
    return False

def remove_user_sessions(user_id):
    """Entfernt alle Sessions eines Users"""
    tokens_to_remove = [token for token, uid in active_sessions.items() if uid == user_id]
    for token in tokens_to_remove:
        del active_sessions[token]
    return len(tokens_to_remove)

# Validierungsfunktionen

def validate_email(email):
    """Validiert E-Mail-Format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validiert Passwort (mindestens 6 Zeichen)"""
    return len(password) >= 6

def validate_name(name):
    """Validiert Benutzername (mindestens 3 Zeichen, nur Buchstaben, Zahlen, Unterstriche)"""
    if len(name) < 3:
        return False
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, name) is not None

def validate_note_data(title, content):
    """Validiert Notiz-Daten"""
    if not title or not title.strip():
        return False, "Titel darf nicht leer sein"
    if not content or not content.strip():
        return False, "Inhalt darf nicht leer sein"
    if len(title) > 200:
        return False, "Titel darf maximal 200 Zeichen haben"
    return True, None

# Authentifizierungs-Decorator

def require_auth(f):
    """Decorator für Authentifizierung erforderlich"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Nicht autorisiert'}), 401
        
        # Bearer Token Format unterstützen
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = get_user_from_session(token)
        if not user_id:
            return jsonify({'error': 'Ungültiges Session-Token'}), 401
        
        # User-ID an die Funktion weitergeben
        return f(user_id, *args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator für Admin-Berechtigung erforderlich"""
    @wraps(f)
    def decorated_function(user_id, *args, **kwargs):
        from .crud import db_service
        user = db_service.get_user_by_id(user_id)
        if not user or not user.admin:
            return jsonify({'error': 'Admin-Berechtigung erforderlich'}), 403
        
        return f(user_id, *args, **kwargs)
    
    return decorated_function

# Response-Hilfsfunktionen

def success_response(message, data=None, status_code=200):
    """Standardisierte Erfolgs-Antwort"""
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code

def error_response(message, status_code=400):
    """Standardisierte Fehler-Antwort"""
    return jsonify({'error': message}), status_code

def paginate_results(items, page=1, per_page=10):
    """Paginierung für Ergebnislisten"""
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': items[start:end],
        'total': len(items),
        'page': page,
        'per_page': per_page,
        'pages': (len(items) + per_page - 1) // per_page
    }

# Logging-Hilfsfunktionen

def log_api_request(endpoint, method, user_id=None):
    """Loggt API-Anfragen (vereinfacht)"""
    print(f"API Request: {method} {endpoint} - User: {user_id}")

def log_error(error, context=""):
    """Loggt Fehler (vereinfacht)"""
    print(f"ERROR {context}: {str(error)}")

# Datenkonvertierung

def safe_int(value, default=None):
    """Sichere Integer-Konvertierung"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def clean_string(value):
    """Bereinigt String-Eingaben"""
    if not value:
        return ""
    return str(value).strip()

# Konfigurationshilfen

def get_app_config():
    """Gibt App-Konfiguration zurück"""
    return {
        'database': 'SQLAlchemy mit Mock-Layer',
        'version': '1.0.0',
        'features': [
            'User Management',
            'Note Management', 
            'Session Authentication',
            'Admin Functions',
            'Statistics'
        ]
    }