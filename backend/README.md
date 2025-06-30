# Flask Backend API - Notizen-Verwaltungssystem

Ein funktionales Web-Backend mit Python Flask für die Verwaltung von Benutzern und Notizen.

## 🚀 Features

- **Benutzer-Registrierung und -Anmeldung**
- **Session-basierte Authentifizierung**
- **CRUD-Operationen für Notizen**
- **Admin-Funktionen**
- **REST-API mit JSON**
- **In-Memory Datenspeicher**
- **CORS-Unterstützung**

## 📋 Datenmodell

### Users Tabelle
- `id` (INTEGER, Primary Key, unique)
- `name` (TEXT, unique)
- `email` (TEXT, unique)
- `admin` (BOOLEAN)

### Notes Tabelle
- `id` (INTEGER, Primary Key)
- `title` (TEXT)
- `content` (TEXT)
- `owner_id` (INTEGER, Foreign Key → users.id)

## 🛠️ Installation

1. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Server starten:**
   ```bash
   python app.py
   ```

Der Server läuft auf `http://localhost:12000`

## 👥 Dummy-Benutzer

Das System wird mit folgenden Test-Benutzern initialisiert:

- **Admin:** `admin@example.com` / `admin123`
- **Benutzer:** `john@example.com` / `password123`

## 📚 API-Endpunkte

### Basis
- `GET /` - API-Informationen

### Authentifizierung
- `POST /register` - Benutzer registrieren
- `POST /login` - Benutzer anmelden
- `POST /logout` - Benutzer abmelden

### Notizen (Authentifizierung erforderlich)
- `GET /notes` - Alle eigenen Notizen abrufen
- `POST /notes` - Neue Notiz erstellen
- `GET /notes/<id>` - Spezifische Notiz abrufen
- `PUT /notes/<id>` - Notiz bearbeiten
- `DELETE /notes/<id>` - Notiz löschen

### Admin-Funktionen (Admin-Berechtigung erforderlich)
- `GET /admin/users` - Alle Benutzer abrufen
- `DELETE /admin/users/<id>` - Benutzer löschen

## 🔐 Authentifizierung

Die API verwendet Session-Tokens für die Authentifizierung. Nach erfolgreichem Login erhalten Sie ein Token, das in den `Authorization`-Header eingetragen werden muss:

```
Authorization: <session_token>
```

## 📝 API-Beispiele

### Benutzer registrieren
```bash
curl -X POST http://localhost:12000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "neuer_benutzer",
    "email": "neu@example.com",
    "password": "sicherespasswort"
  }'
```

### Anmelden
```bash
curl -X POST http://localhost:12000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "neu@example.com",
    "password": "sicherespasswort"
  }'
```

### Notiz erstellen
```bash
curl -X POST http://localhost:12000/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: <session_token>" \
  -d '{
    "title": "Meine Notiz",
    "content": "Das ist der Inhalt meiner Notiz."
  }'
```

### Notizen abrufen
```bash
curl -X GET http://localhost:12000/notes \
  -H "Authorization: <session_token>"
```

### Notiz bearbeiten
```bash
curl -X PUT http://localhost:12000/notes/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: <session_token>" \
  -d '{
    "title": "Bearbeiteter Titel",
    "content": "Bearbeiteter Inhalt"
  }'
```

### Notiz löschen
```bash
curl -X DELETE http://localhost:12000/notes/1 \
  -H "Authorization: <session_token>"
```

## 🧪 Tests ausführen

```bash
python test_api.py
```

Das Test-Skript führt alle CRUD-Operationen durch und zeigt die Funktionalität der API.

## 🏗️ Architektur

- **Flask**: Web-Framework
- **Flask-CORS**: Cross-Origin Resource Sharing
- **In-Memory Storage**: Listen für Users und Notes
- **Session Management**: Dictionary für Session-Tokens
- **Password Hashing**: SHA-256 (vereinfacht für Demo)

## 🔒 Sicherheitshinweise

⚠️ **Nur für Entwicklung/Demo geeignet!**

- Passwörter werden nur mit SHA-256 gehashed (nicht sicher für Produktion)
- Session-Tokens sind einfache UUIDs
- Daten werden nur im Arbeitsspeicher gespeichert
- Keine Rate-Limiting oder erweiterte Sicherheitsmaßnahmen

## 📊 Funktionsübersicht

✅ **Implementiert:**
- Benutzer-Registrierung mit Validierung
- Login/Logout mit Session-Management
- Vollständige CRUD-Operationen für Notizen
- Admin-Funktionen zum Löschen von Benutzern
- Autorisierung und Zugriffskontrolle
- JSON-basierte REST-API
- Fehlerbehandlung und Validierung
- CORS-Unterstützung
- Dummy-Daten für Tests

## 🌐 Zugriff

Der Server ist unter folgenden URLs erreichbar:
- Lokal: `http://localhost:12000`
- Extern: `https://work-1-vjjazqvcxvmibmgf.prod-runtime.all-hands.dev`

## 📁 Projektstruktur

```
backend/
├── app.py              # Haupt-Flask-Anwendung
├── test_api.py         # API-Tests
├── requirements.txt    # Python-Dependencies
└── README.md          # Diese Dokumentation
```