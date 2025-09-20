"""
Google My Business Publisher
Handles publishing to Google My Business via Google My Business API
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.publishers.base import (
    BasePublisher, MediaItem, PlatformOptions, ExternalReference, 
    PreviewResult, PublisherError, AuthenticationError, ValidationError, PublishingError
)
from app.models.publishing import PlatformType, PublishingStatus
from app.utils.social_media_client import SocialMediaClient, APIError, HTTPError
import logging

logger = logging.getLogger(__name__)


class GoogleGBPPublisher(BasePublisher):
    """Publisher for Google My Business posts"""
    
    def __init__(self):
        super().__init__(PlatformType.GOOGLE_GBP)
        self.base_url = "https://mybusiness.googleapis.com/v4"
        self.max_text_length = 1500  # Google My Business post limit
        self.max_media_items = 10
        self.max_hashtags = 3
    
    async def preview(
        self, 
        content: str, 
        media: List[MediaItem], 
        platform_opts: PlatformOptions
    ) -> PreviewResult:
        """Preview and validate content for Google My Business"""
        errors = []
        warnings = []
        
        # Validate content length
        if len(content) > self.max_text_length:
            errors.append(f"Content exceeds {self.max_text_length} character limit")
        
        # Validate media
        media_errors = self.validate_media(media)
        errors.extend(media_errors)
        
        if len(media) > self.max_media_items:
            errors.append(f"Too many media items. Maximum {self.max_media_items} allowed")
        
        # Check hashtags
        hashtag_count = content.count('#')
        if hashtag_count > self.max_hashtags:
            warnings.append(f"Google My Business recommends maximum {self.max_hashtags} hashtags")
        
        # Check for local business keywords
        local_keywords = ['near me', 'local', 'visit', 'location', 'address']
        if not any(keyword in content.lower() for keyword in local_keywords):
            warnings.append("Consider including local business keywords for better visibility")
        
        # Apply constraints
        sanitized_content, constraints = self.apply_platform_constraints(content, media)
        constraints.update({
            'max_text_length': self.max_text_length,
            'max_media_items': self.max_media_items,
            'max_hashtags': self.max_hashtags
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
        """Publish content to Google My Business"""
        try:
            # Validate credentials
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing Google My Business access token")
            
            # Preview content first
            preview = await self.preview(content, media, platform_opts)
            if not preview.is_valid:
                raise ValidationError(f"Content validation failed: {', '.join(preview.errors)}")
            
            access_token = platform_opts.settings['access_token']
            account_id = platform_opts.settings.get('account_id')
            location_id = platform_opts.settings.get('location_id')
            
            if not account_id or not location_id:
                raise ValidationError("Missing account_id or location_id in platform options")
            
            async with SocialMediaClient("google", self.base_url) as client:
                # Prepare post data
                post_data = {
                    "summary": preview.sanitized_content,
                    "callToAction": {
                        "actionType": "LEARN_MORE",
                        "url": platform_opts.settings.get('cta_url', '')
                    }
                }
                
                # Add media to post
                if media:
                    media_items = []
                    for media_item in media:
                        if media_item.type == "image":
                            media_items.append({
                                "mediaFormat": "PHOTO",
                                "sourceUrl": media_item.url
                            })
                        elif media_item.type == "video":
                            media_items.append({
                                "mediaFormat": "VIDEO",
                                "sourceUrl": media_item.url
                            })
                    
                    if media_items:
                        post_data["media"] = media_items
                
                # Schedule post if specified
                if schedule_at:
                    post_data["scheduledTime"] = schedule_at.isoformat() + "Z"
                
                # Publish to Google My Business
                response = await client.post(
                    f"/accounts/{account_id}/locations/{location_id}/localPosts",
                    data=post_data,
                    access_token=access_token
                )
                
                external_id = response.get("name", "").split("/")[-1]
                if not external_id:
                    raise PublishingError("Failed to get post ID from Google My Business API")
                
                external_url = f"https://business.google.com/posts/{external_id}"
                
                return ExternalReference(
                    platform=self.platform,
                    external_id=external_id,
                    url=external_url,
                    status=PublishingStatus.PUBLISHED if not schedule_at else PublishingStatus.SCHEDULED,
                    platform_data={
                        'account_id': account_id,
                        'location_id': location_id,
                        'scheduled_at': schedule_at.isoformat() if schedule_at else None,
                        'media_count': len(media),
                        'hashtag_count': content.count('#'),
                        'published_at': datetime.now().isoformat()
                    },
                    published_at=datetime.now() if not schedule_at else schedule_at
                )
            
        except APIError as e:
            if "authentication" in str(e).lower() or e.status_code == 401:
                raise AuthenticationError(f"Google My Business authentication failed: {e.message}")
            raise PublishingError(f"Google My Business API error: {e.message}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise PublishingError(f"Failed to publish to Google My Business: {str(e)}")
    
    async def get_status(self, external_id: str, platform_opts: PlatformOptions) -> ExternalReference:
        """Get status of published content"""
        try:
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing access token")
            
            access_token = platform_opts.settings['access_token']
            account_id = platform_opts.settings.get('account_id')
            location_id = platform_opts.settings.get('location_id')
            
            if not account_id or not location_id:
                raise ValidationError("Missing account_id or location_id in platform options")
            
            async with SocialMediaClient("google", self.base_url) as client:
                response = await client.get(
                    f"/accounts/{account_id}/locations/{location_id}/localPosts/{external_id}",
                    access_token=access_token
                )
                
                status = PublishingStatus.PUBLISHED
                if response.get("state") == "LIVE":
                    status = PublishingStatus.PUBLISHED
                elif response.get("state") == "REJECTED":
                    status = PublishingStatus.FAILED
                elif response.get("state") == "PENDING":
                    status = PublishingStatus.PENDING
                
                return ExternalReference(
                    platform=self.platform,
                    external_id=external_id,
                    url=f"https://business.google.com/posts/{external_id}",
                    status=status,
                    platform_data={
                        'last_checked': datetime.now().isoformat(),
                        'state': response.get("state"),
                        'createTime': response.get("createTime"),
                        'updateTime': response.get("updateTime")
                    }
                )
                
        except APIError as e:
            if e.status_code == 404:
                raise PublishingError(f"Post not found: {external_id}")
            raise PublishingError(f"Google My Business API error: {e.message}")
        except Exception as e:
            raise PublishingError(f"Failed to get status from Google My Business: {str(e)}")
    
    async def delete(self, external_id: str, platform_opts: PlatformOptions) -> bool:
        """Delete published content"""
        try:
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing access token")
            
            access_token = platform_opts.settings['access_token']
            account_id = platform_opts.settings.get('account_id')
            location_id = platform_opts.settings.get('location_id')
            
            if not account_id or not location_id:
                raise ValidationError("Missing account_id or location_id in platform options")
            
            async with SocialMediaClient("google", self.base_url) as client:
                await client.delete(
                    f"/accounts/{account_id}/locations/{location_id}/localPosts/{external_id}",
                    access_token=access_token
                )
                return True
                
        except APIError as e:
            if e.status_code == 404:
                logger.warning(f"Post {external_id} not found for deletion")
                return True  # Consider it deleted if not found
            raise PublishingError(f"Google My Business API error: {e.message}")
        except Exception as e:
            raise PublishingError(f"Failed to delete from Google My Business: {str(e)}")
