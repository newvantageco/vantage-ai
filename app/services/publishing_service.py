"""
Publishing Service
Abstracts platform-specific publishing logic with driver pattern
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum


class PlatformType(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    GOOGLE_GBP = "google_gbp"
    TIKTOK_ADS = "tiktok_ads"
    GOOGLE_ADS = "google_ads"
    WHATSAPP = "whatsapp"


class PlatformDriver(ABC):
    """Abstract base class for platform drivers"""
    
    @abstractmethod
    def sanitize_content(self, content: str) -> str:
        """Sanitize content for the platform"""
        pass
    
    @abstractmethod
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content against platform rules"""
        pass
    
    @abstractmethod
    def publish_content(self, content: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to the platform"""
        pass
    
    @abstractmethod
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to the platform"""
        pass


class FacebookDriver(PlatformDriver):
    """Facebook publishing driver"""
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content for Facebook"""
        # Remove excessive hashtags (Facebook recommends max 2-3)
        lines = content.split('\n')
        sanitized_lines = []
        for line in lines:
            hashtags = [tag for tag in line.split() if tag.startswith('#')]
            if len(hashtags) > 3:
                # Keep only first 3 hashtags
                words = line.split()
                hashtag_count = 0
                new_words = []
                for word in words:
                    if word.startswith('#') and hashtag_count < 3:
                        new_words.append(word)
                        hashtag_count += 1
                    elif not word.startswith('#'):
                        new_words.append(word)
                line = ' '.join(new_words)
            sanitized_lines.append(line)
        return '\n'.join(sanitized_lines)
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content for Facebook"""
        errors = []
        warnings = []
        constraints = {}
        
        # Character limit
        if len(content) > 63206:  # Facebook's character limit
            errors.append("Content exceeds Facebook's character limit (63,206 characters)")
        
        # Hashtag limit
        hashtag_count = content.count('#')
        if hashtag_count > 3:
            warnings.append(f"Facebook recommends max 3 hashtags, found {hashtag_count}")
        
        constraints = {
            "character_limit": 63206,
            "hashtag_recommendation": 3,
            "max_hashtags": 30
        }
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "constraints": constraints
        }
    
    def publish_content(self, content: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to Facebook"""
        # FIXME: Implement actual Facebook Graph API call
        return {
            "success": True,
            "post_id": f"fb_post_{hash(content)}",
            "url": f"https://facebook.com/posts/{hash(content)}",
            "platform": "facebook"
        }
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Facebook connection"""
        # FIXME: Implement actual Facebook API test
        return {"success": True, "message": "Facebook connection successful"}


class InstagramDriver(PlatformDriver):
    """Instagram publishing driver"""
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content for Instagram"""
        # Instagram allows up to 30 hashtags
        lines = content.split('\n')
        sanitized_lines = []
        for line in lines:
            hashtags = [tag for tag in line.split() if tag.startswith('#')]
            if len(hashtags) > 30:
                # Keep only first 30 hashtags
                words = line.split()
                hashtag_count = 0
                new_words = []
                for word in words:
                    if word.startswith('#') and hashtag_count < 30:
                        new_words.append(word)
                        hashtag_count += 1
                    elif not word.startswith('#'):
                        new_words.append(word)
                line = ' '.join(new_words)
            sanitized_lines.append(line)
        return '\n'.join(sanitized_lines)
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content for Instagram"""
        errors = []
        warnings = []
        constraints = {}
        
        # Character limit
        if len(content) > 2200:  # Instagram's character limit
            errors.append("Content exceeds Instagram's character limit (2,200 characters)")
        
        # Hashtag limit
        hashtag_count = content.count('#')
        if hashtag_count > 30:
            errors.append(f"Instagram allows max 30 hashtags, found {hashtag_count}")
        
        constraints = {
            "character_limit": 2200,
            "max_hashtags": 30,
            "max_mentions": 20
        }
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "constraints": constraints
        }
    
    def publish_content(self, content: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to Instagram"""
        # FIXME: Implement actual Instagram Graph API call
        return {
            "success": True,
            "post_id": f"ig_post_{hash(content)}",
            "url": f"https://instagram.com/p/{hash(content)}",
            "platform": "instagram"
        }
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Instagram connection"""
        # FIXME: Implement actual Instagram API test
        return {"success": True, "message": "Instagram connection successful"}


class LinkedInDriver(PlatformDriver):
    """LinkedIn publishing driver"""
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content for LinkedIn"""
        # LinkedIn is more professional, limit hashtags
        lines = content.split('\n')
        sanitized_lines = []
        for line in lines:
            hashtags = [tag for tag in line.split() if tag.startswith('#')]
            if len(hashtags) > 5:
                # Keep only first 5 hashtags
                words = line.split()
                hashtag_count = 0
                new_words = []
                for word in words:
                    if word.startswith('#') and hashtag_count < 5:
                        new_words.append(word)
                        hashtag_count += 1
                    elif not word.startswith('#'):
                        new_words.append(word)
                line = ' '.join(new_words)
            sanitized_lines.append(line)
        return '\n'.join(sanitized_lines)
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content for LinkedIn"""
        errors = []
        warnings = []
        constraints = {}
        
        # Character limit
        if len(content) > 3000:  # LinkedIn's character limit
            errors.append("Content exceeds LinkedIn's character limit (3,000 characters)")
        
        # Hashtag limit
        hashtag_count = content.count('#')
        if hashtag_count > 5:
            warnings.append(f"LinkedIn recommends max 5 hashtags, found {hashtag_count}")
        
        constraints = {
            "character_limit": 3000,
            "max_hashtags": 5,
            "max_mentions": 10
        }
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "constraints": constraints
        }
    
    def publish_content(self, content: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to LinkedIn"""
        # FIXME: Implement actual LinkedIn API call
        return {
            "success": True,
            "post_id": f"li_post_{hash(content)}",
            "url": f"https://linkedin.com/posts/{hash(content)}",
            "platform": "linkedin"
        }
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test LinkedIn connection"""
        # FIXME: Implement actual LinkedIn API test
        return {"success": True, "message": "LinkedIn connection successful"}


class GoogleGBPDriver(PlatformDriver):
    """Google My Business publishing driver"""
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content for Google My Business"""
        # GMB has strict content policies
        return content
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content for Google My Business"""
        errors = []
        warnings = []
        constraints = {}
        
        # Character limit
        if len(content) > 1500:  # GMB's character limit
            errors.append("Content exceeds Google My Business character limit (1,500 characters)")
        
        constraints = {
            "character_limit": 1500,
            "max_hashtags": 0,  # GMB doesn't support hashtags
            "max_mentions": 0
        }
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "constraints": constraints
        }
    
    def publish_content(self, content: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to Google My Business"""
        # FIXME: Implement actual GMB API call
        return {
            "success": True,
            "post_id": f"gmb_post_{hash(content)}",
            "url": f"https://business.google.com/posts/{hash(content)}",
            "platform": "google_gbp"
        }
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Google My Business connection"""
        # FIXME: Implement actual GMB API test
        return {"success": True, "message": "Google My Business connection successful"}


class TikTokAdsDriver(PlatformDriver):
    """TikTok Ads publishing driver (stub)"""
    
    def sanitize_content(self, content: str) -> str:
        return content
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        return {"is_valid": True, "errors": [], "warnings": [], "constraints": {}}
    
    def publish_content(self, content: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        # FIXME: Implement TikTok Ads API
        return {"success": False, "error": "TikTok Ads integration not implemented"}
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error": "TikTok Ads integration not implemented"}


class GoogleAdsDriver(PlatformDriver):
    """Google Ads publishing driver (stub)"""
    
    def sanitize_content(self, content: str) -> str:
        return content
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        return {"is_valid": True, "errors": [], "warnings": [], "constraints": {}}
    
    def publish_content(self, content: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        # FIXME: Implement Google Ads API
        return {"success": False, "error": "Google Ads integration not implemented"}
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error": "Google Ads integration not implemented"}


class WhatsAppDriver(PlatformDriver):
    """WhatsApp Business publishing driver (stub)"""
    
    def sanitize_content(self, content: str) -> str:
        return content
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        return {"is_valid": True, "errors": [], "warnings": [], "constraints": {}}
    
    def publish_content(self, content: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        # FIXME: Implement WhatsApp Business API
        return {"success": False, "error": "WhatsApp integration not implemented"}
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": False, "error": "WhatsApp integration not implemented"}


class PublishingService:
    """Main publishing service that manages platform drivers"""
    
    def __init__(self):
        self.drivers = {
            PlatformType.FACEBOOK: FacebookDriver(),
            PlatformType.INSTAGRAM: InstagramDriver(),
            PlatformType.LINKEDIN: LinkedInDriver(),
            PlatformType.GOOGLE_GBP: GoogleGBPDriver(),
            PlatformType.TIKTOK_ADS: TikTokAdsDriver(),
            PlatformType.GOOGLE_ADS: GoogleAdsDriver(),
            PlatformType.WHATSAPP: WhatsAppDriver(),
        }
    
    def get_driver(self, platform: str) -> PlatformDriver:
        """Get the appropriate driver for a platform"""
        if platform not in self.drivers:
            raise ValueError(f"Unsupported platform: {platform}")
        return self.drivers[platform]
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return list(self.drivers.keys())
    
    def is_platform_supported(self, platform: str) -> bool:
        """Check if a platform is supported"""
        return platform in self.drivers
