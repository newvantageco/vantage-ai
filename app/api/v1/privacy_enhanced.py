"""
Enhanced Privacy API endpoints
Handles data export, deletion, and privacy compliance operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.privacy_service import PrivacyService

router = APIRouter()


class ExportRequest(BaseModel):
    format_type: str = "json"  # json, csv, zip


class ExportResponse(BaseModel):
    export_id: str
    job_id: str
    status: str
    format_type: str
    expires_at: str
    estimated_completion: str


class ExportStatusResponse(BaseModel):
    export_id: str
    status: str
    format_type: str
    created_at: str
    expires_at: str
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None


class DeletionRequest(BaseModel):
    reason: Optional[str] = ""


class DeletionResponse(BaseModel):
    deletion_id: str
    job_id: str
    status: str
    reason: str
    scheduled_for: str
    grace_period_hours: int


class DeletionStatusResponse(BaseModel):
    deletion_id: str
    status: str
    reason: str
    requested_at: str
    scheduled_for: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class DataSummaryResponse(BaseModel):
    organization_id: str
    organization_name: str
    data_summary: Dict[str, int]
    oldest_data: Optional[str] = None
    data_retention_policy: str
    last_export: Optional[str] = None
    last_deletion_request: Optional[str] = None


@router.post("/privacy/export", response_model=ExportResponse)
async def create_data_export(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a data export request for the organization"""
    try:
        # Validate format type
        if request.format_type not in ["json", "csv", "zip"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format type. Must be 'json', 'csv', or 'zip'"
            )
        
        privacy_service = PrivacyService(db)
        
        result = privacy_service.create_data_export(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            format_type=request.format_type
        )
        
        return ExportResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create data export: {str(e)}"
        )


@router.get("/privacy/export/{export_id}", response_model=ExportStatusResponse)
async def get_export_status(
    export_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get the status of a data export"""
    try:
        privacy_service = PrivacyService(db)
        
        result = privacy_service.get_export_status(
            export_id=export_id,
            org_id=current_user["org_id"]
        )
        
        return ExportStatusResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get export status: {str(e)}"
        )


@router.get("/privacy/export/{export_id}/download")
async def download_export_file(
    export_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Download the exported data file"""
    try:
        privacy_service = PrivacyService(db)
        
        # Get file path (with security checks)
        file_path = privacy_service.download_export_file(
            file_name=f"{export_id}.json",  # or other format
            org_id=current_user["org_id"]
        )
        
        # Return file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Determine content type based on file extension
        if file_path.endswith('.json'):
            media_type = 'application/json'
        elif file_path.endswith('.csv'):
            media_type = 'text/csv'
        elif file_path.endswith('.zip'):
            media_type = 'application/zip'
        else:
            media_type = 'application/octet-stream'
        
        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={export_id}.{file_path.split('.')[-1]}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download export file: {str(e)}"
        )


@router.post("/privacy/delete", response_model=DeletionResponse)
async def create_deletion_request(
    request: DeletionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a data deletion request for the organization"""
    try:
        privacy_service = PrivacyService(db)
        
        result = privacy_service.create_deletion_request(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            reason=request.reason
        )
        
        return DeletionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deletion request: {str(e)}"
        )


@router.get("/privacy/delete/{deletion_id}", response_model=DeletionStatusResponse)
async def get_deletion_status(
    deletion_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get the status of a deletion request"""
    try:
        privacy_service = PrivacyService(db)
        
        result = privacy_service.get_deletion_status(
            deletion_id=deletion_id,
            org_id=current_user["org_id"]
        )
        
        return DeletionStatusResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deletion status: {str(e)}"
        )


@router.post("/privacy/delete/{deletion_id}/cancel")
async def cancel_deletion_request(
    deletion_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel a pending deletion request"""
    try:
        privacy_service = PrivacyService(db)
        
        result = privacy_service.cancel_deletion_request(
            deletion_id=deletion_id,
            org_id=current_user["org_id"],
            user_id=current_user["user_id"]
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel deletion request: {str(e)}"
        )


@router.get("/privacy/summary", response_model=DataSummaryResponse)
async def get_data_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a summary of organization data for privacy compliance"""
    try:
        privacy_service = PrivacyService(db)
        
        result = privacy_service.get_organization_data_summary(
            org_id=current_user["org_id"]
        )
        
        return DataSummaryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data summary: {str(e)}"
        )


@router.get("/privacy/exports")
async def list_exports(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List organization's data exports"""
    try:
        from app.models.privacy import DataExport
        
        exports = db.query(DataExport).filter(
            DataExport.organization_id == current_user["org_id"]
        ).order_by(DataExport.created_at.desc()).limit(limit).all()
        
        return {
            "exports": [
                {
                    "id": export.id,
                    "format_type": export.format_type,
                    "status": export.status.value,
                    "created_at": export.created_at.isoformat(),
                    "completed_at": export.completed_at.isoformat() if export.completed_at else None,
                    "expires_at": export.expires_at.isoformat(),
                    "file_size": export.file_size,
                    "error_message": export.error_message
                }
                for export in exports
            ],
            "total": len(exports)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list exports: {str(e)}"
        )


@router.get("/privacy/deletions")
async def list_deletion_requests(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List organization's deletion requests"""
    try:
        from app.models.privacy import DeletionRequest
        
        deletions = db.query(DeletionRequest).filter(
            DeletionRequest.organization_id == current_user["org_id"]
        ).order_by(DeletionRequest.created_at.desc()).limit(limit).all()
        
        return {
            "deletions": [
                {
                    "id": deletion.id,
                    "reason": deletion.reason,
                    "status": deletion.status.value,
                    "created_at": deletion.created_at.isoformat(),
                    "scheduled_for": deletion.scheduled_for.isoformat(),
                    "completed_at": deletion.completed_at.isoformat() if deletion.completed_at else None,
                    "canceled_at": deletion.canceled_at.isoformat() if deletion.canceled_at else None,
                    "error_message": deletion.error_message
                }
                for deletion in deletions
            ],
            "total": len(deletions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deletion requests: {str(e)}"
        )


@router.get("/privacy/health")
async def privacy_health_check(
    db: Session = Depends(get_db)
):
    """Health check for privacy service"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Test export directory
        from app.core.config import get_settings
        settings = get_settings()
        export_dir = settings.data_export_path or "/tmp/exports"
        import os
        os.makedirs(export_dir, exist_ok=True)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_connected": True,
            "export_directory_accessible": True
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "database_connected": False,
            "export_directory_accessible": False
        }
