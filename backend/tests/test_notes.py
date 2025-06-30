"""
Integrationstests für Notizen-Funktionalität (CRUD-Operationen)
"""
import pytest


@pytest.mark.integration
@pytest.mark.notes
class TestNotesCreation:
    """Tests für Notizen-Erstellung"""
    
    def test_create_note_success(self, client, authenticated_user, sample_note_data):
        """Test erfolgreiche Notiz-Erstellung"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        response = client.post('/notes', json=sample_note_data, headers=headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Notiz erfolgreich erstellt'
        assert data['note']['title'] == sample_note_data['title']
        assert data['note']['content'] == sample_note_data['content']
        assert 'id' in data['note']
        # Vérification que la note appartient à l'utilisateur - utilise user_id
        assert data['note']['user_id'] == authenticated_user['user']['id']
    
    def test_create_note_without_auth(self, client, sample_note_data):
        """Test Notiz-Erstellung ohne Authentifizierung"""
        response = client.post('/notes', json=sample_note_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Nicht autorisiert' in data['error']
    
    def test_create_note_invalid_token(self, client, sample_note_data):
        """Test Notiz-Erstellung mit ungültigem Token"""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = client.post('/notes', json=sample_note_data, headers=headers)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'ungültig' in data['error'].lower()
    
    def test_create_note_missing_fields(self, client, authenticated_user):
        """Test Notiz-Erstellung mit fehlenden Feldern"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        incomplete_data = {'title': 'Only Title'}
        response = client.post('/notes', json=incomplete_data, headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_note_empty_content(self, client, authenticated_user):
        """Test Notiz-Erstellung mit leerem Inhalt"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        empty_data = {'title': 'Empty Note', 'content': ''}
        response = client.post('/notes', json=empty_data, headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'darf nicht leer sein' in data['error']


@pytest.mark.integration
@pytest.mark.notes
class TestNotesRetrieval:
    """Tests für Notizen-Abruf"""
    
    def test_get_all_notes_success(self, client, authenticated_user, sample_note_data):
        """Test erfolgreicher Abruf aller Notizen"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        
        # Erstelle eine Notiz
        client.post('/notes', json=sample_note_data, headers=headers)
        
        # Rufe alle Notizen ab
        response = client.get('/notes', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'notes' in data
        assert len(data['notes']) >= 1
        # Prüfe, ob die erstellte Notiz in der Liste ist
        note_titles = [note['title'] for note in data['notes']]
        assert sample_note_data['title'] in note_titles
    
    def test_get_notes_without_auth(self, client):
        """Test Notizen-Abruf ohne Authentifizierung"""
        response = client.get('/notes')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Nicht autorisiert' in data['error']
    
    def test_get_specific_note_success(self, client, authenticated_user, sample_note_data):
        """Test erfolgreicher Abruf einer spezifischen Notiz"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        
        # Erstelle eine Notiz
        create_response = client.post('/notes', json=sample_note_data, headers=headers)
        note_id = create_response.get_json()['note']['id']
        
        # Rufe spezifische Notiz ab
        response = client.get(f'/notes/{note_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['note']['id'] == note_id
        assert data['note']['title'] == sample_note_data['title']
    
    def test_get_nonexistent_note(self, client, authenticated_user):
        """Test Abruf einer nicht existierenden Notiz"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        response = client.get('/notes/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'nicht gefunden' in data['error']
    
    def test_get_note_from_other_user(self, client, sample_user_data, sample_note_data):
        """Test Abruf einer Notiz eines anderen Benutzers"""
        # Erstelle ersten Benutzer und Notiz
        client.post('/register', json=sample_user_data)
        login_response1 = client.post('/userlogin', json={
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        })
        user1_token = login_response1.get_json()['session_token']
        headers1 = {'Authorization': f"Bearer {user1_token}"}
        
        create_response = client.post('/notes', json=sample_note_data, headers=headers1)
        note_id = create_response.get_json()['note']['id']
        
        # Erstelle zweiten Benutzer
        user2_data = {
            'name': 'user2',
            'email': 'user2@example.com',
            'password': 'password123'
        }
        client.post('/register', json=user2_data)
        login_response2 = client.post('/userlogin', json={
            'email': user2_data['email'],
            'password': user2_data['password']
        })
        user2_token = login_response2.get_json()['session_token']
        headers2 = {'Authorization': f"Bearer {user2_token}"}
        
        # Versuche Zugriff auf Notiz des ersten Benutzers
        response = client.get(f'/notes/{note_id}', headers=headers2)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Zugriff verweigert' in data['error']


@pytest.mark.integration
@pytest.mark.notes
class TestNotesUpdate:
    """Tests für Notizen-Aktualisierung"""
    
    def test_update_note_success(self, client, authenticated_user, sample_note_data):
        """Test erfolgreiche Notiz-Aktualisierung"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        
        # Erstelle eine Notiz
        create_response = client.post('/notes', json=sample_note_data, headers=headers)
        note_id = create_response.get_json()['note']['id']
        
        # Aktualisiere die Notiz
        updated_data = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        response = client.put(f'/notes/{note_id}', json=updated_data, headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Notiz erfolgreich aktualisiert'
        assert data['note']['title'] == updated_data['title']
        assert data['note']['content'] == updated_data['content']
    
    def test_update_nonexistent_note(self, client, authenticated_user):
        """Test Aktualisierung einer nicht existierenden Notiz"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        updated_data = {'title': 'New Title', 'content': 'New content'}
        
        response = client.put('/notes/999', json=updated_data, headers=headers)
        
        assert response.status_code in [403, 404]
        data = response.get_json()
        # Flexible Fehlermeldung - kann "nicht gefunden" oder "Zugriff verweigert" sein
        assert any(phrase in data['error'] for phrase in ['nicht gefunden', 'Zugriff verweigert', 'nicht berechtigt'])
    
    def test_update_note_without_auth(self, client):
        """Test Notiz-Aktualisierung ohne Authentifizierung"""
        updated_data = {'title': 'New Title', 'content': 'New content'}
        response = client.put('/notes/1', json=updated_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Nicht autorisiert' in data['error']


@pytest.mark.integration
@pytest.mark.notes
class TestNotesDeletion:
    """Tests für Notizen-Löschung"""
    
    def test_delete_note_success(self, client, authenticated_user, sample_note_data):
        """Test erfolgreiche Notiz-Löschung"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        
        # Erstelle eine Notiz
        create_response = client.post('/notes', json=sample_note_data, headers=headers)
        note_id = create_response.get_json()['note']['id']
        
        # Lösche die Notiz
        response = client.delete(f'/notes/{note_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'erfolgreich gelöscht' in data['message']
        
        # Verifiziere, dass die Notiz gelöscht wurde
        get_response = client.get(f'/notes/{note_id}', headers=headers)
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_note(self, client, authenticated_user):
        """Test Löschung einer nicht existierenden Notiz"""
        headers = {'Authorization': f"Bearer {authenticated_user['session_token']}"}
        response = client.delete('/notes/999', headers=headers)
        
        assert response.status_code in [403, 404]
        data = response.get_json()
        # Flexible Fehlermeldung - kann "nicht gefunden" oder "Zugriff verweigert" sein
        assert any(phrase in data['error'] for phrase in ['nicht gefunden', 'Zugriff verweigert', 'nicht berechtigt'])
    
    def test_delete_note_without_auth(self, client):
        """Test Notiz-Löschung ohne Authentifizierung"""
        response = client.delete('/notes/1')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Nicht autorisiert' in data['error']