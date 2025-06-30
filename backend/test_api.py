#!/usr/bin/env python3
"""
Test-Skript für das Flask Backend API
Testet alle CRUD-Operationen und Funktionen
"""

import requests
import json

BASE_URL = "http://localhost:12000"

def print_response(response, description):
    """Hilfsfunktion zum Ausgeben von API-Antworten"""
    print(f"\n{'='*50}")
    print(f"TEST: {description}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response Text: {response.text}")

def test_api():
    """Führt alle API-Tests durch"""
    
    # 1. Basis-Endpunkt testen
    print("🚀 Starte API-Tests...")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Basis-Endpunkt")
    
    # 2. Neuen Benutzer registrieren
    new_user_data = {
        "name": "test_user",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/register", json=new_user_data)
    print_response(response, "Benutzer registrieren")
    
    # 3. Mit dem neuen Benutzer anmelden
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response(response, "Benutzer anmelden")
    
    if response.status_code == 200:
        user_token = response.json()["session_token"]
        headers = {"Authorization": user_token}
        
        # 4. Notizen des Benutzers abrufen (sollte leer sein)
        response = requests.get(f"{BASE_URL}/notes", headers=headers)
        print_response(response, "Notizen abrufen (leer)")
        
        # 5. Neue Notiz erstellen
        note_data = {
            "title": "Meine Test-Notiz",
            "content": "Das ist der Inhalt meiner Test-Notiz."
        }
        response = requests.post(f"{BASE_URL}/notes", json=note_data, headers=headers)
        print_response(response, "Notiz erstellen")
        
        if response.status_code == 201:
            note_id = response.json()["note"]["id"]
            
            # 6. Notizen erneut abrufen (sollte jetzt eine Notiz enthalten)
            response = requests.get(f"{BASE_URL}/notes", headers=headers)
            print_response(response, "Notizen abrufen (mit Inhalt)")
            
            # 7. Spezifische Notiz abrufen
            response = requests.get(f"{BASE_URL}/notes/{note_id}", headers=headers)
            print_response(response, "Spezifische Notiz abrufen")
            
            # 8. Notiz bearbeiten
            update_data = {
                "title": "Bearbeitete Test-Notiz",
                "content": "Das ist der bearbeitete Inhalt meiner Test-Notiz."
            }
            response = requests.put(f"{BASE_URL}/notes/{note_id}", json=update_data, headers=headers)
            print_response(response, "Notiz bearbeiten")
            
            # 9. Notiz löschen
            response = requests.delete(f"{BASE_URL}/notes/{note_id}", headers=headers)
            print_response(response, "Notiz löschen")
    
    # 10. Mit Admin anmelden
    admin_login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/login", json=admin_login_data)
    print_response(response, "Admin anmelden")
    
    if response.status_code == 200:
        admin_token = response.json()["session_token"]
        admin_headers = {"Authorization": admin_token}
        
        # 11. Alle Benutzer abrufen (Admin-Funktion)
        response = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
        print_response(response, "Alle Benutzer abrufen (Admin)")
        
        # 12. Benutzer löschen (Admin-Funktion)
        # Finde die ID des test_user
        if response.status_code == 200:
            users = response.json()["users"]
            test_user = next((u for u in users if u["email"] == "test@example.com"), None)
            if test_user:
                response = requests.delete(f"{BASE_URL}/admin/users/{test_user['id']}", headers=admin_headers)
                print_response(response, "Benutzer löschen (Admin)")
    
    # 13. Mit normalem Benutzer anmelden
    normal_login_data = {
        "email": "john@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", json=normal_login_data)
    print_response(response, "Normaler Benutzer anmelden")
    
    if response.status_code == 200:
        normal_token = response.json()["session_token"]
        normal_headers = {"Authorization": normal_token}
        
        # 14. Notizen des normalen Benutzers abrufen
        response = requests.get(f"{BASE_URL}/notes", headers=normal_headers)
        print_response(response, "Notizen des normalen Benutzers")
    
    print(f"\n{'='*50}")
    print("✅ Alle Tests abgeschlossen!")
    print(f"{'='*50}")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Fehler: Kann keine Verbindung zum Server herstellen.")
        print("Stellen Sie sicher, dass der Flask-Server läuft (python app.py)")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")