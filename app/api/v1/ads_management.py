from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets

from app.db.session import get_db
from app.api.deps import get_current_user
from app.publishers.tiktok import TikTokAdsProvider
from app.publishers.google_ads import GoogleAdsProvider
from pydantic import BaseModel

router = APIRouter()


class CampaignCreateRequest(BaseModel):
    name: str
    platform: str  # "tiktok" or "google_ads"
    objective: Optional[str] = "TRAFFIC"
    budget: int = 100  # Daily budget in cents
    landing_page_url: str
    status: str = "active"


class AdGroupCreateRequest(BaseModel):
    name: str
    platform: str
    campaign_id: str
    budget: int = 50  # Daily budget in cents
    bid_price: int = 100  # Bid in cents
    status: str = "active"


class AdCreateRequest(BaseModel):
    name: str
    platform: str
    ad_group_id: str
    ad_text: str
    landing_page_url: str
    call_to_action: Optional[str] = "LEARN_MORE"
    status: str = "active"


class MetricsRequest(BaseModel):
    platform: str
    entity_id: str  # campaign_id, ad_group_id, or ad_id
    entity_type: str  # "campaign", "ad_group", or "ad"
    start_date: str
    end_date: str


class BudgetUpdateRequest(BaseModel):
    platform: str
    campaign_id: str
    budget: int


class CampaignStatusRequest(BaseModel):
    platform: str
    campaign_id: str
    action: str  # "pause" or "resume"


