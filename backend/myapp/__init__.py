"""
MyApp - Modulares Flask Backend mit SQLAlchemy
===============================================

Ein strukturiertes Flask-Backend mit SQLAlchemy-Integration und Mock-Database-Layer.

Architektur:
- models.py: SQLAlchemy ORM-Modelle
- db.py: Datenbankverbindung und Mock-Layer
- crud.py: CRUD-Operationen und Business Logic
- routes.py: API-Endpunkte und Request-Handling
- utils.py: Hilfsfunktionen und Utilities
"""

from flask import Flask
from flask_cors import CORS
from .routes import api
from .db import MockDatabase

__version__ = "1.0.0"
__author__ = "OpenHands"


def create_app(config=None):
    """
    Application Factory Pattern für Flask-App
    
    Args:
        config: Optionale Konfiguration für die App
        
    Returns:
        Flask: Konfigurierte Flask-Anwendung
    """
    app = Flask(__name__)
    
    # Standard-Konfiguration
    app.config.update({
        'SECRET_KEY': 'dev-secret-key-change-in-production',
        'TESTING': False,
        'DEBUG': True
    })
    
    # Überschreibe mit benutzerdefinierter Konfiguration
    if config:
        app.config.update(config)
    
    # CORS aktivieren
    CORS(app)
    
    # Mock-Database initialisieren
    mock_db = MockDatabase()
    app.mock_db = mock_db
    
    # Blueprints registrieren
    app.register_blueprint(api)
    
    return app