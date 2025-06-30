"""
Haupteinstiegspunkt für das Flask-Backend
Modulare Struktur mit SQLAlchemy und Mock-Database
"""

from myapp import create_app

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    print("Flask Backend mit SQLAlchemy gestartet...")
    print("Database: SQLAlchemy mit Mock-Layer")
    print("Dummy-Benutzer:")
    print("- Admin: admin@example.com / admin123")
    print("- Benutzer: john@example.com / password123")
    
    # App mit Factory-Pattern erstellen
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///notes_app.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'dev-secret-key'
    })
    
    # Serveur démarré sur le port 12002 - modification pour éviter les conflits
    app.run(host='0.0.0.0', port=12002, debug=True)

if __name__ == '__main__':
    main()