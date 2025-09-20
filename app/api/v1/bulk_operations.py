"""
Bulk Operations API Router
Handles bulk operations for content management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.api.deps import get_db, get_current_user
from app.schemas.bulk_operations import (
    BulkContentUpdateRequest, BulkContentUpdateResponse,
    BulkContentDeleteRequest, BulkContentDeleteResponse,
    BulkContentScheduleRequest, BulkContentScheduleResponse,
    BulkContentStatusUpdateRequest, BulkContentStatusUpdateResponse,
    BulkContentDuplicateRequest, BulkContentDuplicateResponse,
    BulkOperationStatus, BulkOperationResponse
)
from app.models.cms import ContentItem, Schedule, UserAccount
from app.workers.tasks.scheduler_tasks import schedule_content_publish, cancel_scheduled_content

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/content/update", response_model=BulkContentUpdateResponse)
async def bulk_update_content(
    request: BulkContentUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BulkContentUpdateResponse:
    """Bulk update content items"""
    try:
        updated_count = 0
        failed_count = 0
        failed_ids = []
        
        for content_id in request.content_ids:
            try:
                # Get content item
                content = db.query(ContentItem).filter(
                    ContentItem.id == content_id,
                    ContentItem.organization_id == current_user.organization_id
                ).first()
                
                if not content:
                    failed_count += 1
                    failed_ids.append(content_id)
                    continue
                
                # Apply updates
                update_data = request.update_data.dict(exclude_unset=True)
                for field, value in update_data.items():
                    if hasattr(content, field):
                        setattr(content, field, value)
                
                db.commit()
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update content {content_id}: {str(e)}")
                failed_count += 1
                failed_ids.append(content_id)
                db.rollback()
        
        return BulkContentUpdateResponse(
            updated_count=updated_count,
            failed_count=failed_count,
            failed_ids=failed_ids
        )
        
    except Exception as e:
        logger.error(f"Bulk content update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk content update failed: {str(e)}"
        )


@router.post("/content/delete", response_model=BulkContentDeleteResponse)
async def bulk_delete_content(
    request: BulkContentDeleteRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BulkContentDeleteResponse:
    """Bulk delete content items"""
    try:
        deleted_count = 0
        failed_count = 0
        failed_ids = []
        
        for content_id in request.content_ids:
            try:
                # Get content item
                content = db.query(ContentItem).filter(
                    ContentItem.id == content_id,
                    ContentItem.organization_id == current_user.organization_id
                ).first()
                
                if not content:
                    failed_count += 1
                    failed_ids.append(content_id)
                    continue
                
                # Cancel any scheduled content
                schedules = db.query(Schedule).filter(
                    Schedule.content_item_id == content_id,
                    Schedule.status == "scheduled"
                ).all()
                
                for schedule in schedules:
                    schedule.status = "cancelled"
                
                # Delete content
                db.delete(content)
                db.commit()
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Failed to delete content {content_id}: {str(e)}")
                failed_count += 1
                failed_ids.append(content_id)
                db.rollback()
        
        return BulkContentDeleteResponse(
            deleted_count=deleted_count,
            failed_count=failed_count,
            failed_ids=failed_ids
        )
        
    except Exception as e:
        logger.error(f"Bulk content deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk content deletion failed: {str(e)}"
        )


@router.post("/content/schedule", response_model=BulkContentScheduleResponse)
async def bulk_schedule_content(
    request: BulkContentScheduleRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BulkContentScheduleResponse:
    """Bulk schedule content for publishing"""
    try:
        scheduled_count = 0
        failed_count = 0
        failed_ids = []
        schedule_ids = []
        
        for content_id in request.content_ids:
            try:
                # Get content item
                content = db.query(ContentItem).filter(
                    ContentItem.id == content_id,
                    ContentItem.organization_id == current_user.organization_id
                ).first()
                
                if not content:
                    failed_count += 1
                    failed_ids.append(content_id)
                    continue
                
                # Create schedule
                schedule = Schedule(
                    organization_id=current_user.organization_id,
                    content_item_id=content_id,
                    scheduled_at=request.scheduled_at,
                    platforms=request.platforms,
                    status="scheduled"
                )
                
                db.add(schedule)
                db.commit()
                db.refresh(schedule)
                
                # Update content status
                content.status = "scheduled"
                db.commit()
                
                # Schedule the actual publishing task
                task = schedule_content_publish.delay(
                    content_id=content_id,
                    publish_at=request.scheduled_at.isoformat(),
                    platforms=request.platforms
                )
                
                scheduled_count += 1
                schedule_ids.append(schedule.id)
                
            except Exception as e:
                logger.error(f"Failed to schedule content {content_id}: {str(e)}")
                failed_count += 1
                failed_ids.append(content_id)
                db.rollback()
        
        return BulkContentScheduleResponse(
            scheduled_count=scheduled_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
            schedule_ids=schedule_ids
        )
        
    except Exception as e:
        logger.error(f"Bulk content scheduling failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk content scheduling failed: {str(e)}"
        )


@router.post("/content/status", response_model=BulkContentStatusUpdateResponse)
async def bulk_update_content_status(
    request: BulkContentStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BulkContentStatusUpdateResponse:
    """Bulk update content status"""
    try:
        updated_count = 0
        failed_count = 0
        failed_ids = []
        
        for content_id in request.content_ids:
            try:
                # Get content item
                content = db.query(ContentItem).filter(
                    ContentItem.id == content_id,
                    ContentItem.organization_id == current_user.organization_id
                ).first()
                
                if not content:
                    failed_count += 1
                    failed_ids.append(content_id)
                    continue
                
                # Update status
                content.status = request.status
                
                # If setting to published, update published_at
                if request.status == "published":
                    content.published_at = datetime.utcnow()
                
                # If setting to draft, cancel any scheduled content
                if request.status == "draft":
                    schedules = db.query(Schedule).filter(
                        Schedule.content_item_id == content_id,
                        Schedule.status == "scheduled"
                    ).all()
                    
                    for schedule in schedules:
                        schedule.status = "cancelled"
                
                db.commit()
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update content status {content_id}: {str(e)}")
                failed_count += 1
                failed_ids.append(content_id)
                db.rollback()
        
        return BulkContentStatusUpdateResponse(
            updated_count=updated_count,
            failed_count=failed_count,
            failed_ids=failed_ids
        )
        
    except Exception as e:
        logger.error(f"Bulk content status update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk content status update failed: {str(e)}"
        )


@router.post("/content/duplicate", response_model=BulkContentDuplicateResponse)
async def bulk_duplicate_content(
    request: BulkContentDuplicateRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BulkContentDuplicateResponse:
    """Bulk duplicate content items"""
    try:
        duplicated_count = 0
        failed_count = 0
        failed_ids = []
        new_content_ids = []
        
        for content_id in request.content_ids:
            try:
                # Get original content item
                original_content = db.query(ContentItem).filter(
                    ContentItem.id == content_id,
                    ContentItem.organization_id == current_user.organization_id
                ).first()
                
                if not original_content:
                    failed_count += 1
                    failed_ids.append(content_id)
                    continue
                
                # Create duplicate
                duplicate_content = ContentItem(
                    organization_id=original_content.organization_id,
                    created_by_id=current_user.id,
                    campaign_id=original_content.campaign_id,
                    brand_guide_id=original_content.brand_guide_id,
                    title=f"{original_content.title} (Copy)",
                    content=original_content.content,
                    content_type=original_content.content_type,
                    status="draft",
                    media_urls=original_content.media_urls,
                    hashtags=original_content.hashtags,
                    mentions=original_content.mentions,
                    platform_content=original_content.platform_content,
                    tags=original_content.tags,
                    content_metadata=original_content.content_metadata
                )
                
                db.add(duplicate_content)
                db.commit()
                db.refresh(duplicate_content)
                
                duplicated_count += 1
                new_content_ids.append(duplicate_content.id)
                
            except Exception as e:
                logger.error(f"Failed to duplicate content {content_id}: {str(e)}")
                failed_count += 1
                failed_ids.append(content_id)
                db.rollback()
        
        return BulkContentDuplicateResponse(
            duplicated_count=duplicated_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
            new_content_ids=new_content_ids
        )
        
    except Exception as e:
        logger.error(f"Bulk content duplication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk content duplication failed: {str(e)}"
        )


@router.post("/content/cancel-schedule", response_model=BulkContentStatusUpdateResponse)
async def bulk_cancel_scheduled_content(
    request: BulkContentStatusUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> BulkContentStatusUpdateResponse:
    """Bulk cancel scheduled content"""
    try:
        cancelled_count = 0
        failed_count = 0
        failed_ids = []
        
        for content_id in request.content_ids:
            try:
                # Cancel scheduled content
                task = cancel_scheduled_content.delay(content_id)
                
                cancelled_count += 1
                
            except Exception as e:
                logger.error(f"Failed to cancel scheduled content {content_id}: {str(e)}")
                failed_count += 1
                failed_ids.append(content_id)
        
        return BulkContentStatusUpdateResponse(
            updated_count=cancelled_count,
            failed_count=failed_count,
            failed_ids=failed_ids
        )
        
    except Exception as e:
        logger.error(f"Bulk cancel scheduled content failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk cancel scheduled content failed: {str(e)}"
        )
