from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import secrets
import json

from app.db.session import get_db
from app.models.exports import ExportJob, ExportCredential, ExportTable, ExportStatus, ExportTarget, EXPORT_TABLES
from app.models.entities import Organization
from app.core.security import get_current_user
from app.workers.export_worker import process_export_job
from pydantic import BaseModel

router = APIRouter()


class ExportJobCreate(BaseModel):
    target: str
    target_config: Dict[str, Any]
    tables: List[str]


class ExportJobResponse(BaseModel):
    id: str
    target: str
    status: str
    progress_percent: int
    current_table: Optional[str]
    records_exported: int
    total_records: int
    error_message: Optional[str]
    file_path: Optional[str]
    file_size_bytes: Optional[int]
    download_url: Optional[str]
    created_at: str
    started_at: Optional[str]
    finished_at: Optional[str]

    class Config:
        from_attributes = True


class ExportCredentialCreate(BaseModel):
    target: str
    name: str
    credentials: Dict[str, Any]


class ExportCredentialResponse(BaseModel):
    id: str
    target: str
    name: str
    is_active: bool
    last_used_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/exports/start", response_model=ExportJobResponse)
async def start_export(
    export_data: ExportJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start a new export job."""
    # Validate target
    try:
        target = ExportTarget(export_data.target)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target. Must be one of: {[t.value for t in ExportTarget]}"
        )
    
    # Validate tables
    available_tables = list(EXPORT_TABLES.keys())
    invalid_tables = [t for t in export_data.tables if t not in available_tables]
    if invalid_tables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tables: {invalid_tables}. Available tables: {available_tables}"
        )
    
    # Create export job
    export_job = ExportJob(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        user_id=current_user["user_id"],
        target=target,
        target_config=json.dumps(export_data.target_config),
        tables=json.dumps(export_data.tables),
        status=ExportStatus.pending
    )
    
    db.add(export_job)
    db.commit()
    db.refresh(export_job)
    
    # Start background task
    background_tasks.add_task(process_export_job, export_job.id)
    
    return ExportJobResponse(
        id=export_job.id,
        target=export_job.target.value,
        status=export_job.status.value,
        progress_percent=export_job.progress_percent,
        current_table=export_job.current_table,
        records_exported=export_job.records_exported,
        total_records=export_job.total_records,
        error_message=export_job.error_message,
        file_path=export_job.file_path,
        file_size_bytes=export_job.file_size_bytes,
        download_url=export_job.download_url,
        created_at=export_job.created_at.isoformat(),
        started_at=export_job.started_at.isoformat() if export_job.started_at else None,
        finished_at=export_job.finished_at.isoformat() if export_job.finished_at else None
    )


@router.get("/exports/status/{job_id}", response_model=ExportJobResponse)
async def get_export_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get the status of an export job."""
    export_job = db.query(ExportJob).filter(
        ExportJob.id == job_id,
        ExportJob.org_id == current_user["org_id"]
    ).first()
    
    if not export_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found"
        )
    
    return ExportJobResponse(
        id=export_job.id,
        target=export_job.target.value,
        status=export_job.status.value,
        progress_percent=export_job.progress_percent,
        current_table=export_job.current_table,
        records_exported=export_job.records_exported,
        total_records=export_job.total_records,
        error_message=export_job.error_message,
        file_path=export_job.file_path,
        file_size_bytes=export_job.file_size_bytes,
        download_url=export_job.download_url,
        created_at=export_job.created_at.isoformat(),
        started_at=export_job.started_at.isoformat() if export_job.started_at else None,
        finished_at=export_job.finished_at.isoformat() if export_job.finished_at else None
    )


@router.get("/exports", response_model=List[ExportJobResponse])
async def list_exports(
    status: Optional[str] = None,
    target: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List export jobs with optional filtering."""
    query = db.query(ExportJob).filter(ExportJob.org_id == current_user["org_id"])
    
    if status:
        try:
            status_enum = ExportStatus(status)
            query = query.filter(ExportJob.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in ExportStatus]}"
            )
    
    if target:
        try:
            target_enum = ExportTarget(target)
            query = query.filter(ExportJob.target == target_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid target. Must be one of: {[t.value for t in ExportTarget]}"
            )
    
    export_jobs = query.order_by(ExportJob.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        ExportJobResponse(
            id=job.id,
            target=job.target.value,
            status=job.status.value,
            progress_percent=job.progress_percent,
            current_table=job.current_table,
            records_exported=job.records_exported,
            total_records=job.total_records,
            error_message=job.error_message,
            file_path=job.file_path,
            file_size_bytes=job.file_size_bytes,
            download_url=job.download_url,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            finished_at=job.finished_at.isoformat() if job.finished_at else None
        )
        for job in export_jobs
    ]


@router.delete("/exports/{job_id}")
async def cancel_export(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel an export job."""
    export_job = db.query(ExportJob).filter(
        ExportJob.id == job_id,
        ExportJob.org_id == current_user["org_id"]
    ).first()
    
    if not export_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found"
        )
    
    if export_job.status in [ExportStatus.completed, ExportStatus.failed, ExportStatus.cancelled]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed, failed, or already cancelled job"
        )
    
    export_job.status = ExportStatus.cancelled
    export_job.finished_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Export job cancelled successfully"}


