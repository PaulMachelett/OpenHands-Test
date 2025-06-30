#!/usr/bin/env python3
"""
Test-Skript für das Flask Backend API mit SQLAlchemy
Testet alle CRUD-Operationen und SQLAlchemy-spezifische Funktionen
"""

import requests
import json

BASE_URL = "http://localhost:12001"

def print_response(response, description):
    """Hilfsfunktion zum Ausgeben von API-Antworten"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response Text: {response.text}")

def test_sqlalchemy_api():
    """Führt alle SQLAlchemy API-Tests durch"""
    
    print("🚀 Starte SQLAlchemy API-Tests...")
    
    # 1. Basis-Endpunkt testen
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Basis-Endpunkt mit SQLAlchemy")
    
    # 2. Statistiken abrufen (ohne Auth - sollte fehlschlagen)
    response = requests.get(f"{BASE_URL}/stats")
    print_response(response, "Statistiken ohne Auth (sollte fehlschlagen)")
    
    # 3. Neuen Benutzer registrieren
    new_user_data = {
        "name": "sqlalchemy_user",
        "email": "sqlalchemy@example.com",
        "password": "sqlalchemy123"
    }
    response = requests.post(f"{BASE_URL}/register", json=new_user_data)
    print_response(response, "SQLAlchemy Benutzer registrieren")
    
    # 4. Mit dem neuen Benutzer anmelden
    login_data = {
        "email": "sqlalchemy@example.com",
        "password": "sqlalchemy123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response(response, "SQLAlchemy Benutzer anmelden")
    
    if response.status_code == 200:
        user_token = response.json()["session_token"]
        headers = {"Authorization": user_token}
        
        # 5. Statistiken mit Auth abrufen
        response = requests.get(f"{BASE_URL}/stats", headers=headers)
        print_response(response, "Benutzer-Statistiken abrufen")
        
        # 6. Mehrere Notizen erstellen (SQLAlchemy Batch-Test)
        notes_data = [
            {
                "title": "SQLAlchemy Note 1",
                "content": "Das ist eine Notiz mit SQLAlchemy-Modellen."
            },
            {
                "title": "Database Test Note",
                "content": "Diese Notiz testet die Datenbankfunktionalität."
            },
            {
                "title": "ORM Test",
                "content": "Object-Relational Mapping mit SQLAlchemy."
            }
        ]
        
        created_notes = []
        for i, note_data in enumerate(notes_data):
            response = requests.post(f"{BASE_URL}/notes", json=note_data, headers=headers)
            print_response(response, f"Notiz {i+1} erstellen (SQLAlchemy)")
            if response.status_code == 201:
                created_notes.append(response.json()["note"])
        
        # 7. Alle Notizen abrufen
        response = requests.get(f"{BASE_URL}/notes", headers=headers)
        print_response(response, "Alle Notizen abrufen (SQLAlchemy)")
        
        # 8. Spezifische Notiz bearbeiten
        if created_notes:
            note_id = created_notes[0]["id"]
            update_data = {
                "title": "Bearbeitete SQLAlchemy Notiz",
                "content": "Diese Notiz wurde über SQLAlchemy-Modelle bearbeitet."
            }
            response = requests.put(f"{BASE_URL}/notes/{note_id}", json=update_data, headers=headers)
            print_response(response, "Notiz bearbeiten (SQLAlchemy)")
        
        # 9. Statistiken nach Notiz-Erstellung
        response = requests.get(f"{BASE_URL}/stats", headers=headers)
        print_response(response, "Aktualisierte Statistiken")
    
    # 10. Mit Admin anmelden
    admin_login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/login", json=admin_login_data)
    print_response(response, "Admin anmelden (SQLAlchemy)")
    
    if response.status_code == 200:
        admin_token = response.json()["session_token"]
        admin_headers = {"Authorization": admin_token}
        
        # 11. Admin-Statistiken abrufen
        response = requests.get(f"{BASE_URL}/stats", headers=admin_headers)
        print_response(response, "Admin-Statistiken mit User-Details")
        
        # 12. Alle Benutzer abrufen (Admin-Funktion)
        response = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
        print_response(response, "Alle Benutzer abrufen (SQLAlchemy Admin)")
        
        # 13. Benutzer löschen (Admin-Funktion mit Cascade Delete)
        if response.status_code == 200:
            users = response.json()["users"]
            test_user = next((u for u in users if u["email"] == "sqlalchemy@example.com"), None)
            if test_user:
                response = requests.delete(f"{BASE_URL}/admin/users/{test_user['id']}", headers=admin_headers)
                print_response(response, "Benutzer löschen mit Cascade Delete (SQLAlchemy)")
                
                # 14. Statistiken nach User-Löschung
                response = requests.get(f"{BASE_URL}/stats", headers=admin_headers)
                print_response(response, "Statistiken nach Cascade Delete")
    
    # 15. Mit normalem Benutzer anmelden
    normal_login_data = {
        "email": "john@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", json=normal_login_data)
    print_response(response, "Normaler Benutzer anmelden (SQLAlchemy)")
    
    if response.status_code == 200:
        normal_token = response.json()["session_token"]
        normal_headers = {"Authorization": normal_token}
        
        # 16. Notizen des normalen Benutzers (sollten noch existieren)
        response = requests.get(f"{BASE_URL}/notes", headers=normal_headers)
        print_response(response, "Notizen des normalen Benutzers (nach Cascade Delete)")
        
        # 17. Fehlertest: Zugriff auf nicht-existente Notiz
        response = requests.get(f"{BASE_URL}/notes/999", headers=normal_headers)
        print_response(response, "Zugriff auf nicht-existente Notiz (Fehlertest)")
        
        # 18. Fehlertest: Leere Notiz erstellen
        empty_note_data = {
            "title": "",
            "content": ""
        }
        response = requests.post(f"{BASE_URL}/notes", json=empty_note_data, headers=normal_headers)
        print_response(response, "Leere Notiz erstellen (Validierungstest)")
    
    print(f"\n{'='*60}")
    print("✅ Alle SQLAlchemy API-Tests abgeschlossen!")
    print("🔍 Getestete Features:")
    print("  - SQLAlchemy-Modelle (User, Note)")
    print("  - Mock-Database-Layer")
    print("  - Database-Service-Layer")
    print("  - Cascade Delete (User → Notes)")
    print("  - Erweiterte Statistiken")
    print("  - Fehlerbehandlung und Validierung")
    print("  - Session-Management")
    print(f"{'='*60}")

if __name__ == "__main__":
    try:
        test_sqlalchemy_api()
    except requests.exceptions.ConnectionError:
        print("❌ Fehler: Kann keine Verbindung zum Server herstellen.")
        print("Stellen Sie sicher, dass der Flask-Server läuft (python app_sqlalchemy.py)")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")