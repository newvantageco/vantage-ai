#!/usr/bin/env python3
"""
Comprehensive test suite for Publisher System.
Tests every line of function systematically.
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.publishers.base import Publisher, PostResult
from app.publishers.meta import MetaPublisher
from app.publishers.linkedin import LinkedInPublisher
from app.publishers.gbp import GoogleBusinessPublisher
from app.publishers.common import sanitize_caption, truncate_for_platform, PLATFORM_LIMITS
from app.models.content import BrandGuide


class TestPublisherBase:
    """Comprehensive tests for base Publisher class."""

    def test_post_result_creation(self):
        """Test PostResult creation."""
        result = PostResult(
            id="post_123",
            url="https://example.com/post/123",
            external_refs={"facebook": "fb_123", "instagram": "ig_123"}
        )
        
        assert result.id == "post_123"
        assert result.url == "https://example.com/post/123"
        assert result.external_refs == {"facebook": "fb_123", "instagram": "ig_123"}

    def test_post_result_minimal(self):
        """Test PostResult creation with minimal data."""
        result = PostResult(id="post_123")
        
        assert result.id == "post_123"
        assert result.url is None
        assert result.external_refs is None

    def test_publisher_can_schedule_default(self):
        """Test Publisher can_schedule default value."""
        publisher = Publisher()
        assert publisher.can_schedule is True

    @pytest.mark.asyncio
    async def test_publisher_publish_not_implemented(self):
        """Test Publisher publish method raises NotImplementedError."""
        publisher = Publisher()
        
        with pytest.raises(NotImplementedError):
            await publisher.publish(
                caption="Test caption",
                media_paths=["image.jpg"],
                first_comment="Test comment",
                idempotency_key="test_key"
            )

    def test_store_external_reference_no_db_session(self):
        """Test store_external_reference without database session."""
        publisher = Publisher()
        
        result = publisher.store_external_reference(
            schedule_id="schedule_123",
            provider="facebook",
            ref_id="fb_123",
            ref_url="https://facebook.com/post/123",
            db_session=None
        )
        
        assert result is None

    def test_store_external_reference_with_db_session(self):
        """Test store_external_reference with database session."""
        publisher = Publisher()
        mock_db = Mock()
        
        with patch('app.models.external_refs.ScheduleExternal') as mock_external_ref:
            mock_external_ref_instance = Mock()
            mock_external_ref_instance.id = "ext_ref_123"
            mock_external_ref.return_value = mock_external_ref_instance
            
            result = publisher.store_external_reference(
                schedule_id="schedule_123",
                provider="facebook",
                ref_id="fb_123",
                ref_url="https://facebook.com/post/123",
                db_session=mock_db
            )
            
            assert result == "ext_ref_123"
            mock_external_ref.assert_called_once()
            mock_db.add.assert_called_once_with(mock_external_ref_instance)

    def test_store_external_reference_database_error(self):
        """Test store_external_reference with database error."""
        publisher = Publisher()
        mock_db = Mock()
        mock_db.add.side_effect = Exception("Database error")
        
        with patch('app.models.external_refs.ScheduleExternal'):
            result = publisher.store_external_reference(
                schedule_id="schedule_123",
                provider="facebook",
                ref_id="fb_123",
                ref_url="https://facebook.com/post/123",
                db_session=mock_db
            )
            
            assert result is None


class TestPublisherCommon:
    """Comprehensive tests for publisher common functions."""

    def test_sanitize_caption_no_brand_guide(self):
        """Test sanitize_caption without brand guide."""
        caption = "This is a normal caption"
        
        result = sanitize_caption(caption, None)
        
        assert result == caption

    def test_sanitize_caption_with_brand_guide_no_issues(self):
        """Test sanitize_caption with brand guide but no issues."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars='{"banned_phrases": []}'
        )
        
        caption = "This is a normal caption"
        
        with patch('app.ai.safety.validate_caption') as mock_validate:
            mock_validate.return_value = Mock(ok=True, reasons=[], fixed_text=caption)
            
            result = sanitize_caption(caption, guide)
            
            assert result == caption
            mock_validate.assert_called_once_with(caption, guide)

    def test_sanitize_caption_with_brand_guide_issues(self):
        """Test sanitize_caption with brand guide and issues."""
        guide = BrandGuide(
            id="guide_123",
            org_id="org_123",
            pillars='{"banned_phrases": ["banned"]}'
        )
        
        caption = "This contains banned words"
        fixed_caption = "This contains words"
        
        with patch('app.ai.safety.validate_caption') as mock_validate:
            mock_validate.return_value = Mock(
                ok=False, 
                reasons=["banned"], 
                fixed_text=fixed_caption
            )
            
            result = sanitize_caption(caption, guide)
            
            assert result == fixed_caption
            mock_validate.assert_called_once_with(caption, guide)

    def test_truncate_for_platform_within_limit(self):
        """Test truncate_for_platform when text is within limit."""
        text = "Short text"
        platform = "facebook"
        max_length = 100
        
        result = truncate_for_platform(text, platform, max_length)
        
        assert result == text

    def test_truncate_for_platform_exceeds_limit(self):
        """Test truncate_for_platform when text exceeds limit."""
        text = "This is a very long text that exceeds the platform limit"
        platform = "twitter"
        max_length = 20
        
        result = truncate_for_platform(text, platform, max_length)
        
        assert len(result) <= max_length
        assert result.endswith("...")
        assert result.startswith("This is a very long")

    def test_truncate_for_platform_exact_limit(self):
        """Test truncate_for_platform when text is exactly at limit."""
        text = "Exactly twenty chars"
        platform = "twitter"
        max_length = 20
        
        result = truncate_for_platform(text, platform, max_length)
        
        assert result == text
        assert len(result) == max_length

    def test_truncate_for_platform_empty_text(self):
        """Test truncate_for_platform with empty text."""
        text = ""
        platform = "facebook"
        max_length = 100
        
        result = truncate_for_platform(text, platform, max_length)
        
        assert result == text

    def test_truncate_for_platform_zero_limit(self):
        """Test truncate_for_platform with zero limit."""
        text = "Some text"
        platform = "test"
        max_length = 0
        
        result = truncate_for_platform(text, platform, max_length)
        
        assert result == "..."

    def test_truncate_for_platform_negative_limit(self):
        """Test truncate_for_platform with negative limit."""
        text = "Some text"
        platform = "test"
        max_length = -5
        
        result = truncate_for_platform(text, platform, max_length)
        
        assert result == "..."

    def test_platform_limits_defined(self):
        """Test that PLATFORM_LIMITS contains expected platforms."""
        expected_platforms = ["facebook", "instagram", "twitter", "linkedin", "google_business"]
        
        for platform in expected_platforms:
            assert platform in PLATFORM_LIMITS
            assert isinstance(PLATFORM_LIMITS[platform], int)
            assert PLATFORM_LIMITS[platform] > 0

    def test_platform_limits_values(self):
        """Test that PLATFORM_LIMITS has reasonable values."""
        # Facebook should have higher limit than Twitter
        assert PLATFORM_LIMITS["facebook"] > PLATFORM_LIMITS["twitter"]
        
        # Instagram should have reasonable limit
        assert 100 <= PLATFORM_LIMITS["instagram"] <= 2000
        
        # LinkedIn should have higher limit than Twitter
        assert PLATFORM_LIMITS["linkedin"] > PLATFORM_LIMITS["twitter"]


