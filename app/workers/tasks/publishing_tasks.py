"""
Publishing Celery Tasks
Handles content publishing to various platforms
"""

from celery import Task
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from app.workers.celery_app import celery_app
from app.models.publishing import PublishingJob, ExternalReference
from app.services.publishing_service import PublishingService


class PublishingTask(Task):
    """Base task for publishing operations"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        print(f"Publishing Task {task_id} failed: {exc}")
        # FIXME: Add proper error logging and notification
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        print(f"Publishing Task {task_id} completed successfully")


@celery_app.task(bind=True, base=PublishingTask, default_retry_delay=600, max_retries=5)
def publish_content_task(
    self,
    job_id: str,
    content_id: int,
    platform: str,
    organization_id: int,
    scheduled_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publish content to a specific platform using real API calls.
    """
    try:
        logger.info(f"Publishing content {content_id} to {platform} for job {job_id}")
        
        # Get database session
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        try:
            # Get content from database
            from app.models.cms import ContentItem
            content = db.query(ContentItem).filter(
                ContentItem.id == content_id,
                ContentItem.organization_id == organization_id
            ).first()
            
            if not content:
                logger.error(f"Content {content_id} not found for organization {organization_id}")
                return {"success": False, "error": "Content not found"}
            
            # Get platform integration credentials
            from app.models.publishing import PlatformIntegration
            integration = db.query(PlatformIntegration).filter(
                PlatformIntegration.organization_id == organization_id,
                PlatformIntegration.platform == platform,
                PlatformIntegration.status == "active"
            ).first()
            
            if not integration:
                logger.error(f"No active {platform} integration found for organization {organization_id}")
                return {"success": False, "error": f"No active {platform} integration found"}
            
            # Initialize publishing service
            publishing_service = PublishingService()
            
            # Get platform driver
            driver = publishing_service.get_driver(platform)
            
            # Prepare content and media
            content_text = content.content
            media_items = []
            
            # Add media items if present
            if hasattr(content, 'media_items') and content.media_items:
                for media_item in content.media_items:
                    media_items.append({
                        "url": media_item.url,
                        "type": media_item.media_type,
                        "caption": media_item.caption
                    })
            
            # Prepare platform options
            from app.services.publishers.base import PlatformOptions
            platform_opts = PlatformOptions(
                account_id=integration.user_id,
                settings=integration.settings or {}
            )
            
            # Parse scheduled time if provided
            schedule_at = None
            if scheduled_time:
                from datetime import datetime
                schedule_at = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            
            # Publish content using real API
            result = driver.publish(
                content=content_text,
                media=media_items,
                platform_opts=platform_opts,
                schedule_at=schedule_at
            )
            
            if result:
                # Create external reference
                external_reference = ExternalReference(
                    organization_id=organization_id,
                    content_item_id=content_id,
                    platform=platform,
                    external_id=result.external_id,
                    external_url=result.url,
                    status=result.status.value,
                    platform_data=result.platform_data,
                    published_at=result.published_at
                )
                
                db.add(external_reference)
                db.commit()
                
                logger.info(f"Successfully published content {content_id} to {platform}")
                return {
                    "success": True,
                    "external_id": result.external_id,
                    "url": result.url,
                    "status": result.status.value
                }
            else:
                logger.error(f"Failed to publish content {content_id} to {platform}")
                return {"success": False, "error": "Publishing failed"}
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error publishing content {content_id} to {platform}: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=PublishingTask, default_retry_delay=300, max_retries=3)
def bulk_publish_content_task(
    self,
    job_id: str,
    content_ids: list,
    platforms: list,
    organization_id: int,
    scheduled_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publish multiple content items to multiple platforms.
    """
    try:
        print(f"Bulk publishing {len(content_ids)} content items to {len(platforms)} platforms for job {job_id}")
        
        results = []
        total_tasks = len(content_ids) * len(platforms)
        completed_tasks = 0
        
        # Publish each content item to each platform
        for content_id in content_ids:
            for platform in platforms:
                try:
                    # Call individual publish task
                    result = publish_content_task.delay(
                        job_id=job_id,
                        content_id=content_id,
                        platform=platform,
                        organization_id=organization_id,
                        scheduled_time=scheduled_time
                    )
                    
                    results.append({
                        "content_id": content_id,
                        "platform": platform,
                        "task_id": result.id,
                        "status": "queued"
                    })
                    
                    completed_tasks += 1
                    
                    # Update progress
                    self.update_state(
                        state="PROGRESS",
                        meta={
                            "current": completed_tasks,
                            "total": total_tasks,
                            "completed": completed_tasks
                        }
                    )
                    
                except Exception as e:
                    print(f"Error queuing publish task for content {content_id} to {platform}: {e}")
                    results.append({
                        "content_id": content_id,
                        "platform": platform,
                        "error": str(e),
                        "status": "failed"
                    })
        
        print(f"Bulk publishing job {job_id} queued {completed_tasks} tasks")
        
        return {
            "success": True,
            "job_id": job_id,
            "total_tasks": total_tasks,
            "queued_tasks": completed_tasks,
            "results": results
        }
        
    except Exception as e:
        print(f"Error in bulk publishing job {job_id}: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=PublishingTask, default_retry_delay=300, max_retries=3)
def republish_content_task(
    self,
    content_id: int,
    platform: str,
    organization_id: int,
    reason: str = "retry"
) -> Dict[str, Any]:
    """
    Republish content to a platform (for retries or updates).
    """
    try:
        print(f"Republishing content {content_id} to {platform} (reason: {reason})")
        
        # Call the regular publish task
        result = publish_content_task.delay(
            job_id=f"republish_{content_id}_{platform}",
            content_id=content_id,
            platform=platform,
            organization_id=organization_id
        )
        
        return {
            "success": True,
            "content_id": content_id,
            "platform": platform,
            "task_id": result.id,
            "reason": reason
        }
        
    except Exception as e:
        print(f"Error republishing content {content_id} to {platform}: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=PublishingTask, default_retry_delay=300, max_retries=3)
def delete_published_content_task(
    self,
    external_reference_id: int,
    organization_id: int
) -> Dict[str, Any]:
    """
    Delete published content from a platform.
    """
    try:
        print(f"Deleting published content {external_reference_id}")
        
        # FIXME: Get external reference from database
        # external_ref = db.query(ExternalReference).filter(
        #     ExternalReference.id == external_reference_id,
        #     ExternalReference.organization_id == organization_id
        # ).first()
        # 
        # if not external_ref:
        #     return {"success": False, "error": "External reference not found"}
        
        # Initialize publishing service
        publishing_service = PublishingService()
        
        # Get platform driver
        # driver = publishing_service.get_driver(external_ref.platform)
        
        # Get platform credentials
        # FIXME: Get credentials from database
        credentials = {"access_token": "mock_token", "account_id": "mock_account"}
        
        # Delete content from platform
        # result = driver.delete_content(external_ref.external_id, credentials)
        
        # Mock result for now
        result = {"success": True, "message": "Content deleted successfully"}
        
        if result.get("success"):
            # Update external reference status
            # external_ref.status = "deleted"
            # external_ref.updated_at = datetime.utcnow()
            # db.commit()
            
            print(f"Published content {external_reference_id} deleted successfully")
            return {
                "success": True,
                "external_reference_id": external_reference_id,
                "message": "Content deleted successfully"
            }
        else:
            print(f"Failed to delete published content {external_reference_id}: {result.get('error')}")
            return {
                "success": False,
                "external_reference_id": external_reference_id,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Error deleting published content {external_reference_id}: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=PublishingTask, default_retry_delay=300, max_retries=3)
def update_published_content_task(
    self,
    external_reference_id: int,
    new_content: str,
    organization_id: int
) -> Dict[str, Any]:
    """
    Update published content on a platform.
    """
    try:
        print(f"Updating published content {external_reference_id}")
        
        # FIXME: Get external reference from database
        # external_ref = db.query(ExternalReference).filter(
        #     ExternalReference.id == external_reference_id,
        #     ExternalReference.organization_id == organization_id
        # ).first()
        # 
        # if not external_ref:
        #     return {"success": False, "error": "External reference not found"}
        
        # Initialize publishing service
        publishing_service = PublishingService()
        
        # Get platform driver
        # driver = publishing_service.get_driver(external_ref.platform)
        
        # Get platform credentials
        # FIXME: Get credentials from database
        credentials = {"access_token": "mock_token", "account_id": "mock_account"}
        
        # Update content on platform
        # result = driver.update_content(external_ref.external_id, new_content, credentials)
        
        # Mock result for now
        result = {"success": True, "message": "Content updated successfully"}
        
        if result.get("success"):
            # Update external reference
            # external_ref.updated_at = datetime.utcnow()
            # db.commit()
            
            print(f"Published content {external_reference_id} updated successfully")
            return {
                "success": True,
                "external_reference_id": external_reference_id,
                "message": "Content updated successfully"
            }
        else:
            print(f"Failed to update published content {external_reference_id}: {result.get('error')}")
            return {
                "success": False,
                "external_reference_id": external_reference_id,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Error updating published content {external_reference_id}: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=PublishingTask, default_retry_delay=300, max_retries=3)
def sync_published_content_task(
    self,
    platform: str,
    organization_id: int,
    last_sync_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sync published content from platform to get latest status.
    """
    try:
        print(f"Syncing published content for {platform}")
        
        # Initialize publishing service
        publishing_service = PublishingService()
        
        # Get platform driver
        driver = publishing_service.get_driver(platform)
        
        # Get platform credentials
        # FIXME: Get credentials from database
        credentials = {"access_token": "mock_token", "account_id": "mock_account"}
        
        # Sync content from platform
        # result = driver.sync_content(credentials, last_sync_time)
        
        # Mock result for now
        result = {
            "success": True,
            "synced_count": 10,
            "updated_count": 5,
            "new_count": 2
        }
        
        if result.get("success"):
            print(f"Synced {result.get('synced_count', 0)} published content items for {platform}")
            return {
                "success": True,
                "platform": platform,
                "synced_count": result.get("synced_count", 0),
                "updated_count": result.get("updated_count", 0),
                "new_count": result.get("new_count", 0)
            }
        else:
            print(f"Failed to sync published content for {platform}: {result.get('error')}")
            return {
                "success": False,
                "platform": platform,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Error syncing published content for {platform}: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=PublishingTask, default_retry_delay=300, max_retries=3)
def test_platform_connection_task(
    self,
    platform: str,
    organization_id: int
) -> Dict[str, Any]:
    """
    Test connection to a platform.
    """
    try:
        print(f"Testing connection to {platform}")
        
        # Initialize publishing service
        publishing_service = PublishingService()
        
        # Get platform driver
        driver = publishing_service.get_driver(platform)
        
        # Get platform credentials
        # FIXME: Get credentials from database
        credentials = {"access_token": "mock_token", "account_id": "mock_account"}
        
        # Test connection
        result = driver.test_connection(credentials)
        
        if result.get("success"):
            print(f"Connection to {platform} tested successfully")
            return {
                "success": True,
                "platform": platform,
                "message": "Connection successful"
            }
        else:
            print(f"Connection to {platform} failed: {result.get('error')}")
            return {
                "success": False,
                "platform": platform,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Error testing connection to {platform}: {e}")
        self.retry(exc=e)