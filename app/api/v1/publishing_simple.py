"""
Simple Publishing API
A minimal publishing endpoint that works with existing publisher infrastructure
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.services.publishers import PublisherRegistry
from app.models.publishing import PlatformType

logger = logging.getLogger(__name__)
router = APIRouter()


class MediaItem(BaseModel):
    url: str
    type: str  # "image", "video"
    caption: Optional[str] = None


class PublishRequest(BaseModel):
    content: str
    platform: str  # "facebook", "instagram", "linkedin", "google_gbp"
    media: List[MediaItem] = []
    page_id: Optional[str] = None
    access_token: Optional[str] = None


class PublishResponse(BaseModel):
    success: bool
    platform: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    message: str
    errors: List[str] = []


class PreviewRequest(BaseModel):
    content: str
    platform: str
    media: List[MediaItem] = []


class PreviewResponse(BaseModel):
    is_valid: bool
    sanitized_content: str
    character_count: int
    warnings: List[str] = []
    errors: List[str] = []
    constraints: Dict[str, Any] = {}


@router.post("/publish/preview", response_model=PreviewResponse)
async def preview_content(request: PreviewRequest) -> PreviewResponse:
    """
    Preview and validate content for a specific platform
    """
    try:
        # Map string platform to PlatformType enum
        platform_map = {
            "facebook": PlatformType.FACEBOOK,
            "instagram": PlatformType.INSTAGRAM,
            "linkedin": PlatformType.LINKEDIN,
            "google_gbp": PlatformType.GOOGLE_GBP
        }
        
        if request.platform not in platform_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {request.platform}"
            )
        
        platform_type = platform_map[request.platform]
        
        # Get publisher
        publisher = PublisherRegistry.get_publisher(platform_type)
        
        # Convert media items
        from app.services.publishers.base import MediaItem as PublisherMediaItem
        media_items = [
            PublisherMediaItem(
                url=item.url,
                type=item.type,
                alt_text=item.caption
            ) for item in request.media
        ]
        
        # Create platform options (minimal for preview)
        from app.services.publishers.base import PlatformOptions
        platform_opts = PlatformOptions(
            platform=platform_type,
            account_id="preview",
            settings={}
        )
        
        # Get preview
        preview = await publisher.preview(request.content, media_items, platform_opts)
        
        return PreviewResponse(
            is_valid=preview.is_valid,
            sanitized_content=preview.sanitized_content,
            character_count=preview.character_count,
            warnings=preview.warnings,
            errors=preview.errors,
            constraints=preview.constraints_applied
        )
        
    except Exception as e:
        logger.error(f"Preview error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview failed: {str(e)}"
        )


@router.post("/publish/test", response_model=PublishResponse)
async def test_publish(request: PublishRequest) -> PublishResponse:
    """
    Test publishing (dry run) - validates content without actually posting
    """
    try:
        # Map string platform to PlatformType enum
        platform_map = {
            "facebook": PlatformType.FACEBOOK,
            "instagram": PlatformType.INSTAGRAM,
            "linkedin": PlatformType.LINKEDIN,
            "google_gbp": PlatformType.GOOGLE_GBP
        }
        
        if request.platform not in platform_map:
            return PublishResponse(
                success=False,
                platform=request.platform,
                message=f"Unsupported platform: {request.platform}",
                errors=[f"Platform {request.platform} is not supported"]
            )
        
        platform_type = platform_map[request.platform]
        
        # Get publisher
        publisher = PublisherRegistry.get_publisher(platform_type)
        
        # Convert media items
        from app.services.publishers.base import MediaItem as PublisherMediaItem
        media_items = [
            PublisherMediaItem(
                url=item.url,
                type=item.type,
                alt_text=item.caption
            ) for item in request.media
        ]
        
        # Create platform options
        from app.services.publishers.base import PlatformOptions
        platform_opts = PlatformOptions(
            platform=platform_type,
            account_id="test_user",
            settings={
                "access_token": request.access_token or "test_token",
                "page_id": request.page_id or "test_page"
            }
        )
        
        # Preview content
        preview = await publisher.preview(request.content, media_items, platform_opts)
        
        if not preview.is_valid:
            return PublishResponse(
                success=False,
                platform=request.platform,
                message="Content validation failed",
                errors=preview.errors
            )
        
        # For test mode, we don't actually publish
        return PublishResponse(
            success=True,
            platform=request.platform,
            post_id="test_post_123",
            url=f"https://{request.platform}.com/test_post_123",
            message="Test publish successful - content is valid and ready to publish",
            errors=[]
        )
        
    except Exception as e:
        logger.error(f"Test publish error: {e}")
        return PublishResponse(
            success=False,
            platform=request.platform,
            message=f"Test publish failed: {str(e)}",
            errors=[str(e)]
        )


@router.get("/publish/platforms")
async def get_supported_platforms():
    """Get list of supported publishing platforms"""
    return {
        "platforms": [
            {
                "id": "facebook",
                "name": "Facebook",
                "max_text_length": 2200,
                "max_media_items": 10,
                "supported_media": ["image", "video"]
            },
            {
                "id": "instagram",
                "name": "Instagram",
                "max_text_length": 2200,
                "max_media_items": 10,
                "supported_media": ["image", "video"]
            },
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "max_text_length": 3000,
                "max_media_items": 9,
                "supported_media": ["image"]
            },
            {
                "id": "google_gbp",
                "name": "Google Business Profile",
                "max_text_length": 1500,
                "max_media_items": 10,
                "supported_media": ["image", "video"]
            }
        ]
    }


@router.get("/publish/status")
async def get_publishing_status():
    """Get publishing service status"""
    return {
        "status": "operational",
        "supported_platforms": ["facebook", "instagram", "linkedin", "google_gbp"],
        "features": [
            "content_preview",
            "content_validation", 
            "test_publishing",
            "platform_optimization"
        ],
        "version": "1.0.0",
        "message": "Publishing service is ready!"
    }
