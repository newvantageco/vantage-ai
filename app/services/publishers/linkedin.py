"""
LinkedIn Publisher
Handles publishing to LinkedIn via LinkedIn API
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


class LinkedInPublisher(BasePublisher):
    """Publisher for LinkedIn posts"""
    
    def __init__(self):
        super().__init__(PlatformType.LINKEDIN)
        self.base_url = "https://api.linkedin.com/v2"
        self.max_text_length = 3000  # LinkedIn post limit
        self.max_media_items = 9
        self.max_hashtags = 5
    
    async def preview(
        self, 
        content: str, 
        media: List[MediaItem], 
        platform_opts: PlatformOptions
    ) -> PreviewResult:
        """Preview and validate content for LinkedIn"""
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
            warnings.append(f"LinkedIn recommends maximum {self.max_hashtags} hashtags")
        
        # Check for professional tone
        if any(word in content.lower() for word in ['urgent', 'asap', '!!!']):
            warnings.append("Consider using a more professional tone for LinkedIn")
        
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
        """Publish content to LinkedIn"""
        try:
            # Validate credentials
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing LinkedIn access token")
            
            # Preview content first
            preview = await self.preview(content, media, platform_opts)
            if not preview.is_valid:
                raise ValidationError(f"Content validation failed: {', '.join(preview.errors)}")
            
            access_token = platform_opts.settings['access_token']
            person_urn = platform_opts.settings.get('person_urn')
            
            if not person_urn:
                raise ValidationError("Missing person_urn in platform options")
            
            async with SocialMediaClient("linkedin", self.base_url) as client:
                # Upload media if present
                media_urns = []
                if media:
                    media_urns = await self._upload_media(client, media, access_token)
                
                # Prepare post data
                post_data = {
                    "author": person_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": preview.sanitized_content
                            },
                            "shareMediaCategory": "NONE"
                        }
                    }
                }
                
                # Add media to post
                if media_urns:
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = media_urns
                
                # LinkedIn doesn't support scheduling via API, so we ignore schedule_at
                if schedule_at:
                    logger.warning("LinkedIn doesn't support scheduled posts via API. Publishing immediately.")
                
                # Publish to LinkedIn
                response = await client.post(
                    "/ugcPosts",
                    data=post_data,
                    access_token=access_token
                )
                
                external_id = response.get("id")
                if not external_id:
                    raise PublishingError("Failed to get post ID from LinkedIn API")
                
                external_url = f"https://linkedin.com/feed/update/{external_id}"
                
                return ExternalReference(
                    platform=self.platform,
                    external_id=external_id,
                    url=external_url,
                    status=PublishingStatus.PUBLISHED,
                    platform_data={
                        'account_id': platform_opts.account_id,
                        'person_urn': person_urn,
                        'scheduled_at': schedule_at.isoformat() if schedule_at else None,
                        'media_count': len(media),
                        'media_urns': media_urns,
                        'hashtag_count': content.count('#'),
                        'published_at': datetime.now().isoformat()
                    },
                    published_at=datetime.now()
                )
            
        except APIError as e:
            if "authentication" in str(e).lower() or e.status_code == 401:
                raise AuthenticationError(f"LinkedIn authentication failed: {e.message}")
            raise PublishingError(f"LinkedIn API error: {e.message}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise PublishingError(f"Failed to publish to LinkedIn: {str(e)}")
    
    async def get_status(self, external_id: str, platform_opts: PlatformOptions) -> ExternalReference:
        """Get status of published content"""
        try:
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing access token")
            
            access_token = platform_opts.settings['access_token']
            
            async with SocialMediaClient("linkedin", self.base_url) as client:
                response = await client.get(
                    f"/ugcPosts/{external_id}",
                    params={"fields": "id,lifecycleState,created,lastModified"},
                    access_token=access_token
                )
                
                status = PublishingStatus.PUBLISHED
                if response.get("lifecycleState") == "DRAFT":
                    status = PublishingStatus.DRAFT
                elif response.get("lifecycleState") == "PUBLISHED":
                    status = PublishingStatus.PUBLISHED
                
                return ExternalReference(
                    platform=self.platform,
                    external_id=external_id,
                    url=f"https://linkedin.com/feed/update/{external_id}",
                    status=status,
                    platform_data={
                        'last_checked': datetime.now().isoformat(),
                        'lifecycle_state': response.get("lifecycleState"),
                        'created': response.get("created"),
                        'last_modified': response.get("lastModified")
                    }
                )
                
        except APIError as e:
            if e.status_code == 404:
                raise PublishingError(f"Post not found: {external_id}")
            raise PublishingError(f"LinkedIn API error: {e.message}")
        except Exception as e:
            raise PublishingError(f"Failed to get status from LinkedIn: {str(e)}")
    
    async def delete(self, external_id: str, platform_opts: PlatformOptions) -> bool:
        """Delete published content"""
        try:
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing access token")
            
            access_token = platform_opts.settings['access_token']
            
            async with SocialMediaClient("linkedin", self.base_url) as client:
                await client.delete(f"/ugcPosts/{external_id}", access_token=access_token)
                return True
                
        except APIError as e:
            if e.status_code == 404:
                logger.warning(f"Post {external_id} not found for deletion")
                return True  # Consider it deleted if not found
            raise PublishingError(f"LinkedIn API error: {e.message}")
        except Exception as e:
            raise PublishingError(f"Failed to delete from LinkedIn: {str(e)}")
    
    async def _upload_media(
        self, 
        client: SocialMediaClient, 
        media: List[MediaItem], 
        access_token: str
    ) -> List[Dict[str, Any]]:
        """Upload media files to LinkedIn and return media URNs"""
        media_urns = []
        
        for media_item in media:
            try:
                if media_item.type == "image":
                    # Register upload
                    register_data = {
                        "registerUploadRequest": {
                            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                            "owner": "urn:li:person:YOUR_PERSON_ID",  # This should be passed in
                            "serviceRelationships": [
                                {
                                    "relationshipType": "OWNER",
                                    "identifier": "urn:li:userGeneratedContent"
                                }
                            ]
                        }
                    }
                    
                    register_response = await client.post(
                        "/assets?action=registerUpload",
                        data=register_data,
                        access_token=access_token
                    )
                    
                    upload_url = register_response.get("value", {}).get("uploadMechanism", {}).get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
                    asset_id = register_response.get("value", {}).get("asset")
                    
                    if not upload_url or not asset_id:
                        raise PublishingError("Failed to get upload URL from LinkedIn")
                    
                    # Upload the actual file (this would need to be implemented with proper file handling)
                    # For now, we'll use the URL directly
                    media_urns.append({
                        "status": "READY",
                        "description": {
                            "text": media_item.caption or ""
                        },
                        "media": asset_id,
                        "title": {
                            "text": media_item.caption or "Image"
                        }
                    })
                    
                else:
                    logger.warning(f"Unsupported media type for LinkedIn: {media_item.type}")
                    
            except APIError as e:
                logger.error(f"Failed to upload media {media_item.url}: {e.message}")
                raise PublishingError(f"Failed to upload media: {e.message}")
        
        return media_urns
