"""
Base Publisher Interface
Defines the standard interface for all platform publishers
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from app.models.publishing import PlatformType, PublishingStatus


@dataclass
class MediaItem:
    """Represents a media item to be published"""
    url: str
    type: str  # 'image', 'video', 'gif', etc.
    alt_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PlatformOptions:
    """Platform-specific publishing options"""
    platform: PlatformType
    account_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


@dataclass
class ExternalReference:
    """Represents a published item on an external platform"""
    platform: PlatformType
    external_id: str
    url: Optional[str] = None
    status: PublishingStatus = PublishingStatus.PENDING
    error_message: Optional[str] = None
    platform_data: Optional[Dict[str, Any]] = None
    published_at: Optional[datetime] = None


@dataclass
class PreviewResult:
    """Result of content preview validation"""
    is_valid: bool
    sanitized_content: str
    warnings: List[str]
    errors: List[str]
    character_count: int
    constraints_applied: Dict[str, Any]


class BasePublisher(ABC):
    """Base class for all platform publishers"""
    
    def __init__(self, platform: PlatformType):
        self.platform = platform
    
    @abstractmethod
    async def preview(
        self, 
        content: str, 
        media: List[MediaItem], 
        platform_opts: PlatformOptions
    ) -> PreviewResult:
        """
        Preview and validate content before publishing
        
        Args:
            content: Text content to publish
            media: List of media items
            platform_opts: Platform-specific options
            
        Returns:
            PreviewResult with validation details
        """
        pass
    
    @abstractmethod
    async def publish(
        self, 
        content: str, 
        media: List[MediaItem], 
        platform_opts: PlatformOptions,
        schedule_at: Optional[datetime] = None
    ) -> ExternalReference:
        """
        Publish content to the platform
        
        Args:
            content: Text content to publish
            media: List of media items
            platform_opts: Platform-specific options
            schedule_at: Optional scheduled publish time
            
        Returns:
            ExternalReference with platform details
        """
        pass
    
    @abstractmethod
    async def get_status(self, external_id: str, platform_opts: PlatformOptions) -> ExternalReference:
        """
        Get the current status of a published item
        
        Args:
            external_id: Platform-specific ID
            platform_opts: Platform-specific options
            
        Returns:
            Updated ExternalReference with current status
        """
        pass
    
    @abstractmethod
    async def delete(self, external_id: str, platform_opts: PlatformOptions) -> bool:
        """
        Delete a published item
        
        Args:
            external_id: Platform-specific ID
            platform_opts: Platform-specific options
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def validate_media(self, media: List[MediaItem]) -> List[str]:
        """Validate media items for platform constraints"""
        errors = []
        
        for item in media:
            if not item.url:
                errors.append(f"Media item missing URL")
            if not item.type:
                errors.append(f"Media item missing type")
        
        return errors
    
    def sanitize_content(self, content: str) -> str:
        """Basic content sanitization"""
        # Remove potentially harmful characters
        content = content.replace('\x00', '')
        return content.strip()
    
    def get_character_count(self, content: str) -> int:
        """Get character count for content"""
        return len(content)
    
    def apply_platform_constraints(
        self, 
        content: str, 
        media: List[MediaItem]
    ) -> tuple[str, Dict[str, Any]]:
        """
        Apply platform-specific constraints to content and media
        
        Returns:
            Tuple of (sanitized_content, constraints_applied)
        """
        constraints = {}
        sanitized = self.sanitize_content(content)
        
        # Basic constraints that all platforms should apply
        constraints['character_count'] = self.get_character_count(sanitized)
        constraints['media_count'] = len(media)
        
        return sanitized, constraints


class PublisherError(Exception):
    """Base exception for publisher errors"""
    pass


class AuthenticationError(PublisherError):
    """Authentication failed with platform"""
    pass


class ValidationError(PublisherError):
    """Content validation failed"""
    pass


class PublishingError(PublisherError):
    """Publishing operation failed"""
    pass


class RateLimitError(PublisherError):
    """Rate limit exceeded"""
    pass
