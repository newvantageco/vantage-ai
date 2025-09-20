"""
Tests for Billing Service
Tests Stripe integration, subscription management, and billing operations
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import stripe

from app.services.billing_service import BillingService
from app.models.billing import Plan, Subscription, SubscriptionStatus, BillingEvent
from app.models.entities import Organization
from app.main import app


class TestBillingService:
    """Test the billing service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = Mock(spec=Session)
        return db
    
    @pytest.fixture
    def billing_service(self, mock_db):
        """Billing service instance"""
        return BillingService(mock_db)
    
    @pytest.fixture
    def sample_organization(self):
        """Sample organization for testing"""
        return Mock(
            id=1,
            name="Test Organization",
            slug="test-org",
            stripe_customer_id="cus_test123"
        )
    
    @pytest.fixture
    def sample_plan(self):
        """Sample plan for testing"""
        return Mock(
            id=1,
            name="growth",
            display_name="Growth Plan",
            description="Perfect for growing businesses",
            price=2900,  # $29.00
            currency="USD",
            billing_interval="month",
            stripe_price_id="price_test123",
            features=["AI Content Generation", "Analytics", "Team Collaboration"],
            ai_request_limit=1000,
            ai_token_limit=100000,
            content_post_limit=100
        )
    
    @pytest.fixture
    def sample_subscription(self):
        """Sample subscription for testing"""
        return Mock(
            id=1,
            organization_id=1,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            plan_id=1,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
    
    def test_get_organization_subscription_success(self, billing_service, mock_db, sample_subscription):
        """Test successful subscription retrieval"""
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_subscription
        mock_db.query.return_value = mock_query
        
        result = billing_service.get_organization_subscription(org_id=1)
        
        assert result == sample_subscription
        mock_db.query.assert_called_once_with(Subscription)
    
    def test_get_organization_subscription_not_found(self, billing_service, mock_db):
        """Test subscription retrieval when not found"""
        # Mock database query returning None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = billing_service.get_organization_subscription(org_id=1)
        
        assert result is None
    
    def test_get_organization_plan_success(self, billing_service, mock_db, sample_subscription, sample_plan):
        """Test successful plan retrieval"""
        # Mock subscription query
        mock_sub_query = Mock()
        mock_sub_query.filter.return_value.first.return_value = sample_subscription
        mock_db.query.return_value = mock_sub_query
        
        # Mock plan relationship
        sample_subscription.plan = sample_plan
        
        result = billing_service.get_organization_plan(org_id=1)
        
        assert result == sample_plan
    
    def test_get_organization_plan_no_subscription(self, billing_service, mock_db):
        """Test plan retrieval when no subscription exists"""
        # Mock subscription query returning None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = billing_service.get_organization_plan(org_id=1)
        
        assert result is None
    
    @patch('app.services.billing_service.stripe.checkout.Session.create')
    @patch('app.services.billing_service.BillingService._get_or_create_stripe_customer')
    def test_create_checkout_session_success(
        self, 
        mock_get_customer, 
        mock_stripe_create, 
        billing_service, 
        mock_db, 
        sample_organization, 
        sample_plan
    ):
        """Test successful checkout session creation"""
        # Mock database queries
        mock_org_query = Mock()
        mock_org_query.filter.return_value.first.return_value = sample_organization
        mock_plan_query = Mock()
        mock_plan_query.filter.return_value.first.return_value = sample_plan
        
        def mock_query_side_effect(model):
            if model == Organization:
                return mock_org_query
            elif model == Plan:
                return mock_plan_query
            return Mock()
        
        mock_db.query.side_effect = mock_query_side_effect
        
        # Mock Stripe customer creation
        mock_get_customer.return_value = "cus_test123"
        
        # Mock Stripe checkout session creation
        mock_stripe_create.return_value = Mock(
            url="https://checkout.stripe.com/test123",
            id="cs_test123"
        )
        
        result = billing_service.create_checkout_session(
            org_id=1,
            plan_type="growth",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        
        assert "checkout_url" in result
        assert "session_id" in result
        assert result["plan"] == "growth"
        assert result["amount"] == 2900
        
        # Verify Stripe was called correctly
        mock_stripe_create.assert_called_once()
        call_args = mock_stripe_create.call_args
        assert call_args[1]["customer"] == "cus_test123"
        assert call_args[1]["line_items"][0]["price"] == "price_test123"
    
    @patch('app.services.billing_service.stripe.billing_portal.Session.create')
    def test_create_portal_session_success(
        self, 
        mock_stripe_create, 
        billing_service, 
        mock_db, 
        sample_organization
    ):
        """Test successful portal session creation"""
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_organization
        mock_db.query.return_value = mock_query
        
        # Mock Stripe portal session creation
        mock_stripe_create.return_value = Mock(
            url="https://billing.stripe.com/test123",
            id="bps_test123"
        )
        
        result = billing_service.create_portal_session(
            org_id=1,
            return_url="https://example.com/billing"
        )
        
        assert "portal_url" in result
        assert "session_id" in result
        assert result["portal_url"] == "https://billing.stripe.com/test123"
        
        # Verify Stripe was called correctly
        mock_stripe_create.assert_called_once()
        call_args = mock_stripe_create.call_args
        assert call_args[1]["customer"] == "cus_test123"
        assert call_args[1]["return_url"] == "https://example.com/billing"
    
    def test_handle_webhook_event_checkout_completed(self, billing_service, mock_db):
        """Test handling checkout completed webhook event"""
        event_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "customer": "cus_test123",
                    "metadata": {
                        "organization_id": "1",
                        "plan_type": "growth"
                    }
                }
            }
        }
        
        # Mock database queries
        mock_org_query = Mock()
        mock_org_query.filter.return_value.first.return_value = Mock(id=1, stripe_customer_id=None)
        mock_plan_query = Mock()
        mock_plan_query.filter.return_value.first.return_value = Mock(id=1)
        
        def mock_query_side_effect(model):
            if model == Organization:
                return mock_org_query
            elif model == Plan:
                return mock_plan_query
            return Mock()
        
        mock_db.query.side_effect = mock_query_side_effect
        
        result = billing_service.handle_webhook_event(event_data)
        
        assert result["status"] == "processed"
        assert result["event_type"] == "checkout.session.completed"
    
    def test_handle_webhook_event_subscription_created(self, billing_service, mock_db):
        """Test handling subscription created webhook event"""
        event_data = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "metadata": {
                        "organization_id": "1",
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
        
        # Mock database queries
        mock_org_query = Mock()
        mock_org_query.filter.return_value.first.return_value = Mock(id=1)
        mock_plan_query = Mock()
        mock_plan_query.filter.return_value.first.return_value = Mock(id=1)
        
        def mock_query_side_effect(model):
            if model == Organization:
                return mock_org_query
            elif model == Plan:
                return mock_plan_query
            return Mock()
        
        mock_db.query.side_effect = mock_query_side_effect
        
        result = billing_service.handle_webhook_event(event_data)
        
        assert result["status"] == "processed"
        assert result["event_type"] == "customer.subscription.created"
    
    def test_handle_webhook_event_subscription_updated(self, billing_service, mock_db, sample_subscription):
        """Test handling subscription updated webhook event"""
        event_data = {
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
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_subscription
        mock_db.query.return_value = mock_query
        
        result = billing_service.handle_webhook_event(event_data)
        
        assert result["status"] == "processed"
        assert result["event_type"] == "customer.subscription.updated"
    
    def test_handle_webhook_event_subscription_deleted(self, billing_service, mock_db, sample_subscription):
        """Test handling subscription deleted webhook event"""
        event_data = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test123"
                }
            }
        }
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_subscription
        mock_db.query.return_value = mock_query
        
        result = billing_service.handle_webhook_event(event_data)
        
        assert result["status"] == "processed"
        assert result["event_type"] == "customer.subscription.deleted"
    
    def test_handle_webhook_event_payment_succeeded(self, billing_service, mock_db):
        """Test handling payment succeeded webhook event"""
        event_data = {
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
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = Mock(id=1)
        mock_db.query.return_value = mock_query
        
        result = billing_service.handle_webhook_event(event_data)
        
        assert result["status"] == "processed"
        assert result["event_type"] == "invoice.payment_succeeded"
    
    def test_handle_webhook_event_unknown_type(self, billing_service, mock_db):
        """Test handling unknown webhook event type"""
        event_data = {
            "type": "unknown.event.type",
            "data": {
                "object": {}
            }
        }
        
        result = billing_service.handle_webhook_event(event_data)
        
        assert result["status"] == "ignored"
        assert result["event_type"] == "unknown.event.type"
    
    def test_get_organization_usage(self, billing_service, mock_db, sample_subscription, sample_plan):
        """Test getting organization usage"""
        # Mock subscription query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_subscription
        mock_db.query.return_value = mock_query
        
        # Mock plan relationship
        sample_subscription.plan = sample_plan
        
        result = billing_service.get_organization_usage(org_id=1)
        
        assert "month" in result
        assert "ai_requests" in result
        assert "ai_tokens" in result
        assert "content_posts" in result
        assert "plan_limits" in result
        assert "usage_percentage" in result
    
    def test_get_organization_usage_no_subscription(self, billing_service, mock_db):
        """Test getting usage when no subscription exists"""
        # Mock subscription query returning None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = billing_service.get_organization_usage(org_id=1)
        
        assert "month" in result
        assert result["plan_limits"] == {}


class TestBillingAPI:
    """Test billing API endpoints"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Mock current user"""
        return {
            "org_id": 1,
            "user_id": 1,
            "email": "test@example.com"
        }
    
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_create_checkout_session_endpoint(self, mock_billing_service, client, mock_user):
        """Test checkout session creation endpoint"""
        # Mock the billing service
        mock_service_instance = Mock()
        mock_service_instance.create_checkout_session.return_value = {
            "checkout_url": "https://checkout.stripe.com/test123",
            "session_id": "cs_test123",
            "plan": "growth",
            "amount": 2900,
            "currency": "USD"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.billing_enhanced.get_current_user', return_value=mock_user):
            response = client.post(
                "/api/v1/billing/checkout-session",
                json={
                    "plan": "growth",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "checkout_url" in data
        assert data["plan"] == "growth"
    
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_create_portal_session_endpoint(self, mock_billing_service, client, mock_user):
        """Test portal session creation endpoint"""
        # Mock the billing service
        mock_service_instance = Mock()
        mock_service_instance.create_portal_session.return_value = {
            "portal_url": "https://billing.stripe.com/test123",
            "session_id": "bps_test123"
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.billing_enhanced.get_current_user', return_value=mock_user):
            response = client.post(
                "/api/v1/billing/portal-link",
                json={
                    "return_url": "https://example.com/billing"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "portal_url" in data
    
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_get_billing_status_endpoint(self, mock_billing_service, client, mock_user):
        """Test billing status endpoint"""
        # Mock the billing service
        mock_service_instance = Mock()
        mock_service_instance.get_organization_subscription.return_value = Mock(
            id=1,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        mock_service_instance.get_organization_plan.return_value = Mock(
            id=1,
            name="growth",
            display_name="Growth Plan",
            price=2900,
            currency="USD"
        )
        mock_service_instance.get_organization_usage.return_value = {
            "month": "2024-01",
            "ai_requests": 100,
            "ai_tokens": 10000,
            "content_posts": 10,
            "plan_limits": {
                "ai_requests": 1000,
                "ai_tokens": 100000,
                "content_posts": 100
            },
            "usage_percentage": {
                "ai_requests": 10,
                "ai_tokens": 10,
                "content_posts": 10
            }
        }
        mock_billing_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.billing_enhanced.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/billing/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "has_subscription" in data
        assert "plan" in data
        assert "usage" in data
    
    @patch('app.api.v1.billing_enhanced.stripe.Webhook.construct_event')
    @patch('app.api.v1.billing_enhanced.BillingService')
    def test_webhook_endpoint(self, mock_billing_service, mock_stripe_webhook, client):
        """Test Stripe webhook endpoint"""
        # Mock Stripe webhook verification
        mock_stripe_webhook.return_value = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123"
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
                data='{"type": "customer.subscription.created"}',
                headers={"stripe-signature": "test_signature"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
    
    def test_get_available_plans_endpoint(self, client):
        """Test available plans endpoint"""
        with patch('app.api.v1.billing_enhanced.get_db') as mock_get_db:
            mock_db = Mock()
            mock_plan = Mock()
            mock_plan.id = 1
            mock_plan.name = "growth"
            mock_plan.display_name = "Growth Plan"
            mock_plan.description = "Perfect for growing businesses"
            mock_plan.price = 2900
            mock_plan.currency = "USD"
            mock_plan.billing_interval = "month"
            mock_plan.features = ["AI Content Generation"]
            mock_plan.ai_request_limit = 1000
            mock_plan.ai_token_limit = 100000
            mock_plan.content_post_limit = 100
            mock_plan.stripe_price_id = "price_test123"
            
            mock_query = Mock()
            mock_query.filter.return_value.all.return_value = [mock_plan]
            mock_db.query.return_value = mock_query
            mock_get_db.return_value = mock_db
            
            response = client.get("/api/v1/billing/plans")
        
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 1
        assert data["plans"][0]["name"] == "growth"


if __name__ == "__main__":
    pytest.main([__file__])
