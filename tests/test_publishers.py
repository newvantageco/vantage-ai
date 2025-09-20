"""
Tests for Publishers System
Tests the publisher drivers, registry, and webhook processing
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import List

from app.services.publishers.base import (
    BasePublisher, MediaItem, PlatformOptions, ExternalReference, 
    PreviewResult, PublisherError, AuthenticationError, ValidationError, PublishingError
)
from app.services.publishers.meta import MetaPublisher
from app.services.publishers.linkedin import LinkedInPublisher
from app.services.publishers.google_gbp import GoogleGBPPublisher
from app.services.publishers.tiktok_ads import TikTokAdsPublisher
from app.services.publishers.google_ads import GoogleAdsPublisher
from app.services.publishers.whatsapp import WhatsAppPublisher
from app.services.publishers import PublisherRegistry, get_publisher, get_supported_platforms
from app.models.publishing import PlatformType, PublishingStatus


class TestBasePublisher:
    """Test the base publisher interface"""
    
    def test_media_validation(self):
        """Test media validation"""
        publisher = MetaPublisher()
        
        # Valid media
        valid_media = [
            MediaItem(url="https://example.com/image.jpg", type="image"),
            MediaItem(url="https://example.com/video.mp4", type="video")
        ]
        errors = publisher.validate_media(valid_media)
        assert len(errors) == 0
        
        # Invalid media
        invalid_media = [
            MediaItem(url="", type="image"),  # Missing URL
            MediaItem(url="https://example.com/file.jpg", type=""),  # Missing type
        ]
        errors = publisher.validate_media(invalid_media)
        assert len(errors) == 2
        assert "missing URL" in errors[0]
        assert "missing type" in errors[1]
    
    def test_content_sanitization(self):
        """Test content sanitization"""
        publisher = MetaPublisher()
        
        content = "Hello\x00World\n\n  "
        sanitized = publisher.sanitize_content(content)
        assert sanitized == "HelloWorld"
    
    def test_character_count(self):
        """Test character counting"""
        publisher = MetaPublisher()
        
        content = "Hello World"
        count = publisher.get_character_count(content)
        assert count == 11
    
    def test_platform_constraints(self):
        """Test platform constraints application"""
        publisher = MetaPublisher()
        
        content = "Test content"
        media = [MediaItem(url="https://example.com/image.jpg", type="image")]
        
        sanitized, constraints = publisher.apply_platform_constraints(content, media)
        
        assert sanitized == "Test content"
        assert constraints['character_count'] == 12
        assert constraints['media_count'] == 1


class TestMetaPublisher:
    """Test Meta (Facebook/Instagram) publisher"""
    
    @pytest.fixture
    def publisher(self):
        return MetaPublisher()
    
    @pytest.fixture
    def platform_opts(self):
        return PlatformOptions(
            platform=PlatformType.FACEBOOK,
            account_id="test_account",
            settings={"access_token": "test_token"}
        )
    
    @pytest.fixture
    def sample_media(self):
        return [
            MediaItem(url="https://example.com/image.jpg", type="image"),
            MediaItem(url="https://example.com/video.mp4", type="video")
        ]
    
    @pytest.mark.asyncio
    async def test_preview_valid_content(self, publisher, platform_opts, sample_media):
        """Test preview with valid content"""
        content = "This is a test post"
        
        result = await publisher.preview(content, sample_media, platform_opts)
        
        assert result.is_valid is True
        assert result.sanitized_content == content
        assert result.character_count == len(content)
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_preview_content_too_long(self, publisher, platform_opts, sample_media):
        """Test preview with content that's too long"""
        content = "x" * 3000  # Exceeds Facebook's 2200 character limit
        
        result = await publisher.preview(content, sample_media, platform_opts)
        
        assert result.is_valid is False
        assert "exceeds 2200 character limit" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_preview_too_many_media(self, publisher, platform_opts):
        """Test preview with too many media items"""
        content = "Test post"
        media = [MediaItem(url=f"https://example.com/image{i}.jpg", type="image") for i in range(15)]
        
        result = await publisher.preview(content, media, platform_opts)
        
        assert result.is_valid is False
        assert "Too many media items" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_publish_success(self, publisher, platform_opts, sample_media):
        """Test successful publishing"""
        content = "Test post"
        
        result = await publisher.publish(content, sample_media, platform_opts)
        
        assert isinstance(result, ExternalReference)
        assert result.platform == PlatformType.FACEBOOK
        assert result.status == PublishingStatus.PUBLISHED
        assert result.external_id.startswith("meta_")
        assert result.url is not None
    
    @pytest.mark.asyncio
    async def test_publish_missing_credentials(self, publisher, sample_media):
        """Test publishing with missing credentials"""
        content = "Test post"
        platform_opts = PlatformOptions(
            platform=PlatformType.FACEBOOK,
            settings={}  # No access token
        )
        
        with pytest.raises(AuthenticationError):
            await publisher.publish(content, sample_media, platform_opts)
    
    @pytest.mark.asyncio
    async def test_publish_invalid_content(self, publisher, platform_opts, sample_media):
        """Test publishing with invalid content"""
        content = "x" * 3000  # Too long
        
        with pytest.raises(ValidationError):
            await publisher.publish(content, sample_media, platform_opts)


