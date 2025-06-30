"""
Datenexport-Funktionen für das Flask Backend
Exportiert Daten aus der Datenbank in Textdateien
"""

import os
from datetime import datetime
from myapp import create_app
from myapp.crud import db_service


def export_database_to_text():
    """
    Exportiert alle Benutzer und Notizen aus der Datenbank in eine Textdatei.
    Erstellt eine strukturierte Übersicht aller Daten im lesbaren Format.
    """
    # App-Kontext erstellen
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///notes_app.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'dev-secret-key'
    })
    
    with app.app_context():
        # Alle Benutzer abrufen
        users = db_service.get_all_users()
        
        # Dateiname mit Zeitstempel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_export_{timestamp}.txt"
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("DATENBANK EXPORT - FLASK BACKEND\n")
            f.write("=" * 60 + "\n")
            f.write(f"Exportiert am: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}\n")
            f.write(f"Anzahl Benutzer: {len(users)}\n\n")
            
            # Benutzer exportieren
            f.write("BENUTZER:\n")
            f.write("-" * 40 + "\n")
            
            for user in users:
                user_dict = user.to_dict()
                f.write(f"ID: {user_dict['id']}\n")
                f.write(f"Name: {user_dict['name']}\n")
                f.write(f"E-Mail: {user_dict['email']}\n")
                f.write(f"Administrator: {'Ja' if user_dict['admin'] else 'Nein'}\n")
                f.write(f"Erstellt am: {user_dict['created_at']}\n")
                
                # Notizen des Benutzers abrufen
                notes = db_service.get_notes_by_user(user_dict['id'])
                f.write(f"Anzahl Notizen: {len(notes)}\n")
                
                if notes:
                    f.write("\nNotizen:\n")
                    for note in notes:
                        note_dict = note.to_dict()
                        f.write(f"  - [{note_dict['id']}] {note_dict['title']}\n")
                        f.write(f"    Inhalt: {note_dict['content'][:100]}{'...' if len(note_dict['content']) > 100 else ''}\n")
                        f.write(f"    Erstellt: {note_dict['created_at']}\n")
                        f.write(f"    Aktualisiert: {note_dict['updated_at']}\n")
                        f.write(f"    User-ID: {note_dict['user_id']}\n\n")  # Verwendung von user_id
                
                f.write("-" * 40 + "\n")
            
            # Statistiken
            stats = db_service.get_stats()
            admin_count = sum(1 for user in users if user.to_dict()['admin'])
            regular_count = len(users) - admin_count
            
            f.write("\nSTATISTIKEN:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Gesamtanzahl Benutzer: {stats['total_users']}\n")
            f.write(f"Gesamtanzahl Notizen: {stats['total_notes']}\n")
            f.write(f"Administratoren: {admin_count}\n")
            f.write(f"Normale Benutzer: {regular_count}\n")
            
        print(f"✅ Datenbank erfolgreich exportiert nach: {filepath}")
        print(f"📊 Exportierte Daten: {len(users)} Benutzer")
        
        return filepath


def export_notes_summary():
    """
    Erstellt eine Zusammenfassung aller Notizen gruppiert nach Benutzern.
    Exportiert nur die wichtigsten Informationen in kompakter Form.
    """
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///notes_app.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'dev-secret-key'
    })
    
    with app.app_context():
        users = db_service.get_all_users()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"notes_summary_{timestamp}.txt"
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("NOTIZEN ZUSAMMENFASSUNG\n")
            f.write("=" * 50 + "\n\n")
            
            total_notes = 0
            for user in users:
                user_dict = user.to_dict()
                notes = db_service.get_notes_by_user(user_dict['id'])
                total_notes += len(notes)
                
                f.write(f"👤 {user_dict['name']} ({user_dict['email']})\n")
                f.write(f"   {'🔧 Administrator' if user_dict['admin'] else '👥 Benutzer'}\n")
                f.write(f"   📝 {len(notes)} Notizen\n")
                
                if notes:
                    for note in notes:
                        note_dict = note.to_dict()
                        f.write(f"   • {note_dict['title']} (ID: {note_dict['id']}, User-ID: {note_dict['user_id']})\n")
                
                f.write("\n")
            
            f.write(f"📊 GESAMT: {total_notes} Notizen von {len(users)} Benutzern\n")
        
        print(f"✅ Notizen-Zusammenfassung exportiert nach: {filepath}")
        print(f"📝 Zusammengefasst: {total_notes} Notizen")
        
        return filepath


if __name__ == "__main__":
    print("🚀 Starte Datenexport...")
    
    # Vollständigen Export durchführen
    export_file = export_database_to_text()
    
    # Notizen-Zusammenfassung erstellen
    summary_file = export_notes_summary()
    
    print("\n✨ Export abgeschlossen!")
    print(f"📁 Dateien erstellt:")
    print(f"   - {export_file}")
    print(f"   - {summary_file}")