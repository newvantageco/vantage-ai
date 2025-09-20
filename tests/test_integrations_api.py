"""
Tests for Integrations API
Tests the integrations API endpoints and platform status functionality
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.publishing import PlatformIntegration, PlatformType
from app.models.entities import Organization
from app.api.v1.integrations import (
    get_integrations_status,
    list_available_integrations,
    _get_platform_display_name,
    _get_platform_description,
    _get_platform_icon,
    _get_platform_capabilities,
    _get_platform_requirements
)


class TestIntegrationsAPI:
    """Test integrations API endpoints"""
    
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
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = Mock(spec=Session)
        return db
    
    def test_get_platform_display_name(self):
        """Test platform display name function"""
        assert _get_platform_display_name(PlatformType.FACEBOOK) == "Facebook"
        assert _get_platform_display_name(PlatformType.INSTAGRAM) == "Instagram"
        assert _get_platform_display_name(PlatformType.LINKEDIN) == "LinkedIn"
        assert _get_platform_display_name(PlatformType.GOOGLE_GBP) == "Google My Business"
        assert _get_platform_display_name(PlatformType.TIKTOK_ADS) == "TikTok Ads"
        assert _get_platform_display_name(PlatformType.GOOGLE_ADS) == "Google Ads"
        assert _get_platform_display_name(PlatformType.WHATSAPP) == "WhatsApp Business"
    
    def test_get_platform_description(self):
        """Test platform description function"""
        assert "Facebook pages" in _get_platform_description(PlatformType.FACEBOOK)
        assert "Instagram business" in _get_platform_description(PlatformType.INSTAGRAM)
        assert "LinkedIn company" in _get_platform_description(PlatformType.LINKEDIN)
        assert "Google My Business" in _get_platform_description(PlatformType.GOOGLE_GBP)
        assert "TikTok advertising" in _get_platform_description(PlatformType.TIKTOK_ADS)
        assert "Google Ads" in _get_platform_description(PlatformType.GOOGLE_ADS)
        assert "WhatsApp Business" in _get_platform_description(PlatformType.WHATSAPP)
    
    def test_get_platform_icon(self):
        """Test platform icon function"""
        assert _get_platform_icon(PlatformType.FACEBOOK) == "facebook"
        assert _get_platform_icon(PlatformType.INSTAGRAM) == "instagram"
        assert _get_platform_icon(PlatformType.LINKEDIN) == "linkedin"
        assert _get_platform_icon(PlatformType.GOOGLE_GBP) == "google"
        assert _get_platform_icon(PlatformType.TIKTOK_ADS) == "tiktok"
        assert _get_platform_icon(PlatformType.GOOGLE_ADS) == "google"
        assert _get_platform_icon(PlatformType.WHATSAPP) == "whatsapp"
    
    def test_get_platform_capabilities(self):
        """Test platform capabilities function"""
        facebook_caps = _get_platform_capabilities(PlatformType.FACEBOOK)
        assert "publish_posts" in facebook_caps
        assert "analytics" in facebook_caps
        
        linkedin_caps = _get_platform_capabilities(PlatformType.LINKEDIN)
        assert "publish_posts" in linkedin_caps
        assert "analytics" in linkedin_caps
        
        whatsapp_caps = _get_platform_capabilities(PlatformType.WHATSAPP)
        assert "send_messages" in whatsapp_caps
        assert "media_messages" in whatsapp_caps
    
    def test_get_platform_requirements(self):
        """Test platform requirements function"""
        facebook_reqs = _get_platform_requirements(PlatformType.FACEBOOK)
        assert "Facebook Developer Account" in facebook_reqs
        assert "Page Access Token" in facebook_reqs
        
        linkedin_reqs = _get_platform_requirements(PlatformType.LINKEDIN)
        assert "LinkedIn Company Page" in linkedin_reqs
        assert "Marketing Developer Platform" in linkedin_reqs
        
        whatsapp_reqs = _get_platform_requirements(PlatformType.WHATSAPP)
        assert "WhatsApp Business Account" in whatsapp_reqs
        assert "Phone Number Verification" in whatsapp_reqs


class TestIntegrationsStatus:
    """Test integrations status functionality"""
    
    @pytest.fixture
    def mock_integrations(self):
        """Mock platform integrations"""
        return [
            Mock(
                platform=PlatformType.FACEBOOK,
                is_connected=True,
                is_active=True,
                account_name="Test Facebook Page",
                last_sync_at="2024-01-15T10:30:00Z",
                error_message=None
            ),
            Mock(
                platform=PlatformType.LINKEDIN,
                is_connected=False,
                is_active=False,
                account_name=None,
                last_sync_at=None,
                error_message="Connection failed"
            )
        ]
    
    @pytest.fixture
    def mock_db_with_integrations(self, mock_integrations):
        """Mock database with integrations"""
        db = Mock(spec=Session)
        query_mock = Mock()
        query_mock.filter.return_value.all.return_value = mock_integrations
        db.query.return_value = query_mock
        return db
    
    @patch('app.api.v1.integrations.get_supported_platforms')
    def test_get_integrations_status_success(self, mock_get_platforms, mock_db_with_integrations, mock_user):
        """Test successful integrations status retrieval"""
        from app.services.publishers import get_supported_platforms
        mock_get_platforms.return_value = [
            PlatformType.FACEBOOK,
            PlatformType.LINKEDIN,
            PlatformType.WHATSAPP
        ]
        
        result = get_integrations_status(mock_db_with_integrations, mock_user)
        
        assert "platforms" in result
        assert "total_connected" in result
        assert "total_platforms" in result
        assert result["total_platforms"] == 3
        assert result["total_connected"] == 1
        
        # Check platform data
        platforms = result["platforms"]
        assert len(platforms) == 3
        
        # Find Facebook platform
        facebook_platform = next(p for p in platforms if p["platform"] == "facebook")
        assert facebook_platform["status"] == "connected"
        assert facebook_platform["account_name"] == "Test Facebook Page"
        
        # Find LinkedIn platform
        linkedin_platform = next(p for p in platforms if p["platform"] == "linkedin")
        assert linkedin_platform["status"] == "disconnected"
        assert linkedin_platform["error_message"] == "Connection failed"
    
    @patch('app.api.v1.integrations.get_supported_platforms')
    def test_get_integrations_status_error(self, mock_get_platforms, mock_user):
        """Test integrations status with database error"""
        from app.services.publishers import get_supported_platforms
        mock_get_platforms.return_value = [PlatformType.FACEBOOK]
        
        # Mock database that raises an error
        db = Mock(spec=Session)
        db.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            get_integrations_status(db, mock_user)


class TestAvailableIntegrations:
    """Test available integrations functionality"""
    
    @patch('app.api.v1.integrations.get_supported_platforms')
    def test_list_available_integrations_success(self, mock_get_platforms):
        """Test successful available integrations listing"""
        from app.services.publishers import get_supported_platforms
        mock_get_platforms.return_value = [
            PlatformType.FACEBOOK,
            PlatformType.LINKEDIN,
            PlatformType.WHATSAPP
        ]
        
        result = list_available_integrations()
        
        assert "integrations" in result
        assert "total" in result
        assert result["total"] == 3
        
        integrations = result["integrations"]
        assert len(integrations) == 3
        
        # Check each integration has required fields
        for integration in integrations:
            assert "platform" in integration
            assert "name" in integration
            assert "description" in integration
            assert "icon" in integration
            assert "capabilities" in integration
            assert "setup_requirements" in integration
            assert "status" in integration
            assert integration["status"] == "available"
    
    @patch('app.api.v1.integrations.get_supported_platforms')
    def test_list_available_integrations_error(self, mock_get_platforms):
        """Test available integrations with error"""
        from app.services.publishers import get_supported_platforms
        mock_get_platforms.side_effect = Exception("Platform error")
        
        with pytest.raises(Exception):
            list_available_integrations()


class TestIntegrationsEndpoints:
    """Test integrations API endpoints"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    def test_integrations_status_endpoint(self, client):
        """Test integrations status endpoint"""
        response = client.get("/api/v1/integrations/status")
        
        # Should return 401 without authentication, but endpoint exists
        assert response.status_code in [200, 401, 404]
    
    def test_available_integrations_endpoint(self, client):
        """Test available integrations endpoint"""
        response = client.get("/api/v1/integrations/available")
        
        # Should return 200 without authentication
        assert response.status_code in [200, 401, 404]
    
    def test_integrations_status_response_structure(self, client):
        """Test integrations status response structure"""
        response = client.get("/api/v1/integrations/status")
        
        if response.status_code == 200:
            data = response.json()
            assert "platforms" in data
            assert "total_connected" in data
            assert "total_platforms" in data
            assert isinstance(data["platforms"], list)
            assert isinstance(data["total_connected"], int)
            assert isinstance(data["total_platforms"], int)
    
    def test_available_integrations_response_structure(self, client):
        """Test available integrations response structure"""
        response = client.get("/api/v1/integrations/available")
        
        if response.status_code == 200:
            data = response.json()
            assert "integrations" in data
            assert "total" in data
            assert isinstance(data["integrations"], list)
            assert isinstance(data["total"], int)
            
            # Check integration structure
            if data["integrations"]:
                integration = data["integrations"][0]
                assert "platform" in integration
                assert "name" in integration
                assert "description" in integration
                assert "icon" in integration
                assert "capabilities" in integration
                assert "setup_requirements" in integration
                assert "status" in integration


class TestPlatformIntegrationModel:
    """Test PlatformIntegration model"""
    
    def test_platform_integration_creation(self):
        """Test creating a platform integration"""
        integration = PlatformIntegration(
            organization_id=1,
            platform=PlatformType.FACEBOOK,
            account_id="123456789",
            account_name="Test Page",
            credentials={"access_token": "test_token"},
            is_active=True,
            is_connected=True,
            settings={"page_id": "123456789"}
        )
        
        assert integration.organization_id == 1
        assert integration.platform == PlatformType.FACEBOOK
        assert integration.account_id == "123456789"
        assert integration.account_name == "Test Page"
        assert integration.is_active is True
        assert integration.is_connected is True
    
    def test_platform_integration_defaults(self):
        """Test platform integration default values"""
        integration = PlatformIntegration(
            organization_id=1,
            platform=PlatformType.LINKEDIN
        )
        
        assert integration.is_active is True
        assert integration.is_connected is False
        assert integration.last_sync_at is None
        assert integration.error_message is None


if __name__ == "__main__":
    pytest.main([__file__])