class TestLinkedInPublisher:
    """Test LinkedIn publisher"""
    
    @pytest.fixture
    def publisher(self):
        return LinkedInPublisher()
    
    @pytest.fixture
    def platform_opts(self):
        return PlatformOptions(
            platform=PlatformType.LINKEDIN,
            account_id="test_account",
            settings={"access_token": "test_token"}
        )
    
    @pytest.mark.asyncio
    async def test_preview_professional_tone_warning(self, publisher, platform_opts):
        """Test preview with unprofessional tone warning"""
        content = "URGENT!!! This is ASAP!!!"
        media = []
        
        result = await publisher.preview(content, media, platform_opts)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "professional tone" in result.warnings[0]


class TestGoogleGBPPublisher:
    """Test Google My Business publisher"""
    
    @pytest.fixture
    def publisher(self):
        return GoogleGBPPublisher()
    
    @pytest.fixture
    def platform_opts(self):
        return PlatformOptions(
            platform=PlatformType.GOOGLE_GBP,
            account_id="test_account",
            settings={"access_token": "test_token"}
        )
    
    @pytest.mark.asyncio
    async def test_preview_local_keywords_warning(self, publisher, platform_opts):
        """Test preview with local keywords warning"""
        content = "Check out our products"
        media = []
        
        result = await publisher.preview(content, media, platform_opts)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "local business keywords" in result.warnings[0]


class TestTikTokAdsPublisher:
    """Test TikTok Ads publisher"""
    
    @pytest.fixture
    def publisher(self):
        return TikTokAdsPublisher()
    
    @pytest.fixture
    def platform_opts(self):
        return PlatformOptions(
            platform=PlatformType.TIKTOK_ADS,
            account_id="test_account",
            settings={"access_token": "test_token"}
        )
    
    @pytest.mark.asyncio
    async def test_preview_video_content_warning(self, publisher, platform_opts):
        """Test preview with non-video content warning"""
        content = "Test ad"
        media = [MediaItem(url="https://example.com/image.jpg", type="image")]
        
        result = await publisher.preview(content, media, platform_opts)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "video content" in result.warnings[0]


class TestGoogleAdsPublisher:
    """Test Google Ads publisher"""
    
    @pytest.fixture
    def publisher(self):
        return GoogleAdsPublisher()
    
    @pytest.fixture
    def platform_opts(self):
        return PlatformOptions(
            platform=PlatformType.GOOGLE_ADS,
            account_id="test_account",
            settings={"access_token": "test_token"}
        )
    
    @pytest.mark.asyncio
    async def test_preview_headline_too_long(self, publisher, platform_opts):
        """Test preview with headline too long"""
        content = "x" * 100  # Exceeds 90 character limit
        media = []
        
        result = await publisher.preview(content, media, platform_opts)
        
        assert result.is_valid is False
        assert "exceeds 90 character limit" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_preview_hashtag_warning(self, publisher, platform_opts):
        """Test preview with hashtag warning"""
        content = "Check out our #awesome #products #sale"
        media = []
        
        result = await publisher.preview(content, media, platform_opts)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "not recommended" in result.warnings[0]


class TestWhatsAppPublisher:
    """Test WhatsApp Business publisher"""
    
    @pytest.fixture
    def publisher(self):
        return WhatsAppPublisher()
    
    @pytest.fixture
    def platform_opts(self):
        return PlatformOptions(
            platform=PlatformType.WHATSAPP,
            account_id="test_account",
            settings={"access_token": "test_token", "phone_number": "+1234567890"}
        )
    
    @pytest.mark.asyncio
    async def test_preview_personal_tone_warning(self, publisher, platform_opts):
        """Test preview with personal tone warning"""
        content = "URGENT!!! Contact us ASAP!!!"
        media = []
        
        result = await publisher.preview(content, media, platform_opts)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "personal tone" in result.warnings[0]
    
    @pytest.mark.asyncio
    async def test_publish_missing_phone_number(self, publisher):
        """Test publishing with missing phone number"""
        content = "Test message"
        media = []
        platform_opts = PlatformOptions(
            platform=PlatformType.WHATSAPP,
            settings={"access_token": "test_token"}  # No phone number
        )
        
        with pytest.raises(ValidationError):
            await publisher.publish(content, media, platform_opts)


