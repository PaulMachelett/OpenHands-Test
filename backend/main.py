"""
Haupteinstiegspunkt für das Flask-Backend
Modulare Struktur mit SQLAlchemy und Mock-Database
"""

from flask import Flask
from flask_cors import CORS

# Import der eigenen Module
from myapp.models import db
from myapp.db import init_db
from myapp.routes import api

def create_app():
    """Flask-App erstellen und konfigurieren"""
    app = Flask(__name__)
    
    # CORS konfigurieren
    CORS(app, origins="*", allow_headers="*", methods="*")
    
    # App-Konfiguration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    # SQLAlchemy initialisieren (für Modell-Definitionen)
    db.init_app(app)
    
    # Mock-Database initialisieren
    with app.app_context():
        mock_db = init_db(app)
    
    # Blueprint registrieren
    app.register_blueprint(api)
    
    return app, mock_db

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    print("Flask Backend mit SQLAlchemy gestartet...")
    print("Database: SQLAlchemy mit Mock-Layer")
    print("Dummy-Benutzer:")
    print("- Admin: admin@example.com / admin123")
    print("- Benutzer: john@example.com / password123")
    
    app, mock_db = create_app()
    
    # Server starten
    app.run(host='0.0.0.0', port=12001, debug=True)

if __name__ == '__main__':
    main()