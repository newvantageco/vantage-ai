"""
Metrics Collection API
Endpoints for triggering and monitoring metrics collection
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

from app.api.deps import get_db, get_current_user
from app.models.entities import UserAccount
from app.workers.tasks.metrics_collection import (
    collect_all_platform_metrics,
    collect_platform_metrics_for_org
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/collect", status_code=status.HTTP_202_ACCEPTED)
async def trigger_metrics_collection(
    platform: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Trigger metrics collection for the current organization
    """
    try:
        organization_id = current_user.organization_id
        
        if platform:
            # Collect for specific platform
            task = collect_platform_metrics_for_org.delay(
                organization_id=organization_id,
                platform=platform
            )
            message = f"Metrics collection started for {platform}"
        else:
            # Collect for all platforms
            task = collect_platform_metrics_for_org.delay(
                organization_id=organization_id
            )
            message = "Metrics collection started for all platforms"
        
        logger.info(f"Triggered metrics collection for organization {organization_id}")
        
        return {
            "success": True,
            "message": message,
            "task_id": task.id,
            "organization_id": organization_id,
            "platform": platform
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger metrics collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger metrics collection: {str(e)}"
        )


@router.get("/status")
async def get_collection_status(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the status of metrics collection for the current organization
    """
    try:
        from app.services.analytics_service import AnalyticsService
        from app.models.publishing import ExternalReference, PublishingStatus
        from datetime import datetime, timedelta
        
        analytics_service = AnalyticsService(db)
        organization_id = current_user.organization_id
        
        # Get recent metrics collection stats
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Count published posts in the last 7 days
        recent_posts = db.query(ExternalReference).filter(
            ExternalReference.organization_id == organization_id,
            ExternalReference.status == PublishingStatus.PUBLISHED,
            ExternalReference.published_at >= start_date
        ).count()
        
        # Get real-time metrics
        realtime_metrics = analytics_service.get_real_time_metrics(
            org_id=organization_id,
            hours=24
        )
        
        # Get platform integrations status
        from app.models.publishing import PlatformIntegration
        integrations = db.query(PlatformIntegration).filter(
            PlatformIntegration.organization_id == organization_id,
            PlatformIntegration.status == "active"
        ).all()
        
        platform_status = {}
        for integration in integrations:
            platform_status[integration.platform] = {
                "connected": True,
                "last_sync": integration.last_sync_at.isoformat() if integration.last_sync_at else None,
                "status": integration.status
            }
        
        return {
            "success": True,
            "organization_id": organization_id,
            "recent_posts": recent_posts,
            "platform_integrations": platform_status,
            "realtime_metrics": realtime_metrics,
            "last_updated": end_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get collection status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collection status: {str(e)}"
        )


@router.post("/test/{platform}")
async def test_platform_connection(
    platform: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Test connection to a specific platform for metrics collection
    """
    try:
        from app.models.publishing import PlatformIntegration
        from app.workers.tasks.analytics_tasks import get_platform_integration
        
        organization_id = current_user.organization_id
        
        # Get platform integration
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.organization_id == organization_id,
            PlatformIntegration.platform == platform,
            PlatformIntegration.status == "active"
        ).first()
        
        if not integration:
            return {
                "success": False,
                "message": f"No active integration found for {platform}",
                "platform": platform
            }
        
        # Get analytics integration
        analytics_integration = get_platform_integration(platform)
        if not analytics_integration:
            return {
                "success": False,
                "message": f"Analytics integration not available for {platform}",
                "platform": platform
            }
        
        # Test with a sample post if available
        from app.models.publishing import ExternalReference, PublishingStatus
        sample_post = db.query(ExternalReference).filter(
            ExternalReference.organization_id == organization_id,
            ExternalReference.platform == platform,
            ExternalReference.status == PublishingStatus.PUBLISHED
        ).first()
        
        if sample_post:
            # Try to collect metrics for the sample post
            settings = integration.settings or {}
            access_token = None
            
            if settings.get("access_token"):
                try:
                    if platform == "facebook":
                        from app.integrations.oauth.meta import MetaOAuth
                        oauth = MetaOAuth()
                        access_token = oauth._decrypt_token(settings["access_token"])
                    elif platform == "linkedin":
                        from app.integrations.oauth.linkedin import LinkedInOAuth
                        oauth = LinkedInOAuth()
                        access_token = oauth._decrypt_token(settings["access_token"])
                    elif platform == "google_gbp":
                        from app.integrations.oauth.google import GoogleOAuth
                        oauth = GoogleOAuth()
                        access_token = oauth._decrypt_token(settings["access_token"])
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Failed to decrypt access token: {str(e)}",
                        "platform": platform
                    }
            
            if access_token:
                # Test metrics collection
                try:
                    if platform == "facebook":
                        page_id = sample_post.platform_data.get("page_id") if sample_post.platform_data else None
                        metrics = await analytics_integration.get_post_metrics(
                            post_id=sample_post.external_id,
                            access_token=access_token,
                            page_id=page_id
                        )
                    elif platform == "linkedin":
                        metrics = await analytics_integration.get_post_metrics(
                            post_id=sample_post.external_id,
                            access_token=access_token
                        )
                    elif platform == "google_gbp":
                        account_name = sample_post.platform_data.get("account_id") if sample_post.platform_data else None
                        location_name = sample_post.platform_data.get("location_id") if sample_post.platform_data else None
                        if account_name and location_name:
                            metrics = await analytics_integration.get_post_metrics(
                                post_id=sample_post.external_id,
                                access_token=access_token,
                                account_name=account_name,
                                location_name=location_name
                            )
                        else:
                            metrics = None
                    
                    if metrics:
                        return {
                            "success": True,
                            "message": f"Successfully collected metrics for {platform}",
                            "platform": platform,
                            "sample_metrics": metrics
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Failed to collect metrics for {platform}",
                            "platform": platform
                        }
                        
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Metrics collection failed: {str(e)}",
                        "platform": platform
                    }
            else:
                return {
                    "success": False,
                    "message": f"No access token available for {platform}",
                    "platform": platform
                }
        else:
            return {
                "success": True,
                "message": f"Platform {platform} is connected but no published posts found for testing",
                "platform": platform
            }
        
    except Exception as e:
        logger.error(f"Failed to test platform connection for {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test platform connection: {str(e)}"
        )