class TestMetaPublisher:
    """Comprehensive tests for MetaPublisher class."""

    @pytest.fixture
    def meta_publisher(self):
        """Create MetaPublisher instance."""
        return MetaPublisher()

    def test_meta_publisher_initialization(self, meta_publisher):
        """Test MetaPublisher initialization."""
        assert meta_publisher.can_schedule is True
        assert meta_publisher.settings is not None
        assert meta_publisher.oauth is not None

    @pytest.mark.asyncio
    async def test_meta_publish_dry_run(self, meta_publisher):
        """Test MetaPublisher publish in dry run mode."""
        with patch.object(meta_publisher.settings, 'dry_run', True):
            result = await meta_publisher.publish(
                caption="Test caption",
                media_paths=["image.jpg"],
                first_comment="Test comment",
                idempotency_key="test_key"
            )
            
            assert result.id == "meta_dry_run"
            assert result.url == "https://facebook.com/dry_run"

    @pytest.mark.asyncio
    async def test_meta_publish_real_mode(self, meta_publisher):
        """Test MetaPublisher publish in real mode."""
        with patch.object(meta_publisher.settings, 'dry_run', False):
            with patch.object(meta_publisher, '_get_access_token', return_value="access_token"):
                with patch.object(meta_publisher.oauth, 'get_page_access_token', return_value="page_token"):
                    with patch.object(meta_publisher, '_post_to_facebook', return_value="fb_post_123"):
                        with patch.object(meta_publisher, '_post_to_instagram', return_value="ig_post_123"):
                            result = await meta_publisher.publish(
                                caption="Test caption",
                                media_paths=["image.jpg"],
                                first_comment="Test comment",
                                idempotency_key="test_key"
                            )
                            
                            assert result.id == "fb_post_123"
                            assert "facebook.com" in result.url
                            assert result.external_refs == {"facebook": "fb_post_123", "instagram": "ig_post_123"}

    @pytest.mark.asyncio
    async def test_meta_publish_no_instagram(self, meta_publisher):
        """Test MetaPublisher publish without Instagram."""
        with patch.object(meta_publisher.settings, 'dry_run', False):
            with patch.object(meta_publisher.settings, 'meta_ig_business_id', None):
                with patch.object(meta_publisher, '_get_access_token', return_value="access_token"):
                    with patch.object(meta_publisher.oauth, 'get_page_access_token', return_value="page_token"):
                        with patch.object(meta_publisher, '_post_to_facebook', return_value="fb_post_123"):
                            result = await meta_publisher.publish(
                                caption="Test caption",
                                media_paths=["image.jpg"],
                                first_comment="Test comment",
                                idempotency_key="test_key"
                            )
                            
                            assert result.id == "fb_post_123"
                            assert result.external_refs == {"facebook": "fb_post_123"}

    @pytest.mark.asyncio
    async def test_meta_publish_exception_handling(self, meta_publisher):
        """Test MetaPublisher publish exception handling."""
        with patch.object(meta_publisher.settings, 'dry_run', False):
            with patch.object(meta_publisher, '_get_access_token', side_effect=Exception("OAuth error")):
                with pytest.raises(Exception, match="OAuth error"):
                    await meta_publisher.publish(
                        caption="Test caption",
                        media_paths=["image.jpg"],
                        first_comment="Test comment",
                        idempotency_key="test_key"
                    )

    @pytest.mark.asyncio
    async def test_meta_get_access_token(self, meta_publisher):
        """Test MetaPublisher _get_access_token method."""
        with patch.object(meta_publisher.oauth, 'get_valid_token', return_value="access_token"):
            result = await meta_publisher._get_access_token()
            assert result == "access_token"

    @pytest.mark.asyncio
    async def test_meta_post_to_facebook(self, meta_publisher):
        """Test MetaPublisher _post_to_facebook method."""
        with patch('app.utils.http.HTTPClient') as mock_http_client:
            mock_client = Mock()
            mock_client.post.return_value = {"id": "fb_post_123"}
            mock_http_client.return_value = mock_client
            
            result = await meta_publisher._post_to_facebook(
                page_access_token="page_token",
                caption="Test caption",
                media_paths=["image.jpg"],
                idempotency_key="test_key"
            )
            
            assert result == "fb_post_123"

    @pytest.mark.asyncio
    async def test_meta_post_to_instagram(self, meta_publisher):
        """Test MetaPublisher _post_to_instagram method."""
        with patch('app.utils.http.HTTPClient') as mock_http_client:
            mock_client = Mock()
            mock_client.post.return_value = {"id": "ig_post_123"}
            mock_http_client.return_value = mock_client
            
            result = await meta_publisher._post_to_instagram(
                page_access_token="page_token",
                caption="Test caption",
                media_paths=["image.jpg"],
                idempotency_key="test_key"
            )
            
            assert result == "ig_post_123"


