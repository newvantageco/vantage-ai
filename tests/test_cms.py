"""
Unit tests for CMS API
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from datetime import datetime


class TestCMSAPI:
    """Test CMS endpoints"""
    
    def test_create_campaign_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful campaign creation"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/campaigns",
                json={
                    "name": "Test Campaign",
                    "description": "A test campaign",
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-12-31T23:59:59Z",
                    "target_audience": {"age_range": "25-35"},
                    "goals": {"reach": 10000},
                    "budget": 5000
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Campaign"
            assert data["description"] == "A test campaign"
            assert data["organization_id"] == mock_user.organization_id
            assert data["created_by_id"] == mock_user.id
    
    def test_list_campaigns(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing campaigns"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/campaigns")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_campaign_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting a specific campaign"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            # First create a campaign
            create_response = client.post(
                "/api/v1/campaigns",
                json={
                    "name": "Test Campaign",
                    "description": "A test campaign"
                }
            )
            campaign_id = create_response.json()["id"]
            
            # Then get it
            response = client.get(f"/api/v1/campaigns/{campaign_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Test Campaign"
    
    def test_get_campaign_not_found(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test getting a non-existent campaign"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/campaigns/999")
            
            assert response.status_code == 404
    
    def test_update_campaign_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful campaign update"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            # First create a campaign
            create_response = client.post(
                "/api/v1/campaigns",
                json={
                    "name": "Test Campaign",
                    "description": "A test campaign"
                }
            )
            campaign_id = create_response.json()["id"]
            
            # Then update it
            response = client.put(
                f"/api/v1/campaigns/{campaign_id}",
                json={
                    "name": "Updated Campaign",
                    "description": "An updated test campaign"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Campaign"
    
    def test_delete_campaign_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful campaign deletion"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            # First create a campaign
            create_response = client.post(
                "/api/v1/campaigns",
                json={
                    "name": "Test Campaign",
                    "description": "A test campaign"
                }
            )
            campaign_id = create_response.json()["id"]
            
            # Then delete it
            response = client.delete(f"/api/v1/campaigns/{campaign_id}")
            
            assert response.status_code == 204
    
    def test_create_content_item_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful content item creation"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/content",
                json={
                    "title": "Test Content",
                    "content": "This is test content",
                    "content_type": "text",
                    "campaign_id": None,
                    "brand_guide_id": None,
                    "hashtags": ["#test", "#content"],
                    "tags": ["marketing", "social"]
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test Content"
            assert data["content"] == "This is test content"
            assert data["organization_id"] == mock_user.organization_id
            assert data["created_by_id"] == mock_user.id
    
    def test_list_content_items(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing content items"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/content")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_list_content_items_with_filters(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing content items with filters"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/content?status=draft&campaign_id=1")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_brand_guide_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful brand guide creation"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/brand-guides",
                json={
                    "name": "Test Brand Guide",
                    "description": "A test brand guide",
                    "tone_of_voice": "Professional and friendly",
                    "writing_style": "Clear and concise",
                    "color_palette": {"primary": "#FF0000", "secondary": "#00FF00"},
                    "ai_prompts": {"content": "Write in a professional tone"}
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Brand Guide"
            assert data["organization_id"] == mock_user.organization_id
    
    def test_list_brand_guides(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing brand guides"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/brand-guides")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_calendar_endpoint(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test calendar endpoint"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/calendar",
                params={
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-12-31T23:59:59Z",
                    "page": 1,
                    "size": 20
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data
            assert "size" in data
            assert "total_pages" in data
            assert isinstance(data["items"], list)
    
    def test_calendar_pagination(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test calendar pagination"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get(
                "/api/v1/calendar",
                params={
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-12-31T23:59:59Z",
                    "page": 2,
                    "size": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 2
            assert data["size"] == 10
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to CMS endpoints"""
        endpoints = [
            ("/api/v1/campaigns", "GET"),
            ("/api/v1/content", "GET"),
            ("/api/v1/brand-guides", "GET"),
            ("/api/v1/calendar", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401
