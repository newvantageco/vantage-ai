"""
Tests for Analytics Service
Tests analytics queries, data aggregation, and CSV export functionality
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import io
import csv

from app.services.analytics_service import AnalyticsService
from app.models.publishing import ExternalReference, PublishingStatus, PlatformType
from app.models.analytics import AnalyticsEvent, EventType
from app.main import app


class TestAnalyticsService:
    """Test the analytics service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = Mock(spec=Session)
        return db
    
    @pytest.fixture
    def analytics_service(self, mock_db):
        """Analytics service instance"""
        return AnalyticsService(mock_db)
    
    @pytest.fixture
    def sample_external_refs(self):
        """Sample external references for testing"""
        now = datetime.utcnow()
        return [
            Mock(
                id=1,
                organization_id=1,
                platform=PlatformType.FACEBOOK,
                external_id="fb_123",
                url="https://facebook.com/posts/123",
                status=PublishingStatus.PUBLISHED,
                created_at=now - timedelta(days=1),
                published_at=now - timedelta(days=1),
                platform_data={"clicks": 100, "impressions": 1000, "campaign_id": "campaign_1"}
            ),
            Mock(
                id=2,
                organization_id=1,
                platform=PlatformType.LINKEDIN,
                external_id="li_456",
                url="https://linkedin.com/posts/456",
                status=PublishingStatus.PUBLISHED,
                created_at=now - timedelta(days=2),
                published_at=now - timedelta(days=2),
                platform_data={"clicks": 50, "impressions": 500, "campaign_id": "campaign_1"}
            ),
            Mock(
                id=3,
                organization_id=1,
                platform=PlatformType.FACEBOOK,
                external_id="fb_789",
                url="https://facebook.com/posts/789",
                status=PublishingStatus.FAILED,
                created_at=now - timedelta(days=3),
                published_at=None,
                platform_data={"campaign_id": "campaign_2"}
            )
        ]
    
    def test_get_analytics_summary_success(self, analytics_service, mock_db, sample_external_refs):
        """Test successful analytics summary retrieval"""
        # Mock database query results
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 2  # Published posts
        mock_db.query.return_value = mock_query
        
        # Mock platform breakdown query
        mock_breakdown_query = Mock()
        mock_breakdown_query.filter.return_value.group_by.return_value.all.return_value = [
            Mock(platform=PlatformType.FACEBOOK, count=2, published_count=1),
            Mock(platform=PlatformType.LINKEDIN, count=1, published_count=1)
        ]
        
        # Mock the query method to return different results based on the model
        def mock_query_side_effect(model):
            if model == ExternalReference:
                return mock_query
            return mock_breakdown_query
        
        mock_db.query.side_effect = mock_query_side_effect
        
        # Test the method
        result = analytics_service.get_analytics_summary(org_id=1, days=30)
        
        # Verify the result structure
        assert "period" in result
        assert "metrics" in result
        assert "platform_breakdown" in result
        
        assert result["metrics"]["total_posts"] == 2
        assert result["metrics"]["success_rate"] == 100.0  # 2 published out of 2 total attempts
        assert len(result["platform_breakdown"]) == 2
    
    def test_get_analytics_summary_with_filters(self, analytics_service, mock_db):
        """Test analytics summary with platform and campaign filters"""
        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 1
        mock_db.query.return_value = mock_query
        
        # Mock platform breakdown
        mock_breakdown_query = Mock()
        mock_breakdown_query.filter.return_value.group_by.return_value.all.return_value = [
            Mock(platform=PlatformType.FACEBOOK, count=1, published_count=1)
        ]
        
        def mock_query_side_effect(model):
            if model == ExternalReference:
                return mock_query
            return mock_breakdown_query
        
        mock_db.query.side_effect = mock_query_side_effect
        
        # Test with filters
        result = analytics_service.get_analytics_summary(
            org_id=1, 
            days=30, 
            platform=PlatformType.FACEBOOK,
            campaign_id="campaign_1"
        )
        
        assert result["metrics"]["total_posts"] == 1
        assert len(result["platform_breakdown"]) == 1
        assert result["platform_breakdown"][0]["platform"] == "facebook"
    
    def test_get_timeseries_data(self, analytics_service, mock_db):
        """Test timeseries data retrieval"""
        # Mock timeseries query results
        mock_query = Mock()
        mock_results = [
            Mock(
                date=datetime.utcnow() - timedelta(days=1),
                platform=PlatformType.FACEBOOK,
                total_count=2,
                published_count=1,
                failed_count=1
            ),
            Mock(
                date=datetime.utcnow() - timedelta(days=2),
                platform=PlatformType.LINKEDIN,
                total_count=1,
                published_count=1,
                failed_count=0
            )
        ]
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_results
        mock_db.query.return_value = mock_query
        
        result = analytics_service.get_timeseries_data(org_id=1, days=30)
        
        assert len(result) == 2
        assert result[0]["platform"] == "facebook"
        assert result[0]["total_count"] == 2
        assert result[0]["success_rate"] == 50.0  # 1 published out of 2 total
    
    def test_get_platform_comparison(self, analytics_service, mock_db):
        """Test platform comparison data retrieval"""
        # Mock platform comparison query results
        mock_query = Mock()
        mock_results = [
            Mock(
                platform=PlatformType.FACEBOOK,
                total_posts=2,
                published_posts=1,
                failed_posts=1,
                success_rate=0.5
            ),
            Mock(
                platform=PlatformType.LINKEDIN,
                total_posts=1,
                published_posts=1,
                failed_posts=0,
                success_rate=1.0
            )
        ]
        mock_query.filter.return_value.group_by.return_value.all.return_value = mock_results
        mock_db.query.return_value = mock_query
        
        result = analytics_service.get_platform_comparison(org_id=1, days=30)
        
        assert len(result) == 2
        assert result[0]["platform"] == "facebook"
        assert result[0]["success_rate"] == 50.0
        assert result[1]["platform"] == "linkedin"
        assert result[1]["success_rate"] == 100.0
    
    def test_get_ctr_over_time(self, analytics_service, mock_db):
        """Test CTR over time data retrieval"""
        # Mock CTR query results
        mock_query = Mock()
        mock_results = [
            Mock(
                date=datetime.utcnow() - timedelta(days=1),
                platform=PlatformType.FACEBOOK,
                total_posts=1,
                avg_clicks=100.0,
                avg_impressions=1000.0
            )
        ]
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_results
        mock_db.query.return_value = mock_query
        
        result = analytics_service.get_ctr_over_time(org_id=1, days=30)
        
        assert len(result) == 1
        assert result[0]["platform"] == "facebook"
        assert result[0]["ctr"] == 10.0  # 100 clicks / 1000 impressions * 100
    
    def test_export_analytics_csv(self, analytics_service, mock_db, sample_external_refs):
        """Test CSV export functionality"""
        # Mock database query for CSV export
        mock_query = Mock()
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = sample_external_refs
        mock_db.query.return_value = mock_query
        
        # Test CSV export
        response = analytics_service.export_analytics_csv(
            org_id=1, 
            days=30, 
            include_metrics=True
        )
        
        # Verify it returns a StreamingResponse
        assert hasattr(response, 'body_iterator')
        assert response.media_type == "text/csv"
        assert "attachment" in response.headers["Content-Disposition"]
    
    def test_get_campaign_analytics_success(self, analytics_service, mock_db, sample_external_refs):
        """Test campaign analytics retrieval"""
        # Mock campaign query
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_external_refs[:2]  # First 2 refs
        mock_db.query.return_value = mock_query
        
        result = analytics_service.get_campaign_analytics(
            org_id=1, 
            campaign_id="campaign_1", 
            days=30
        )
        
        assert result["campaign_id"] == "campaign_1"
        assert result["metrics"]["total_posts"] == 2
        assert result["metrics"]["published_posts"] == 2
        assert result["metrics"]["success_rate"] == 100.0
        assert "facebook" in result["platform_breakdown"]
        assert "linkedin" in result["platform_breakdown"]
    
    def test_get_campaign_analytics_not_found(self, analytics_service, mock_db):
        """Test campaign analytics when campaign not found"""
        # Mock empty query result
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        mock_db.query.return_value = mock_query
        
        result = analytics_service.get_campaign_analytics(
            org_id=1, 
            campaign_id="nonexistent", 
            days=30
        )
        
        assert "error" in result
        assert "not found" in result["error"]


