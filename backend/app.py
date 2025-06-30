from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import hashlib
import uuid
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*", methods="*")

# In-Memory Datenspeicher (Listen)
users = []
notes = []
sessions = {}  # session_token -> user_id

# Dummy-Daten erstellen
def init_dummy_data():
    global users, notes
    
    # Admin-Benutzer
    admin_user = {
        'id': 1,
        'name': 'admin',
        'email': 'admin@example.com',
        'password': hash_password('admin123'),
        'admin': True
    }
    
    # Normaler Benutzer
    normal_user = {
        'id': 2,
        'name': 'john_doe',
        'email': 'john@example.com',
        'password': hash_password('password123'),
        'admin': False
    }
    
    users.extend([admin_user, normal_user])
    
    # Dummy-Notizen
    dummy_notes = [
        {
            'id': 1,
            'title': 'Erste Notiz',
            'content': 'Das ist meine erste Notiz im System.',
            'owner_id': 2
        },
        {
            'id': 2,
            'title': 'Einkaufsliste',
            'content': 'Milch, Brot, Eier, Käse',
            'owner_id': 2
        },
        {
            'id': 3,
            'title': 'Admin Notiz',
            'content': 'Wichtige Admin-Informationen',
            'owner_id': 1
        }
    ]
    
    notes.extend(dummy_notes)

