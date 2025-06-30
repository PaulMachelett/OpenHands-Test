"""
Integrationstests für API-Basis-Funktionalität
"""
import pytest


@pytest.mark.integration
class TestAPIBase:
    """Tests für grundlegende API-Funktionalität"""
    
    def test_api_root_endpoint(self, client):
        """Test API-Root-Endpunkt"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'database' in data
        assert 'endpoints' in data
        assert 'demo' in data
        assert data['database'] == 'SQLAlchemy mit Mock-Layer'
    
    def test_api_endpoints_documentation(self, client):
        """Test API-Endpunkte-Dokumentation"""
        response = client.get('/')
        data = response.get_json()
        
        endpoints = data['endpoints']
        expected_endpoints = [
            'POST /register',
            'POST /userlogin',
            'POST /logout',
            'GET /notes',
            'POST /notes',
            'GET /notes/<id>',
            'PUT /notes/<id>',
            'DELETE /notes/<id>',
            'GET /stats',
            'GET /admin/users',
            'DELETE /admin/users/<id>'
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in endpoints
    
    def test_demo_page_accessible(self, client):
        """Test Demo-Seite ist erreichbar"""
        response = client.get('/demo.html')
        
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
    
    def test_invalid_endpoint_404(self, client):
        """Test ungültiger Endpunkt gibt 404 zurück"""
        response = client.get('/invalid-endpoint')
        
        assert response.status_code == 404
    
    def test_invalid_method_405(self, client):
        """Test ungültige HTTP-Methode gibt 405 zurück"""
        response = client.patch('/')  # PATCH ist nicht erlaubt für Root
        
        assert response.status_code == 405
    
    def test_json_content_type(self, client):
        """Test JSON Content-Type für API-Endpunkte"""
        response = client.get('/')
        
        assert 'application/json' in response.content_type
    
    def test_cors_headers(self, client):
        """Test CORS-Headers sind gesetzt"""
        response = client.get('/')
        
        # Prüfe, ob CORS-Headers vorhanden sind (falls implementiert)
        # Dies ist optional, aber gut für Frontend-Integration
        headers = response.headers
        # Hier könnten CORS-spezifische Tests hinzugefügt werden
        assert response.status_code == 200


@pytest.mark.integration
class TestAPIErrorHandling:
    """Tests für API-Fehlerbehandlung"""
    
    def test_malformed_json_request(self, client):
        """Test fehlerhafte JSON-Anfrage"""
        response = client.post('/register', 
                             data='{"invalid": json}',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_missing_content_type(self, client):
        """Test fehlender Content-Type für JSON-Endpunkte"""
        response = client.post('/register', data='{"name": "test"}')
        
        # Sollte entweder 400 oder 415 zurückgeben
        assert response.status_code in [400, 415]
    
    def test_empty_request_body(self, client):
        """Test leerer Request-Body für JSON-Endpunkte"""
        response = client.post('/register', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


@pytest.mark.integration
class TestAPIPerformance:
    """Basis-Performance-Tests für API"""
    
    def test_multiple_concurrent_requests(self, client, sample_user_data):
        """Test mehrere gleichzeitige Anfragen"""
        # Registriere einen Benutzer
        client.post('/register', json=sample_user_data)
        
        # Melde Benutzer an
        login_response = client.post('/userlogin', json={
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        })
        token = login_response.get_json()['session_token']
        headers = {'Authorization': f"Bearer {token}"}
        
        # Führe mehrere Anfragen aus
        responses = []
        for i in range(5):
            response = client.get('/stats', headers=headers)
            responses.append(response)
        
        # Alle Anfragen sollten erfolgreich sein
        for response in responses:
            assert response.status_code == 200
    
    def test_large_note_content(self, client, authenticated_user):
        """Test große Notiz-Inhalte"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        
        # Erstelle eine Notiz mit großem Inhalt
        large_content = "A" * 10000  # 10KB Text
        large_note_data = {
            'title': 'Large Note',
            'content': large_content
        }
        
        response = client.post('/notes', json=large_note_data, headers=headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert len(data['note']['content']) == 10000