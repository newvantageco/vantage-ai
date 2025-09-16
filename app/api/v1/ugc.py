from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import secrets

from app.db.session import get_db
from app.models.ugc import UGCAsset, UGCRequest, UGCUsage, UGCStatus, UGCRequestStatus, UGCChannel
from app.models.entities import Organization
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()


class UGCAssetCreate(BaseModel):
    source_url: str
    asset_type: str
    platform: str
    platform_id: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    author_username: Optional[str] = None
    author_display_name: Optional[str] = None
    author_profile_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    media_url: Optional[str] = None
    media_width: Optional[int] = None
    media_height: Optional[int] = None


class UGCAssetResponse(BaseModel):
    id: str
    source_url: str
    asset_type: str
    platform: str
    platform_id: Optional[str]
    status: str
    rights_status: str
    rights_proof_url: Optional[str]
    caption: Optional[str]
    hashtags: Optional[str]
    author_username: Optional[str]
    author_display_name: Optional[str]
    author_profile_url: Optional[str]
    thumbnail_url: Optional[str]
    media_url: Optional[str]
    media_width: Optional[int]
    media_height: Optional[int]
    created_at: str
    updated_at: str
    rights_expires_at: Optional[str]

    class Config:
        from_attributes = True


class UGCRequestCreate(BaseModel):
    asset_id: str
    message: str
    channel: str
    expires_at: Optional[str] = None


class UGCRequestResponse(BaseModel):
    id: str
    asset_id: str
    message: str
    channel: str
    status: str
    platform_message_id: Optional[str]
    platform_thread_id: Optional[str]
    response_message: Optional[str]
    response_choice: Optional[str]
    sent_at: Optional[str]
    responded_at: Optional[str]
    expires_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class UGCUsageCreate(BaseModel):
    asset_id: str
    campaign_id: Optional[str] = None
    schedule_id: Optional[str] = None
    usage_type: str
    platform: str
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    impressions: Optional[int] = None
    engagement: Optional[int] = None


