"""
Integrationstests für Admin-Funktionalität
"""
import pytest


@pytest.mark.integration
@pytest.mark.admin
class TestAdminUserManagement:
    """Tests für Admin-Benutzerverwaltung"""
    
    def test_admin_get_all_users(self, client, authenticated_admin):
        """Test Admin kann alle Benutzer abrufen"""
        headers = {'Authorization': f"Bearer {authenticated_admin['session_token']}"}
        response = client.get('/admin/users', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert len(data['users']) >= 1  # Mindestens der Admin selbst
    
    def test_non_admin_cannot_get_users(self, client, authenticated_user):
        """Test normaler Benutzer kann nicht alle Benutzer abrufen"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        response = client.get('/admin/users', headers=headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Admin-Berechtigung erforderlich' in data['error']
    
    def test_admin_delete_user_success(self, client, authenticated_admin, sample_user_data):
        """Test Admin kann Benutzer löschen"""
        # Erstelle einen normalen Benutzer
        client.post('/register', json=sample_user_data)
        
        # Admin ruft alle Benutzer ab, um die ID zu finden
        admin_headers = {'Authorization': f"Bearer {authenticated_admin['session_token']}"}
        users_response = client.get('/admin/users', headers=admin_headers)
        users = users_response.get_json()['users']
        
        # Finde den erstellten Benutzer
        target_user = None
        for user in users:
            if user['email'] == sample_user_data['email']:
                target_user = user
                break
        
        assert target_user is not None
        
        # Lösche den Benutzer
        response = client.delete(f'/admin/users/{target_user["id"]}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'erfolgreich gelöscht' in data['message']
        
        # Verifiziere, dass der Benutzer gelöscht wurde
        users_response_after = client.get('/admin/users', headers=admin_headers)
        users_after = users_response_after.get_json()['users']
        user_emails = [user['email'] for user in users_after]
        assert sample_user_data['email'] not in user_emails
    
    def test_admin_delete_nonexistent_user(self, client, authenticated_admin):
        """Test Admin versucht nicht existierenden Benutzer zu löschen"""
        headers = {'Authorization': f"Bearer {authenticated_admin['session_token']}"}
        response = client.delete('/admin/users/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'nicht gefunden' in data['error']
    
    def test_non_admin_cannot_delete_user(self, client, authenticated_user):
        """Test normaler Benutzer kann keine Benutzer löschen"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        response = client.delete('/admin/users/1', headers=headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Admin-Berechtigung erforderlich' in data['error']
    
    def test_admin_cannot_delete_self(self, client, authenticated_admin):
        """Test Admin kann sich nicht selbst löschen"""
        admin_id = authenticated_admin['user']['id']
        headers = {'Authorization': f"Bearer {authenticated_admin['session_token']}"}
        response = client.delete(f'/admin/users/{admin_id}', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'sich selbst löschen' in data['error']
    
    def test_admin_access_without_auth(self, client):
        """Test Admin-Endpunkt ohne Authentifizierung"""
        response = client.get('/admin/users')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Nicht autorisiert' in data['error']
    
    def test_admin_access_invalid_token(self, client):
        """Test Admin-Endpunkt mit ungültigem Token"""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = client.get('/admin/users', headers=headers)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'ungültig' in data['error'].lower()


@pytest.mark.integration
@pytest.mark.admin
class TestAdminStatistics:
    """Tests für Admin-Statistiken"""
    
    def test_admin_can_access_stats(self, client, authenticated_admin):
        """Test Admin kann Statistiken abrufen"""
        headers = {'Authorization': f"Bearer {authenticated_admin['session_token']}"}
        response = client.get('/stats', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_users' in data
        assert 'total_notes' in data
        assert 'admin_users' in data
        assert isinstance(data['total_users'], int)
        assert isinstance(data['total_notes'], int)
        assert isinstance(data['admin_users'], int)
    
    def test_normal_user_can_access_stats(self, client, authenticated_user):
        """Test normaler Benutzer kann auch Statistiken abrufen"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        response = client.get('/stats', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_users' in data
        assert 'total_notes' in data
    
    def test_stats_without_auth(self, client):
        """Test Statistiken ohne Authentifizierung"""
        response = client.get('/stats')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Nicht autorisiert' in data['error']