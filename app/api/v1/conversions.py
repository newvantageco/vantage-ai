from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets

from app.db.session import get_db
from app.models.conversions import Conversion, ConversionGoal, ConversionAttribution, ConversionTypes, ConversionSources
from app.models.entities import Organization
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()


class ConversionTrack(BaseModel):
    tracking_code: str
    conversion_type: str
    value_cents: Optional[int] = None
    user_ref: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None


class ConversionGoalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    conversion_type: str
    value_cents: Optional[int] = None
    attribution_window_days: int = 30
    require_utm: bool = False


class ConversionGoalResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    conversion_type: str
    tracking_code: str
    value_cents: Optional[int]
    attribution_window_days: int
    require_utm: bool
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class ConversionReport(BaseModel):
    total_conversions: int
    total_value_cents: int
    conversions_by_type: Dict[str, int]
    conversions_by_source: Dict[str, int]
    conversions_by_campaign: Dict[str, int]
    top_content: List[Dict[str, Any]]
    conversion_rate: float
    avg_value_cents: float


@router.post("/conversions/track")
async def track_conversion(
    conversion_data: ConversionTrack,
    db: Session = Depends(get_db)
):
    """Track a conversion (public endpoint with tracking code)."""
    
    # Find the conversion goal by tracking code
    goal = db.query(ConversionGoal).filter(
        ConversionGoal.tracking_code == conversion_data.tracking_code,
        ConversionGoal.is_active == True
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid tracking code"
        )
    
    # Validate conversion type
    if not ConversionTypes.validate_type(conversion_data.conversion_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversion type. Must be one of: {ConversionTypes.ALL_TYPES}"
        )
    
    # Create conversion record
    conversion = Conversion(
        id=secrets.token_urlsafe(16),
        org_id=goal.org_id,
        conversion_type=conversion_data.conversion_type,
        source=conversion_data.utm_source or "direct",
        value_cents=conversion_data.value_cents or goal.value_cents,
        user_ref=conversion_data.user_ref,
        utm_source=conversion_data.utm_source,
        utm_medium=conversion_data.utm_medium,
        utm_campaign=conversion_data.utm_campaign,
        utm_term=conversion_data.utm_term,
        utm_content=conversion_data.utm_content,
        page_url=conversion_data.page_url,
        referrer=conversion_data.referrer
    )
    
    db.add(conversion)
    db.commit()
    db.refresh(conversion)
    
    # TODO: Find and create attribution records
    # This would look for recent content (schedules, ads) that might have led to this conversion
    
    return {
        "message": "Conversion tracked successfully",
        "conversion_id": conversion.id,
        "tracking_code": conversion_data.tracking_code
    }


