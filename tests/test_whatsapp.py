"""
Unit tests for WhatsApp Business API
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


class TestWhatsAppAPI:
    """Test WhatsApp Business endpoints"""
    
    def test_send_whatsapp_message_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful WhatsApp message sending"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/whatsapp/send",
                json={
                    "to_phone_number": "+1234567890",
                    "message_type": "text",
                    "text_content": "Hello, this is a test message"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["to_phone_number"] == "+1234567890"
            assert data["message_type"] == "text"
            assert data["text_content"] == "Hello, this is a test message"
            assert "whatsapp_message_id" in data
            assert "status" in data
    
    def test_send_whatsapp_message_different_types(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test sending different types of WhatsApp messages"""
        message_types = [
            {"message_type": "text", "text_content": "Text message"},
            {"message_type": "image", "media_url": "https://example.com/image.jpg", "media_caption": "Image caption"},
            {"message_type": "document", "media_url": "https://example.com/doc.pdf", "media_caption": "Document caption"},
            {"message_type": "template", "template_name": "welcome_template", "template_params": {"name": "John"}}
        ]
        
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            for msg_data in message_types:
                response = client.post(
                    "/api/v1/whatsapp/send",
                    json={
                        "to_phone_number": "+1234567890",
                        **msg_data
                    }
                )
                
                assert response.status_code == 201
                data = response.json()
                assert data["message_type"] == msg_data["message_type"]
    
    def test_send_whatsapp_message_no_business_account(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test sending message when no business account exists"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            # Mock no business account found
            with patch("app.api.v1.whatsapp.db.query") as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None
                
                response = client.post(
                    "/api/v1/whatsapp/send",
                    json={
                        "to_phone_number": "+1234567890",
                        "message_type": "text",
                        "text_content": "Hello"
                    }
                )
                
                assert response.status_code == 404
    
    def test_list_whatsapp_messages(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing WhatsApp messages"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/whatsapp/messages")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_list_whatsapp_messages_with_filters(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing WhatsApp messages with filters"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/whatsapp/messages",
                params={
                    "to_phone_number": "+1234567890",
                    "message_type": "text",
                    "status": "sent",
                    "skip": 0,
                    "limit": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_whatsapp_message_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting a specific WhatsApp message"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/whatsapp/messages/1")
            
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "to_phone_number" in data
            assert "message_type" in data
    
    def test_get_whatsapp_message_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting non-existent WhatsApp message"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/whatsapp/messages/999")
            
            assert response.status_code == 404
    
    def test_list_whatsapp_templates(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing WhatsApp templates"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/whatsapp/templates")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_list_whatsapp_templates_with_filters(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing WhatsApp templates with filters"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/whatsapp/templates",
                params={
                    "category": "AUTHENTICATION",
                    "language": "en",
                    "status": "approved"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_whatsapp_template_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful WhatsApp template creation"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/whatsapp/templates",
                json={
                    "name": "welcome_template",
                    "category": "AUTHENTICATION",
                    "language": "en",
                    "header": {"type": "TEXT", "text": "Welcome!"},
                    "body": {"type": "TEXT", "text": "Hello {{name}}, welcome to our service!"},
                    "footer": {"type": "TEXT", "text": "Thank you"}
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "welcome_template"
            assert data["category"] == "AUTHENTICATION"
            assert data["language"] == "en"
    
    def test_create_whatsapp_template_no_business_account(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test creating template when no business account exists"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            # Mock no business account found
            with patch("app.api.v1.whatsapp.db.query") as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None
                
                response = client.post(
                    "/api/v1/whatsapp/templates",
                    json={
                        "name": "welcome_template",
                        "category": "AUTHENTICATION",
                        "language": "en",
                        "body": {"type": "TEXT", "text": "Hello!"}
                    }
                )
                
                assert response.status_code == 404
    
    def test_list_whatsapp_contacts(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing WhatsApp contacts"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/whatsapp/contacts")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_list_whatsapp_contacts_with_filters(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing WhatsApp contacts with filters"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/whatsapp/contacts",
                params={
                    "is_blocked": False,
                    "is_opted_in": True,
                    "skip": 0,
                    "limit": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_block_whatsapp_contact_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test blocking WhatsApp contact"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post("/api/v1/whatsapp/contacts/1/block")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_block_whatsapp_contact_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test blocking non-existent WhatsApp contact"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post("/api/v1/whatsapp/contacts/999/block")
            
            assert response.status_code == 404
    
    def test_unblock_whatsapp_contact_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test unblocking WhatsApp contact"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post("/api/v1/whatsapp/contacts/1/unblock")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_list_whatsapp_business_accounts(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing WhatsApp business accounts"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/whatsapp/business-accounts")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_whatsapp_business_account_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful WhatsApp business account creation"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/whatsapp/business-accounts",
                json={
                    "whatsapp_business_account_id": "123456789",
                    "business_name": "Test Business",
                    "phone_number_id": "987654321",
                    "phone_number": "+1234567890",
                    "access_token": "test_token",
                    "verify_token": "test_verify_token",
                    "webhook_url": "https://example.com/webhook"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["whatsapp_business_account_id"] == "123456789"
            assert data["business_name"] == "Test Business"
            assert data["is_active"] == True
    
    def test_whatsapp_webhook_verification(self, client: TestClient):
        """Test WhatsApp webhook verification"""
        response = client.get(
            "/api/v1/whatsapp/webhooks",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_verify_token",
                "hub.challenge": "test_challenge"
            }
        )
        
        assert response.status_code == 200
        assert response.text == "test_challenge"
    
    def test_whatsapp_webhook_verification_failed(self, client: TestClient):
        """Test WhatsApp webhook verification with wrong token"""
        response = client.get(
            "/api/v1/whatsapp/webhooks",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token",
                "hub.challenge": "test_challenge"
            }
        )
        
        assert response.status_code == 403
    
    def test_whatsapp_webhook_event_processing(self, client: TestClient):
        """Test WhatsApp webhook event processing"""
        webhook_data = {
            "entry": [{
                "changes": [{
                    "field": "messages",
                    "value": {
                        "messages": [{
                            "from": "+1234567890",
                            "id": "msg_123",
                            "type": "text",
                            "text": {"body": "Hello"}
                        }]
                    }
                }]
            }]
        }
        
        response = client.post(
            "/api/v1/whatsapp/webhooks",
            json=webhook_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_list_whatsapp_webhook_events(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing WhatsApp webhook events"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/whatsapp/webhook-events")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to WhatsApp endpoints"""
        endpoints = [
            ("/api/v1/whatsapp/send", "POST"),
            ("/api/v1/whatsapp/messages", "GET"),
            ("/api/v1/whatsapp/templates", "GET"),
            ("/api/v1/whatsapp/contacts", "GET"),
            ("/api/v1/whatsapp/business-accounts", "GET"),
            ("/api/v1/whatsapp/webhook-events", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401
