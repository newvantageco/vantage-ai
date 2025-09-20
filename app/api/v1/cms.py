"""
CMS API Router
Handles content management, campaigns, brand guides, and scheduling
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.schemas.cms import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    ContentItemCreate, ContentItemUpdate, ContentItemResponse,
    BrandGuideCreate, BrandGuideUpdate, BrandGuideResponse,
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    CalendarRequest, CalendarResponse, CalendarItem,
    UserAccountResponse
)
from app.models.cms import (
    Campaign, ContentItem, BrandGuide, Schedule, Organization, UserAccount
)

router = APIRouter()


# Campaign endpoints
@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> CampaignResponse:
    """Create a new campaign."""
    db_campaign = Campaign(
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        **campaign.dict()
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return CampaignResponse.from_orm(db_campaign)


@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[CampaignResponse]:
    """List campaigns for the current organization."""
    campaigns = db.query(Campaign).filter(
        Campaign.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return [CampaignResponse.from_orm(campaign) for campaign in campaigns]


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> CampaignResponse:
    """Get a specific campaign."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user.organization_id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignResponse.from_orm(campaign)


@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> CampaignResponse:
    """Update a campaign."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user.organization_id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    update_data = campaign_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    return CampaignResponse.from_orm(campaign)


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Delete a campaign."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user.organization_id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    db.delete(campaign)
    db.commit()


# Content Item endpoints
@router.post("/content", response_model=ContentItemResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content: ContentItemCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentItemResponse:
    """Create a new content item."""
    db_content = ContentItem(
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        **content.dict()
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return ContentItemResponse.from_orm(db_content)


@router.get("/content", response_model=List[ContentItemResponse])
async def list_content(
    skip: int = 0,
    limit: int = 20,
    campaign_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ContentItemResponse]:
    """List content items for the current organization."""
    query = db.query(ContentItem).filter(
        ContentItem.organization_id == current_user.organization_id
    )
    
    if campaign_id:
        query = query.filter(ContentItem.campaign_id == campaign_id)
    if status:
        query = query.filter(ContentItem.status == status)
    
    content_items = query.offset(skip).limit(limit).all()
    return [ContentItemResponse.from_orm(item) for item in content_items]


@router.get("/content/{content_id}", response_model=ContentItemResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentItemResponse:
    """Get a specific content item."""
    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.organization_id == current_user.organization_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found"
        )
    
    return ContentItemResponse.from_orm(content)


@router.put("/content/{content_id}", response_model=ContentItemResponse)
async def update_content(
    content_id: int,
    content_update: ContentItemUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentItemResponse:
    """Update a content item."""
    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.organization_id == current_user.organization_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found"
        )
    
    update_data = content_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    db.commit()
    db.refresh(content)
    return ContentItemResponse.from_orm(content)


@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Delete a content item."""
    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.organization_id == current_user.organization_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found"
        )
    
    db.delete(content)
    db.commit()


# Brand Guide endpoints
@router.post("/brand-guides", response_model=BrandGuideResponse, status_code=status.HTTP_201_CREATED)
async def create_brand_guide(
    brand_guide: BrandGuideCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BrandGuideResponse:
    """Create a new brand guide."""
    db_brand_guide = BrandGuide(
        organization_id=current_user.organization_id,
        **brand_guide.dict()
    )
    db.add(db_brand_guide)
    db.commit()
    db.refresh(db_brand_guide)
    return BrandGuideResponse.from_orm(db_brand_guide)


@router.get("/brand-guides", response_model=List[BrandGuideResponse])
async def list_brand_guides(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[BrandGuideResponse]:
    """List brand guides for the current organization."""
    brand_guides = db.query(BrandGuide).filter(
        BrandGuide.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return [BrandGuideResponse.from_orm(guide) for guide in brand_guides]


@router.get("/brand-guides/{brand_guide_id}", response_model=BrandGuideResponse)
async def get_brand_guide(
    brand_guide_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BrandGuideResponse:
    """Get a specific brand guide."""
    brand_guide = db.query(BrandGuide).filter(
        BrandGuide.id == brand_guide_id,
        BrandGuide.organization_id == current_user.organization_id
    ).first()
    
    if not brand_guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand guide not found"
        )
    
    return BrandGuideResponse.from_orm(brand_guide)


@router.put("/brand-guides/{brand_guide_id}", response_model=BrandGuideResponse)
async def update_brand_guide(
    brand_guide_id: int,
    brand_guide_update: BrandGuideUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BrandGuideResponse:
    """Update a brand guide."""
    brand_guide = db.query(BrandGuide).filter(
        BrandGuide.id == brand_guide_id,
        BrandGuide.organization_id == current_user.organization_id
    ).first()
    
    if not brand_guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand guide not found"
        )
    
    update_data = brand_guide_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand_guide, field, value)
    
    db.commit()
    db.refresh(brand_guide)
    return BrandGuideResponse.from_orm(brand_guide)


@router.delete("/brand-guides/{brand_guide_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand_guide(
    brand_guide_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Delete a brand guide."""
    brand_guide = db.query(BrandGuide).filter(
        BrandGuide.id == brand_guide_id,
        BrandGuide.organization_id == current_user.organization_id
    ).first()
    
    if not brand_guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand guide not found"
        )
    
    db.delete(brand_guide)
    db.commit()


# Schedule endpoints
@router.post("/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ScheduleResponse:
    """Create a new schedule."""
    # Verify content item exists and belongs to organization
    content = db.query(ContentItem).filter(
        ContentItem.id == schedule.content_item_id,
        ContentItem.organization_id == current_user.organization_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found"
        )
    
    db_schedule = Schedule(
        organization_id=current_user.organization_id,
        **schedule.dict()
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return ScheduleResponse.from_orm(db_schedule)


@router.get("/schedules", response_model=List[ScheduleResponse])
async def list_schedules(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ScheduleResponse]:
    """List schedules for the current organization."""
    schedules = db.query(Schedule).filter(
        Schedule.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return [ScheduleResponse.from_orm(schedule) for schedule in schedules]


# Calendar endpoint
@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    start_date: datetime = Query(..., description="Start date for calendar"),
    end_date: datetime = Query(..., description="End date for calendar"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> CalendarResponse:
    """Get paginated list of scheduled posts by date range."""
    skip = (page - 1) * size
    
    # Query scheduled posts in date range
    schedules = db.query(Schedule).join(ContentItem).filter(
        Schedule.organization_id == current_user.organization_id,
        Schedule.scheduled_at >= start_date,
        Schedule.scheduled_at <= end_date
    ).offset(skip).limit(size).all()
    
    # Get total count
    total = db.query(Schedule).join(ContentItem).filter(
        Schedule.organization_id == current_user.organization_id,
        Schedule.scheduled_at >= start_date,
        Schedule.scheduled_at <= end_date
    ).count()
    
    # Build calendar items
    items = []
    for schedule in schedules:
        content = schedule.content_item
        user = db.query(UserAccount).filter(UserAccount.id == content.created_by_id).first()
        
        items.append(CalendarItem(
            id=schedule.id,
            title=content.title,
            content=content.content,
            scheduled_at=schedule.scheduled_at,
            platforms=schedule.platforms,
            status=schedule.status,
            content_type=content.content_type,
            created_by=user.first_name + " " + user.last_name if user else "Unknown"
        ))
    
    total_pages = (total + size - 1) // size
    
    return CalendarResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )