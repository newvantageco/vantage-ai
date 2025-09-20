"""
Meta (Facebook/Instagram) Publisher
Handles publishing to Facebook and Instagram via Graph API
"""

import httpx
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


class MetaPublisher(BasePublisher):
    """Publisher for Facebook and Instagram via Meta Graph API"""
    
    def __init__(self):
        super().__init__(PlatformType.FACEBOOK)
        self.base_url = "https://graph.facebook.com/v18.0"
        self.max_text_length = 2200  # Facebook post limit
        self.max_media_items = 10
    
    async def preview(
        self, 
        content: str, 
        media: List[MediaItem], 
        platform_opts: PlatformOptions
    ) -> PreviewResult:
        """Preview and validate content for Meta platforms"""
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
        
        # Check for hashtags
        hashtag_count = content.count('#')
        if hashtag_count > 30:
            warnings.append("High number of hashtags may reduce reach")
        
        # Apply constraints
        sanitized_content, constraints = self.apply_platform_constraints(content, media)
        constraints['max_text_length'] = self.max_text_length
        constraints['max_media_items'] = self.max_media_items
        
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
        """Publish content to Meta platform"""
        try:
            # Validate credentials
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing access token")
            
            # Preview content first
            preview = await self.preview(content, media, platform_opts)
            if not preview.is_valid:
                raise ValidationError(f"Content validation failed: {', '.join(preview.errors)}")
            
            access_token = platform_opts.settings['access_token']
            page_id = platform_opts.settings.get('page_id')
            
            if not page_id:
                raise ValidationError("Missing page_id in platform options")
            
            async with SocialMediaClient("meta", self.base_url) as client:
                # Upload media if present
                media_ids = []
                if media:
                    media_ids = await self._upload_media(client, media, access_token, page_id)
                
                # Prepare post data
                post_data = {
                    "message": preview.sanitized_content
                }
                
                # Add media to post
                if media_ids:
                    if len(media_ids) == 1:
                        post_data["attached_media"] = [{"media_fbid": media_ids[0]}]
                    else:
                        post_data["attached_media"] = [{"media_fbid": mid} for mid in media_ids]
                
                # Schedule post if specified
                if schedule_at:
                    post_data["scheduled_publish_time"] = int(schedule_at.timestamp())
                    post_data["published"] = False
                
                # Publish to Facebook
                response = await client.post(
                    f"/{page_id}/feed",
                    data=post_data,
                    access_token=access_token
                )
                
                external_id = response.get("id")
                if not external_id:
                    raise PublishingError("Failed to get post ID from Meta API")
                
                external_url = f"https://facebook.com/{external_id}"
                
                return ExternalReference(
                    platform=self.platform,
                    external_id=external_id,
                    url=external_url,
                    status=PublishingStatus.PUBLISHED if not schedule_at else PublishingStatus.SCHEDULED,
                    platform_data={
                        'account_id': platform_opts.account_id,
                        'page_id': page_id,
                        'scheduled_at': schedule_at.isoformat() if schedule_at else None,
                        'media_count': len(media),
                        'media_ids': media_ids,
                        'published_at': datetime.now().isoformat()
                    },
                    published_at=datetime.now() if not schedule_at else schedule_at
                )
            
        except APIError as e:
            if "authentication" in str(e).lower() or e.status_code == 401:
                raise AuthenticationError(f"Meta authentication failed: {e.message}")
            raise PublishingError(f"Meta API error: {e.message}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise PublishingError(f"Failed to publish to Meta: {str(e)}")
    
    async def get_status(self, external_id: str, platform_opts: PlatformOptions) -> ExternalReference:
        """Get status of published content"""
        try:
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing access token")
            
            access_token = platform_opts.settings['access_token']
            
            async with SocialMediaClient("meta", self.base_url) as client:
                response = await client.get(
                    f"/{external_id}",
                    params={"fields": "id,message,created_time,status_type"},
                    access_token=access_token
                )
                
                status = PublishingStatus.PUBLISHED
                if response.get("status_type") == "scheduled":
                    status = PublishingStatus.SCHEDULED
                elif response.get("status_type") == "draft":
                    status = PublishingStatus.DRAFT
                
                return ExternalReference(
                    platform=self.platform,
                    external_id=external_id,
                    url=f"https://facebook.com/{external_id}",
                    status=status,
                    platform_data={
                        'last_checked': datetime.now().isoformat(),
                        'message': response.get("message"),
                        'created_time': response.get("created_time"),
                        'status_type': response.get("status_type")
                    }
                )
                
        except APIError as e:
            if e.status_code == 404:
                raise PublishingError(f"Post not found: {external_id}")
            raise PublishingError(f"Meta API error: {e.message}")
        except Exception as e:
            raise PublishingError(f"Failed to get status from Meta: {str(e)}")
    
    async def delete(self, external_id: str, platform_opts: PlatformOptions) -> bool:
        """Delete published content"""
        try:
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing access token")
            
            access_token = platform_opts.settings['access_token']
            
            async with SocialMediaClient("meta", self.base_url) as client:
                await client.delete(f"/{external_id}", access_token=access_token)
                return True
                
        except APIError as e:
            if e.status_code == 404:
                logger.warning(f"Post {external_id} not found for deletion")
                return True  # Consider it deleted if not found
            raise PublishingError(f"Meta API error: {e.message}")
        except Exception as e:
            raise PublishingError(f"Failed to delete from Meta: {str(e)}")
    
    async def _upload_media(
        self, 
        client: SocialMediaClient, 
        media: List[MediaItem], 
        access_token: str, 
        page_id: str
    ) -> List[str]:
        """Upload media files to Meta and return media IDs"""
        media_ids = []
        
        for media_item in media:
            try:
                if media_item.type == "image":
                    # Upload image
                    upload_data = {
                        "url": media_item.url,
                        "published": False
                    }
                    
                    response = await client.post(
                        f"/{page_id}/photos",
                        data=upload_data,
                        access_token=access_token
                    )
                    
                    media_ids.append(response.get("id"))
                    
                elif media_item.type == "video":
                    # Upload video (requires different endpoint)
                    upload_data = {
                        "file_url": media_item.url,
                        "description": media_item.caption or "",
                        "published": False
                    }
                    
                    response = await client.post(
                        f"/{page_id}/videos",
                        data=upload_data,
                        access_token=access_token
                    )
                    
                    media_ids.append(response.get("id"))
                    
                else:
                    logger.warning(f"Unsupported media type: {media_item.type}")
                    
            except APIError as e:
                logger.error(f"Failed to upload media {media_item.url}: {e.message}")
                raise PublishingError(f"Failed to upload media: {e.message}")
        
        return media_ids