@router.post("/conversions/goals", response_model=ConversionGoalResponse)
async def create_conversion_goal(
    goal_data: ConversionGoalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversion goal."""
    
    # Validate conversion type
    if not ConversionTypes.validate_type(goal_data.conversion_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversion type. Must be one of: {ConversionTypes.ALL_TYPES}"
        )
    
    # Generate unique tracking code
    tracking_code = ConversionGoal.generate_tracking_code()
    
    # Create conversion goal
    goal = ConversionGoal(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        name=goal_data.name,
        description=goal_data.description,
        conversion_type=goal_data.conversion_type,
        tracking_code=tracking_code,
        value_cents=goal_data.value_cents,
        attribution_window_days=goal_data.attribution_window_days,
        require_utm=goal_data.require_utm
    )
    
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    return ConversionGoalResponse(
        id=goal.id,
        name=goal.name,
        description=goal.description,
        conversion_type=goal.conversion_type,
        tracking_code=goal.tracking_code,
        value_cents=goal.value_cents,
        attribution_window_days=goal.attribution_window_days,
        require_utm=goal.require_utm,
        is_active=goal.is_active,
        created_at=goal.created_at.isoformat()
    )


@router.get("/conversions/goals", response_model=List[ConversionGoalResponse])
async def list_conversion_goals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List conversion goals for the organization."""
    goals = db.query(ConversionGoal).filter(
        ConversionGoal.org_id == current_user["org_id"]
    ).all()
    
    return [
        ConversionGoalResponse(
            id=goal.id,
            name=goal.name,
            description=goal.description,
            conversion_type=goal.conversion_type,
            tracking_code=goal.tracking_code,
            value_cents=goal.value_cents,
            attribution_window_days=goal.attribution_window_days,
            require_utm=goal.require_utm,
            is_active=goal.is_active,
            created_at=goal.created_at.isoformat()
        )
        for goal in goals
    ]


@router.get("/conversions/goals/{goal_id}", response_model=ConversionGoalResponse)
async def get_conversion_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific conversion goal."""
    goal = db.query(ConversionGoal).filter(
        ConversionGoal.id == goal_id,
        ConversionGoal.org_id == current_user["org_id"]
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversion goal not found"
        )
    
    return ConversionGoalResponse(
        id=goal.id,
        name=goal.name,
        description=goal.description,
        conversion_type=goal.conversion_type,
        tracking_code=goal.tracking_code,
        value_cents=goal.value_cents,
        attribution_window_days=goal.attribution_window_days,
        require_utm=goal.require_utm,
        is_active=goal.is_active,
        created_at=goal.created_at.isoformat()
    )


@router.put("/conversions/goals/{goal_id}", response_model=ConversionGoalResponse)
async def update_conversion_goal(
    goal_id: str,
    goal_data: ConversionGoalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a conversion goal."""
    goal = db.query(ConversionGoal).filter(
        ConversionGoal.id == goal_id,
        ConversionGoal.org_id == current_user["org_id"]
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversion goal not found"
        )
    
    # Validate conversion type
    if not ConversionTypes.validate_type(goal_data.conversion_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversion type. Must be one of: {ConversionTypes.ALL_TYPES}"
        )
    
    # Update fields
    goal.name = goal_data.name
    goal.description = goal_data.description
    goal.conversion_type = goal_data.conversion_type
    goal.value_cents = goal_data.value_cents
    goal.attribution_window_days = goal_data.attribution_window_days
    goal.require_utm = goal_data.require_utm
    
    db.commit()
    db.refresh(goal)
    
    return ConversionGoalResponse(
        id=goal.id,
        name=goal.name,
        description=goal.description,
        conversion_type=goal.conversion_type,
        tracking_code=goal.tracking_code,
        value_cents=goal.value_cents,
        attribution_window_days=goal.attribution_window_days,
        require_utm=goal.require_utm,
        is_active=goal.is_active,
        created_at=goal.created_at.isoformat()
    )


@router.delete("/conversions/goals/{goal_id}")
async def delete_conversion_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversion goal."""
    goal = db.query(ConversionGoal).filter(
        ConversionGoal.id == goal_id,
        ConversionGoal.org_id == current_user["org_id"]
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversion goal not found"
        )
    
    db.delete(goal)
    db.commit()
    
    return {"message": "Conversion goal deleted successfully"}


@router.get("/conversions/report", response_model=ConversionReport)
async def get_conversion_report(
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    campaign: Optional[str] = Query(None, description="Filter by campaign"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get conversion report with analytics."""
    
    # Calculate date range
    if from_date:
        try:
            start_date = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid from_date format"
            )
    else:
        start_date = datetime.utcnow() - timedelta(days=30)
    
    if to_date:
        try:
            end_date = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid to_date format"
            )
    else:
        end_date = datetime.utcnow()
    
    # Build base query
    query = db.query(Conversion).filter(
        Conversion.org_id == current_user["org_id"],
        Conversion.created_at >= start_date,
        Conversion.created_at <= end_date
    )
    
    # Apply filters
    if channel:
        # This would need to join with schedules/channels
        pass
    
    if campaign:
        # This would need to join with campaigns
        pass
    
    # Get all conversions
    conversions = query.all()
    
    # Calculate metrics
    total_conversions = len(conversions)
    total_value_cents = sum(c.value_cents or 0 for c in conversions)
    avg_value_cents = total_value_cents / total_conversions if total_conversions > 0 else 0
    
    # Group by conversion type
    conversions_by_type = {}
    for conv in conversions:
        conv_type = conv.conversion_type
        conversions_by_type[conv_type] = conversions_by_type.get(conv_type, 0) + 1
    
    # Group by source
    conversions_by_source = {}
    for conv in conversions:
        source = conv.source
        conversions_by_source[source] = conversions_by_source.get(source, 0) + 1
    
    # Group by campaign (UTM)
    conversions_by_campaign = {}
    for conv in conversions:
        campaign = conv.utm_campaign or "No Campaign"
        conversions_by_campaign[campaign] = conversions_by_campaign.get(campaign, 0) + 1
    
    # Get top content (this would need to join with attribution data)
    top_content = []
    
    # Calculate conversion rate (this would need total visitors/impressions)
    conversion_rate = 0.0  # This would be calculated based on total traffic
    
    return ConversionReport(
        total_conversions=total_conversions,
        total_value_cents=total_value_cents,
        conversions_by_type=conversions_by_type,
        conversions_by_source=conversions_by_source,
        conversions_by_campaign=conversions_by_campaign,
        top_content=top_content,
        conversion_rate=conversion_rate,
        avg_value_cents=avg_value_cents
    )


