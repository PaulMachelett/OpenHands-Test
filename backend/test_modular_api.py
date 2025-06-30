"""
Test-Suite für die modulare Flask-API-Struktur
Testet alle Endpunkte der umstrukturierten Anwendung
"""

import requests
import json

BASE_URL = "http://localhost:12001"

def print_response(response, description):
    """Hilfsfunktion zum Ausgeben von API-Antworten"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print('='*60)
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")

def test_modular_api():
    """Haupttest-Funktion für die modulare API"""
    print("🚀 Starte Tests für modulare API-Struktur...")
    
    # Test 1: Basis-Endpunkt
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Modulare API Basis-Endpunkt")
    
    # Test 2: Benutzer registrieren
    register_data = {
        "name": "modular_user",
        "email": "modular@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print_response(response, "Benutzer registrieren (modulare Struktur)")
    
    # Test 3: Benutzer anmelden
    login_data = {
        "email": "modular@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response(response, "Benutzer anmelden (modulare Struktur)")
    
    if response.status_code == 200:
        session_token = response.json()['session_token']
        headers = {'Authorization': f'Bearer {session_token}'}
        
        # Test 4: Statistiken abrufen
        response = requests.get(f"{BASE_URL}/stats", headers=headers)
        print_response(response, "Benutzer-Statistiken (modulare Struktur)")
        
        # Test 5: Notiz erstellen
        note_data = {
            "title": "Modulare Notiz",
            "content": "Diese Notiz wurde mit der modularen API-Struktur erstellt."
        }
        response = requests.post(f"{BASE_URL}/notes", json=note_data, headers=headers)
        print_response(response, "Notiz erstellen (modulare Struktur)")
        
        if response.status_code == 201:
            note_id = response.json()['note']['id']
            
            # Test 6: Notiz abrufen
            response = requests.get(f"{BASE_URL}/notes/{note_id}", headers=headers)
            print_response(response, "Spezifische Notiz abrufen (modulare Struktur)")
            
            # Test 7: Notiz bearbeiten
            update_data = {
                "title": "Bearbeitete modulare Notiz",
                "content": "Diese Notiz wurde über die modulare API bearbeitet."
            }
            response = requests.put(f"{BASE_URL}/notes/{note_id}", json=update_data, headers=headers)
            print_response(response, "Notiz bearbeiten (modulare Struktur)")
        
        # Test 8: Alle Notizen abrufen
        response = requests.get(f"{BASE_URL}/notes", headers=headers)
        print_response(response, "Alle Notizen abrufen (modulare Struktur)")
        
        # Test 9: Abmelden
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        print_response(response, "Benutzer abmelden (modulare Struktur)")
    
    # Test 10: Admin-Login
    admin_login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/login", json=admin_login_data)
    print_response(response, "Admin anmelden (modulare Struktur)")
    
    if response.status_code == 200:
        admin_token = response.json()['session_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Test 11: Admin-Statistiken
        response = requests.get(f"{BASE_URL}/stats", headers=admin_headers)
        print_response(response, "Admin-Statistiken (modulare Struktur)")
        
        # Test 12: Alle Benutzer abrufen
        response = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
        print_response(response, "Alle Benutzer abrufen (modulare Admin)")
    
    # Test 13: Validierungstest - Leere Notiz
    invalid_note_data = {
        "title": "",
        "content": ""
    }
    response = requests.post(f"{BASE_URL}/notes", json=invalid_note_data, headers=headers)
    print_response(response, "Validierungstest - Leere Notiz (modulare Struktur)")
    
    # Test 14: Fehlertest - Nicht existente Notiz
    response = requests.get(f"{BASE_URL}/notes/999", headers=headers)
    print_response(response, "Fehlertest - Nicht existente Notiz (modulare Struktur)")
    
    print(f"\n{'='*60}")
    print("✅ Alle Tests für modulare API-Struktur abgeschlossen!")
    print("🔍 Getestete Module:")
    print("  - myapp/models.py: SQLAlchemy-Modelle")
    print("  - myapp/db.py: Mock-Database-Layer")
    print("  - myapp/crud.py: CRUD-Operationen")
    print("  - myapp/routes.py: API-Endpunkte")
    print("  - myapp/utils.py: Hilfsfunktionen")
    print("  - main.py: Haupteinstiegspunkt")
    print('='*60)

if __name__ == "__main__":
    test_modular_api()