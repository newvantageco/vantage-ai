"""
Unit tests for Publishing API
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


class TestPublishingAPI:
    """Test Publishing endpoints"""
    
    def test_publish_preview_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful publish preview"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/publish/preview",
                json={
                    "content_id": 1,
                    "platform": "facebook"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["content_id"] == 1
            assert data["platform"] == "facebook"
            assert "sanitized_content" in data
            assert "is_valid" in data
            assert "constraints_applied" in data
    
    def test_publish_preview_different_platforms(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test publish preview for different platforms"""
        platforms = ["facebook", "instagram", "linkedin", "twitter", "google_gbp"]
        
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            for platform in platforms:
                response = client.post(
                    "/api/v1/publish/preview",
                    json={
                        "content_id": 1,
                        "platform": platform
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["platform"] == platform
                assert "constraints_applied" in data
    
    def test_publish_send_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful publish send"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/publish/send",
                json={
                    "content_id": 1,
                    "platforms": ["facebook", "instagram"],
                    "scheduled_time": "2024-01-01T12:00:00Z"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "job_id" in data
            assert data["content_id"] == 1
            assert data["platforms"] == ["facebook", "instagram"]
            assert "status_url" in data
    
    def test_publish_send_multiple_platforms(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test publish send to multiple platforms"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/publish/send",
                json={
                    "content_id": 1,
                    "platforms": ["facebook", "instagram", "linkedin", "twitter"],
                    "scheduled_time": None
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["platforms"]) == 4
            assert "facebook" in data["platforms"]
            assert "instagram" in data["platforms"]
            assert "linkedin" in data["platforms"]
            assert "twitter" in data["platforms"]
    
    def test_get_publishing_job_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting publishing job status"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            # First create a job
            send_response = client.post(
                "/api/v1/publish/send",
                json={
                    "content_id": 1,
                    "platforms": ["facebook"],
                    "scheduled_time": None
                }
            )
            job_id = send_response.json()["job_id"]
            
            # Then get job status
            response = client.get(f"/api/v1/publishing/jobs/{job_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == job_id
            assert "status" in data
            assert "total_platforms" in data
    
    def test_get_publishing_job_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting non-existent publishing job"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/publishing/jobs/non-existent-job")
            
            assert response.status_code == 404
    
    def test_list_publishing_jobs(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing publishing jobs"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/publishing/jobs")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_list_external_references(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing external references"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/external-references")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_list_external_references_with_filters(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing external references with filters"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/external-references?platform=facebook&content_id=1")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_list_platforms(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing available platforms"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/platforms")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_test_platform_connection(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test platform connection testing"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post("/api/v1/platforms/facebook/test")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "message" in data
    
    def test_publish_preview_content_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test publish preview with non-existent content"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/publish/preview",
                json={
                    "content_id": 999,
                    "platform": "facebook"
                }
            )
            
            assert response.status_code == 404
    
    def test_publish_send_content_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test publish send with non-existent content"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/publish/send",
                json={
                    "content_id": 999,
                    "platforms": ["facebook"],
                    "scheduled_time": None
                }
            )
            
            assert response.status_code == 404
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to publishing endpoints"""
        endpoints = [
            ("/api/v1/publish/preview", "POST"),
            ("/api/v1/publish/send", "POST"),
            ("/api/v1/publishing/jobs", "GET"),
            ("/api/v1/external-references", "GET"),
            ("/api/v1/platforms", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401