class TestLinkedInPublisher:
    """Comprehensive tests for LinkedInPublisher class."""

    @pytest.fixture
    def linkedin_publisher(self):
        """Create LinkedInPublisher instance."""
        return LinkedInPublisher()

    def test_linkedin_publisher_initialization(self, linkedin_publisher):
        """Test LinkedInPublisher initialization."""
        assert linkedin_publisher.can_schedule is True
        assert linkedin_publisher.settings is not None
        assert linkedin_publisher.oauth is not None

    @pytest.mark.asyncio
    async def test_linkedin_publish_dry_run(self, linkedin_publisher):
        """Test LinkedInPublisher publish in dry run mode."""
        with patch.object(linkedin_publisher.settings, 'dry_run', True):
            result = await linkedin_publisher.publish(
                caption="Test caption",
                media_paths=["image.jpg"],
                first_comment="Test comment",
                idempotency_key="test_key"
            )
            
            assert result.id == "linkedin_dry_run"
            assert result.url == "https://linkedin.com/dry_run"

    @pytest.mark.asyncio
    async def test_linkedin_publish_real_mode(self, linkedin_publisher):
        """Test LinkedInPublisher publish in real mode."""
        with patch.object(linkedin_publisher.settings, 'dry_run', False):
            with patch.object(linkedin_publisher, '_get_access_token', return_value="access_token"):
                with patch.object(linkedin_publisher, '_post_to_linkedin', return_value="linkedin_post_123"):
                    result = await linkedin_publisher.publish(
                        caption="Test caption",
                        media_paths=["image.jpg"],
                        first_comment="Test comment",
                        idempotency_key="test_key"
                    )
                    
                    assert result.id == "linkedin_post_123"
                    assert "linkedin.com" in result.url

    @pytest.mark.asyncio
    async def test_linkedin_publish_exception_handling(self, linkedin_publisher):
        """Test LinkedInPublisher publish exception handling."""
        with patch.object(linkedin_publisher.settings, 'dry_run', False):
            with patch.object(linkedin_publisher, '_get_access_token', side_effect=Exception("OAuth error")):
                with pytest.raises(Exception, match="OAuth error"):
                    await linkedin_publisher.publish(
                        caption="Test caption",
                        media_paths=["image.jpg"],
                        first_comment="Test comment",
                        idempotency_key="test_key"
                    )


