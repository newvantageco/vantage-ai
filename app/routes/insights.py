from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models.content import Schedule, ContentStatus
from app.models.entities import Channel
from app.models.external_refs import ScheduleExternal
from app.models.post_metrics import PostMetrics
from app.services.insights_mapper import InsightsMapper
from app.integrations.meta_insights import MetaInsightsFetcher
from app.integrations.linkedin_insights import LinkedInInsightsFetcher
from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])


class FetchInsightsRequest(BaseModel):
    force_refresh: bool = False


class FetchInsightsResponse(BaseModel):
    success: bool
    message: str
    metrics: Optional[Dict[str, Any]] = None
    schedule_id: str
    provider: str


class InsightsService:
    """Service for fetching and storing post insights."""
    
    def __init__(self):
        self.settings = get_settings()
        self.insights_mapper = InsightsMapper()
        self.meta_fetcher = MetaInsightsFetcher()
        self.linkedin_fetcher = LinkedInInsightsFetcher()
    
    async def fetch_insights_for_schedule(
        self, 
        schedule_id: str, 
        db: Session,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch insights for a specific schedule.
        
        Args:
            schedule_id: Schedule ID
            db: Database session
            force_refresh: Whether to force refresh even if recent data exists
            
        Returns:
            Dict containing insights data
        """
        logger.info(f"[Insights Service] Fetching insights for schedule {schedule_id}")
        
        # Get schedule
        schedule = db.get(Schedule, schedule_id)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found"
            )
        
        # Check if schedule is posted
        if schedule.status != ContentStatus.posted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Schedule {schedule_id} is not posted (status: {schedule.status})"
            )
        
        # Get channel to determine provider
        channel = db.get(Channel, schedule.channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Channel not found for schedule {schedule_id}"
            )
        
        provider = channel.provider.lower()
        
        # Check if we should use fake insights
        if not self.insights_mapper.should_fetch_real_insights():
            logger.info(f"[Insights Service] Using fake insights for {provider} schedule {schedule_id}")
            post_metrics = self.insights_mapper.generate_fake_metrics(schedule_id, provider)
            db.add(post_metrics)
            db.commit()
            
            return {
                "success": True,
                "message": "Fake insights generated",
                "metrics": self._post_metrics_to_dict(post_metrics),
                "provider": provider
            }
        
        # Get external reference for the schedule
        external_ref = db.query(ScheduleExternal).filter(
            ScheduleExternal.schedule_id == schedule_id,
            ScheduleExternal.provider == provider
        ).first()
        
        if not external_ref:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No external reference found for schedule {schedule_id} on {provider}"
            )
        
        # Check if we already have recent metrics (unless force refresh)
        if not force_refresh:
            recent_metrics = db.query(PostMetrics).filter(
                PostMetrics.schedule_id == schedule_id,
                PostMetrics.fetched_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).first()
            
            if recent_metrics:
                logger.info(f"[Insights Service] Recent metrics already exist for schedule {schedule_id}")
                return {
                    "success": True,
                    "message": "Recent metrics already exist",
                    "metrics": self._post_metrics_to_dict(recent_metrics),
                    "provider": provider
                }
        
        # Fetch real insights from platform
        try:
            insights = await self._fetch_platform_insights(
                external_ref.ref_id, 
                provider, 
                external_ref.schedule_id
            )
            
            # Map to PostMetrics
            post_metrics = self.insights_mapper.map_platform_to_post_metrics(
                insights, schedule_id, provider
            )
            
            # Store in database
            db.add(post_metrics)
            db.commit()
            
            logger.info(f"[Insights Service] Successfully fetched and stored insights for schedule {schedule_id}")
            
            return {
                "success": True,
                "message": "Insights fetched successfully",
                "metrics": self._post_metrics_to_dict(post_metrics),
                "provider": provider
            }
            
        except Exception as e:
            logger.error(f"[Insights Service] Failed to fetch insights for schedule {schedule_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch insights: {str(e)}"
            )
    
    async def _fetch_platform_insights(
        self, 
        ref_id: str, 
        provider: str,
        schedule_id: str
    ) -> Dict[str, Any]:
        """Fetch insights from the appropriate platform."""
        # This is a simplified version - in practice, you'd need to get access tokens
        # from your token storage system
        
        if provider in ["facebook", "instagram"]:
            # For now, return empty dict - would need access token
            logger.warning(f"[Insights Service] Meta insights not implemented yet for {ref_id}")
            return {}
        elif provider == "linkedin":
            # For now, return empty dict - would need access token
            logger.warning(f"[Insights Service] LinkedIn insights not implemented yet for {ref_id}")
            return {}
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _post_metrics_to_dict(self, post_metrics: PostMetrics) -> Dict[str, Any]:
        """Convert PostMetrics to dictionary for API response."""
        return {
            "id": post_metrics.id,
            "schedule_id": post_metrics.schedule_id,
            "impressions": post_metrics.impressions,
            "reach": post_metrics.reach,
            "likes": post_metrics.likes,
            "comments": post_metrics.comments,
            "shares": post_metrics.shares,
            "clicks": post_metrics.clicks,
            "video_views": post_metrics.video_views,
            "saves": post_metrics.saves,
            "cost_cents": post_metrics.cost_cents,
            "fetched_at": post_metrics.fetched_at.isoformat(),
            "created_at": post_metrics.created_at.isoformat()
        }


# Initialize service
insights_service = InsightsService()


@router.post("/fetch/{schedule_id}")
async def fetch_insights(
    schedule_id: str,
    request: FetchInsightsRequest = FetchInsightsRequest(),
    db: Session = Depends(get_db)
) -> FetchInsightsResponse:
    """
    Fetch insights for a specific schedule.
    
    Args:
        schedule_id: Schedule ID
        request: Request body with optional force_refresh flag
        db: Database session
        
    Returns:
        FetchInsightsResponse with insights data
    """
    try:
        result = await insights_service.fetch_insights_for_schedule(
            schedule_id, db, request.force_refresh
        )
        
        return FetchInsightsResponse(
            success=result["success"],
            message=result["message"],
            metrics=result["metrics"],
            schedule_id=schedule_id,
            provider=result["provider"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Insights API] Unexpected error fetching insights for {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/metrics/{schedule_id}")
async def get_schedule_metrics(
    schedule_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get stored metrics for a schedule.
    
    Args:
        schedule_id: Schedule ID
        db: Database session
        
    Returns:
        Dict containing metrics data
    """
    # Get the most recent metrics for this schedule
    post_metrics = db.query(PostMetrics).filter(
        PostMetrics.schedule_id == schedule_id
    ).order_by(PostMetrics.fetched_at.desc()).first()
    
    if not post_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No metrics found for schedule {schedule_id}"
        )
    
    return insights_service._post_metrics_to_dict(post_metrics)


@router.get("/metrics/{schedule_id}/history")
async def get_schedule_metrics_history(
    schedule_id: str,
    limit: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get metrics history for a schedule.
    
    Args:
        schedule_id: Schedule ID
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        Dict containing metrics history
    """
    # Get metrics history for this schedule
    post_metrics_list = db.query(PostMetrics).filter(
        PostMetrics.schedule_id == schedule_id
    ).order_by(PostMetrics.fetched_at.desc()).limit(limit).all()
    
    if not post_metrics_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No metrics history found for schedule {schedule_id}"
        )
    
    return {
        "schedule_id": schedule_id,
        "metrics": [
            insights_service._post_metrics_to_dict(metrics) 
            for metrics in post_metrics_list
        ],
        "count": len(post_metrics_list)
    }
