"""
Publishing API Router
Handles content publishing with platform abstraction and external references
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid

from app.api.deps import get_db, get_current_user
from app.schemas.publishing import (
    PublishPreviewRequest, PublishPreviewResponse,
    PublishSendRequest, PublishSendResponse,
    PublishingJobResponse, ExternalReferenceResponse
)
from app.models.publishing import (
    PublishingJob, ExternalReference, PublishingPreview, PlatformIntegration
)
from app.models.cms import ContentItem, UserAccount
from app.services.publishing_service import PublishingService
from app.services.safety import safety_service
from app.workers.tasks.publishing_tasks import publish_content_task

router = APIRouter()


@router.post("/publish/preview", response_model=PublishPreviewResponse)
async def preview_publish(
    request: PublishPreviewRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> PublishPreviewResponse:
    """
    Preview and validate content for publishing to a specific platform with safety checks.
    """
    try:
        # Get content item
        content = db.query(ContentItem).filter(
            ContentItem.id == request.content_id,
            ContentItem.organization_id == current_user.organization_id
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content item not found"
            )
        
        # Initialize publishing service
        publishing_service = PublishingService()
        
        # Get platform driver
        driver = publishing_service.get_driver(request.platform)
        
        # Sanitize and validate content
        sanitized_content = driver.sanitize_content(content.content)
        validation_result = driver.validate_content(sanitized_content)
        
        # Safety check on content
        safety_result = await safety_service.check_content(
            content=sanitized_content,
            platform=request.platform,
            brand_guide_id=str(content.brand_guide_id) if hasattr(content, 'brand_guide_id') and content.brand_guide_id else None,
            user_id=current_user.id
        )
        
        # Combine validation and safety results
        all_errors = validation_result.get("errors", [])
        all_warnings = validation_result.get("warnings", [])
        
        # Add safety violations to errors/warnings
        for violation in safety_result.violations:
            if violation.level.value == "blocked":
                all_errors.append(f"Safety: {violation.message}")
            else:
                all_warnings.append(f"Safety: {violation.message}")
        
        # Add safety suggestions to warnings
        all_warnings.extend(safety_result.suggestions)
        
        # Determine overall validity
        is_valid = validation_result["is_valid"] and safety_result.is_safe
        
        # Save preview
        preview = PublishingPreview(
            organization_id=current_user.organization_id,
            content_item_id=request.content_id,
            platform=request.platform,
            original_content=content.content,
            sanitized_content=sanitized_content,
            is_valid=is_valid,
            validation_errors=all_errors,
            warnings=all_warnings,
            constraints_applied=validation_result.get("constraints", {}),
            character_count=len(sanitized_content),
            hashtag_count=sanitized_content.count("#")
        )
        
        db.add(preview)
        db.commit()
        db.refresh(preview)
        
        return PublishPreviewResponse(
            content_id=request.content_id,
            platform=request.platform,
            sanitized_content=sanitized_content,
            is_valid=is_valid,
            validation_errors=all_errors,
            warnings=all_warnings,
            constraints_applied=validation_result.get("constraints", {}),
            character_count=len(sanitized_content),
            hashtag_count=sanitized_content.count("#")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Publish preview failed: {str(e)}"
        )


@router.post("/publish/send", response_model=PublishSendResponse)
async def send_publish(
    request: PublishSendRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> PublishSendResponse:
    """
    Queue content for publishing to multiple platforms.
    """
    try:
        # Verify content item exists
        content = db.query(ContentItem).filter(
            ContentItem.id == request.content_id,
            ContentItem.organization_id == current_user.organization_id
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content item not found"
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create publishing job
        publishing_job = PublishingJob(
            organization_id=current_user.organization_id,
            content_item_id=request.content_id,
            job_id=job_id,
            platforms=request.platforms,
            total_platforms=len(request.platforms),
            status="pending"
        )
        
        db.add(publishing_job)
        db.commit()
        db.refresh(publishing_job)
        
        # Queue Celery task for each platform
        for platform in request.platforms:
            task = publish_content_task.delay(
                job_id=job_id,
                content_id=request.content_id,
                platform=platform,
                organization_id=current_user.organization_id,
                scheduled_time=request.scheduled_time
            )
        
        return PublishSendResponse(
            job_id=job_id,
            content_id=request.content_id,
            platforms=request.platforms,
            status="pending",
            status_url=f"/api/v1/publishing/jobs/{job_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Publish send failed: {str(e)}"
        )


@router.get("/publishing/jobs/{job_id}", response_model=PublishingJobResponse)
async def get_publishing_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> PublishingJobResponse:
    """
    Get the status of a publishing job.
    """
    job = db.query(PublishingJob).filter(
        PublishingJob.job_id == job_id,
        PublishingJob.organization_id == current_user.organization_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publishing job not found"
        )
    
    return PublishingJobResponse.from_orm(job)


@router.get("/publishing/jobs", response_model=List[PublishingJobResponse])
async def list_publishing_jobs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[PublishingJobResponse]:
    """
    List publishing jobs for the current organization.
    """
    jobs = db.query(PublishingJob).filter(
        PublishingJob.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    
    return [PublishingJobResponse.from_orm(job) for job in jobs]


@router.get("/external-references", response_model=List[ExternalReferenceResponse])
async def list_external_references(
    content_id: int = None,
    platform: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ExternalReferenceResponse]:
    """
    List external references (published posts) for the current organization.
    """
    query = db.query(ExternalReference).filter(
        ExternalReference.organization_id == current_user.organization_id
    )
    
    if content_id:
        query = query.filter(ExternalReference.content_item_id == content_id)
    if platform:
        query = query.filter(ExternalReference.platform == platform)
    
    references = query.offset(skip).limit(limit).all()
    return [ExternalReferenceResponse.from_orm(ref) for ref in references]


@router.get("/platforms", response_model=List[Dict[str, Any]])
async def list_platforms(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    List available publishing platforms and their status.
    """
    integrations = db.query(PlatformIntegration).filter(
        PlatformIntegration.organization_id == current_user.organization_id
    ).all()
    
    platforms = []
    for integration in integrations:
        platforms.append({
            "platform": integration.platform,
            "account_name": integration.account_name,
            "is_connected": integration.is_connected,
            "is_active": integration.is_active,
            "last_sync_at": integration.last_sync_at
        })
    
    return platforms


@router.post("/platforms/{platform}/test", status_code=status.HTTP_200_OK)
async def test_platform_connection(
    platform: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Test connection to a specific platform.
    """
    try:
        # Get platform integration
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.organization_id == current_user.organization_id,
            PlatformIntegration.platform == platform
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform integration not found"
            )
        
        # Initialize publishing service
        publishing_service = PublishingService()
        
        # Test connection
        driver = publishing_service.get_driver(platform)
        test_result = driver.test_connection(integration.credentials)
        
        if test_result["success"]:
            integration.is_connected = True
            integration.error_message = None
        else:
            integration.is_connected = False
            integration.error_message = test_result.get("error", "Connection test failed")
        
        db.commit()
        
        return {"status": "success", "message": "Platform connection tested successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Platform test failed: {str(e)}"
        )