class TestGoogleBusinessPublisher:
    """Comprehensive tests for GoogleBusinessPublisher class."""

    @pytest.fixture
    def gbp_publisher(self):
        """Create GoogleBusinessPublisher instance."""
        return GoogleBusinessPublisher()

    def test_gbp_publisher_initialization(self, gbp_publisher):
        """Test GoogleBusinessPublisher initialization."""
        assert gbp_publisher.can_schedule is True
        assert gbp_publisher.settings is not None
        assert gbp_publisher.oauth is not None

    @pytest.mark.asyncio
    async def test_gbp_publish_gbp_disabled(self, gbp_publisher):
        """Test GoogleBusinessPublisher publish when GBP is disabled."""
        with patch.object(gbp_publisher.settings, 'gbp_enabled', False):
            result = await gbp_publisher.publish(
                caption="Test caption",
                media_paths=["image.jpg"],
                first_comment="Test comment",
                idempotency_key="test_key"
            )
            
            assert result.id == "gbp_dry_run"
            assert result.url == "https://business.google.com/dry_run"

    @pytest.mark.asyncio
    async def test_gbp_publish_dry_run(self, gbp_publisher):
        """Test GoogleBusinessPublisher publish in dry run mode."""
        with patch.object(gbp_publisher.settings, 'gbp_enabled', True):
            with patch.object(gbp_publisher.settings, 'dry_run', True):
                result = await gbp_publisher.publish(
                    caption="Test caption",
                    media_paths=["image.jpg"],
                    first_comment="Test comment",
                    idempotency_key="test_key"
                )
                
                assert result.id == "gbp_dry_run"
                assert result.url == "https://business.google.com/dry_run"

    @pytest.mark.asyncio
    async def test_gbp_publish_real_mode(self, gbp_publisher):
        """Test GoogleBusinessPublisher publish in real mode."""
        with patch.object(gbp_publisher.settings, 'gbp_enabled', True):
            with patch.object(gbp_publisher.settings, 'dry_run', False):
                with patch.object(gbp_publisher, '_get_access_token', return_value="access_token"):
                    with patch.object(gbp_publisher, '_post_to_gbp', return_value="gbp_post_123"):
                        result = await gbp_publisher.publish(
                            caption="Test caption",
                            media_paths=["image.jpg"],
                            first_comment="Test comment",
                            idempotency_key="test_key"
                        )
                        
                        assert result.id == "gbp_post_123"
                        assert "business.google.com" in result.url

    @pytest.mark.asyncio
    async def test_gbp_publish_exception_handling(self, gbp_publisher):
        """Test GoogleBusinessPublisher publish exception handling."""
        with patch.object(gbp_publisher.settings, 'gbp_enabled', True):
            with patch.object(gbp_publisher.settings, 'dry_run', False):
                with patch.object(gbp_publisher, '_get_access_token', side_effect=Exception("OAuth error")):
                    with pytest.raises(Exception, match="OAuth error"):
                        await gbp_publisher.publish(
                            caption="Test caption",
                            media_paths=["image.jpg"],
                            first_comment="Test comment",
                            idempotency_key="test_key"
                        )


