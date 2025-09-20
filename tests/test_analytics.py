"""
Unit tests for Analytics API
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestAnalyticsAPI:
    """Test Analytics endpoints"""
    
    def test_analytics_summary_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful analytics summary"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/analytics/summary?range=last_30d")
            
            assert response.status_code == 200
            data = response.json()
            assert "period_start" in data
            assert "period_end" in data
            assert "total_impressions" in data
            assert "total_reach" in data
            assert "total_clicks" in data
            assert "total_engagements" in data
            assert "total_conversions" in data
            assert "avg_ctr" in data
            assert "avg_engagement_rate" in data
            assert "platform_breakdown" in data
    
    def test_analytics_summary_different_ranges(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test analytics summary with different time ranges"""
        ranges = ["last_7d", "last_30d", "last_90d"]
        
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            for range_val in ranges:
                response = client.get(f"/api/v1/analytics/summary?range={range_val}")
                
                assert response.status_code == 200
                data = response.json()
                assert "period_start" in data
                assert "period_end" in data
    
    def test_analytics_summary_custom_range(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test analytics summary with custom date range"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/analytics/summary",
                params={
                    "range": "custom",
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-31T23:59:59Z"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "period_start" in data
            assert "period_end" in data
    
    def test_analytics_summary_with_platform_filter(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test analytics summary with platform filter"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/analytics/summary?range=last_30d&platform=facebook"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "platform_breakdown" in data
    
    def test_analytics_timeseries_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful analytics timeseries"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/analytics/timeseries",
                params={
                    "metric": "impressions",
                    "group_by": "platform",
                    "from_date": "2024-01-01T00:00:00Z",
                    "to_date": "2024-01-31T23:59:59Z"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["metric"] == "impressions"
            assert data["group_by"] == "platform"
            assert "data" in data
            assert isinstance(data["data"], list)
    
    def test_analytics_timeseries_different_metrics(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test analytics timeseries with different metrics"""
        metrics = ["impressions", "reach", "clicks", "engagements", "conversions", "ctr", "engagement_rate"]
        
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            for metric in metrics:
                response = client.get(
                    "/api/v1/analytics/timeseries",
                    params={
                        "metric": metric,
                        "group_by": "platform",
                        "from_date": "2024-01-01T00:00:00Z",
                        "to_date": "2024-01-31T23:59:59Z"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["metric"] == metric
    
    def test_analytics_timeseries_different_grouping(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test analytics timeseries with different grouping"""
        group_by_options = ["platform", "day", "week", "month"]
        
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            for group_by in group_by_options:
                response = client.get(
                    "/api/v1/analytics/timeseries",
                    params={
                        "metric": "impressions",
                        "group_by": group_by,
                        "from_date": "2024-01-01T00:00:00Z",
                        "to_date": "2024-01-31T23:59:59Z"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["group_by"] == group_by
    
    def test_analytics_timeseries_invalid_metric(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test analytics timeseries with invalid metric"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/analytics/timeseries",
                params={
                    "metric": "invalid_metric",
                    "group_by": "platform",
                    "from_date": "2024-01-01T00:00:00Z",
                    "to_date": "2024-01-31T23:59:59Z"
                }
            )
            
            assert response.status_code == 400
    
    def test_list_post_metrics(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing post metrics"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/analytics/posts")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_list_post_metrics_with_filters(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing post metrics with filters"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/analytics/posts",
                params={
                    "platform": "facebook",
                    "from_date": "2024-01-01T00:00:00Z",
                    "to_date": "2024-01-31T23:59:59Z",
                    "skip": 0,
                    "limit": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_analytics_export(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test creating analytics export"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/analytics/export",
                json={
                    "export_type": "csv",
                    "date_range_start": "2024-01-01T00:00:00Z",
                    "date_range_end": "2024-01-31T23:59:59Z",
                    "platforms": ["facebook", "instagram"],
                    "metrics": ["impressions", "clicks", "engagements"]
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["export_type"] == "csv"
            assert data["organization_id"] == mock_user.organization_id
            assert data["user_id"] == mock_user.id
    
    def test_get_analytics_export(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting analytics export"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            # First create an export
            create_response = client.post(
                "/api/v1/analytics/export",
                json={
                    "export_type": "csv",
                    "date_range_start": "2024-01-01T00:00:00Z",
                    "date_range_end": "2024-01-31T23:59:59Z"
                }
            )
            export_id = create_response.json()["id"]
            
            # Then get it
            response = client.get(f"/api/v1/analytics/export/{export_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == export_id
    
    def test_get_analytics_export_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting non-existent analytics export"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/analytics/export/999")
            
            assert response.status_code == 404
    
    def test_analytics_export_csv(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test analytics CSV export"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/analytics/export.csv",
                params={
                    "from_date": "2024-01-01T00:00:00Z",
                    "to_date": "2024-01-31T23:59:59Z",
                    "platform": "facebook"
                }
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    def test_trigger_metrics_collection(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test triggering metrics collection"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/analytics/collect",
                params={
                    "platform": "facebook",
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-31T23:59:59Z"
                }
            )
            
            assert response.status_code == 202
            data = response.json()
            assert "message" in data
            assert "task_id" in data
            assert data["platform"] == "facebook"
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to analytics endpoints"""
        endpoints = [
            ("/api/v1/analytics/summary", "GET"),
            ("/api/v1/analytics/timeseries", "GET"),
            ("/api/v1/analytics/posts", "GET"),
            ("/api/v1/analytics/export", "POST"),
            ("/api/v1/analytics/collect", "POST")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401