class TestAnalyticsAPI:
    """Test analytics API endpoints"""
    
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
    
    @patch('app.api.v1.analytics_enhanced.AnalyticsService')
    def test_analytics_summary_endpoint(self, mock_analytics_service, client, mock_user):
        """Test analytics summary endpoint"""
        # Mock the analytics service
        mock_service_instance = Mock()
        mock_service_instance.get_analytics_summary.return_value = {
            "period": {"start_date": "2024-01-01", "end_date": "2024-01-31", "days": 30},
            "metrics": {"total_posts": 10, "success_rate": 90.0},
            "platform_breakdown": []
        }
        mock_analytics_service.return_value = mock_service_instance
        
        # Mock authentication
        with patch('app.api.v1.analytics_enhanced.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/analytics/summary?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "metrics" in data
        assert data["metrics"]["total_posts"] == 10
    
    @patch('app.api.v1.analytics_enhanced.AnalyticsService')
    def test_timeseries_endpoint(self, mock_analytics_service, client, mock_user):
        """Test timeseries endpoint"""
        mock_service_instance = Mock()
        mock_service_instance.get_timeseries_data.return_value = [
            {"date": "2024-01-01", "platform": "facebook", "total_count": 5, "published_count": 4}
        ]
        mock_analytics_service.return_value = mock_service_instance
        
        with patch('app.api.v1.analytics_enhanced.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/analytics/timeseries?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
    
    @patch('app.api.v1.analytics_enhanced.AnalyticsService')
    def test_platform_comparison_endpoint(self, mock_analytics_service, client, mock_user):
        """Test platform comparison endpoint"""
        mock_service_instance = Mock()
        mock_service_instance.get_platform_comparison.return_value = [
            {"platform": "facebook", "total_posts": 5, "success_rate": 80.0}
        ]
        mock_analytics_service.return_value = mock_service_instance
        
        with patch('app.api.v1.analytics_enhanced.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/analytics/platform-comparison?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
    
    @patch('app.api.v1.analytics_enhanced.AnalyticsService')
    def test_ctr_endpoint(self, mock_analytics_service, client, mock_user):
        """Test CTR over time endpoint"""
        mock_service_instance = Mock()
        mock_service_instance.get_ctr_over_time.return_value = [
            {"date": "2024-01-01", "platform": "facebook", "ctr": 5.0}
        ]
        mock_analytics_service.return_value = mock_service_instance
        
        with patch('app.api.v1.analytics_enhanced.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/analytics/ctr-over-time?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "avg_ctr" in data
    
    @patch('app.api.v1.analytics_enhanced.AnalyticsService')
    def test_csv_export_endpoint(self, mock_analytics_service, client, mock_user):
        """Test CSV export endpoint"""
        mock_service_instance = Mock()
        mock_response = Mock()
        mock_response.media_type = "text/csv"
        mock_service_instance.export_analytics_csv.return_value = mock_response
        mock_analytics_service.return_value = mock_service_instance
        
        with patch('app.api.v1.analytics_enhanced.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/analytics/export/csv?days=30")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
    
    def test_analytics_health_endpoint(self, client, mock_user):
        """Test analytics health check endpoint"""
        with patch('app.api.v1.analytics_enhanced.get_current_user', return_value=mock_user):
            with patch('app.api.v1.analytics_enhanced.AnalyticsService') as mock_service:
                mock_service_instance = Mock()
                mock_service_instance.get_analytics_summary.return_value = {"test": "data"}
                mock_service.return_value = mock_service_instance
                
                response = client.get("/api/v1/analytics/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAnalyticsDataSeeding:
    """Test analytics data seeding for tests"""
    
    def test_seed_sample_data(self):
        """Test seeding sample analytics data"""
        # This would be used in test setup to create sample data
        sample_data = [
            {
                "organization_id": 1,
                "platform": PlatformType.FACEBOOK,
                "external_id": "test_fb_1",
                "status": PublishingStatus.PUBLISHED,
                "created_at": datetime.utcnow() - timedelta(days=1),
                "platform_data": {"clicks": 100, "impressions": 1000, "campaign_id": "test_campaign"}
            },
            {
                "organization_id": 1,
                "platform": PlatformType.LINKEDIN,
                "external_id": "test_li_1",
                "status": PublishingStatus.PUBLISHED,
                "created_at": datetime.utcnow() - timedelta(days=2),
                "platform_data": {"clicks": 50, "impressions": 500, "campaign_id": "test_campaign"}
            },
            {
                "organization_id": 1,
                "platform": PlatformType.FACEBOOK,
                "external_id": "test_fb_2",
                "status": PublishingStatus.FAILED,
                "created_at": datetime.utcnow() - timedelta(days=3),
                "platform_data": {"campaign_id": "test_campaign_2"}
            }
        ]
        
        assert len(sample_data) == 3
        assert sample_data[0]["platform"] == PlatformType.FACEBOOK
        assert sample_data[0]["status"] == PublishingStatus.PUBLISHED
        assert sample_data[2]["status"] == PublishingStatus.FAILED


if __name__ == "__main__":
    pytest.main([__file__])