@router.get("/conversions")
async def list_conversions(
    conversion_type: Optional[str] = Query(None, description="Filter by conversion type"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List conversions with optional filtering."""
    query = db.query(Conversion).filter(Conversion.org_id == current_user["org_id"])
    
    if conversion_type:
        query = query.filter(Conversion.conversion_type == conversion_type)
    
    if source:
        query = query.filter(Conversion.source == source)
    
    conversions = query.order_by(desc(Conversion.created_at)).offset(offset).limit(limit).all()
    
    return [
        {
            "id": conv.id,
            "conversion_type": conv.conversion_type,
            "source": conv.source,
            "value_cents": conv.value_cents,
            "user_ref": conv.user_ref,
            "utm_source": conv.utm_source,
            "utm_medium": conv.utm_medium,
            "utm_campaign": conv.utm_campaign,
            "utm_term": conv.utm_term,
            "utm_content": conv.utm_content,
            "page_url": conv.page_url,
            "referrer": conv.referrer,
            "created_at": conv.created_at.isoformat()
        }
        for conv in conversions
    ]


@router.get("/conversions/available-types")
async def get_available_conversion_types():
    """Get available conversion types and sources."""
    return {
        "conversion_types": [
            {"id": ConversionTypes.FORM_FILL, "name": "Form Fill", "description": "User filled out a form"},
            {"id": ConversionTypes.PURCHASE, "name": "Purchase", "description": "User made a purchase"},
            {"id": ConversionTypes.SIGNUP, "name": "Signup", "description": "User signed up for an account"},
            {"id": ConversionTypes.DOWNLOAD, "name": "Download", "description": "User downloaded a file"},
            {"id": ConversionTypes.CLICK, "name": "Click", "description": "User clicked a link"},
            {"id": ConversionTypes.VIEW, "name": "View", "description": "User viewed a page"},
            {"id": ConversionTypes.CUSTOM, "name": "Custom", "description": "Custom conversion type"}
        ],
        "sources": [
            {"id": ConversionSources.ORGANIC, "name": "Organic", "description": "Organic search or direct traffic"},
            {"id": ConversionSources.PAID, "name": "Paid", "description": "Paid advertising"},
            {"id": ConversionSources.EMAIL, "name": "Email", "description": "Email marketing"},
            {"id": ConversionSources.DIRECT, "name": "Direct", "description": "Direct traffic"},
            {"id": ConversionSources.REFERRAL, "name": "Referral", "description": "Referral traffic"},
            {"id": ConversionSources.SOCIAL, "name": "Social", "description": "Social media"},
            {"id": ConversionSources.CUSTOM, "name": "Custom", "description": "Custom source"}
        ]
    }
