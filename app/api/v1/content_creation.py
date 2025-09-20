"""
Content Creation API
Handles real content creation, editing, and management
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.entities import UserAccount, Organization
from app.models.content import ContentItem, Schedule
from app.services.limits import LimitsService, LimitType
from app.services.feature_gating import FeatureGatingService, FeatureType
# from app.workers.tasks.content_tasks import generate_ai_content_task

router = APIRouter()


class ContentCreateRequest(BaseModel):
    """Request model for creating content"""
    content: str = Field(..., min_length=1, max_length=10000, description="Content text")
    platforms: List[str] = Field(..., min_items=1, description="Target platforms")
    content_type: str = Field(default="text", description="Type of content")
    scheduled_date: Optional[datetime] = Field(None, description="When to publish")
    media_urls: Optional[List[str]] = Field(None, description="Media file URLs")
    hashtags: Optional[List[str]] = Field(None, description="Hashtags")
    mentions: Optional[List[str]] = Field(None, description="User mentions")
    brand_guide_id: Optional[int] = Field(None, description="Brand guide to follow")
    locale: str = Field(default="en", description="Content locale")


class ContentResponse(BaseModel):
    """Response model for content"""
    id: int
    content: str
    platforms: List[str]
    content_type: str
    status: str
    created_at: datetime
    scheduled_date: Optional[datetime]
    media_urls: Optional[List[str]]
    hashtags: Optional[List[str]]
    mentions: Optional[List[str]]
    author_id: int
    organization_id: int


class ContentListResponse(BaseModel):
    """Response model for content list"""
    items: List[ContentResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class AIContentRequest(BaseModel):
    """Request model for AI content generation"""
    prompt: str = Field(..., min_length=1, max_length=1000)
    content_type: str = Field(default="post", description="Type of content to generate")
    brand_voice: Optional[str] = Field(None, description="Brand voice description")
    platform: Optional[str] = Field(None, description="Target platform")
    locale: str = Field(default="en", description="Content locale")


class AIContentResponse(BaseModel):
    """Response model for AI generated content"""
    content: str
    content_type: str
    platform: Optional[str]
    generated_at: datetime
    tokens_used: int
    cost_usd: float


@router.post("/create", response_model=ContentResponse)
async def create_content(
    request: ContentCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Create new content item"""
    
    # Check feature access
    limits_service = LimitsService(db)
    feature_gate = FeatureGatingService(limits_service)
    
    # Check if user has access to content creation
    content_access = feature_gate.check_feature_access(
        current_user.organization_id, 
        FeatureType.CONTENT_SCHEDULING
    )
    
    if not content_access.has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=content_access.upgrade_message
        )
    
    # Check content items limit
    content_limit = limits_service.check_limit(
        current_user.organization_id, 
        LimitType.CONTENT_ITEMS
    )
    
    if not content_limit.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Content limit reached ({content_limit.current}/{content_limit.limit}). Upgrade to create more content."
        )
    
    # Validate platforms
    valid_platforms = ["facebook", "instagram", "linkedin", "twitter", "whatsapp", "google_business"]
    for platform in request.platforms:
        if platform not in valid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform: {platform}"
            )
    
    # Create content item
    content_item = ContentItem(
        content=request.content,
        content_type=request.content_type,
        status="draft",
        author_id=current_user.id,
        organization_id=current_user.organization_id,
        media_urls=request.media_urls or [],
        hashtags=request.hashtags or [],
        mentions=request.mentions or [],
        brand_guide_id=request.brand_guide_id,
        locale=request.locale,
        created_at=datetime.utcnow()
    )
    
    db.add(content_item)
    db.commit()
    db.refresh(content_item)
    
    # Create schedule if scheduled_date is provided
    if request.scheduled_date:
        schedule = Schedule(
            content_id=content_item.id,
            scheduled_at=request.scheduled_date,
            platforms=request.platforms,
            status="scheduled",
            organization_id=current_user.organization_id,
            created_at=datetime.utcnow()
        )
        db.add(schedule)
        db.commit()
    
    return ContentResponse(
        id=content_item.id,
        content=content_item.content,
        platforms=request.platforms,
        content_type=content_item.content_type,
        status=content_item.status,
        created_at=content_item.created_at,
        scheduled_date=request.scheduled_date,
        media_urls=content_item.media_urls,
        hashtags=content_item.hashtags,
        mentions=content_item.mentions,
        author_id=content_item.author_id,
        organization_id=content_item.organization_id
    )