@router.post("/ugc/assets", response_model=UGCAssetResponse)
async def create_ugc_asset(
    asset_data: UGCAssetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new UGC asset."""
    ugc_asset = UGCAsset(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        source_url=asset_data.source_url,
        asset_type=asset_data.asset_type,
        platform=asset_data.platform,
        platform_id=asset_data.platform_id,
        caption=asset_data.caption,
        hashtags=asset_data.hashtags,
        author_username=asset_data.author_username,
        author_display_name=asset_data.author_display_name,
        author_profile_url=asset_data.author_profile_url,
        thumbnail_url=asset_data.thumbnail_url,
        media_url=asset_data.media_url,
        media_width=asset_data.media_width,
        media_height=asset_data.media_height,
        status=UGCStatus.pending,
        rights_status="pending"
    )
    
    db.add(ugc_asset)
    db.commit()
    db.refresh(ugc_asset)
    
    return UGCAssetResponse(
        id=ugc_asset.id,
        source_url=ugc_asset.source_url,
        asset_type=ugc_asset.asset_type,
        platform=ugc_asset.platform,
        platform_id=ugc_asset.platform_id,
        status=ugc_asset.status.value,
        rights_status=ugc_asset.rights_status,
        rights_proof_url=ugc_asset.rights_proof_url,
        caption=ugc_asset.caption,
        hashtags=ugc_asset.hashtags,
        author_username=ugc_asset.author_username,
        author_display_name=ugc_asset.author_display_name,
        author_profile_url=ugc_asset.author_profile_url,
        thumbnail_url=ugc_asset.thumbnail_url,
        media_url=ugc_asset.media_url,
        media_width=ugc_asset.media_width,
        media_height=ugc_asset.media_height,
        created_at=ugc_asset.created_at.isoformat(),
        updated_at=ugc_asset.updated_at.isoformat(),
        rights_expires_at=ugc_asset.rights_expires_at.isoformat() if ugc_asset.rights_expires_at else None
    )


@router.get("/ugc/assets", response_model=List[UGCAssetResponse])
async def list_ugc_assets(
    status: Optional[str] = None,
    rights_status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List UGC assets with optional filtering."""
    query = db.query(UGCAsset).filter(UGCAsset.org_id == current_user["org_id"])
    
    if status:
        query = query.filter(UGCAsset.status == status)
    if rights_status:
        query = query.filter(UGCAsset.rights_status == rights_status)
    if platform:
        query = query.filter(UGCAsset.platform == platform)
    
    assets = query.offset(offset).limit(limit).all()
    
    return [
        UGCAssetResponse(
            id=asset.id,
            source_url=asset.source_url,
            asset_type=asset.asset_type,
            platform=asset.platform,
            platform_id=asset.platform_id,
            status=asset.status.value,
            rights_status=asset.rights_status,
            rights_proof_url=asset.rights_proof_url,
            caption=asset.caption,
            hashtags=asset.hashtags,
            author_username=asset.author_username,
            author_display_name=asset.author_display_name,
            author_profile_url=asset.author_profile_url,
            thumbnail_url=asset.thumbnail_url,
            media_url=asset.media_url,
            media_width=asset.media_width,
            media_height=asset.media_height,
            created_at=asset.created_at.isoformat(),
            updated_at=asset.updated_at.isoformat(),
            rights_expires_at=asset.rights_expires_at.isoformat() if asset.rights_expires_at else None
        )
        for asset in assets
    ]


@router.get("/ugc/assets/{asset_id}", response_model=UGCAssetResponse)
async def get_ugc_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific UGC asset."""
    asset = db.query(UGCAsset).filter(
        UGCAsset.id == asset_id,
        UGCAsset.org_id == current_user["org_id"]
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UGC asset not found"
        )
    
    return UGCAssetResponse(
        id=asset.id,
        source_url=asset.source_url,
        asset_type=asset.asset_type,
        platform=asset.platform,
        platform_id=asset.platform_id,
        status=asset.status.value,
        rights_status=asset.rights_status,
        rights_proof_url=asset.rights_proof_url,
        caption=asset.caption,
        hashtags=asset.hashtags,
        author_username=asset.author_username,
        author_display_name=asset.author_display_name,
        author_profile_url=asset.author_profile_url,
        thumbnail_url=asset.thumbnail_url,
        media_url=asset.media_url,
        media_width=asset.media_width,
        media_height=asset.media_height,
        created_at=asset.created_at.isoformat(),
        updated_at=asset.updated_at.isoformat(),
        rights_expires_at=asset.rights_expires_at.isoformat() if asset.rights_expires_at else None
    )


@router.post("/ugc/request", response_model=UGCRequestResponse)
async def create_ugc_request(
    request_data: UGCRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a UGC consent request."""
    # Verify asset exists and belongs to org
    asset = db.query(UGCAsset).filter(
        UGCAsset.id == request_data.asset_id,
        UGCAsset.org_id == current_user["org_id"]
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UGC asset not found"
        )
    
    # Create request
    ugc_request = UGCRequest(
        id=secrets.token_urlsafe(16),
        asset_id=request_data.asset_id,
        org_id=current_user["org_id"],
        message=request_data.message,
        channel=UGCChannel(request_data.channel),
        status=UGCRequestStatus.sent,
        expires_at=datetime.fromisoformat(request_data.expires_at) if request_data.expires_at else None
    )
    
    db.add(ugc_request)
    db.commit()
    db.refresh(ugc_request)
    
    # TODO: Send actual DM/email based on channel
    # This would integrate with the messaging system
    
    return UGCRequestResponse(
        id=ugc_request.id,
        asset_id=ugc_request.asset_id,
        message=ugc_request.message,
        channel=ugc_request.channel.value,
        status=ugc_request.status.value,
        platform_message_id=ugc_request.platform_message_id,
        platform_thread_id=ugc_request.platform_thread_id,
        response_message=ugc_request.response_message,
        response_choice=ugc_request.response_choice,
        sent_at=ugc_request.sent_at.isoformat() if ugc_request.sent_at else None,
        responded_at=ugc_request.responded_at.isoformat() if ugc_request.responded_at else None,
        expires_at=ugc_request.expires_at.isoformat() if ugc_request.expires_at else None,
        created_at=ugc_request.created_at.isoformat()
    )


@router.post("/ugc/callback")
async def handle_ugc_callback(
    request_id: str,
    response_choice: str,
    response_message: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle UGC consent response callback."""
    ugc_request = db.query(UGCRequest).filter(UGCRequest.id == request_id).first()
    
    if not ugc_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UGC request not found"
        )
    
    # Update request
    ugc_request.status = UGCRequestStatus.responded
    ugc_request.response_choice = response_choice
    ugc_request.response_message = response_message
    ugc_request.responded_at = datetime.utcnow()
    
    # Update asset rights status
    asset = db.query(UGCAsset).filter(UGCAsset.id == ugc_request.asset_id).first()
    if asset:
        if response_choice.upper() == "YES":
            asset.rights_status = "granted"
            asset.status = UGCStatus.approved
        else:
            asset.rights_status = "denied"
            asset.status = UGCStatus.rejected
    
    db.commit()
    
    return {"message": "UGC response recorded successfully"}


@router.post("/ugc/usage", response_model=dict)
async def record_ugc_usage(
    usage_data: UGCUsageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Record usage of a UGC asset."""
    # Verify asset exists and has granted rights
    asset = db.query(UGCAsset).filter(
        UGCAsset.id == usage_data.asset_id,
        UGCAsset.org_id == current_user["org_id"],
        UGCAsset.rights_status == "granted"
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UGC asset not found or rights not granted"
        )
    
    # Create usage record
    ugc_usage = UGCUsage(
        id=secrets.token_urlsafe(16),
        asset_id=usage_data.asset_id,
        org_id=current_user["org_id"],
        campaign_id=usage_data.campaign_id,
        schedule_id=usage_data.schedule_id,
        usage_type=usage_data.usage_type,
        platform=usage_data.platform,
        platform_post_id=usage_data.platform_post_id,
        platform_url=usage_data.platform_url,
        impressions=usage_data.impressions,
        engagement=usage_data.engagement
    )
    
    db.add(ugc_usage)
    db.commit()
    
    return {"message": "UGC usage recorded successfully"}


@router.get("/ugc/requests", response_model=List[UGCRequestResponse])
async def list_ugc_requests(
    asset_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List UGC requests with optional filtering."""
    query = db.query(UGCRequest).filter(UGCRequest.org_id == current_user["org_id"])
    
    if asset_id:
        query = query.filter(UGCRequest.asset_id == asset_id)
    if status:
        query = query.filter(UGCRequest.status == status)
    
    requests = query.offset(offset).limit(limit).all()
    
    return [
        UGCRequestResponse(
            id=req.id,
            asset_id=req.asset_id,
            message=req.message,
            channel=req.channel.value,
            status=req.status.value,
            platform_message_id=req.platform_message_id,
            platform_thread_id=req.platform_thread_id,
            response_message=req.response_message,
            response_choice=req.response_choice,
            sent_at=req.sent_at.isoformat() if req.sent_at else None,
            responded_at=req.responded_at.isoformat() if req.responded_at else None,
            expires_at=req.expires_at.isoformat() if req.expires_at else None,
            created_at=req.created_at.isoformat()
        )
        for req in requests
    ]


@router.get("/ugc/usage/{asset_id}", response_model=List[dict])
async def get_ugc_usage(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get usage history for a UGC asset."""
    # Verify asset belongs to org
    asset = db.query(UGCAsset).filter(
        UGCAsset.id == asset_id,
        UGCAsset.org_id == current_user["org_id"]
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UGC asset not found"
        )
    
    usage_records = db.query(UGCUsage).filter(UGCUsage.asset_id == asset_id).all()
    
    return [
        {
            "id": usage.id,
            "campaign_id": usage.campaign_id,
            "schedule_id": usage.schedule_id,
            "usage_type": usage.usage_type,
            "platform": usage.platform,
            "platform_post_id": usage.platform_post_id,
            "platform_url": usage.platform_url,
            "impressions": usage.impressions,
            "engagement": usage.engagement,
            "used_at": usage.used_at.isoformat()
        }
        for usage in usage_records
    ]
