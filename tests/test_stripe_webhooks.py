"""
Tests for Stripe Webhook Integration
Tests webhook handling, signature verification, and state updates
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import json

from app.main import app
from app.models.billing import Subscription, SubscriptionStatus, Plan
from app.models.entities import Organization


class TestStripeWebhooks:
    """Test Stripe webhook integration"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_organization(self):
        """Sample organization for testing"""
        return Organization(
            id="org_123",
            name="Test Organization",
            slug="test-org",
            stripe_customer_id="cus_test123",
            is_active=True
        )
    
    @pytest.fixture
    def sample_plan(self):
        """Sample plan for testing"""
        return Plan(
            id=1,
            name="growth",
            display_name="Growth Plan",
            description="Perfect for growing businesses",
            price=2900,
            currency="USD",
            billing_interval="month",
            stripe_price_id="price_growth_monthly",
            features=["AI Content Generation", "Analytics"],
            ai_request_limit=1000,
            ai_token_limit=100000,
            content_post_limit=100,
            is_active=True
        )
    
    @pytest.fixture
    def sample_subscription(self):
        """Sample subscription for testing"""
        return Subscription(
            id=1,
            organization_id="org_123",
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            plan_id=1,
            status=SubscriptionStatus.ACTIVE,
            amount=2900,
            currency="USD",
            interval="month",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_checkout_session_completed_webhook(
        self, 
        mock_billing_service, 
        mock_stripe_webhook, 
        client, 
        sample_organization
    ):
        """Test checkout session completed webhook"""
        # Mock Stripe webhook verification
        mock_stripe_webhook.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "customer": "cus_test123",
                    "metadata": {
                        "organization_id": "org_123",
                        "plan_type": "growth"
                    }
                }
            }
        }
        
        # Mock billing service
        mock_service_instance = Mock()
        mock_service_instance.handle_webhook_event.return_value = {
            "status": "processed",
            "event_type": "checkout.session.completed"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock environment variables
        with patch('app.api.v1.billing_enhanced.get_settings') as mock_settings:
            mock_settings.return_value.stripe_webhook_secret = "whsec_test123"
            
            response = client.post(
                "/api/v1/billing/webhook",
                data=json.dumps({
                    "type": "checkout.session.completed",
                    "data": {
                        "object": {
                            "id": "cs_test123",
                            "customer": "cus_test123",
                            "metadata": {
                                "organization_id": "org_123",
                                "plan_type": "growth"
                            }
                        }
                    }
                }),
                headers={"stripe-signature": "test_signature"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["event_type"] == "checkout.session.completed"
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_subscription_created_webhook(
        self, 
        mock_billing_service, 
        mock_stripe_webhook, 
        client
    ):
        """Test subscription created webhook"""
        # Mock Stripe webhook verification
        mock_stripe_webhook.return_value = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "metadata": {
                        "organization_id": "org_123",
                        "plan_type": "growth"
                    },
                    "current_period_start": 1640995200,  # 2022-01-01
                    "current_period_end": 1643673600,    # 2022-02-01
                    "items": {
                        "data": [{
                            "price": {
                                "unit_amount": 2900
                            }
                        }]
                    }
                }
            }
        }
        
        # Mock billing service
        mock_service_instance = Mock()
        mock_service_instance.handle_webhook_event.return_value = {
            "status": "processed",
            "event_type": "customer.subscription.created"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock environment variables
        with patch('app.api.v1.billing_enhanced.get_settings') as mock_settings:
            mock_settings.return_value.stripe_webhook_secret = "whsec_test123"
            
            response = client.post(
                "/api/v1/billing/webhook",
                data=json.dumps({
                    "type": "customer.subscription.created",
                    "data": {
                        "object": {
                            "id": "sub_test123",
                            "customer": "cus_test123",
                            "metadata": {
                                "organization_id": "org_123",
                                "plan_type": "growth"
                            }
                        }
                    }
                }),
                headers={"stripe-signature": "test_signature"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["event_type"] == "customer.subscription.created"
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_subscription_updated_webhook(
        self, 
        mock_billing_service, 
        mock_stripe_webhook, 
        client
    ):
        """Test subscription updated webhook"""
        # Mock Stripe webhook verification
        mock_stripe_webhook.return_value = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "status": "active",
                    "current_period_start": 1640995200,
                    "current_period_end": 1643673600
                }
            }
        }
        
        # Mock billing service
        mock_service_instance = Mock()
        mock_service_instance.handle_webhook_event.return_value = {
            "status": "processed",
            "event_type": "customer.subscription.updated"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock environment variables
        with patch('app.api.v1.billing_enhanced.get_settings') as mock_settings:
            mock_settings.return_value.stripe_webhook_secret = "whsec_test123"
            
            response = client.post(
                "/api/v1/billing/webhook",
                data=json.dumps({
                    "type": "customer.subscription.updated",
                    "data": {
                        "object": {
                            "id": "sub_test123",
                            "status": "active"
                        }
                    }
                }),
                headers={"stripe-signature": "test_signature"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["event_type"] == "customer.subscription.updated"
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_subscription_deleted_webhook(
        self, 
        mock_billing_service, 
        mock_stripe_webhook, 
        client
    ):
        """Test subscription deleted webhook"""
        # Mock Stripe webhook verification
        mock_stripe_webhook.return_value = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test123"
                }
            }
        }
        
        # Mock billing service
        mock_service_instance = Mock()
        mock_service_instance.handle_webhook_event.return_value = {
            "status": "processed",
            "event_type": "customer.subscription.deleted"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock environment variables
        with patch('app.api.v1.billing_enhanced.get_settings') as mock_settings:
            mock_settings.return_value.stripe_webhook_secret = "whsec_test123"
            
            response = client.post(
                "/api/v1/billing/webhook",
                data=json.dumps({
                    "type": "customer.subscription.deleted",
                    "data": {
                        "object": {
                            "id": "sub_test123"
                        }
                    }
                }),
                headers={"stripe-signature": "test_signature"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["event_type"] == "customer.subscription.deleted"
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_payment_succeeded_webhook(
        self, 
        mock_billing_service, 
        mock_stripe_webhook, 
        client
    ):
        """Test payment succeeded webhook"""
        # Mock Stripe webhook verification
        mock_stripe_webhook.return_value = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "amount_paid": 2900,
                    "currency": "usd"
                }
            }
        }
        
        # Mock billing service
        mock_service_instance = Mock()
        mock_service_instance.handle_webhook_event.return_value = {
            "status": "processed",
            "event_type": "invoice.payment_succeeded"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock environment variables
        with patch('app.api.v1.billing_enhanced.get_settings') as mock_settings:
            mock_settings.return_value.stripe_webhook_secret = "whsec_test123"
            
            response = client.post(
                "/api/v1/billing/webhook",
                data=json.dumps({
                    "type": "invoice.payment_succeeded",
                    "data": {
                        "object": {
                            "id": "in_test123",
                            "customer": "cus_test123",
                            "amount_paid": 2900
                        }
                    }
                }),
                headers={"stripe-signature": "test_signature"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["event_type"] == "invoice.payment_succeeded"
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_payment_failed_webhook(
        self, 
        mock_billing_service, 
        mock_stripe_webhook, 
        client
    ):
        """Test payment failed webhook"""
        # Mock Stripe webhook verification
        mock_stripe_webhook.return_value = {
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "amount_due": 2900,
                    "currency": "usd"
                }
            }
        }
        
        # Mock billing service
        mock_service_instance = Mock()
        mock_service_instance.handle_webhook_event.return_value = {
            "status": "processed",
            "event_type": "invoice.payment_failed"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock environment variables
        with patch('app.api.v1.billing_enhanced.get_settings') as mock_settings:
            mock_settings.return_value.stripe_webhook_secret = "whsec_test123"
            
            response = client.post(
                "/api/v1/billing/webhook",
                data=json.dumps({
                    "type": "invoice.payment_failed",
                    "data": {
                        "object": {
                            "id": "in_test123",
                            "customer": "cus_test123",
                            "amount_due": 2900
                        }
                    }
                }),
                headers={"stripe-signature": "test_signature"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["event_type"] == "invoice.payment_failed"
    
    def test_webhook_missing_signature(self, client):
        """Test webhook with missing signature header"""
        response = client.post(
            "/api/v1/billing/webhook",
            data=json.dumps({"type": "test.event"}),
            headers={}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Missing stripe-signature header" in data["detail"]
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    def test_webhook_invalid_signature(self, mock_stripe_webhook, client):
        """Test webhook with invalid signature"""
        # Mock Stripe webhook verification to raise signature error
        mock_stripe_webhook.side_effect = Exception("Invalid signature")
        
        response = client.post(
            "/api/v1/billing/webhook",
            data=json.dumps({"type": "test.event"}),
            headers={"stripe-signature": "invalid_signature"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid signature" in data["detail"]
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_webhook_unknown_event_type(
        self, 
        mock_billing_service, 
        mock_stripe_webhook, 
        client
    ):
        """Test webhook with unknown event type"""
        # Mock Stripe webhook verification
        mock_stripe_webhook.return_value = {
            "type": "unknown.event.type",
            "data": {
                "object": {}
            }
        }
        
        # Mock billing service
        mock_service_instance = Mock()
        mock_service_instance.handle_webhook_event.return_value = {
            "status": "ignored",
            "event_type": "unknown.event.type"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock environment variables
        with patch('app.api.v1.billing_enhanced.get_settings') as mock_settings:
            mock_settings.return_value.stripe_webhook_secret = "whsec_test123"
            
            response = client.post(
                "/api/v1/billing/webhook",
                data=json.dumps({
                    "type": "unknown.event.type",
                    "data": {"object": {}}
                }),
                headers={"stripe-signature": "test_signature"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
        assert data["event_type"] == "unknown.event.type"


class TestBillingStateUpdates:
    """Test billing state updates from webhooks"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    def test_subscription_status_update(self, mock_db):
        """Test subscription status update from webhook"""
        from app.services.billing_service import BillingService
        
        # Mock existing subscription
        existing_subscription = Mock()
        existing_subscription.organization_id = "org_123"
        existing_subscription.status = SubscriptionStatus.ACTIVE
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = existing_subscription
        mock_db.query.return_value = mock_query
        
        billing_service = BillingService(mock_db)
        
        # Test subscription updated event
        event_data = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "status": "past_due",
                    "current_period_start": 1640995200,
                    "current_period_end": 1643673600
                }
            }
        }
        
        result = billing_service.handle_webhook_event(event_data)
        
        assert result["status"] == "processed"
        assert result["event_type"] == "customer.subscription.updated"
        
        # Verify subscription was updated
        assert existing_subscription.status == SubscriptionStatus.PAST_DUE
    
    def test_subscription_cancellation(self, mock_db):
        """Test subscription cancellation from webhook"""
        from app.services.billing_service import BillingService
        
        # Mock existing subscription
        existing_subscription = Mock()
        existing_subscription.organization_id = "org_123"
        existing_subscription.status = SubscriptionStatus.ACTIVE
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = existing_subscription
        mock_db.query.return_value = mock_query
        
        billing_service = BillingService(mock_db)
        
        # Test subscription deleted event
        event_data = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test123"
                }
            }
        }
        
        result = billing_service.handle_webhook_event(event_data)
        
        assert result["status"] == "processed"
        assert result["event_type"] == "customer.subscription.deleted"
        
        # Verify subscription was canceled
        assert existing_subscription.status == SubscriptionStatus.CANCELED
        assert existing_subscription.canceled_at is not None


if __name__ == "__main__":
    pytest.main([__file__])
