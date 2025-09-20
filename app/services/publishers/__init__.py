"""
Publishers Registry
Central registry for all platform publishers with routing by platform key
"""

from typing import Dict, Type, Optional
from app.services.publishers.base import BasePublisher
from app.services.publishers.meta import MetaPublisher
from app.services.publishers.linkedin import LinkedInPublisher
from app.services.publishers.google_gbp import GoogleGBPPublisher
from app.services.publishers.tiktok_ads import TikTokAdsPublisher
from app.services.publishers.google_ads import GoogleAdsPublisher
from app.services.publishers.whatsapp import WhatsAppPublisher
from app.models.publishing import PlatformType


class PublisherRegistry:
    """Central registry for platform publishers"""
    
    _publishers: Dict[PlatformType, Type[BasePublisher]] = {
        PlatformType.FACEBOOK: MetaPublisher,
        PlatformType.INSTAGRAM: MetaPublisher,  # Same as Facebook
        PlatformType.LINKEDIN: LinkedInPublisher,
        PlatformType.GOOGLE_GBP: GoogleGBPPublisher,
        PlatformType.TIKTOK_ADS: TikTokAdsPublisher,
        PlatformType.GOOGLE_ADS: GoogleAdsPublisher,
        PlatformType.WHATSAPP: WhatsAppPublisher,
    }
    
    @classmethod
    def get_publisher(cls, platform: PlatformType) -> BasePublisher:
        """
        Get publisher instance for a platform
        
        Args:
            platform: Platform type
            
        Returns:
            Publisher instance
            
        Raises:
            ValueError: If platform is not supported
        """
        if platform not in cls._publishers:
            raise ValueError(f"Unsupported platform: {platform}")
        
        publisher_class = cls._publishers[platform]
        return publisher_class()
    
    @classmethod
    def get_supported_platforms(cls) -> list[PlatformType]:
        """Get list of supported platforms"""
        return list(cls._publishers.keys())
    
    @classmethod
    def is_platform_supported(cls, platform: PlatformType) -> bool:
        """Check if platform is supported"""
        return platform in cls._publishers
    
    @classmethod
    def register_publisher(cls, platform: PlatformType, publisher_class: Type[BasePublisher]):
        """
        Register a new publisher for a platform
        
        Args:
            platform: Platform type
            publisher_class: Publisher class
        """
        cls._publishers[platform] = publisher_class


# Convenience functions
def get_publisher(platform: PlatformType) -> BasePublisher:
    """Get publisher instance for a platform"""
    return PublisherRegistry.get_publisher(platform)


def get_supported_platforms() -> list[PlatformType]:
    """Get list of supported platforms"""
    return PublisherRegistry.get_supported_platforms()


def is_platform_supported(platform: PlatformType) -> bool:
    """Check if platform is supported"""
    return PublisherRegistry.is_platform_supported(platform)


# Export main classes and functions
__all__ = [
    'PublisherRegistry',
    'get_publisher',
    'get_supported_platforms', 
    'is_platform_supported',
    'BasePublisher',
    'MetaPublisher',
    'LinkedInPublisher',
    'GoogleGBPPublisher',
    'TikTokAdsPublisher',
    'GoogleAdsPublisher',
    'WhatsAppPublisher'
]
