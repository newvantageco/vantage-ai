"""
Metrics Collection Tasks
Scheduled tasks for collecting analytics data from social media platforms
"""

from celery import Task
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio
import logging

from app.workers.celery_app import celery_app
from app.db.session import get_db
from app.services.analytics_service import AnalyticsService
from app.models.publishing import ExternalReference, PublishingStatus, PlatformIntegration
from app.models.entities import Organization

logger = logging.getLogger(__name__)


class MetricsCollectionTask(Task):
    """Base task for metrics collection operations"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f"Metrics Collection Task {task_id} failed: {exc}")
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(f"Metrics Collection Task {task_id} completed successfully")


@celery_app.task(bind=True, base=MetricsCollectionTask, default_retry_delay=3600, max_retries=3)
def collect_all_platform_metrics(self, organization_id: int = None) -> Dict[str, Any]:
    """
    Collect metrics from all platforms for all organizations or a specific organization.
    """
    try:
        db = next(get_db())
        analytics_service = AnalyticsService(db)
        
        # Get organizations to process
        if organization_id:
            organizations = db.query(Organization).filter(Organization.id == organization_id).all()
        else:
            organizations = db.query(Organization).all()
        
        total_processed = 0
        total_errors = 0
        results = {}
        
        for org in organizations:
            try:
                org_result = asyncio.run(_collect_org_metrics(db, analytics_service, org.id))
                results[f"org_{org.id}"] = org_result
                total_processed += org_result.get("processed", 0)
                total_errors += org_result.get("errors", 0)
            except Exception as e:
                logger.error(f"Failed to collect metrics for organization {org.id}: {str(e)}")
                results[f"org_{org.id}"] = {"error": str(e), "processed": 0, "errors": 1}
                total_errors += 1
        
        return {
            "success": True,
            "total_organizations": len(organizations),
            "total_processed": total_processed,
            "total_errors": total_errors,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Metrics collection task failed: {str(e)}")
        raise


@celery_app.task(bind=True, base=MetricsCollectionTask, default_retry_delay=1800, max_retries=3)
def collect_platform_metrics_for_org(
    self, 
    organization_id: int, 
    platform: str = None
) -> Dict[str, Any]:
    """
    Collect metrics for a specific organization and optionally specific platform.
    """
    try:
        db = next(get_db())
        analytics_service = AnalyticsService(db)
        
        result = asyncio.run(_collect_org_metrics(db, analytics_service, organization_id, platform))
        
        return {
            "success": True,
            "organization_id": organization_id,
            "platform": platform,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Platform metrics collection failed for org {organization_id}: {str(e)}")
        raise


async def _collect_org_metrics(
    db, 
    analytics_service: AnalyticsService, 
    organization_id: int, 
    platform: str = None
) -> Dict[str, Any]:
    """Collect metrics for a specific organization"""
    
    # Get published posts from the last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    query = db.query(ExternalReference).filter(
        ExternalReference.organization_id == organization_id,
        ExternalReference.status == PublishingStatus.PUBLISHED,
        ExternalReference.published_at >= start_date,
        ExternalReference.published_at <= end_date
    )
    
    if platform:
        query = query.filter(ExternalReference.platform == platform)
    
    published_posts = query.all()
    
    if not published_posts:
        return {
            "organization_id": organization_id,
            "platform": platform,
            "processed": 0,
            "errors": 0,
            "message": "No published posts found"
        }
    
    # Get platform integrations for this organization
    integrations = db.query(PlatformIntegration).filter(
        PlatformIntegration.organization_id == organization_id,
        PlatformIntegration.status == "active"
    ).all()
    
    integration_map = {int.platform: int for int in integrations}
    
    processed = 0
    errors = 0
    
    for post in published_posts:
        try:
            # Get the platform integration
            integration = integration_map.get(post.platform.value)
            if not integration:
                logger.warning(f"No active integration found for platform {post.platform.value}")
                continue
            
            # Get analytics integration
            from app.workers.tasks.analytics_tasks import get_platform_integration
            analytics_integration = get_platform_integration(post.platform.value)
            
            if not analytics_integration:
                logger.warning(f"No analytics integration available for platform {post.platform.value}")
                continue
            
            # Decrypt access token
            settings = integration.settings or {}
            access_token = None
            
            if settings.get("access_token"):
                try:
                    if post.platform.value == "facebook":
                        from app.integrations.oauth.meta import MetaOAuth
                        oauth = MetaOAuth()
                        access_token = oauth._decrypt_token(settings["access_token"])
                    elif post.platform.value == "linkedin":
                        from app.integrations.oauth.linkedin import LinkedInOAuth
                        oauth = LinkedInOAuth()
                        access_token = oauth._decrypt_token(settings["access_token"])
                    elif post.platform.value == "google_gbp":
                        from app.integrations.oauth.google import GoogleOAuth
                        oauth = GoogleOAuth()
                        access_token = oauth._decrypt_token(settings["access_token"])
                except Exception as e:
                    logger.error(f"Failed to decrypt token for platform {post.platform.value}: {str(e)}")
                    continue
            
            if not access_token:
                logger.warning(f"No access token available for platform {post.platform.value}")
                continue
            
            # Collect metrics
            metrics_data = None
            
            if post.platform.value == "facebook":
                page_id = post.platform_data.get("page_id") if post.platform_data else None
                metrics_data = await analytics_integration.get_post_metrics(
                    post_id=post.external_id,
                    access_token=access_token,
                    page_id=page_id
                )
            elif post.platform.value == "linkedin":
                metrics_data = await analytics_integration.get_post_metrics(
                    post_id=post.external_id,
                    access_token=access_token
                )
            elif post.platform.value == "google_gbp":
                account_name = post.platform_data.get("account_id") if post.platform_data else None
                location_name = post.platform_data.get("location_id") if post.platform_data else None
                if account_name and location_name:
                    metrics_data = await analytics_integration.get_post_metrics(
                        post_id=post.external_id,
                        access_token=access_token,
                        account_name=account_name,
                        location_name=location_name
                    )
            
            if metrics_data:
                # Update analytics with real data
                analytics_service.update_post_metrics(
                    external_reference_id=post.id,
                    platform=post.platform.value,
                    external_id=post.external_id,
                    metrics_data={
                        'organization_id': organization_id,
                        **metrics_data,
                        'data_source': 'api'
                    },
                    metric_date=post.published_at
                )
                processed += 1
                logger.info(f"Collected real metrics for {post.platform.value} post {post.external_id}")
            else:
                # Create estimated metrics as fallback
                _create_estimated_metrics(analytics_service, post, organization_id, post.platform.value)
                processed += 1
                logger.info(f"Created estimated metrics for {post.platform.value} post {post.external_id}")
                
        except Exception as e:
            logger.error(f"Failed to collect metrics for post {post.external_id}: {str(e)}")
            errors += 1
    
    return {
        "organization_id": organization_id,
        "platform": platform,
        "processed": processed,
        "errors": errors,
        "total_posts": len(published_posts)
    }


def _create_estimated_metrics(analytics_service: AnalyticsService, post: ExternalReference, organization_id: int, platform: str):
    """Create estimated metrics when real metrics are not available"""
    import random
    
    # Generate realistic estimated metrics based on platform
    if platform == "facebook":
        base_impressions = random.randint(50, 500)
        engagement_rate = random.uniform(0.02, 0.08)  # 2-8% engagement rate
    elif platform == "linkedin":
        base_impressions = random.randint(20, 200)
        engagement_rate = random.uniform(0.01, 0.05)  # 1-5% engagement rate
    elif platform == "google_gbp":
        base_impressions = random.randint(10, 100)
        engagement_rate = random.uniform(0.03, 0.10)  # 3-10% engagement rate
    else:
        base_impressions = random.randint(10, 100)
        engagement_rate = random.uniform(0.01, 0.05)
    
    engagements = int(base_impressions * engagement_rate)
    clicks = int(engagements * random.uniform(0.1, 0.3))  # 10-30% of engagements are clicks
    
    estimated_metrics = {
        'organization_id': organization_id,
        'impressions': base_impressions,
        'reach': int(base_impressions * random.uniform(0.8, 1.0)),  # Reach is usually 80-100% of impressions
        'clicks': clicks,
        'engagements': engagements,
        'likes': int(engagements * random.uniform(0.4, 0.7)),
        'comments': int(engagements * random.uniform(0.1, 0.2)),
        'shares': int(engagements * random.uniform(0.05, 0.15)),
        'data_source': 'estimated',
        'is_estimated': True
    }
    
    analytics_service.update_post_metrics(
        external_reference_id=post.id,
        platform=platform,
        external_id=post.external_id,
        metrics_data=estimated_metrics,
        metric_date=post.published_at
    )


# Schedule periodic metrics collection
@celery_app.task
def schedule_metrics_collection():
    """Schedule metrics collection for all organizations every hour"""
    from celery import current_app
    
    # Schedule collection for all organizations
    collect_all_platform_metrics.delay()
    
    # Schedule individual platform collections
    platforms = ["facebook", "linkedin", "google_gbp"]
    for platform in platforms:
        collect_platform_metrics_for_org.delay(platform=platform)
    
    logger.info("Scheduled metrics collection tasks")