def hash_password(password):
    """Einfache Passwort-Hash-Funktion"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token():
    """Generiert ein einfaches Session-Token"""
    return str(uuid.uuid4())

def get_user_by_email(email):
    """Findet einen Benutzer anhand der E-Mail"""
    return next((user for user in users if user['email'] == email), None)

def get_user_by_name(name):
    """Findet einen Benutzer anhand des Namens"""
    return next((user for user in users if user['name'] == name), None)

def get_user_by_id(user_id):
    """Findet einen Benutzer anhand der ID"""
    return next((user for user in users if user['id'] == user_id), None)

def get_user_from_session(session_token):
    """Gibt den Benutzer für ein Session-Token zurück"""
    if session_token in sessions:
        user_id = sessions[session_token]
        return get_user_by_id(user_id)
    return None

def get_next_user_id():
    """Gibt die nächste verfügbare Benutzer-ID zurück"""
    return max([user['id'] for user in users], default=0) + 1

def get_next_note_id():
    """Gibt die nächste verfügbare Notiz-ID zurück"""
    return max([note['id'] for note in notes], default=0) + 1

# API Endpunkte

@app.route('/', methods=['GET'])
def home():
    """Basis-Endpunkt zur Überprüfung der API"""
    return jsonify({
        'message': 'Flask Backend API läuft',
        'demo': '/demo.html',
        'endpoints': {
            'POST /register': 'Benutzer registrieren',
            'POST /login': 'Benutzer anmelden',
            'POST /logout': 'Benutzer abmelden',
            'GET /notes': 'Alle Notizen des Benutzers abrufen',
            'POST /notes': 'Neue Notiz erstellen',
            'GET /notes/<id>': 'Spezifische Notiz abrufen',
            'PUT /notes/<id>': 'Notiz bearbeiten',
            'DELETE /notes/<id>': 'Notiz löschen',
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
    
    # Prüfen ob Benutzer bereits existiert
    if get_user_by_email(email):
        return jsonify({'error': 'E-Mail bereits registriert'}), 409
    
    if get_user_by_name(name):
        return jsonify({'error': 'Benutzername bereits vergeben'}), 409
    
    # Neuen Benutzer erstellen
    new_user = {
        'id': get_next_user_id(),
        'name': name,
        'email': email,
        'password': hash_password(password),
        'admin': False  # Neue Benutzer sind standardmäßig keine Admins
    }
    
    users.append(new_user)
    
    return jsonify({
        'message': 'Benutzer erfolgreich registriert',
        'user': {
            'id': new_user['id'],
            'name': new_user['name'],
            'email': new_user['email'],
            'admin': new_user['admin']
        }
    }), 201

@app.route('/login', methods=['POST'])
def login():
    """Benutzer anmelden"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'E-Mail und Passwort sind erforderlich'}), 400
    
    email = data['email'].strip()
    password = data['password']
    
    user = get_user_by_email(email)
    
    if not user or user['password'] != hash_password(password):
        return jsonify({'error': 'Ungültige Anmeldedaten'}), 401
    
    # Session-Token generieren
    session_token = generate_session_token()
    sessions[session_token] = user['id']
    
    return jsonify({
        'message': 'Erfolgreich angemeldet',
        'session_token': session_token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'admin': user['admin']
        }
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
    
    user_notes = [note for note in notes if note['owner_id'] == user['id']]
    
    return jsonify({
        'notes': user_notes,
        'count': len(user_notes)
    })

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
    
    new_note = {
        'id': get_next_note_id(),
        'title': title,
        'content': content,
        'owner_id': user['id']
    }
    
    notes.append(new_note)
    
    return jsonify({
        'message': 'Notiz erfolgreich erstellt',
        'note': new_note
    }), 201

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Spezifische Notiz abrufen"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    note = next((note for note in notes if note['id'] == note_id), None)
    
    if not note:
        return jsonify({'error': 'Notiz nicht gefunden'}), 404
    
    if note['owner_id'] != user['id']:
        return jsonify({'error': 'Zugriff verweigert'}), 403
    
    return jsonify({'note': note})

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Notiz bearbeiten"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    note = next((note for note in notes if note['id'] == note_id), None)
    
    if not note:
        return jsonify({'error': 'Notiz nicht gefunden'}), 404
    
    if note['owner_id'] != user['id']:
        return jsonify({'error': 'Zugriff verweigert'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Keine Daten empfangen'}), 400
    
    # Titel und/oder Inhalt aktualisieren
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': 'Titel darf nicht leer sein'}), 400
        note['title'] = title
    
    if 'content' in data:
        content = data['content'].strip()
        if not content:
            return jsonify({'error': 'Inhalt darf nicht leer sein'}), 400
        note['content'] = content
    
    return jsonify({
        'message': 'Notiz erfolgreich aktualisiert',
        'note': note
    })

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Notiz löschen"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    note = next((note for note in notes if note['id'] == note_id), None)
    
    if not note:
        return jsonify({'error': 'Notiz nicht gefunden'}), 404
    
    if note['owner_id'] != user['id']:
        return jsonify({'error': 'Zugriff verweigert'}), 403
    
    notes.remove(note)
    
    return jsonify({'message': 'Notiz erfolgreich gelöscht'})

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Benutzer löschen (nur für Admins)"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    if not user['admin']:
        return jsonify({'error': 'Admin-Berechtigung erforderlich'}), 403
    
    target_user = get_user_by_id(user_id)
    
    if not target_user:
        return jsonify({'error': 'Benutzer nicht gefunden'}), 404
    
    if target_user['id'] == user['id']:
        return jsonify({'error': 'Sie können sich nicht selbst löschen'}), 400
    
    # Benutzer und alle seine Notizen löschen
    global notes
    notes = [note for note in notes if note['owner_id'] != user_id]
    users.remove(target_user)
    
    # Alle Sessions des gelöschten Benutzers entfernen
    sessions_to_remove = [token for token, uid in sessions.items() if uid == user_id]
    for token in sessions_to_remove:
        del sessions[token]
    
    return jsonify({'message': f'Benutzer {target_user["name"]} erfolgreich gelöscht'})

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    """Alle Benutzer abrufen (nur für Admins)"""
    session_token = request.headers.get('Authorization')
    user = get_user_from_session(session_token)
    
    if not user:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    if not user['admin']:
        return jsonify({'error': 'Admin-Berechtigung erforderlich'}), 403
    
    user_list = [{
        'id': u['id'],
        'name': u['name'],
        'email': u['email'],
        'admin': u['admin']
    } for u in users]
    
    return jsonify({
        'users': user_list,
        'count': len(user_list)
    })

if __name__ == '__main__':
    init_dummy_data()
    print("Flask Backend gestartet...")
    print("Dummy-Benutzer:")
    print("- Admin: admin@example.com / admin123")
    print("- Benutzer: john@example.com / password123")
    app.run(host='0.0.0.0', port=12000, debug=True)