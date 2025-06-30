"""
API-Routen für das Flask-Backend
Alle REST-Endpunkte für User- und Note-Management
"""

from flask import Blueprint, request, jsonify, send_from_directory
from .crud import db_service
from .utils import (
    require_auth, require_admin, create_session, get_user_from_session,
    remove_session, remove_user_sessions, validate_email, validate_password,
    validate_name, validate_note_data, success_response, error_response,
    log_api_request, safe_int, clean_string, get_app_config
)

# Blueprint für API-Routen
api = Blueprint('api', __name__)

@api.route('/', methods=['GET'])
def home():
    """Basis-Endpunkt zur Überprüfung der API"""
    config = get_app_config()
    stats = db_service.get_stats()
    
    return jsonify({
        'message': 'Flask Backend API mit SQLAlchemy läuft',
        'database': config['database'],
        'version': config['version'],
        'demo': '/demo.html',
        'stats': stats,
        'endpoints': {
            'POST /register': 'Benutzer registrieren',
            'POST /login': 'Benutzer anmelden',
            'POST /logout': 'Benutzer abmelden',
            'GET /notes': 'Alle Notizen des Benutzers abrufen',
            'POST /notes': 'Neue Notiz erstellen',
            'GET /notes/<id>': 'Spezifische Notiz abrufen',
            'PUT /notes/<id>': 'Notiz bearbeiten',
            'DELETE /notes/<id>': 'Notiz löschen',
            'GET /admin/users': 'Alle Benutzer abrufen (Admin)',
            'DELETE /admin/users/<id>': 'Benutzer löschen (Admin)',
            'GET /stats': 'Statistiken abrufen'
        }
    })

@api.route('/demo.html')
def demo():
    """Demo-Seite servieren"""
    return send_from_directory('.', 'demo.html')

# Authentifizierungs-Endpunkte

@api.route('/register', methods=['POST'])
def register():
    """Benutzer registrieren"""
    log_api_request('/register', 'POST')
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'email', 'password')):
        return error_response('Name, E-Mail und Passwort sind erforderlich')
    
    name = clean_string(data['name'])
    email = clean_string(data['email'])
    password = data['password']
    
    # Validierung
    if not name or not email or not password:
        return error_response('Alle Felder müssen ausgefüllt sein')
    
    if not validate_name(name):
        return error_response('Benutzername muss mindestens 3 Zeichen haben und darf nur Buchstaben, Zahlen und Unterstriche enthalten')
    
    if not validate_email(email):
        return error_response('Ungültiges E-Mail-Format')
    
    if not validate_password(password):
        return error_response('Passwort muss mindestens 6 Zeichen haben')
    
    # Prüfen ob User bereits existiert
    if db_service.user_exists(name=name, email=email):
        if db_service.get_user_by_email(email):
            return error_response('E-Mail bereits registriert', 409)
        if db_service.get_user_by_name(name):
            return error_response('Benutzername bereits vergeben', 409)
    
    try:
        # Neuen User erstellen
        user = db_service.create_user(name=name, email=email, password=password, admin=False)
        
        return success_response(
            'Benutzer erfolgreich registriert',
            {'user': user.to_dict()},
            201
        )
        
    except Exception as e:
        return error_response(f'Fehler beim Registrieren: {str(e)}', 500)

@api.route('/login', methods=['POST'])
def login():
    """Benutzer anmelden"""
    log_api_request('/login', 'POST')
    data = request.get_json()
    
    if not data or not all(k in data for k in ('email', 'password')):
        return error_response('E-Mail und Passwort sind erforderlich')
    
    email = clean_string(data['email'])
    password = data['password']
    
    if not email or not password:
        return error_response('E-Mail und Passwort dürfen nicht leer sein')
    
    # User authentifizieren
    user = db_service.authenticate_user(email, password)
    if not user:
        return error_response('Ungültige Anmeldedaten', 401)
    
    # Session erstellen
    session_token = create_session(user.id)
    
    return success_response(
        'Erfolgreich angemeldet',
        {
            'session_token': session_token,
            'user': user.to_dict()
        }
    )

@api.route('/logout', methods=['POST'])
@require_auth
def logout(user_id):
    """Benutzer abmelden"""
    log_api_request('/logout', 'POST', user_id)
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if remove_session(token):
        return success_response('Erfolgreich abgemeldet')
    else:
        return error_response('Session nicht gefunden', 404)

# Notiz-Endpunkte

@api.route('/notes', methods=['GET'])
@require_auth
def get_notes(user_id):
    """Alle Notizen des Benutzers abrufen"""
    log_api_request('/notes', 'GET', user_id)
    
    notes = db_service.get_notes_by_user(user_id)
    notes_data = [note.to_dict() for note in notes]
    
    return jsonify({
        'notes': notes_data,
        'count': len(notes_data)
    })

@api.route('/notes', methods=['POST'])
@require_auth
def create_note(user_id):
    """Neue Notiz erstellen"""
    log_api_request('/notes', 'POST', user_id)
    data = request.get_json()
    
    if not data:
        return error_response('JSON-Daten erforderlich')
    
    title = clean_string(data.get('title', ''))
    content = clean_string(data.get('content', ''))
    
    # Validierung
    is_valid, error_msg = validate_note_data(title, content)
    if not is_valid:
        return error_response(error_msg)
    
    try:
        note = db_service.create_note(title=title, content=content, owner_id=user_id)
        
        return success_response(
            'Notiz erfolgreich erstellt',
            {'note': note.to_dict()},
            201
        )
        
    except Exception as e:
        return error_response(f'Fehler beim Erstellen der Notiz: {str(e)}', 500)