@router.post("/ads/campaigns")
async def create_campaign(
    campaign_data: CampaignCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new ad campaign."""
    try:
        if campaign_data.platform == "tiktok":
            provider = TikTokAdsProvider()
            result = provider.create_campaign({
                "name": campaign_data.name,
                "objective": campaign_data.objective,
                "budget": campaign_data.budget,
                "landing_page_url": campaign_data.landing_page_url,
                "status": campaign_data.status
            })
        elif campaign_data.platform == "google_ads":
            provider = GoogleAdsProvider()
            result = provider.create_campaign({
                "name": campaign_data.name,
                "objective": campaign_data.objective,
                "budget": campaign_data.budget,
                "landing_page_url": campaign_data.landing_page_url,
                "status": campaign_data.status
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported platform. Must be 'tiktok' or 'google_ads'"
            )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "message": "Campaign created successfully",
            "campaign_id": result["campaign_id"],
            "platform": campaign_data.platform
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.post("/ads/ad-groups")
async def create_ad_group(
    ad_group_data: AdGroupCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new ad group."""
    try:
        if ad_group_data.platform == "tiktok":
            provider = TikTokAdsProvider()
            result = provider.create_ad_group({
                "name": ad_group_data.name,
                "campaign_id": ad_group_data.campaign_id,
                "budget": ad_group_data.budget,
                "bid_price": ad_group_data.bid_price,
                "status": ad_group_data.status
            })
        elif ad_group_data.platform == "google_ads":
            provider = GoogleAdsProvider()
            result = provider.create_ad_group({
                "name": ad_group_data.name,
                "campaign_id": ad_group_data.campaign_id,
                "budget": ad_group_data.budget,
                "bid_micros": ad_group_data.bid_price * 10000,  # Convert to micros
                "status": ad_group_data.status
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported platform. Must be 'tiktok' or 'google_ads'"
            )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "message": "Ad group created successfully",
            "ad_group_id": result["ad_group_id"],
            "platform": ad_group_data.platform
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ad group: {str(e)}"
        )


@router.post("/ads/ads")
async def create_ad(
    ad_data: AdCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new ad."""
    try:
        if ad_data.platform == "tiktok":
            provider = TikTokAdsProvider()
            result = provider.create_ad({
                "name": ad_data.name,
                "ad_group_id": ad_data.ad_group_id,
                "ad_text": ad_data.ad_text,
                "landing_page_url": ad_data.landing_page_url,
                "call_to_action": ad_data.call_to_action,
                "status": ad_data.status
            })
        elif ad_data.platform == "google_ads":
            provider = GoogleAdsProvider()
            result = provider.create_text_ad({
                "name": ad_data.name,
                "ad_group_id": ad_data.ad_group_id,
                "headline_1": ad_data.ad_text[:30],  # Truncate for headline
                "description_1": ad_data.ad_text,
                "landing_page_url": ad_data.landing_page_url,
                "status": ad_data.status
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported platform. Must be 'tiktok' or 'google_ads'"
            )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "message": "Ad created successfully",
            "ad_id": result["ad_id"],
            "platform": ad_data.platform
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ad: {str(e)}"
        )


@router.get("/ads/metrics")
async def get_metrics(
    platform: str,
    entity_id: str,
    entity_type: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get metrics for a campaign, ad group, or ad."""
    try:
        if platform == "tiktok":
            provider = TikTokAdsProvider()
            if entity_type == "campaign":
                result = provider.get_campaign_metrics(entity_id, start_date, end_date)
            elif entity_type == "ad_group":
                result = provider.get_ad_group_metrics(entity_id, start_date, end_date)
            elif entity_type == "ad":
                result = provider.get_ad_metrics(entity_id, start_date, end_date)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid entity_type. Must be 'campaign', 'ad_group', or 'ad'"
                )
        elif platform == "google_ads":
            provider = GoogleAdsProvider()
            if entity_type == "campaign":
                result = provider.get_campaign_metrics(entity_id, start_date, end_date)
            elif entity_type == "ad_group":
                result = provider.get_ad_group_metrics(entity_id, start_date, end_date)
            elif entity_type == "ad":
                result = provider.get_ad_metrics(entity_id, start_date, end_date)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid entity_type. Must be 'campaign', 'ad_group', or 'ad'"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported platform. Must be 'tiktok' or 'google_ads'"
            )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "platform": platform,
            "metrics": result["metrics"],
            "start_date": start_date,
            "end_date": end_date
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.put("/ads/campaigns/budget")
async def update_campaign_budget(
    budget_data: BudgetUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update campaign budget."""
    try:
        if budget_data.platform == "tiktok":
            provider = TikTokAdsProvider()
            result = provider.update_campaign_budget(budget_data.campaign_id, budget_data.budget)
        elif budget_data.platform == "google_ads":
            provider = GoogleAdsProvider()
            result = provider.update_campaign_budget(budget_data.campaign_id, budget_data.budget)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported platform. Must be 'tiktok' or 'google_ads'"
            )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "message": "Campaign budget updated successfully",
            "campaign_id": budget_data.campaign_id,
            "platform": budget_data.platform
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign budget: {str(e)}"
        )


@router.put("/ads/campaigns/status")
async def update_campaign_status(
    status_data: CampaignStatusRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Pause or resume a campaign."""
    try:
        if status_data.platform == "tiktok":
            provider = TikTokAdsProvider()
            if status_data.action == "pause":
                result = provider.pause_campaign(status_data.campaign_id)
            elif status_data.action == "resume":
                result = provider.resume_campaign(status_data.campaign_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid action. Must be 'pause' or 'resume'"
                )
        elif status_data.platform == "google_ads":
            provider = GoogleAdsProvider()
            if status_data.action == "pause":
                result = provider.pause_campaign(status_data.campaign_id)
            elif status_data.action == "resume":
                result = provider.resume_campaign(status_data.campaign_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid action. Must be 'pause' or 'resume'"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported platform. Must be 'tiktok' or 'google_ads'"
            )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "message": f"Campaign {status_data.action}d successfully",
            "campaign_id": status_data.campaign_id,
            "platform": status_data.platform
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign status: {str(e)}"
        )


@router.get("/ads/platforms")
async def get_supported_platforms():
    """Get list of supported ad platforms."""
    return {
        "platforms": [
            {
                "id": "tiktok",
                "name": "TikTok Business",
                "description": "TikTok Business Ads platform",
                "supported_objectives": ["TRAFFIC", "CONVERSIONS", "REACH", "VIDEO_VIEWS"],
                "min_budget": 100,  # cents
                "max_budget": 1000000  # cents
            },
            {
                "id": "google_ads",
                "name": "Google Ads",
                "description": "Google Ads platform for search and display",
                "supported_objectives": ["TRAFFIC", "CONVERSIONS", "REACH", "BRAND_AWARENESS"],
                "min_budget": 100,  # cents
                "max_budget": 1000000  # cents
            }
        ]
    }


@router.get("/ads/campaigns/{platform}")
async def list_campaigns(
    platform: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List campaigns for a platform."""
    # This would typically query your database for stored campaigns
    # For now, return a placeholder response
    return {
        "platform": platform,
        "campaigns": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }
