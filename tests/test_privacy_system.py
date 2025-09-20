"""
Tests for Privacy System
Tests data export, deletion, and rate limiting functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import json
import os
import tempfile

from app.services.privacy_service import PrivacyService
from app.models.privacy import DataExport, DeletionRequest, ExportStatus, DeletionStatus
from app.models.entities import Organization
from app.main import app


class TestPrivacyService:
    """Test the privacy service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = Mock(spec=Session)
        return db
    
    @pytest.fixture
    def privacy_service(self, mock_db):
        """Privacy service instance"""
        return PrivacyService(mock_db)
    
    @pytest.fixture
    def sample_organization(self):
        """Sample organization for testing"""
        return Mock(
            id="org_123",
            name="Test Organization",
            slug="test-org",
            is_active=True
        )
    
    @patch('app.services.privacy_service.uuid.uuid4')
    @patch('app.workers.tasks.privacy.export_organization_data')
    def test_create_data_export_success(self, mock_celery_task, mock_uuid, privacy_service, mock_db):
        """Test successful data export creation"""
        # Mock UUID generation
        mock_uuid.return_value = "export_123"
        
        # Mock Celery task
        mock_celery_task.delay.return_value = Mock(id="job_123")
        
        # Mock database operations
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        result = privacy_service.create_data_export(
            org_id="org_123",
            user_id="user_456",
            format_type="json"
        )
        
        assert result["export_id"] == "export_123"
        assert result["job_id"] == "job_123"
        assert result["status"] == "pending"
        assert result["format_type"] == "json"
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()
    
    def test_get_export_status_success(self, privacy_service, mock_db):
        """Test successful export status retrieval"""
        # Mock export record
        export_record = Mock()
        export_record.id = "export_123"
        export_record.status = ExportStatus.COMPLETED
        export_record.format_type = "json"
        export_record.created_at = datetime.utcnow()
        export_record.expires_at = datetime.utcnow() + timedelta(days=7)
        export_record.file_path = "/tmp/exports/export_123.json"
        export_record.file_size = 1024
        export_record.error_message = None
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = export_record
        mock_db.query.return_value = mock_query
        
        result = privacy_service.get_export_status("export_123", "org_123")
        
        assert result["export_id"] == "export_123"
        assert result["status"] == "completed"
        assert result["format_type"] == "json"
        assert "download_url" in result
        assert result["file_size"] == 1024
    
    def test_get_export_status_not_found(self, privacy_service, mock_db):
        """Test export status retrieval when export not found"""
        # Mock database query returning None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with pytest.raises(Exception) as exc_info:
            privacy_service.get_export_status("nonexistent", "org_123")
        
        assert "Export not found" in str(exc_info.value)
    
    @patch('app.services.privacy_service.uuid.uuid4')
    @patch('app.workers.tasks.privacy.process_deletion_request')
    def test_create_deletion_request_success(self, mock_celery_task, mock_uuid, privacy_service, mock_db):
        """Test successful deletion request creation"""
        # Mock UUID generation
        mock_uuid.return_value = "deletion_123"
        
        # Mock Celery task
        mock_celery_task.delay.return_value = Mock(id="job_456")
        
        # Mock database operations
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None  # No existing request
        mock_db.query.return_value = mock_query
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        result = privacy_service.create_deletion_request(
            org_id="org_123",
            user_id="user_456",
            reason="Test deletion"
        )
        
        assert result["deletion_id"] == "deletion_123"
        assert result["job_id"] == "job_456"
        assert result["status"] == "pending"
        assert result["reason"] == "Test deletion"
        assert result["grace_period_hours"] == 24
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()
    
    def test_create_deletion_request_already_exists(self, privacy_service, mock_db):
        """Test deletion request creation when one already exists"""
        # Mock existing deletion request
        existing_request = Mock()
        existing_request.status = DeletionStatus.PENDING
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = existing_request
        mock_db.query.return_value = mock_query
        
        with pytest.raises(Exception) as exc_info:
            privacy_service.create_deletion_request(
                org_id="org_123",
                user_id="user_456",
                reason="Test deletion"
            )
        
        assert "Deletion request already exists" in str(exc_info.value)
    
    def test_get_deletion_status_success(self, privacy_service, mock_db):
        """Test successful deletion status retrieval"""
        # Mock deletion request
        deletion_request = Mock()
        deletion_request.id = "deletion_123"
        deletion_request.status = DeletionStatus.PENDING
        deletion_request.reason = "Test deletion"
        deletion_request.created_at = datetime.utcnow()
        deletion_request.scheduled_for = datetime.utcnow() + timedelta(hours=24)
        deletion_request.completed_at = None
        deletion_request.error_message = None
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = deletion_request
        mock_db.query.return_value = mock_query
        
        result = privacy_service.get_deletion_status("deletion_123", "org_123")
        
        assert result["deletion_id"] == "deletion_123"
        assert result["status"] == "pending"
        assert result["reason"] == "Test deletion"
    
    def test_cancel_deletion_request_success(self, privacy_service, mock_db):
        """Test successful deletion request cancellation"""
        # Mock deletion request
        deletion_request = Mock()
        deletion_request.status = DeletionStatus.PENDING
        deletion_request.celery_job_id = "job_123"
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = deletion_request
        mock_db.query.return_value = mock_query
        mock_db.commit = Mock()
        
        result = privacy_service.cancel_deletion_request(
            deletion_id="deletion_123",
            org_id="org_123",
            user_id="user_456"
        )
        
        assert result["deletion_id"] == "deletion_123"
        assert result["status"] == "canceled"
        assert deletion_request.status == DeletionStatus.CANCELED
        assert deletion_request.canceled_by == "user_456"
        
        # Verify database commit
        mock_db.commit.assert_called()
    
    def test_get_organization_data_summary(self, privacy_service, mock_db, sample_organization):
        """Test organization data summary retrieval"""
        # Mock organization
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_organization
        mock_db.query.return_value = mock_query
        
        # Mock count queries
        def mock_count_side_effect(model):
            counts = {
                "UserAccount": 5,
                "Channel": 3,
                "ExternalReference": 10,
                "AnalyticsEvent": 100,
                "Subscription": 1,
                "Invoice": 2
            }
            return counts.get(model.__name__, 0)
        
        mock_db.query.side_effect = mock_count_side_effect
        
        result = privacy_service.get_organization_data_summary("org_123")
        
        assert result["organization_id"] == "org_123"
        assert result["organization_name"] == "Test Organization"
        assert result["data_summary"]["users"] == 5
        assert result["data_summary"]["posts"] == 10
        assert result["data_summary"]["analytics_events"] == 100


class TestPrivacyAPI:
    """Test privacy API endpoints"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Mock current user"""
        return {
            "org_id": "org_123",
            "user_id": "user_456",
            "email": "test@example.com"
        }
    
    @patch('app.api.v1.privacy_enhanced.PrivacyService')
    def test_create_data_export_endpoint(self, mock_privacy_service, client, mock_user):
        """Test data export creation endpoint"""
        # Mock the privacy service
        mock_service_instance = Mock()
        mock_service_instance.create_data_export.return_value = {
            "export_id": "export_123",
            "job_id": "job_123",
            "status": "pending",
            "format_type": "json",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        mock_privacy_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.privacy_enhanced.get_current_user', return_value=mock_user):
            response = client.post(
                "/api/v1/privacy/export",
                json={"format_type": "json"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["export_id"] == "export_123"
        assert data["format_type"] == "json"
    
    @patch('app.api.v1.privacy_enhanced.PrivacyService')
    def test_get_export_status_endpoint(self, mock_privacy_service, client, mock_user):
        """Test export status endpoint"""
        # Mock the privacy service
        mock_service_instance = Mock()
        mock_service_instance.get_export_status.return_value = {
            "export_id": "export_123",
            "status": "completed",
            "format_type": "json",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "download_url": "/api/v1/privacy/export/export_123/download",
            "file_size": 1024
        }
        mock_privacy_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.privacy_enhanced.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/privacy/export/export_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["export_id"] == "export_123"
        assert data["status"] == "completed"
        assert "download_url" in data
    
    @patch('app.api.v1.privacy_enhanced.PrivacyService')
    def test_create_deletion_request_endpoint(self, mock_privacy_service, client, mock_user):
        """Test deletion request creation endpoint"""
        # Mock the privacy service
        mock_service_instance = Mock()
        mock_service_instance.create_deletion_request.return_value = {
            "deletion_id": "deletion_123",
            "job_id": "job_456",
            "status": "pending",
            "reason": "Test deletion",
            "scheduled_for": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "grace_period_hours": 24
        }
        mock_privacy_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.privacy_enhanced.get_current_user', return_value=mock_user):
            response = client.post(
                "/api/v1/privacy/delete",
                json={"reason": "Test deletion"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["deletion_id"] == "deletion_123"
        assert data["reason"] == "Test deletion"
    
    @patch('app.api.v1.privacy_enhanced.PrivacyService')
    def test_get_data_summary_endpoint(self, mock_privacy_service, client, mock_user):
        """Test data summary endpoint"""
        # Mock the privacy service
        mock_service_instance = Mock()
        mock_service_instance.get_organization_data_summary.return_value = {
            "organization_id": "org_123",
            "organization_name": "Test Organization",
            "data_summary": {
                "users": 5,
                "channels": 3,
                "posts": 10,
                "analytics_events": 100,
                "subscriptions": 1,
                "invoices": 2
            },
            "oldest_data": datetime.utcnow().isoformat(),
            "data_retention_policy": "7 years for financial records",
            "last_export": None,
            "last_deletion_request": None
        }
        mock_privacy_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.privacy_enhanced.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/privacy/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["organization_id"] == "org_123"
        assert data["data_summary"]["users"] == 5


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        return Mock()
    
    def test_rate_limiter_allowed(self, mock_redis):
        """Test rate limiter when request is allowed"""
        from app.middleware.rate_limiting import RateLimiter
        
        # Mock Redis eval to return allowed
        mock_redis.eval.return_value = [True, 5, 0]  # allowed, remaining, retry_after
        
        rate_limiter = RateLimiter(mock_redis)
        result = rate_limiter.is_allowed("test_key", 10, 60)
        
        assert result["allowed"] is True
        assert result["remaining"] == 5
        assert result["retry_after"] == 0
    
    def test_rate_limiter_denied(self, mock_redis):
        """Test rate limiter when request is denied"""
        from app.middleware.rate_limiting import RateLimiter
        
        # Mock Redis eval to return denied
        mock_redis.eval.return_value = [False, 0, 30]  # allowed, remaining, retry_after
        
        rate_limiter = RateLimiter(mock_redis)
        result = rate_limiter.is_allowed("test_key", 10, 60)
        
        assert result["allowed"] is False
        assert result["remaining"] == 0
        assert result["retry_after"] == 30
    
    def test_rate_limiter_redis_error(self, mock_redis):
        """Test rate limiter when Redis is unavailable"""
        from app.middleware.rate_limiting import RateLimiter
        
        # Mock Redis error
        mock_redis.eval.side_effect = Exception("Redis connection failed")
        
        rate_limiter = RateLimiter(mock_redis)
        result = rate_limiter.is_allowed("test_key", 10, 60)
        
        # Should allow request when Redis is down
        assert result["allowed"] is True
        assert "error" in result
    
    def test_get_rate_limit_key(self):
        """Test rate limit key generation"""
        from app.middleware.rate_limiting import get_rate_limit_key
        from unittest.mock import Mock
        
        # Mock request
        request = Mock()
        request.client.host = "192.168.1.1"
        
        # Test with org_id
        key = get_rate_limit_key(request, user_id="user_123", org_id="org_456")
        assert key == "rate_limit:org:org_456"
        
        # Test with user_id only
        key = get_rate_limit_key(request, user_id="user_123")
        assert key == "rate_limit:user:user_123"
        
        # Test with IP only
        key = get_rate_limit_key(request)
        assert key == "rate_limit:ip:192.168.1.1"
    
    def test_get_rate_limit_config(self):
        """Test rate limit configuration"""
        from app.middleware.rate_limiting import get_rate_limit_config
        from unittest.mock import Mock
        
        # Test AI endpoint
        request = Mock()
        request.url.path = "/api/v1/ai/generate"
        request.method = "POST"
        
        config = get_rate_limit_config(request)
        assert config["limit"] == 50
        assert config["window_seconds"] == 60
        
        # Test billing endpoint
        request.url.path = "/api/v1/billing/checkout-session"
        config = get_rate_limit_config(request)
        assert config["limit"] == 20
        
        # Test privacy endpoint
        request.url.path = "/api/v1/privacy/export"
        config = get_rate_limit_config(request)
        assert config["limit"] == 10
        
        # Test webhook endpoint
        request.url.path = "/webhooks/stripe"
        config = get_rate_limit_config(request)
        assert config["limit"] == 1000


class TestPrivacyIntegration:
    """Integration tests for privacy system"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Mock current user"""
        return {
            "org_id": "org_123",
            "user_id": "user_456",
            "email": "test@example.com"
        }
    
    @patch('app.api.v1.privacy_enhanced.PrivacyService')
    def test_privacy_workflow_integration(self, mock_privacy_service, client, mock_user):
        """Test complete privacy workflow"""
        # Mock privacy service
        mock_service_instance = Mock()
        mock_privacy_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.privacy_enhanced.get_current_user', return_value=mock_user):
            # Test data summary
            mock_service_instance.get_organization_data_summary.return_value = {
                "organization_id": "org_123",
                "organization_name": "Test Organization",
                "data_summary": {"users": 5, "posts": 10},
                "data_retention_policy": "7 years"
            }
            
            response = client.get("/api/v1/privacy/summary")
            assert response.status_code == 200
            
            # Test export creation
            mock_service_instance.create_data_export.return_value = {
                "export_id": "export_123",
                "job_id": "job_123",
                "status": "pending",
                "format_type": "json",
                "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }
            
            response = client.post(
                "/api/v1/privacy/export",
                json={"format_type": "json"}
            )
            assert response.status_code == 200
            
            # Test deletion request
            mock_service_instance.create_deletion_request.return_value = {
                "deletion_id": "deletion_123",
                "job_id": "job_456",
                "status": "pending",
                "reason": "Test deletion",
                "scheduled_for": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "grace_period_hours": 24
            }
            
            response = client.post(
                "/api/v1/privacy/delete",
                json={"reason": "Test deletion"}
            )
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])
