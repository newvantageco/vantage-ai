"""
TikTok Ads Publisher
Handles publishing to TikTok Ads via TikTok Marketing API
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.publishers.base import (
    BasePublisher, MediaItem, PlatformOptions, ExternalReference, 
    PreviewResult, PublisherError, AuthenticationError, ValidationError, PublishingError
)
from app.models.publishing import PlatformType, PublishingStatus


class TikTokAdsPublisher(BasePublisher):
    """Publisher for TikTok Ads campaigns"""
    
    def __init__(self):
        super().__init__(PlatformType.TIKTOK_ADS)
        self.max_text_length = 2200  # TikTok ad text limit
        self.max_media_items = 1  # TikTok ads typically use single video
        self.max_hashtags = 5
    
    async def preview(
        self, 
        content: str, 
        media: List[MediaItem], 
        platform_opts: PlatformOptions
    ) -> PreviewResult:
        """Preview and validate content for TikTok Ads"""
        errors = []
        warnings = []
        
        # Validate content length
        if len(content) > self.max_text_length:
            errors.append(f"Content exceeds {self.max_text_length} character limit")
        
        # Validate media
        media_errors = self.validate_media(media)
        errors.extend(media_errors)
        
        if len(media) > self.max_media_items:
            errors.append(f"TikTok Ads supports maximum {self.max_media_items} media item")
        
        # Check for video content
        if media and not any(item.type in ['video', 'gif'] for item in media):
            warnings.append("TikTok Ads work best with video content")
        
        # Check hashtags
        hashtag_count = content.count('#')
        if hashtag_count > self.max_hashtags:
            warnings.append(f"TikTok recommends maximum {self.max_hashtags} hashtags")
        
        # Check for trending keywords
        trending_keywords = ['viral', 'trending', 'fyp', 'foryou']
        if not any(keyword in content.lower() for keyword in trending_keywords):
            warnings.append("Consider using trending keywords for better reach")
        
        # Apply constraints
        sanitized_content, constraints = self.apply_platform_constraints(content, media)
        constraints.update({
            'max_text_length': self.max_text_length,
            'max_media_items': self.max_media_items,
            'max_hashtags': self.max_hashtags,
            'requires_video': True
        })
        
        return PreviewResult(
            is_valid=len(errors) == 0,
            sanitized_content=sanitized_content,
            warnings=warnings,
            errors=errors,
            character_count=len(sanitized_content),
            constraints_applied=constraints
        )
    
    async def publish(
        self, 
        content: str, 
        media: List[MediaItem], 
        platform_opts: PlatformOptions,
        schedule_at: Optional[datetime] = None
    ) -> ExternalReference:
        """Publish content to TikTok Ads"""
        try:
            # TODO: Implement actual TikTok Marketing API integration
            # This is a stub implementation
            
            # Validate credentials
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing TikTok Ads access token")
            
            # Preview content first
            preview = await self.preview(content, media, platform_opts)
            if not preview.is_valid:
                raise ValidationError(f"Content validation failed: {', '.join(preview.errors)}")
            
            # TODO: Implement actual API calls
            # For now, return a mock response
            external_id = f"tiktok_ads_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            external_url = f"https://ads.tiktok.com/campaigns/{external_id}"
            
            return ExternalReference(
                platform=self.platform,
                external_id=external_id,
                url=external_url,
                status=PublishingStatus.PUBLISHED,
                platform_data={
                    'account_id': platform_opts.account_id,
                    'scheduled_at': schedule_at.isoformat() if schedule_at else None,
                    'media_count': len(media),
                    'hashtag_count': content.count('#'),
                    'campaign_type': 'video_ad'
                },
                published_at=datetime.now()
            )
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise PublishingError(f"Failed to publish to TikTok Ads: {str(e)}")
    
    async def get_status(self, external_id: str, platform_opts: PlatformOptions) -> ExternalReference:
        """Get status of published content"""
        try:
            # TODO: Implement actual API call to get campaign status
            return ExternalReference(
                platform=self.platform,
                external_id=external_id,
                url=f"https://ads.tiktok.com/campaigns/{external_id}",
                status=PublishingStatus.PUBLISHED,
                platform_data={'last_checked': datetime.now().isoformat()}
            )
        except Exception as e:
            raise PublishingError(f"Failed to get status from TikTok Ads: {str(e)}")
    
    async def delete(self, external_id: str, platform_opts: PlatformOptions) -> bool:
        """Delete published content"""
        try:
            # TODO: Implement actual API call to delete campaign
            return True
        except Exception as e:
            raise PublishingError(f"Failed to delete from TikTok Ads: {str(e)}")
    
    async def _make_api_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict[str, Any]] = None,
        access_token: str = None
    ) -> Dict[str, Any]:
        """Make authenticated request to TikTok Marketing API"""
        # TODO: Implement actual HTTP client with proper error handling
        pass
