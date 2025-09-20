"""
Integration Tests for Analytics System
Tests the complete analytics workflow with real database operations
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import json

from app.main import app
from app.db.session import SessionLocal
from app.models.publishing import ExternalReference, PublishingStatus, PlatformType
from app.models.analytics import AnalyticsEvent, EventType
from app.models.entities import Organization
from tests.seed_analytics_data import seed_analytics_data, clear_analytics_data, get_analytics_summary_stats


class TestAnalyticsIntegration:
    """Integration tests for the complete analytics system"""
    
    @pytest.fixture(scope="class")
    def db(self):
        """Database session for integration tests"""
        db = SessionLocal()
        yield db
        db.close()
    
    @pytest.fixture(scope="class")
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture(scope="class")
    def test_org(self, db):
        """Create test organization"""
        org = Organization(
            id=999,
            name="Test Analytics Org",
            slug="test-analytics-org",
            is_active=True
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        return org
    
    @pytest.fixture(scope="class")
    def seeded_data(self, db, test_org):
        """Seed test data for analytics"""
        # Clear any existing data
        clear_analytics_data(db, org_id=test_org.id)
        
        # Seed new data
        seed_analytics_data(db, org_id=test_org.id, days=30, num_posts=50)
        
        # Get summary stats
        stats = get_analytics_summary_stats(db, org_id=test_org.id)
        
        yield stats
        
        # Cleanup
        clear_analytics_data(db, org_id=test_org.id)
    
    def test_analytics_summary_endpoint_integration(self, client, seeded_data):
        """Test analytics summary endpoint with real data"""
        # Mock authentication
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            response = client.get("/api/v1/analytics/summary?days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "period" in data
        assert "metrics" in data
        assert "platform_breakdown" in data
        
        # Verify metrics match seeded data
        assert data["metrics"]["total_posts"] == seeded_data["total_posts"]
        assert data["metrics"]["published_posts"] == seeded_data["published_posts"]
        assert data["metrics"]["failed_posts"] == seeded_data["failed_posts"]
        assert abs(data["metrics"]["success_rate"] - seeded_data["success_rate"]) < 0.1
        
        # Verify platform breakdown
        assert len(data["platform_breakdown"]) > 0
        for platform in data["platform_breakdown"]:
            assert "platform" in platform
            assert "total_count" in platform
            assert "published_count" in platform
            assert "success_rate" in platform
    
    def test_timeseries_endpoint_integration(self, client, seeded_data):
        """Test timeseries endpoint with real data"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            response = client.get("/api/v1/analytics/timeseries?days=30&group_by=day")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "data" in data
        assert "group_by" in data
        assert "total_points" in data
        
        # Verify data points
        assert len(data["data"]) > 0
        for point in data["data"]:
            assert "date" in point
            assert "platform" in point
            assert "total_count" in point
            assert "published_count" in point
            assert "failed_count" in point
            assert "success_rate" in point
    
    def test_platform_comparison_endpoint_integration(self, client, seeded_data):
        """Test platform comparison endpoint with real data"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            response = client.get("/api/v1/analytics/platform-comparison?days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "data" in data
        assert "total_platforms" in data
        
        # Verify platform data
        assert len(data["data"]) > 0
        for platform in data["data"]:
            assert "platform" in platform
            assert "total_posts" in platform
            assert "published_posts" in platform
            assert "failed_posts" in platform
            assert "success_rate" in platform
    
    def test_ctr_endpoint_integration(self, client, seeded_data):
        """Test CTR over time endpoint with real data"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            response = client.get("/api/v1/analytics/ctr-over-time?days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "data" in data
        assert "avg_ctr" in data
        
        # Verify CTR data
        if len(data["data"]) > 0:
            for point in data["data"]:
                assert "date" in point
                assert "platform" in point
                assert "ctr" in point
                assert "avg_clicks" in point
                assert "avg_impressions" in point
    
    def test_csv_export_integration(self, client, seeded_data):
        """Test CSV export endpoint with real data"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            response = client.get("/api/v1/analytics/export/csv?days=30&include_metrics=true")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        # Verify CSV content
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        assert len(lines) > 1  # Header + data rows
        
        # Check header
        header = lines[0]
        expected_headers = ['Date', 'Platform', 'Post ID', 'Status', 'URL', 'Created At', 'Published At', 'Clicks', 'Impressions', 'CTR', 'Campaign ID']
        for header_name in expected_headers:
            assert header_name in header
    
    def test_analytics_filters_integration(self, client, seeded_data):
        """Test analytics filters with real data"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            # Test platform filter
            response = client.get("/api/v1/analytics/summary?days=30&platform=facebook")
            assert response.status_code == 200
            
            # Test campaign filter
            response = client.get("/api/v1/analytics/summary?days=30&campaign_id=campaign_1")
            assert response.status_code == 200
            
            # Test different time periods
            response = client.get("/api/v1/analytics/summary?days=7")
            assert response.status_code == 200
            
            response = client.get("/api/v1/analytics/summary?days=90")
            assert response.status_code == 200
    
    def test_analytics_health_check_integration(self, client, seeded_data):
        """Test analytics health check with real data"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            response = client.get("/api/v1/analytics/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["org_id"] == 999
        assert data["test_query_successful"] is True
    
    def test_available_platforms_endpoint(self, client):
        """Test available platforms endpoint"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            response = client.get("/api/v1/analytics/platforms")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "platforms" in data
        assert len(data["platforms"]) > 0
        
        for platform in data["platforms"]:
            assert "value" in platform
            assert "label" in platform
            assert "icon" in platform
    
    def test_available_campaigns_endpoint(self, client, seeded_data):
        """Test available campaigns endpoint"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                "org_id": 999,
                "user_id": 1,
                "email": "test@example.com"
            })
            
            response = client.get("/api/v1/analytics/campaigns?days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "campaigns" in data
        assert len(data["campaigns"]) > 0
        
        for campaign in data["campaigns"]:
            assert "id" in campaign
            assert "post_count" in campaign
    
    def test_analytics_performance_with_large_dataset(self, db, test_org):
        """Test analytics performance with larger dataset"""
        # Seed larger dataset
        seed_analytics_data(db, org_id=test_org.id, days=90, num_posts=1000)
        
        try:
            with pytest.MonkeyPatch().context() as m:
                m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                    "org_id": test_org.id,
                    "user_id": 1,
                    "email": "test@example.com"
                })
                
                client = TestClient(app)
                
                # Test summary endpoint performance
                import time
                start_time = time.time()
                response = client.get("/api/v1/analytics/summary?days=90")
                end_time = time.time()
                
                assert response.status_code == 200
                assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
                
                # Test timeseries endpoint performance
                start_time = time.time()
                response = client.get("/api/v1/analytics/timeseries?days=90&group_by=week")
                end_time = time.time()
                
                assert response.status_code == 200
                assert (end_time - start_time) < 3.0  # Should complete within 3 seconds
                
        finally:
            # Cleanup
            clear_analytics_data(db, org_id=test_org.id)


class TestAnalyticsDataConsistency:
    """Test data consistency across different analytics queries"""
    
    @pytest.fixture(scope="class")
    def db(self):
        """Database session"""
        db = SessionLocal()
        yield db
        db.close()
    
    @pytest.fixture(scope="class")
    def test_org(self, db):
        """Create test organization"""
        org = Organization(
            id=998,
            name="Test Consistency Org",
            slug="test-consistency-org",
            is_active=True
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        return org
    
    def test_data_consistency_across_endpoints(self, db, test_org):
        """Test that data is consistent across different analytics endpoints"""
        # Seed data
        seed_analytics_data(db, org_id=test_org.id, days=30, num_posts=20)
        
        try:
            with pytest.MonkeyPatch().context() as m:
                m.setattr("app.api.v1.analytics_enhanced.get_current_user", lambda: {
                    "org_id": test_org.id,
                    "user_id": 1,
                    "email": "test@example.com"
                })
                
                client = TestClient(app)
                
                # Get data from different endpoints
                summary_response = client.get("/api/v1/analytics/summary?days=30")
                timeseries_response = client.get("/api/v1/analytics/timeseries?days=30")
                platform_response = client.get("/api/v1/analytics/platform-comparison?days=30")
                
                assert summary_response.status_code == 200
                assert timeseries_response.status_code == 200
                assert platform_response.status_code == 200
                
                summary_data = summary_response.json()
                timeseries_data = timeseries_response.json()
                platform_data = platform_response.json()
                
                # Verify total posts consistency
                total_posts_from_timeseries = sum(point["total_count"] for point in timeseries_data["data"])
                total_posts_from_platform = sum(platform["total_posts"] for platform in platform_data["data"])
                
                assert summary_data["metrics"]["total_posts"] == total_posts_from_timeseries
                assert summary_data["metrics"]["total_posts"] == total_posts_from_platform
                
                # Verify platform breakdown consistency
                summary_platforms = {p["platform"]: p["total_count"] for p in summary_data["platform_breakdown"]}
                platform_platforms = {p["platform"]: p["total_posts"] for p in platform_data["data"]}
                
                for platform, count in summary_platforms.items():
                    assert platform_platforms[platform] == count
                
        finally:
            # Cleanup
            clear_analytics_data(db, org_id=test_org.id)


if __name__ == "__main__":
    pytest.main([__file__])
