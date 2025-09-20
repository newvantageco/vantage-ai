"""
Enhanced Analytics API endpoints
Handles analytics queries, data aggregation, and CSV export
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.analytics_service import AnalyticsService
from app.models.publishing import PlatformType
from app.models.entities import Organization

router = APIRouter()


class AnalyticsSummaryResponse(BaseModel):
    period: Dict[str, Any]
    metrics: Dict[str, Any]
    platform_breakdown: List[Dict[str, Any]]


class TimeseriesResponse(BaseModel):
    data: List[Dict[str, Any]]
    group_by: str
    total_points: int


class PlatformComparisonResponse(BaseModel):
    data: List[Dict[str, Any]]
    total_platforms: int


class CTRResponse(BaseModel):
    data: List[Dict[str, Any]]
    avg_ctr: float


class CampaignAnalyticsResponse(BaseModel):
    campaign_id: str
    period: Dict[str, Any]
    metrics: Dict[str, Any]
    platform_breakdown: Dict[str, Any]


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics summary for the specified period"""
    try:
        analytics_service = AnalyticsService(db)
        summary = analytics_service.get_analytics_summary(
            org_id=current_user["org_id"],
            days=days,
            platform=platform,
            campaign_id=campaign_id
        )
        
        return AnalyticsSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics summary: {str(e)}"
        )


@router.get("/analytics/timeseries", response_model=TimeseriesResponse)
async def get_timeseries_data(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    group_by: str = Query("day", regex="^(day|week|month)$", description="Grouping period"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get timeseries data for charts"""
    try:
        analytics_service = AnalyticsService(db)
        data = analytics_service.get_timeseries_data(
            org_id=current_user["org_id"],
            days=days,
            platform=platform,
            campaign_id=campaign_id,
            group_by=group_by
        )
        
        return TimeseriesResponse(
            data=data,
            group_by=group_by,
            total_points=len(data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get timeseries data: {str(e)}"
        )


@router.get("/analytics/platform-comparison", response_model=PlatformComparisonResponse)
async def get_platform_comparison(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get platform comparison data for bar charts"""
    try:
        analytics_service = AnalyticsService(db)
        data = analytics_service.get_platform_comparison(
            org_id=current_user["org_id"],
            days=days,
            campaign_id=campaign_id
        )
        
        return PlatformComparisonResponse(
            data=data,
            total_platforms=len(data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform comparison: {str(e)}"
        )


@router.get("/analytics/ctr-over-time", response_model=CTRResponse)
async def get_ctr_over_time(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get CTR (Click-Through Rate) over time data"""
    try:
        analytics_service = AnalyticsService(db)
        data = analytics_service.get_ctr_over_time(
            org_id=current_user["org_id"],
            days=days,
            platform=platform
        )
        
        # Calculate average CTR
        avg_ctr = sum(point["ctr"] for point in data) / len(data) if data else 0
        
        return CTRResponse(
            data=data,
            avg_ctr=round(avg_ctr, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get CTR data: {str(e)}"
        )


@router.get("/analytics/campaign/{campaign_id}", response_model=CampaignAnalyticsResponse)
async def get_campaign_analytics(
    campaign_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a specific campaign"""
    try:
        analytics_service = AnalyticsService(db)
        data = analytics_service.get_campaign_analytics(
            org_id=current_user["org_id"],
            campaign_id=campaign_id,
            days=days
        )
        
        if "error" in data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=data["error"]
            )
        
        return CampaignAnalyticsResponse(**data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign analytics: {str(e)}"
        )


@router.get("/analytics/export/csv")
async def export_analytics_csv(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    include_metrics: bool = Query(True, description="Include detailed metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export analytics data as CSV with streaming response"""
    try:
        analytics_service = AnalyticsService(db)
        return analytics_service.export_analytics_csv(
            org_id=current_user["org_id"],
            days=days,
            platform=platform,
            campaign_id=campaign_id,
            include_metrics=include_metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export analytics data: {str(e)}"
        )


@router.get("/analytics/platforms")
async def get_available_platforms(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of available platforms for filtering"""
    try:
        from app.services.publishers import get_supported_platforms
        
        platforms = get_supported_platforms()
        
        return {
            "platforms": [
                {
                    "value": platform.value,
                    "label": platform.value.replace("_", " ").title(),
                    "icon": platform.value
                }
                for platform in platforms
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available platforms: {str(e)}"
        )


@router.get("/analytics/campaigns")
async def get_available_campaigns(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of available campaigns for filtering"""
    try:
        from app.models.publishing import ExternalReference
        from sqlalchemy import distinct, func
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get unique campaign IDs from platform_data
        campaigns = db.query(
            ExternalReference.platform_data['campaign_id'].astext.label('campaign_id'),
            func.count(ExternalReference.id).label('post_count')
        ).filter(
            ExternalReference.organization_id == current_user["org_id"],
            ExternalReference.created_at >= start_date,
            ExternalReference.created_at <= end_date,
            ExternalReference.platform_data['campaign_id'].isnot(None)
        ).group_by(
            ExternalReference.platform_data['campaign_id'].astext
        ).all()
        
        return {
            "campaigns": [
                {
                    "id": campaign.campaign_id,
                    "post_count": campaign.post_count
                }
                for campaign in campaigns
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available campaigns: {str(e)}"
        )


@router.get("/analytics/health")
async def analytics_health_check(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Health check for analytics service"""
    try:
        analytics_service = AnalyticsService(db)
        
        # Test basic query
        summary = analytics_service.get_analytics_summary(
            org_id=current_user["org_id"],
            days=1
        )
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "org_id": current_user["org_id"],
            "test_query_successful": True
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "test_query_successful": False
        }