@router.get("/list", response_model=ContentListResponse)
async def list_content(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    content_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """List content items for the organization"""
    
    # Build query
    query = db.query(ContentItem).filter(
        ContentItem.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(ContentItem.status == status)
    
    if content_type:
        query = query.filter(ContentItem.content_type == content_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    
    # Convert to response format
    content_items = []
    for item in items:
        # Get platforms from schedules
        schedules = db.query(Schedule).filter(
            Schedule.content_id == item.id
        ).all()
        platforms = list(set([s.platforms for s in schedules]))
        
        content_items.append(ContentResponse(
            id=item.id,
            content=item.content,
            platforms=platforms,
            content_type=item.content_type,
            status=item.status,
            created_at=item.created_at,
            scheduled_date=item.scheduled_at if hasattr(item, 'scheduled_at') else None,
            media_urls=item.media_urls,
            hashtags=item.hashtags,
            mentions=item.mentions,
            author_id=item.author_id,
            organization_id=item.organization_id
        ))
    
    return ContentListResponse(
        items=content_items,
        total=total,
        page=page,
        per_page=per_page,
        has_next=offset + per_page < total,
        has_prev=page > 1
    )


@router.post("/ai/generate", response_model=AIContentResponse)
async def generate_ai_content(
    request: AIContentRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Generate content using AI"""
    
    # Check feature access
    limits_service = LimitsService(db)
    feature_gate = FeatureGatingService(limits_service)
    
    ai_access = feature_gate.check_feature_access(
        current_user.organization_id, 
        FeatureType.AI_CONTENT_GENERATION
    )
    
    if not ai_access.has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ai_access.upgrade_message
        )
    
    # Check AI generations limit
    ai_limit = limits_service.check_limit(
        current_user.organization_id, 
        LimitType.AI_GENERATIONS
    )
    
    if not ai_limit.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"AI generation limit reached ({ai_limit.current}/{ai_limit.limit}). Upgrade to generate more content."
        )
    
    try:
        # Generate AI content (this would call the actual AI service)
        # For now, we'll simulate the response
        generated_content = f"AI Generated Content: {request.prompt[:100]}..."
        
        # In a real implementation, this would call the AI service
        # ai_service = AIService()
        # result = await ai_service.generate_content(
        #     prompt=request.prompt,
        #     content_type=request.content_type,
        #     brand_voice=request.brand_voice,
        #     platform=request.platform,
        #     locale=request.locale
        # )
        
        return AIContentResponse(
            content=generated_content,
            content_type=request.content_type,
            platform=request.platform,
            generated_at=datetime.utcnow(),
            tokens_used=100,  # Simulated
            cost_usd=0.01  # Simulated
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI content: {str(e)}"
        )


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    request: ContentCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Update existing content item"""
    
    # Get content item
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.organization_id == current_user.organization_id
    ).first()
    
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found"
        )
    
    # Update content
    content_item.content = request.content
    content_item.content_type = request.content_type
    content_item.media_urls = request.media_urls or []
    content_item.hashtags = request.hashtags or []
    content_item.mentions = request.mentions or []
    content_item.brand_guide_id = request.brand_guide_id
    content_item.locale = request.locale
    content_item.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(content_item)
    
    return ContentResponse(
        id=content_item.id,
        content=content_item.content,
        platforms=request.platforms,
        content_type=content_item.content_type,
        status=content_item.status,
        created_at=content_item.created_at,
        scheduled_date=request.scheduled_date,
        media_urls=content_item.media_urls,
        hashtags=content_item.hashtags,
        mentions=content_item.mentions,
        author_id=content_item.author_id,
        organization_id=content_item.organization_id
    )


@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Delete content item"""
    
    # Get content item
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.organization_id == current_user.organization_id
    ).first()
    
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found"
        )
    
    # Delete associated schedules
    db.query(Schedule).filter(Schedule.content_id == content_id).delete()
    
    # Delete content item
    db.delete(content_item)
    db.commit()
    
    return {"message": "Content deleted successfully"}


@router.get("/stats")
async def get_content_stats(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Get content statistics for the organization"""
    
    # Get content counts by status
    total_content = db.query(ContentItem).filter(
        ContentItem.organization_id == current_user.organization_id
    ).count()
    
    draft_content = db.query(ContentItem).filter(
        ContentItem.organization_id == current_user.organization_id,
        ContentItem.status == "draft"
    ).count()
    
    scheduled_content = db.query(ContentItem).filter(
        ContentItem.organization_id == current_user.organization_id,
        ContentItem.status == "scheduled"
    ).count()
    
    published_content = db.query(ContentItem).filter(
        ContentItem.organization_id == current_user.organization_id,
        ContentItem.status == "published"
    ).count()
    
    # Get content by type
    content_by_type = db.query(
        ContentItem.content_type,
        db.func.count(ContentItem.id).label('count')
    ).filter(
        ContentItem.organization_id == current_user.organization_id
    ).group_by(ContentItem.content_type).all()
    
    return {
        "total_content": total_content,
        "draft_content": draft_content,
        "scheduled_content": scheduled_content,
        "published_content": published_content,
        "content_by_type": {item.content_type: item.count for item in content_by_type}
    }
