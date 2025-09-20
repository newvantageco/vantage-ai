"""
Unit tests for Billing API
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


class TestBillingAPI:
    """Test Billing endpoints"""
    
    def test_create_checkout_session_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful checkout session creation"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/billing/checkout-session",
                json={
                    "price_id": "price_test_123",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert "url" in data
            assert "expires_at" in data
    
    def test_create_portal_link_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful portal link creation"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/billing/portal-link",
                json={
                    "return_url": "https://example.com/return"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "url" in data
            assert "expires_at" in data
    
    def test_get_subscription_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting subscription details"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/billing/subscription")
            
            assert response.status_code == 200
            data = response.json()
            assert "organization_id" in data
            assert "plan" in data
            assert "status" in data
            assert "amount" in data
            assert "currency" in data
    
    def test_get_subscription_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting subscription when none exists"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            # Mock no subscription found
            with patch("app.api.v1.billing.db.query") as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None
                
                response = client.get("/api/v1/billing/subscription")
                
                assert response.status_code == 404
    
    def test_list_invoices(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing invoices"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/billing/invoices")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_invoice_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting a specific invoice"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/billing/invoices/1")
            
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "organization_id" in data
            assert "amount_due" in data
            assert "currency" in data
    
    def test_get_invoice_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting non-existent invoice"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/billing/invoices/999")
            
            assert response.status_code == 404
    
    def test_list_payment_methods(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing payment methods"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/billing/payment-methods")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_set_default_payment_method_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test setting default payment method"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post("/api/v1/billing/payment-methods/1/set-default")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_set_default_payment_method_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test setting default payment method that doesn't exist"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post("/api/v1/billing/payment-methods/999/set-default")
            
            assert response.status_code == 404
    
    def test_delete_payment_method_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test deleting payment method"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.delete("/api/v1/billing/payment-methods/1")
            
            assert response.status_code == 204
    
    def test_delete_payment_method_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test deleting non-existent payment method"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.delete("/api/v1/billing/payment-methods/999")
            
            assert response.status_code == 404
    
    def test_get_usage_records(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting usage records"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/billing/usage")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_current_usage(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting current usage"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/billing/current-usage")
            
            assert response.status_code == 200
            data = response.json()
            assert "period_start" in data
            assert "period_end" in data
            assert "posts_used" in data
            assert "posts_limit" in data
            assert "ai_requests_used" in data
            assert "ai_requests_limit" in data
    
    def test_get_available_plans(self, client: TestClient):
        """Test getting available plans (no auth required)"""
        response = client.get("/api/v1/billing/plans")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # Starter, Growth, Pro
        
        # Check plan structure
        for plan in data:
            assert "id" in plan
            assert "name" in plan
            assert "price" in plan
            assert "currency" in plan
            assert "interval" in plan
            assert "features" in plan
            assert "limits" in plan
    
    def test_stripe_webhook_success(self, client: TestClient):
        """Test Stripe webhook processing"""
        with patch("app.api.v1.billing.stripe.Webhook.construct_event") as mock_webhook:
            mock_webhook.return_value = {
                "id": "evt_test_123",
                "type": "customer.subscription.created",
                "data": {
                    "object": {
                        "id": "sub_test_123",
                        "customer": "cus_test_123",
                        "status": "active"
                    }
                }
            }
            
            response = client.post(
                "/api/v1/billing/webhooks/stripe",
                headers={"stripe-signature": "test_signature"},
                json={"test": "data"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "event_id" in data
    
    def test_stripe_webhook_invalid_signature(self, client: TestClient):
        """Test Stripe webhook with invalid signature"""
        response = client.post(
            "/api/v1/billing/webhooks/stripe",
            json={"test": "data"}
        )
        
        assert response.status_code == 400
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to billing endpoints"""
        endpoints = [
            ("/api/v1/billing/checkout-session", "POST"),
            ("/api/v1/billing/portal-link", "POST"),
            ("/api/v1/billing/subscription", "GET"),
            ("/api/v1/billing/invoices", "GET"),
            ("/api/v1/billing/payment-methods", "GET"),
            ("/api/v1/billing/usage", "GET"),
            ("/api/v1/billing/current-usage", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401