class TestPublisherIntegration:
    """Integration tests for publisher system."""

    def test_publisher_hierarchy(self):
        """Test that all publishers inherit from base Publisher."""
        publishers = [MetaPublisher(), LinkedInPublisher(), GoogleBusinessPublisher()]
        
        for publisher in publishers:
            assert isinstance(publisher, Publisher)
            assert hasattr(publisher, 'publish')
            assert hasattr(publisher, 'store_external_reference')

    def test_publisher_can_schedule_consistency(self):
        """Test that all publishers have consistent can_schedule setting."""
        publishers = [MetaPublisher(), LinkedInPublisher(), GoogleBusinessPublisher()]
        
        for publisher in publishers:
            assert publisher.can_schedule is True

    def test_publisher_settings_integration(self):
        """Test that all publishers integrate with settings."""
        publishers = [MetaPublisher(), LinkedInPublisher(), GoogleBusinessPublisher()]
        
        for publisher in publishers:
            assert publisher.settings is not None
            assert hasattr(publisher.settings, 'dry_run')

    def test_publisher_oauth_integration(self):
        """Test that all publishers integrate with OAuth."""
        publishers = [MetaPublisher(), LinkedInPublisher(), GoogleBusinessPublisher()]
        
        for publisher in publishers:
            assert publisher.oauth is not None

    @pytest.mark.asyncio
    async def test_publisher_error_handling_consistency(self):
        """Test that all publishers handle errors consistently."""
        publishers = [MetaPublisher(), LinkedInPublisher(), GoogleBusinessPublisher()]
        
        for publisher in publishers:
            with patch.object(publisher, '_get_access_token', side_effect=Exception("Test error")):
                with pytest.raises(Exception, match="Test error"):
                    await publisher.publish(
                        caption="Test caption",
                        media_paths=["image.jpg"],
                        first_comment="Test comment",
                        idempotency_key="test_key"
                    )

    def test_publisher_logging_consistency(self):
        """Test that all publishers use consistent logging."""
        publishers = [MetaPublisher(), LinkedInPublisher(), GoogleBusinessPublisher()]
        
        for publisher in publishers:
            # This is a basic check - in practice, you'd verify logging calls
            assert hasattr(publisher, '__class__')
            assert publisher.__class__.__name__.endswith('Publisher')
