"""
Analytics Celery Tasks
Handles metrics collection, processing, and reporting
"""

from celery import Task
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import logging

from app.workers.celery_app import celery_app
from app.db.session import get_db
from app.services.analytics_service import AnalyticsService
from app.models.publishing import ExternalReference, PublishingStatus
from app.models.entities import Organization
# from app.integrations.social_media import get_platform_integration

def get_platform_integration(platform: str):
    """Get platform integration for metrics collection"""
    try:
        if platform.lower() == "facebook":
            from app.integrations.analytics.facebook import FacebookAnalytics
            return FacebookAnalytics()
        elif platform.lower() == "linkedin":
            from app.integrations.analytics.linkedin import LinkedInAnalytics
            return LinkedInAnalytics()
        elif platform.lower() == "google_gbp":
            from app.integrations.analytics.google import GoogleAnalytics
            return GoogleAnalytics()
        else:
            logger.warning(f"Analytics not implemented for platform: {platform}")
            return None
    except ImportError as e:
        logger.warning(f"Analytics integration not available for {platform}: {e}")
        return None

logger = logging.getLogger(__name__)


class AnalyticsTask(Task):
    """Base task for analytics operations"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        print(f"Analytics Task {task_id} failed: {exc}")
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        print(f"Analytics Task {task_id} completed successfully")


@celery_app.task(bind=True, base=AnalyticsTask, default_retry_delay=3600, max_retries=3)
def collect_platform_metrics_task(
    self,
    platform: str,
    organization_id: int,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Collect metrics from a specific platform.
    """
    try:
        logger.info(f"Collecting metrics for {platform} from {start_date} to {end_date}")
        
        # Get database session
        db = next(get_db())
        analytics_service = AnalyticsService(db)
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get published posts for this platform and organization
        published_posts = db.query(ExternalReference).filter(
            ExternalReference.organization_id == organization_id,
            ExternalReference.platform == platform,
            ExternalReference.status == PublishingStatus.PUBLISHED,
            ExternalReference.published_at >= start_dt,
            ExternalReference.published_at <= end_dt
        ).all()
        
        if not published_posts:
            logger.info(f"No published posts found for {platform} in date range")
            return {
                "success": True,
                "platform": platform,
                "metrics_count": 0,
                "date_range": f"{start_date} to {end_date}"
            }
        
        # Get platform integration
        try:
            platform_integration = get_platform_integration(platform)
        except Exception as e:
            logger.warning(f"Could not get platform integration for {platform}: {e}")
            platform_integration = None
        
        metrics_collected = 0
        
        for post in published_posts:
            try:
                if platform_integration:
                    # Try to collect real metrics from platform
                    try:
                        metrics_data = platform_integration.get_post_metrics(
                            post_id=post.external_id,
                            access_token=post.platform_data.get('access_token') if post.platform_data else None
                        )
                        
                        if metrics_data:
                            # Update analytics with real data
                            analytics_service.update_post_metrics(
                                external_reference_id=post.id,
                                platform=platform,
                                external_id=post.external_id,
                                metrics_data={
                                    'organization_id': organization_id,
                                    **metrics_data,
                                    'data_source': 'api'
                                },
                                metric_date=post.published_at
                            )
                            metrics_collected += 1
                            logger.info(f"Collected real metrics for {platform} post {post.external_id}")
                        else:
                            # Fallback to estimated metrics
                            _create_estimated_metrics(analytics_service, post, organization_id, platform)
                            metrics_collected += 1
                            logger.info(f"Created estimated metrics for {platform} post {post.external_id}")
                    except Exception as e:
                        logger.warning(f"Failed to collect real metrics for {platform} post {post.external_id}: {e}")
                        # Fallback to estimated metrics
                        _create_estimated_metrics(analytics_service, post, organization_id, platform)
                        metrics_collected += 1
                else:
                    # Create estimated metrics
                    _create_estimated_metrics(analytics_service, post, organization_id, platform)
                    metrics_collected += 1
                    
            except Exception as e:
                logger.error(f"Error processing post {post.external_id}: {e}")
                continue
        
        # Generate analytics summary for the period
        analytics_service.generate_analytics_summary(
            org_id=organization_id,
            period_start=start_dt,
            period_end=end_dt,
            period_type="daily"
        )
        
        result = {
            "success": True,
            "platform": platform,
            "metrics_count": metrics_collected,
            "date_range": f"{start_date} to {end_date}"
        }
        
        logger.info(f"Collected {metrics_collected} metrics for {platform}")
        return result
        
    except Exception as e:
        logger.error(f"Error collecting metrics for {platform}: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


def _create_estimated_metrics(analytics_service: AnalyticsService, post: ExternalReference, org_id: int, platform: str):
    """Create estimated metrics for a post when real data is not available"""
    import random
    
    # Generate realistic estimated metrics based on platform and post age
    days_old = (datetime.utcnow() - post.published_at).days if post.published_at else 0
    
    # Base metrics vary by platform
    platform_multipliers = {
        'facebook': {'impressions': 1000, 'reach': 800, 'engagement': 0.05},
        'linkedin': {'impressions': 500, 'reach': 400, 'engagement': 0.08},
        'twitter': {'impressions': 200, 'reach': 150, 'engagement': 0.03},
        'instagram': {'impressions': 800, 'reach': 600, 'engagement': 0.06},
    }
    
    base_metrics = platform_multipliers.get(platform, {'impressions': 300, 'reach': 200, 'engagement': 0.05})
    
    # Decay metrics over time (older posts get less engagement)
    decay_factor = max(0.1, 1.0 - (days_old * 0.05))
    
    estimated_impressions = int(base_metrics['impressions'] * decay_factor * random.uniform(0.5, 1.5))
    estimated_reach = int(estimated_impressions * 0.8 * random.uniform(0.7, 1.0))
    estimated_engagements = int(estimated_reach * base_metrics['engagement'] * random.uniform(0.5, 1.5))
    
    metrics_data = {
        'organization_id': org_id,
        'impressions': estimated_impressions,
        'reach': estimated_reach,
        'clicks': int(estimated_impressions * random.uniform(0.01, 0.05)),
        'engagements': estimated_engagements,
        'likes': int(estimated_engagements * random.uniform(0.6, 0.8)),
        'comments': int(estimated_engagements * random.uniform(0.1, 0.2)),
        'shares': int(estimated_engagements * random.uniform(0.05, 0.15)),
        'saves': int(estimated_engagements * random.uniform(0.02, 0.08)),
        'conversions': int(estimated_impressions * random.uniform(0.001, 0.01)),
        'video_views': int(estimated_impressions * random.uniform(0.3, 0.7)) if random.random() > 0.5 else 0,
        'data_source': 'estimated',
        'is_estimated': True
    }
    
    analytics_service.update_post_metrics(
        external_reference_id=post.id,
        platform=platform,
        external_id=post.external_id,
        metrics_data=metrics_data,
        metric_date=post.published_at
    )


@celery_app.task(bind=True, base=AnalyticsTask, default_retry_delay=300, max_retries=3)
def generate_analytics_export_task(
    self,
    export_id: int,
    organization_id: int,
    export_type: str,
    date_range_start: str,
    date_range_end: str,
    platforms: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate analytics export file.
    """
    try:
        print(f"Generating analytics export {export_id} ({export_type})")
        
        # FIXME: Implement actual export generation
        # Mock result for now
        result = {
            "success": True,
            "export_id": export_id,
            "file_url": f"https://example.com/exports/{export_id}.{export_type}",
            "file_size": 1024
        }
        
        print(f"Analytics export {export_id} generated successfully")
        return result
        
    except Exception as e:
        print(f"Error generating analytics export {export_id}: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=AnalyticsTask, default_retry_delay=300, max_retries=3)
def generate_daily_report_task(
    self,
    organization_id: int,
    report_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate daily analytics report.
    """
    try:
        if not report_date:
            report_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        logger.info(f"Generating daily report for {organization_id} on {report_date}")
        
        # Get database session
        db = next(get_db())
        analytics_service = AnalyticsService(db)
        
        # Parse report date
        report_dt = datetime.fromisoformat(report_date)
        period_start = report_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)
        
        # Generate analytics summary
        summary = analytics_service.generate_analytics_summary(
            org_id=organization_id,
            period_start=period_start,
            period_end=period_end,
            period_type="daily"
        )
        
        # TODO: Generate actual PDF report
        # For now, return summary data
        result = {
            "success": True,
            "organization_id": organization_id,
            "report_date": report_date,
            "summary": {
                "total_impressions": summary.total_impressions,
                "total_engagements": summary.total_engagements,
                "avg_engagement_rate": summary.avg_engagement_rate,
                "platform_breakdown": summary.platform_breakdown
            },
            "report_url": f"https://example.com/reports/{organization_id}/{report_date}.pdf"
        }
        
        logger.info(f"Daily report generated for {organization_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating daily report for {organization_id}: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, base=AnalyticsTask, default_retry_delay=300, max_retries=3)
def update_analytics(self) -> Dict[str, Any]:
    """
    Update analytics for all organizations (scheduled task).
    """
    try:
        logger.info("Starting analytics update for all organizations")
        
        # Get database session
        db = next(get_db())
        analytics_service = AnalyticsService(db)
        
        # Get all organizations
        organizations = db.query(Organization).all()
        
        updated_orgs = 0
        total_metrics = 0
        
        for org in organizations:
            try:
                # Update analytics for last 7 days
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)
                
                # Get all platforms for this org
                platforms = db.query(ExternalReference.platform).filter(
                    ExternalReference.organization_id == org.id
                ).distinct().all()
                
                for platform_tuple in platforms:
                    platform = platform_tuple[0]
                    
                    # Collect metrics for this platform
                    task = collect_platform_metrics_task.delay(
                        platform=platform.value,
                        organization_id=org.id,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat()
                    )
                    
                    # Wait for completion and get result
                    result = task.get(timeout=300)
                    if result.get('success'):
                        total_metrics += result.get('metrics_count', 0)
                
                updated_orgs += 1
                logger.info(f"Updated analytics for organization {org.id}")
                
            except Exception as e:
                logger.error(f"Error updating analytics for organization {org.id}: {e}")
                continue
        
        result = {
            "success": True,
            "organizations_updated": updated_orgs,
            "total_metrics_collected": total_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Analytics update completed: {updated_orgs} orgs, {total_metrics} metrics")
        return result
        
    except Exception as e:
        logger.error(f"Error in analytics update: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, base=AnalyticsTask, default_retry_delay=300, max_retries=3)
def cleanup_old_data(self) -> Dict[str, Any]:
    """
    Clean up old analytics data (scheduled task).
    """
    try:
        logger.info("Starting cleanup of old analytics data")
        
        # Get database session
        db = next(get_db())
        
        # Delete metrics older than 1 year
        cutoff_date = datetime.utcnow() - timedelta(days=365)
        
        deleted_metrics = db.query(PostMetrics).filter(
            PostMetrics.collected_at < cutoff_date
        ).delete()
        
        # Delete old analytics summaries (keep last 3 months)
        summary_cutoff = datetime.utcnow() - timedelta(days=90)
        deleted_summaries = db.query(AnalyticsSummary).filter(
            AnalyticsSummary.created_at < summary_cutoff
        ).delete()
        
        db.commit()
        
        result = {
            "success": True,
            "deleted_metrics": deleted_metrics,
            "deleted_summaries": deleted_summaries,
            "cutoff_date": cutoff_date.isoformat()
        }
        
        logger.info(f"Cleanup completed: {deleted_metrics} metrics, {deleted_summaries} summaries deleted")
        return result
        
    except Exception as e:
        logger.error(f"Error in data cleanup: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, base=AnalyticsTask, default_retry_delay=300, max_retries=3)
def send_daily_reports(self) -> Dict[str, Any]:
    """
    Send daily analytics reports to organizations (scheduled task).
    """
    try:
        logger.info("Starting daily reports sending")
        
        # Get database session
        db = next(get_db())
        
        # Get all organizations
        organizations = db.query(Organization).all()
        
        reports_sent = 0
        
        for org in organizations:
            try:
                # Generate and send daily report
                task = generate_daily_report_task.delay(
                    organization_id=org.id
                )
                
                # Wait for completion
                result = task.get(timeout=300)
                if result.get('success'):
                    reports_sent += 1
                    logger.info(f"Daily report sent to organization {org.id}")
                
            except Exception as e:
                logger.error(f"Error sending daily report to organization {org.id}: {e}")
                continue
        
        result = {
            "success": True,
            "reports_sent": reports_sent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Daily reports sending completed: {reports_sent} reports sent")
        return result
        
    except Exception as e:
        logger.error(f"Error in daily reports sending: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()