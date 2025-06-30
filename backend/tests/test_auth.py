"""
Integrationstests für Authentifizierung (Registrierung und Login)
"""
import pytest


@pytest.mark.integration
@pytest.mark.auth
class TestRegistration:
    """Tests für Benutzerregistrierung"""
    
    def test_successful_registration(self, client):
        """Test erfolgreiche Registrierung"""
        # Verwende eindeutige Daten für jeden Test
        unique_user_data = {
            'name': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        response = client.post('/register', json=unique_user_data)
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert data['message'] == 'Benutzer erfolgreich registriert'
        assert data['user']['name'] == unique_user_data['name']
        assert data['user']['email'] == unique_user_data['email']
        assert 'password' not in data['user']  # Passwort sollte nicht zurückgegeben werden
    
    def test_registration_missing_fields(self, client):
        """Test Registrierung mit fehlenden Feldern"""
        incomplete_data = {'name': 'testuser'}
        response = client.post('/register', json=incomplete_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_registration_duplicate_email(self, client, sample_user_data):
        """Test Registrierung mit bereits existierender E-Mail"""
        # Erste Registrierung
        client.post('/register', json=sample_user_data)
        
        # Zweite Registrierung mit gleicher E-Mail
        duplicate_data = sample_user_data.copy()
        duplicate_data['name'] = 'differentuser'
        response = client.post('/register', json=duplicate_data)
        
        assert response.status_code in [400, 409]
        data = response.get_json()
        assert 'bereits registriert' in data['error']
    
    def test_registration_duplicate_name(self, client, sample_user_data):
        """Test Registrierung mit bereits existierendem Namen"""
        # Erste Registrierung
        client.post('/register', json=sample_user_data)
        
        # Zweite Registrierung mit gleichem Namen
        duplicate_data = sample_user_data.copy()
        duplicate_data['email'] = 'different@example.com'
        response = client.post('/register', json=duplicate_data)
        
        assert response.status_code in [400, 409]
        data = response.get_json()
        assert 'bereits vergeben' in data['error']
    
    def test_registration_invalid_email(self, client):
        """Test Registrierung mit ungültiger E-Mail"""
        invalid_data = {
            'name': 'testuser',
            'email': 'invalid-email',
            'password': 'password123'
        }
        response = client.post('/register', json=invalid_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'E-Mail' in data['error']


@pytest.mark.integration
@pytest.mark.auth
class TestLogin:
    """Tests für Benutzeranmeldung"""
    
    def test_successful_login(self, client, sample_user_data):
        """Test erfolgreiche Anmeldung"""
        # Registriere Benutzer zuerst
        client.post('/register', json=sample_user_data)
        
        # Connexion utilisateur avec la nouvelle route /userlogin
        login_data = {
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        }
        response = client.post('/userlogin', json=login_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'erfolgreich' in data['message'].lower()
        assert data['user']['email'] == sample_user_data['email']
        assert 'session_token' in data
    
    def test_login_invalid_email(self, client):
        """Test Anmeldung mit ungültiger E-Mail"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        response = client.post('/userlogin', json=login_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Ungültige' in data['error']
    
    def test_login_invalid_password(self, client, sample_user_data):
        """Test Anmeldung mit falschem Passwort"""
        # Registriere Benutzer zuerst
        client.post('/register', json=sample_user_data)
        
        # Versuche Anmeldung mit falschem Passwort
        login_data = {
            'email': sample_user_data['email'],
            'password': 'wrongpassword'
        }
        response = client.post('/userlogin', json=login_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Ungültige' in data['error']
    
    def test_login_missing_fields(self, client):
        """Test Anmeldung mit fehlenden Feldern"""
        incomplete_data = {'email': 'test@example.com'}
        response = client.post('/userlogin', json=incomplete_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


@pytest.mark.integration
@pytest.mark.auth
class TestLogout:
    """Tests für Benutzerabmeldung"""
    
    def test_successful_logout(self, client, authenticated_user):
        """Test erfolgreiche Abmeldung"""
        # Verwende das Session-Token vom authentifizierten Benutzer
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        response = client.post('/logout', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'abgemeldet' in data['message'].lower()
    
    def test_logout_without_token(self, client):
        """Test Abmeldung ohne Session-Token"""
        response = client.post('/logout')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Nicht autorisiert' in data['error']
    
    def test_logout_invalid_token(self, client):
        """Test Abmeldung mit ungültigem Token"""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = client.post('/logout', headers=headers)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'ungültig' in data['error'].lower()