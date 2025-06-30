"""
Flask Backend mit SQLAlchemy-Integration und Mock-Database
Vollständige Implementierung mit echten SQLAlchemy-Modellen
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

# Import der eigenen Module
from models import db, User, Note
from database_service import db_service

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*", methods="*")

# SQLAlchemy Konfiguration (wird durch Mock-Layer ersetzt)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

# SQLAlchemy initialisieren (für Modell-Definitionen)
db.init_app(app)

# Session-Management
sessions = {}  # session_token -> user_id

def generate_session_token():
    """Generiert ein Session-Token"""
    return str(uuid.uuid4())

def get_user_from_session(session_token):
    """Gibt den User für ein Session-Token zurück"""
    if session_token in sessions:
        user_id = sessions[session_token]
        return db_service.get_user_by_id(user_id)
    return None

# API Endpunkte

@app.route('/', methods=['GET'])
def home():
    """Basis-Endpunkt zur Überprüfung der API"""
    return jsonify({
        'message': 'Flask Backend API mit SQLAlchemy läuft',
        'database': 'SQLAlchemy mit Mock-Layer',
        'demo': '/demo.html',
        'stats': {
            'users': db_service.get_user_count(),
            'notes': db_service.get_note_count()
        },
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
            'DELETE /admin/users/<id>': 'Benutzer löschen (Admin)'
        }
    })

@app.route('/demo.html')
def demo():
    """Demo-Seite servieren"""
    return send_from_directory('.', 'demo.html')

@app.route('/register', methods=['POST'])
def register():
    """Benutzer registrieren"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'email', 'password')):
        return jsonify({'error': 'Name, E-Mail und Passwort sind erforderlich'}), 400
    
    name = data['name'].strip()
    email = data['email'].strip()
    password = data['password']
    
    if not name or not email or not password:
        return jsonify({'error': 'Alle Felder müssen ausgefüllt sein'}), 400
    
    # Prüfen ob User bereits existiert
    if db_service.get_user_by_email(email):
        return jsonify({'error': 'E-Mail bereits registriert'}), 409
    
    if db_service.get_user_by_name(name):
        return jsonify({'error': 'Benutzername bereits vergeben'}), 409
    
    try:
        # Neuen User erstellen
        user = db_service.create_user(name=name, email=email, password=password, admin=False)
        
        return jsonify({
            'message': 'Benutzer erfolgreich registriert',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Erstellen des Benutzers: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    """Benutzer anmelden"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'E-Mail und Passwort sind erforderlich'}), 400
    
    email = data['email'].strip()
    password = data['password']
    
    # User authentifizieren
    user = db_service.authenticate_user(email, password)
    
    if not user:
        return jsonify({'error': 'Ungültige Anmeldedaten'}), 401
    
    # Session-Token generieren
    session_token = generate_session_token()
    sessions[session_token] = user.id
    
    return jsonify({
        'message': 'Erfolgreich angemeldet',
        'session_token': session_token,
        'user': user.to_dict()
    })

@app.route('/logout', methods=['POST'])
def logout():
    """Benutzer abmelden"""
    session_token = request.headers.get('Authorization')
    
    if session_token and session_token in sessions:
        del sessions[session_token]
        return jsonify({'message': 'Erfolgreich abgemeldet'})
    
    return jsonify({'error': 'Ungültiges Session-Token'}), 401

@app.route('/notes', methods=['GET'])
def get_notes():
    """Alle Notizen des angemeldeten Benutzers abrufen"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    try:
        notes = db_service.get_notes_by_owner(user.id)
        notes_data = [note.to_dict() for note in notes]
        
        return jsonify({
            'notes': notes_data,
            'count': len(notes_data)
        })
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen der Notizen: {str(e)}'}), 500

@app.route('/notes', methods=['POST'])
def create_note():
    """Neue Notiz erstellen"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ('title', 'content')):
        return jsonify({'error': 'Titel und Inhalt sind erforderlich'}), 400
    
    title = data['title'].strip()
    content = data['content'].strip()
    
    if not title or not content:
        return jsonify({'error': 'Titel und Inhalt dürfen nicht leer sein'}), 400
    
    try:
        note = db_service.create_note(title=title, content=content, owner_id=user.id)
        
        return jsonify({
            'message': 'Notiz erfolgreich erstellt',
            'note': note.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Erstellen der Notiz: {str(e)}'}), 500

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Spezifische Notiz abrufen"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    try:
        note = db_service.get_note_by_id(note_id)
        
        if not note:
            return jsonify({'error': 'Notiz nicht gefunden'}), 404
        
        if not db_service.note_belongs_to_user(note_id, user.id):
            return jsonify({'error': 'Zugriff verweigert'}), 403
        
        return jsonify({'note': note.to_dict()})
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen der Notiz: {str(e)}'}), 500

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Notiz bearbeiten"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    if not db_service.note_belongs_to_user(note_id, user.id):
        note = db_service.get_note_by_id(note_id)
        if not note:
            return jsonify({'error': 'Notiz nicht gefunden'}), 404
        return jsonify({'error': 'Zugriff verweigert'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Keine Daten empfangen'}), 400
    
    title = data.get('title', '').strip() if 'title' in data else None
    content = data.get('content', '').strip() if 'content' in data else None
    
    if title is not None and not title:
        return jsonify({'error': 'Titel darf nicht leer sein'}), 400
    
    if content is not None and not content:
        return jsonify({'error': 'Inhalt darf nicht leer sein'}), 400
    
    try:
        updated_note = db_service.update_note(note_id, title=title, content=content)
        
        if not updated_note:
            return jsonify({'error': 'Notiz nicht gefunden'}), 404
        
        return jsonify({
            'message': 'Notiz erfolgreich aktualisiert',
            'note': updated_note.to_dict()
        })
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Aktualisieren der Notiz: {str(e)}'}), 500

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Notiz löschen"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    if not db_service.note_belongs_to_user(note_id, user.id):
        note = db_service.get_note_by_id(note_id)
        if not note:
            return jsonify({'error': 'Notiz nicht gefunden'}), 404
        return jsonify({'error': 'Zugriff verweigert'}), 403
    
    try:
        success = db_service.delete_note(note_id)
        
        if not success:
            return jsonify({'error': 'Notiz nicht gefunden'}), 404
        
        return jsonify({'message': 'Notiz erfolgreich gelöscht'})
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Löschen der Notiz: {str(e)}'}), 500

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    """Alle Benutzer abrufen (nur für Admins)"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    if not user.admin:
        return jsonify({'error': 'Admin-Berechtigung erforderlich'}), 403
    
    try:
        users = db_service.get_all_users()
        users_data = [user.to_dict() for user in users]
        
        return jsonify({
            'users': users_data,
            'count': len(users_data)
        })
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen der Benutzer: {str(e)}'}), 500

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Benutzer löschen (nur für Admins)"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    if not user.admin:
        return jsonify({'error': 'Admin-Berechtigung erforderlich'}), 403
    
    target_user = db_service.get_user_by_id(user_id)
    
    if not target_user:
        return jsonify({'error': 'Benutzer nicht gefunden'}), 404
    
    if target_user.id == user.id:
        return jsonify({'error': 'Sie können sich nicht selbst löschen'}), 400
    
    try:
        # Alle Sessions des gelöschten Benutzers entfernen
        sessions_to_remove = [token for token, uid in sessions.items() if uid == user_id]
        for token in sessions_to_remove:
            del sessions[token]
        
        # User löschen (Cascade Delete für Notes wird automatisch durchgeführt)
        success = db_service.delete_user(user_id)
        
        if not success:
            return jsonify({'error': 'Benutzer konnte nicht gelöscht werden'}), 500
        
        return jsonify({'message': f'Benutzer {target_user.name} erfolgreich gelöscht'})
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Löschen des Benutzers: {str(e)}'}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Statistiken abrufen"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    try:
        stats = {
            'total_users': db_service.get_user_count(),
            'total_notes': db_service.get_note_count(),
            'your_notes': db_service.get_notes_count_by_user(user.id)
        }
        
        if user.admin:
            users = db_service.get_all_users()
            stats['users_detail'] = [
                {
                    'user': u.to_dict(),
                    'notes_count': db_service.get_notes_count_by_user(u.id)
                }
                for u in users
            ]
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen der Statistiken: {str(e)}'}), 500

if __name__ == '__main__':
    print("Flask Backend mit SQLAlchemy gestartet...")
    print("Database: SQLAlchemy mit Mock-Layer")
    print("Dummy-Benutzer:")
    print("- Admin: admin@example.com / admin123")
    print("- Benutzer: john@example.com / password123")
    app.run(host='0.0.0.0', port=12001, debug=True)