@router.get("/exports/tables")
async def get_available_tables():
    """Get available tables for export."""
    return {
        "tables": EXPORT_TABLES,
        "table_names": list(EXPORT_TABLES.keys())
    }


@router.post("/exports/credentials", response_model=ExportCredentialResponse)
async def create_export_credential(
    credential_data: ExportCredentialCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create export credentials for a target."""
    # Validate target
    try:
        target = ExportTarget(credential_data.target)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target. Must be one of: {[t.value for t in ExportTarget]}"
        )
    
    # Validate credentials based on target
    validation_result = await validate_credentials(target, credential_data.credentials)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid credentials: {validation_result['message']}"
        )
    
    # Create credential record
    credential = ExportCredential(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        target=target,
        name=credential_data.name,
        encrypted_credentials=json.dumps(credential_data.credentials)  # In production, encrypt this
    )
    
    db.add(credential)
    db.commit()
    db.refresh(credential)
    
    return ExportCredentialResponse(
        id=credential.id,
        target=credential.target.value,
        name=credential.name,
        is_active=credential.is_active,
        last_used_at=credential.last_used_at.isoformat() if credential.last_used_at else None,
        created_at=credential.created_at.isoformat()
    )


@router.get("/exports/credentials", response_model=List[ExportCredentialResponse])
async def list_export_credentials(
    target: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List export credentials."""
    query = db.query(ExportCredential).filter(ExportCredential.org_id == current_user["org_id"])
    
    if target:
        try:
            target_enum = ExportTarget(target)
            query = query.filter(ExportCredential.target == target_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid target. Must be one of: {[t.value for t in ExportTarget]}"
            )
    
    credentials = query.all()
    
    return [
        ExportCredentialResponse(
            id=cred.id,
            target=cred.target.value,
            name=cred.name,
            is_active=cred.is_active,
            last_used_at=cred.last_used_at.isoformat() if cred.last_used_at else None,
            created_at=cred.created_at.isoformat()
        )
        for cred in credentials
    ]


@router.delete("/exports/credentials/{credential_id}")
async def delete_export_credential(
    credential_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete export credentials."""
    credential = db.query(ExportCredential).filter(
        ExportCredential.id == credential_id,
        ExportCredential.org_id == current_user["org_id"]
    ).first()
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export credential not found"
        )
    
    db.delete(credential)
    db.commit()
    
    return {"message": "Export credential deleted successfully"}


async def validate_credentials(target: ExportTarget, credentials: Dict[str, Any]) -> Dict[str, Any]:
    """Validate credentials for a specific target."""
    if target == ExportTarget.bigquery:
        from app.integrations.bigquery import validate_bigquery_credentials
        return validate_bigquery_credentials(credentials)
    
    elif target == ExportTarget.snowflake:
        from app.integrations.snowflake import validate_snowflake_credentials
        return validate_snowflake_credentials(credentials)
    
    elif target == ExportTarget.s3:
        # Validate S3 credentials
        required_fields = ["bucket", "access_key_id", "secret_access_key", "region"]
        missing_fields = [field for field in required_fields if field not in credentials]
        
        if missing_fields:
            return {
                "valid": False,
                "message": f"Missing required fields: {missing_fields}",
                "details": {}
            }
        
        return {
            "valid": True,
            "message": "S3 credentials are valid",
            "details": {"bucket": credentials["bucket"], "region": credentials["region"]}
        }
    
    elif target == ExportTarget.csv:
        # CSV doesn't need credentials
        return {
            "valid": True,
            "message": "CSV export doesn't require credentials",
            "details": {}
        }
    
    else:
        return {
            "valid": False,
            "message": f"Unknown target: {target}",
            "details": {}
        }
