"""
Tests für E-Mail-Existenz-Prüfung
Testet die neue /check-email/<email> Route
"""

import pytest
from myapp import create_app


@pytest.mark.integration
@pytest.mark.email_check
class TestEmailCheck:
    """Test-Klasse für E-Mail-Existenz-Prüfung"""

    def test_check_existing_email_returns_true(self, client, authenticated_admin):
        """Test: Existierende E-Mail gibt true zurück"""
        # Arrange: authenticated_admin ist bereits registriert mit admin@example.com
        email = "admin@example.com"
        
        # Act
        response = client.get(f'/check-email/{email}')
        
        # Assert
        assert response.status_code == 200
        assert response.get_json() is True

    def test_check_nonexistent_email_returns_false(self, client):
        """Test: Nicht-existierende E-Mail gibt false zurück"""
        # Arrange
        email = "nonexistent@example.com"
        
        # Act
        response = client.get(f'/check-email/{email}')
        
        # Assert
        assert response.status_code == 200
        assert response.get_json() is False

    def test_check_invalid_email_returns_false(self, client):
        """Test: Ungültige E-Mail gibt false zurück"""
        # Arrange
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test..test@example.com",
            "test@example",
            ""
        ]
        
        for email in invalid_emails:
            # Act
            response = client.get(f'/check-email/{email}')
            
            # Assert
            assert response.status_code == 200
            assert response.get_json() is False, f"Email '{email}' should return false"

    def test_check_email_case_insensitive(self, client, authenticated_admin):
        """Test: E-Mail-Prüfung ist case-insensitive"""
        # Arrange: authenticated_admin hat admin@example.com
        emails_to_test = [
            "ADMIN@EXAMPLE.COM",
            "Admin@Example.Com",
            "admin@EXAMPLE.com"
        ]
        
        for email in emails_to_test:
            # Act
            response = client.get(f'/check-email/{email}')
            
            # Assert
            assert response.status_code == 200
            assert response.get_json() is True, f"Email '{email}' should return true (case insensitive)"

    def test_check_email_with_special_characters(self, client):
        """Test: E-Mail mit Sonderzeichen"""
        # Arrange
        special_emails = [
            "test+tag@example.com",
            "test.name@example.com",
            "test_name@example.com",
            "test-name@example.com"
        ]
        
        for email in special_emails:
            # Act
            response = client.get(f'/check-email/{email}')
            
            # Assert
            assert response.status_code == 200
            assert response.get_json() is False  # Diese E-Mails existieren nicht

    def test_check_email_url_encoding(self, client, authenticated_admin):
        """Test: URL-Encoding in E-Mail-Adressen"""
        # Arrange: Teste mit URL-encodierter E-Mail
        email_encoded = "admin%40example.com"  # admin@example.com URL-encoded
        
        # Act
        response = client.get(f'/check-email/{email_encoded}')
        
        # Assert
        assert response.status_code == 200
        # Flask dekodiert URLs automatisch, daher sollte true zurückgegeben werden
        assert response.get_json() is True

    def test_check_email_multiple_users(self, client, authenticated_user, authenticated_admin):
        """Test: Mehrere registrierte Benutzer prüfen"""
        # Arrange: authenticated_user und authenticated_admin sind registriert
        existing_emails = [
            "admin@example.com",  # Admin-User
            "test@example.com"  # Normal-User
        ]
        
        non_existing_emails = [
            "user3@example.com",
            "another@test.com"
        ]
        
        # Act & Assert: Existierende E-Mails
        for email in existing_emails:
            response = client.get(f'/check-email/{email}')
            assert response.status_code == 200
            assert response.get_json() is True, f"Email '{email}' should exist"
        
        # Act & Assert: Nicht-existierende E-Mails
        for email in non_existing_emails:
            response = client.get(f'/check-email/{email}')
            assert response.status_code == 200
            assert response.get_json() is False, f"Email '{email}' should not exist"

    def test_check_email_performance(self, client):
        """Test: Performance bei vielen E-Mail-Prüfungen"""
        import time
        
        # Arrange
        emails_to_check = [f"test{i}@example.com" for i in range(10)]
        
        # Act
        start_time = time.time()
        for email in emails_to_check:
            response = client.get(f'/check-email/{email}')
            assert response.status_code == 200
            assert response.get_json() is False
        end_time = time.time()
        
        # Assert: Sollte schnell sein (unter 1 Sekunde für 10 Anfragen)
        total_time = end_time - start_time
        assert total_time < 1.0, f"E-Mail-Prüfungen zu langsam: {total_time:.2f}s"

    def test_check_email_endpoint_in_api_documentation(self, client):
        """Test: Neue Route ist in der API-Dokumentation enthalten"""
        # Act
        response = client.get('/')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'endpoints' in data
        assert 'GET /check-email/<email>' in data['endpoints']
        assert 'E-Mail-Existenz prüfen' in data['endpoints']['GET /check-email/<email>']