@api.route('/notes/<int:note_id>', methods=['GET'])
@require_auth
def get_note(user_id, note_id):
    """Spezifische Notiz abrufen"""
    log_api_request(f'/notes/{note_id}', 'GET', user_id)
    
    note = db_service.get_note_by_id(note_id)
    if not note:
        return error_response('Notiz nicht gefunden', 404)
    
    if not db_service.note_belongs_to_user(note_id, user_id):
        return error_response('Zugriff verweigert', 403)
    
    return jsonify({'note': note.to_dict()})

@api.route('/notes/<int:note_id>', methods=['PUT'])
@require_auth
def update_note(user_id, note_id):
    """Notiz bearbeiten"""
    log_api_request(f'/notes/{note_id}', 'PUT', user_id)
    
    if not db_service.note_belongs_to_user(note_id, user_id):
        return error_response('Zugriff verweigert', 403)
    
    data = request.get_json()
    if not data:
        return error_response('JSON-Daten erforderlich')
    
    title = clean_string(data.get('title', ''))
    content = clean_string(data.get('content', ''))
    
    # Validierung
    is_valid, error_msg = validate_note_data(title, content)
    if not is_valid:
        return error_response(error_msg)
    
    try:
        note = db_service.update_note(note_id, title=title, content=content)
        if not note:
            return error_response('Notiz nicht gefunden', 404)
        
        return success_response(
            'Notiz erfolgreich aktualisiert',
            {'note': note.to_dict()}
        )
        
    except Exception as e:
        return error_response(f'Fehler beim Aktualisieren der Notiz: {str(e)}', 500)

@api.route('/notes/<int:note_id>', methods=['DELETE'])
@require_auth
def delete_note(user_id, note_id):
    """Notiz löschen"""
    log_api_request(f'/notes/{note_id}', 'DELETE', user_id)
    
    if not db_service.note_belongs_to_user(note_id, user_id):
        return error_response('Zugriff verweigert', 403)
    
    try:
        if db_service.delete_note(note_id):
            return success_response('Notiz erfolgreich gelöscht')
        else:
            return error_response('Notiz nicht gefunden', 404)
            
    except Exception as e:
        return error_response(f'Fehler beim Löschen der Notiz: {str(e)}', 500)

# Statistik-Endpunkte

@api.route('/stats', methods=['GET'])
@require_auth
def get_stats(user_id):
    """Statistiken abrufen"""
    log_api_request('/stats', 'GET', user_id)
    
    user = db_service.get_user_by_id(user_id)
    if not user:
        return error_response('Benutzer nicht gefunden', 404)
    
    user_notes_count = db_service.get_notes_count_by_user(user_id)
    
    stats = {
        'total_users': db_service.get_user_count(),
        'total_notes': db_service.get_note_count(),
        'your_notes': user_notes_count
    }
    
    # Admin bekommt erweiterte Statistiken
    if user.admin:
        detailed_stats = db_service.get_detailed_stats()
        stats.update(detailed_stats)
    
    return jsonify(stats)

# Admin-Endpunkte

@api.route('/admin/users', methods=['GET'])
@require_auth
@require_admin
def get_all_users(user_id):
    """Alle Benutzer abrufen (Admin)"""
    log_api_request('/admin/users', 'GET', user_id)
    
    users = db_service.get_all_users()
    users_data = [user.to_dict() for user in users]
    
    return jsonify({
        'users': users_data,
        'count': len(users_data)
    })

@api.route('/admin/users/<int:target_user_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_user(user_id, target_user_id):
    """Benutzer löschen (Admin)"""
    log_api_request(f'/admin/users/{target_user_id}', 'DELETE', user_id)
    
    # Prüfen ob User existiert
    target_user = db_service.get_user_by_id(target_user_id)
    if not target_user:
        return error_response('Benutzer nicht gefunden', 404)
    
    # Admin kann sich nicht selbst löschen
    if user_id == target_user_id:
        return error_response('Admin kann sich nicht selbst löschen', 400)
    
    try:
        # Alle Sessions des Users entfernen
        removed_sessions = remove_user_sessions(target_user_id)
        
        # User löschen (mit Cascade Delete für Notes)
        if db_service.delete_user(target_user_id):
            return success_response(
                f'Benutzer {target_user.name} erfolgreich gelöscht',
                {'removed_sessions': removed_sessions}
            )
        else:
            return error_response('Fehler beim Löschen des Benutzers', 500)
            
    except Exception as e:
        return error_response(f'Fehler beim Löschen des Benutzers: {str(e)}', 500)

# Fehlerbehandlung

@api.errorhandler(404)
def not_found(error):
    """404 Fehlerbehandlung"""
    return error_response('Endpunkt nicht gefunden', 404)

@api.errorhandler(405)
def method_not_allowed(error):
    """405 Fehlerbehandlung"""
    return error_response('HTTP-Methode nicht erlaubt', 405)

@api.errorhandler(500)
def internal_error(error):
    """500 Fehlerbehandlung"""
    return error_response('Interner Serverfehler', 500)