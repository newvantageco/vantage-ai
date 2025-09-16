from __future__ import annotations

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.entities import UserAccount, Organization
from app.models.retention import PrivacyJob, OrgRetention
from app.workers.privacy_worker import PrivacyWorker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/privacy", tags=["privacy"])


class ExportRequest(BaseModel):
    include_media: bool = True
    format: str = "json"  # json, csv, both


class DeleteRequest(BaseModel):
    confirm_org_name: str
    delete_media: bool = False
    grace_period_days: int = 7


class RetentionUpdate(BaseModel):
    messages_days: Optional[int] = None
    logs_days: Optional[int] = None
    metrics_days: Optional[int] = None


class PrivacyJobOut(BaseModel):
    id: str
    job_type: str
    status: str
    file_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.post("/export")
async def request_data_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Request export of organization data.
    
    Only organization owners can request data exports.
    """
    # Check if user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owners can request data exports"
        )
    
    # Check for existing pending export job
    existing_job = db.query(PrivacyJob).filter(
        PrivacyJob.org_id == current_user.org_id,
        PrivacyJob.job_type == "export",
        PrivacyJob.status.in_(["pending", "processing"])
    ).first()
    
    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Export job already in progress"
        )
    
    # Create export job
    job = PrivacyJob(
        id=str(uuid.uuid4()),
        org_id=current_user.org_id,
        job_type="export",
        status="pending",
        requested_by=current_user.id
    )
    
    db.add(job)
    db.commit()
    
    # Queue background task
    background_tasks.add_task(
        PrivacyWorker.process_export_job,
        job.id,
        request.include_media,
        request.format
    )
    
    logger.info(f"Export job {job.id} created for org {current_user.org_id}")
    
    return {
        "status": "success",
        "job_id": job.id,
        "message": "Export job queued. You will be notified when ready."
    }


@router.post("/delete")
async def request_org_deletion(
    request: DeleteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Request deletion of organization data.
    
    Only organization owners can request data deletion.
    This is irreversible and requires confirmation.
    """
    # Check if user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owners can request data deletion"
        )
    
    # Verify organization name matches
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    if not org or org.name != request.confirm_org_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name does not match"
        )
    
    # Check for existing pending delete job
    existing_job = db.query(PrivacyJob).filter(
        PrivacyJob.org_id == current_user.org_id,
        PrivacyJob.job_type == "delete",
        PrivacyJob.status.in_(["pending", "processing"])
    ).first()
    
    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deletion job already in progress"
        )
    
    # Create delete job
    job = PrivacyJob(
        id=str(uuid.uuid4()),
        org_id=current_user.org_id,
        job_type="delete",
        status="pending",
        requested_by=current_user.id
    )
    
    db.add(job)
    db.commit()
    
    # Queue background task
    background_tasks.add_task(
        PrivacyWorker.process_delete_job,
        job.id,
        request.delete_media,
        request.grace_period_days
    )
    
    logger.info(f"Delete job {job.id} created for org {current_user.org_id}")
    
    return {
        "status": "success",
        "job_id": job.id,
        "message": f"Deletion job queued. Data will be deleted after {request.grace_period_days} days grace period."
    }


@router.get("/jobs")
async def list_privacy_jobs(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """List privacy jobs for the organization."""
    jobs = db.query(PrivacyJob).filter(
        PrivacyJob.org_id == current_user.org_id
    ).order_by(PrivacyJob.created_at.desc()).limit(50).all()
    
    return {
        "jobs": [PrivacyJobOut.from_orm(job) for job in jobs]
    }


@router.get("/jobs/{job_id}")
async def get_privacy_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> PrivacyJobOut:
    """Get details of a specific privacy job."""
    job = db.query(PrivacyJob).filter(
        PrivacyJob.id == job_id,
        PrivacyJob.org_id == current_user.org_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return PrivacyJobOut.from_orm(job)


@router.get("/retention")
async def get_retention_policy(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current retention policy for the organization."""
    policy = db.query(OrgRetention).filter(
        OrgRetention.org_id == current_user.org_id
    ).first()
    
    if not policy:
        # Create default policy
        policy = OrgRetention(
            id=str(uuid.uuid4()),
            org_id=current_user.org_id
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
    
    return {
        "messages_days": policy.messages_days,
        "logs_days": policy.logs_days,
        "metrics_days": policy.metrics_days,
        "created_at": policy.created_at,
        "updated_at": policy.updated_at
    }


@router.put("/retention")
async def update_retention_policy(
    request: RetentionUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update retention policy for the organization.
    
    Only organization owners can modify retention policies.
    """
    # Check if user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owners can modify retention policies"
        )
    
    policy = db.query(OrgRetention).filter(
        OrgRetention.org_id == current_user.org_id
    ).first()
    
    if not policy:
        policy = OrgRetention(
            id=str(uuid.uuid4()),
            org_id=current_user.org_id
        )
        db.add(policy)
    
    # Update fields
    if request.messages_days is not None:
        if request.messages_days < 1 or request.messages_days > 3650:  # Max 10 years
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Messages retention must be between 1 and 3650 days"
            )
        policy.messages_days = request.messages_days
    
    if request.logs_days is not None:
        if request.logs_days < 1 or request.logs_days > 3650:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logs retention must be between 1 and 3650 days"
            )
        policy.logs_days = request.logs_days
    
    if request.metrics_days is not None:
        if request.metrics_days < 1 or request.metrics_days > 3650:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Metrics retention must be between 1 and 3650 days"
            )
        policy.metrics_days = request.metrics_days
    
    policy.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Retention policy updated for org {current_user.org_id}")
    
    return {
        "status": "success",
        "message": "Retention policy updated",
        "policy": {
            "messages_days": policy.messages_days,
            "logs_days": policy.logs_days,
            "metrics_days": policy.metrics_days,
            "updated_at": policy.updated_at
        }
    }
