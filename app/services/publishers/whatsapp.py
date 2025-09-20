"""
WhatsApp Business Publisher
Handles sending messages via WhatsApp Business API
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.publishers.base import (
    BasePublisher, MediaItem, PlatformOptions, ExternalReference, 
    PreviewResult, PublisherError, AuthenticationError, ValidationError, PublishingError
)
from app.models.publishing import PlatformType, PublishingStatus


class WhatsAppPublisher(BasePublisher):
    """Publisher for WhatsApp Business messages"""
    
    def __init__(self):
        super().__init__(PlatformType.WHATSAPP)
        self.max_text_length = 4096  # WhatsApp message limit
        self.max_media_items = 1  # WhatsApp supports one media per message
        self.max_hashtags = 0  # WhatsApp doesn't use hashtags
    
    async def preview(
        self, 
        content: str, 
        media: List[MediaItem], 
        platform_opts: PlatformOptions
    ) -> PreviewResult:
        """Preview and validate content for WhatsApp"""
        errors = []
        warnings = []
        
        # Validate content length
        if len(content) > self.max_text_length:
            errors.append(f"Message exceeds {self.max_text_length} character limit")
        
        # Validate media
        media_errors = self.validate_media(media)
        errors.extend(media_errors)
        
        if len(media) > self.max_media_items:
            errors.append(f"WhatsApp supports maximum {self.max_media_items} media item per message")
        
        # Check for hashtags (not used in WhatsApp)
        hashtag_count = content.count('#')
        if hashtag_count > 0:
            warnings.append("Hashtags are not commonly used in WhatsApp messages")
        
        # Check for personal tone
        if any(word in content.lower() for word in ['urgent', 'asap', '!!!']):
            warnings.append("Consider using a more personal tone for WhatsApp")
        
        # Check for emoji usage
        emoji_count = sum(1 for char in content if ord(char) > 127)
        if emoji_count > 20:
            warnings.append("High emoji usage may affect message delivery")
        
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
        """Send message via WhatsApp Business"""
        try:
            # TODO: Implement actual WhatsApp Business API integration
            # This is a stub implementation
            
            # Validate credentials
            if not platform_opts.settings or not platform_opts.settings.get('access_token'):
                raise AuthenticationError("Missing WhatsApp Business access token")
            
            # Validate phone number
            if not platform_opts.settings.get('phone_number'):
                raise ValidationError("Missing phone number for WhatsApp message")
            
            # Preview content first
            preview = await self.preview(content, media, platform_opts)
            if not preview.is_valid:
                raise ValidationError(f"Content validation failed: {', '.join(preview.errors)}")
            
            # TODO: Implement actual API calls
            # For now, return a mock response
            external_id = f"whatsapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            external_url = f"https://wa.me/{platform_opts.settings.get('phone_number')}"
            
            return ExternalReference(
                platform=self.platform,
                external_id=external_id,
                url=external_url,
                status=PublishingStatus.PUBLISHED,
                platform_data={
                    'account_id': platform_opts.account_id,
                    'phone_number': platform_opts.settings.get('phone_number'),
                    'scheduled_at': schedule_at.isoformat() if schedule_at else None,
                    'media_count': len(media),
                    'message_type': 'text' if not media else 'media'
                },
                published_at=datetime.now()
            )
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise PublishingError(f"Failed to send WhatsApp message: {str(e)}")
    
    async def get_status(self, external_id: str, platform_opts: PlatformOptions) -> ExternalReference:
        """Get status of sent message"""
        try:
            # TODO: Implement actual API call to get message status
            return ExternalReference(
                platform=self.platform,
                external_id=external_id,
                url=f"https://wa.me/{platform_opts.settings.get('phone_number', '')}",
                status=PublishingStatus.PUBLISHED,
                platform_data={'last_checked': datetime.now().isoformat()}
            )
        except Exception as e:
            raise PublishingError(f"Failed to get status from WhatsApp: {str(e)}")
    
    async def delete(self, external_id: str, platform_opts: PlatformOptions) -> bool:
        """Delete sent message (not supported by WhatsApp)"""
        # WhatsApp doesn't support message deletion
        return False
    
    async def _make_api_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict[str, Any]] = None,
        access_token: str = None
    ) -> Dict[str, Any]:
        """Make authenticated request to WhatsApp Business API"""
        # TODO: Implement actual HTTP client with proper error handling
        pass