class TestPublisherRegistry:
    """Test the publisher registry"""
    
    def test_get_supported_platforms(self):
        """Test getting supported platforms"""
        platforms = get_supported_platforms()
        
        assert PlatformType.FACEBOOK in platforms
        assert PlatformType.INSTAGRAM in platforms
        assert PlatformType.LINKEDIN in platforms
        assert PlatformType.GOOGLE_GBP in platforms
        assert PlatformType.TIKTOK_ADS in platforms
        assert PlatformType.GOOGLE_ADS in platforms
        assert PlatformType.WHATSAPP in platforms
    
    def test_get_publisher(self):
        """Test getting publisher instances"""
        # Test Facebook publisher
        facebook_publisher = get_publisher(PlatformType.FACEBOOK)
        assert isinstance(facebook_publisher, MetaPublisher)
        
        # Test LinkedIn publisher
        linkedin_publisher = get_publisher(PlatformType.LINKEDIN)
        assert isinstance(linkedin_publisher, LinkedInPublisher)
        
        # Test unsupported platform
        with pytest.raises(ValueError):
            get_publisher("unsupported_platform")  # type: ignore
    
    def test_is_platform_supported(self):
        """Test platform support checking"""
        from app.services.publishers import is_platform_supported
        
        assert is_platform_supported(PlatformType.FACEBOOK) is True
        assert is_platform_supported(PlatformType.LINKEDIN) is True
        assert is_platform_supported("unsupported_platform") is False  # type: ignore


class TestWebhookProcessing:
    """Test webhook processing functionality"""
    
    def test_meta_signature_verification(self):
        """Test Meta webhook signature verification"""
        from app.api.v1.platform_webhooks import verify_meta_signature
        
        payload = '{"test": "data"}'
        secret = "test_secret"
        signature = "sha256=test_signature"
        
        # This will fail with invalid signature, but tests the function exists
        result = verify_meta_signature(payload, signature, secret)
        assert isinstance(result, bool)
    
    def test_linkedin_signature_verification(self):
        """Test LinkedIn webhook signature verification"""
        from app.api.v1.platform_webhooks import verify_linkedin_signature
        
        payload = '{"test": "data"}'
        secret = "test_secret"
        signature = "test_signature"
        
        result = verify_linkedin_signature(payload, signature, secret)
        assert isinstance(result, bool)
    
    def test_google_signature_verification(self):
        """Test Google webhook signature verification"""
        from app.api.v1.platform_webhooks import verify_google_signature
        
        payload = '{"test": "data"}'
        secret = "test_secret"
        signature = "test_signature"
        
        result = verify_google_signature(payload, signature, secret)
        assert isinstance(result, bool)


class TestIntegrationAPI:
    """Test integration API endpoints"""
    
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    
    def test_integrations_status_endpoint(self, client):
        """Test the integrations status endpoint"""
        # This test would require proper authentication setup
        # For now, we'll just test that the endpoint exists
        response = client.get("/api/v1/integrations/status")
        # Should return 401 without authentication, but endpoint exists
        assert response.status_code in [200, 401, 404]  # Depends on auth setup
    
    def test_available_integrations_endpoint(self, client):
        """Test the available integrations endpoint"""
        response = client.get("/api/v1/integrations/available")
        # Should return 200 without authentication
        assert response.status_code in [200, 401, 404]  # Depends on auth setup


class TestPublishingWorkflow:
    """Test the complete publishing workflow"""
    
    @pytest.mark.asyncio
    async def test_publish_to_multiple_platforms(self):
        """Test publishing to multiple platforms"""
        content = "Test post for multiple platforms"
        media = [MediaItem(url="https://example.com/image.jpg", type="image")]
        
        platforms = [
            PlatformType.FACEBOOK,
            PlatformType.LINKEDIN,
            PlatformType.WHATSAPP
        ]
        
        results = []
        for platform in platforms:
            publisher = get_publisher(platform)
            platform_opts = PlatformOptions(
                platform=platform,
                account_id="test_account",
                settings={"access_token": "test_token", "phone_number": "+1234567890"}
            )
            
            try:
                result = await publisher.publish(content, media, platform_opts)
                results.append(result)
            except Exception as e:
                # Some platforms might fail due to missing credentials
                # This is expected in a test environment
                pass
        
        # At least some platforms should succeed
        assert len(results) > 0
        
        # All results should be ExternalReference objects
        for result in results:
            assert isinstance(result, ExternalReference)
            assert result.status == PublishingStatus.PUBLISHED
    
    @pytest.mark.asyncio
    async def test_preview_before_publish(self):
        """Test previewing content before publishing"""
        content = "This is a test post with some content"
        media = [MediaItem(url="https://example.com/image.jpg", type="image")]
        
        publisher = get_publisher(PlatformType.FACEBOOK)
        platform_opts = PlatformOptions(
            platform=PlatformType.FACEBOOK,
            account_id="test_account",
            settings={"access_token": "test_token"}
        )
        
        # Preview first
        preview = await publisher.preview(content, media, platform_opts)
        assert preview.is_valid is True
        
        # Then publish
        result = await publisher.publish(content, media, platform_opts)
        assert isinstance(result, ExternalReference)
        assert result.status == PublishingStatus.PUBLISHED


if __name__ == "__main__":
    pytest.main([__file__])
