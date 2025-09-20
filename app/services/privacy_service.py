"""
Privacy Service
Handles data export, deletion, and privacy compliance operations
"""

import json
import csv
import zipfile
import io
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
import uuid
import hashlib

from app.models.entities import Organization, UserAccount, Channel
from app.models.publishing import ExternalReference, PublishingJob
from app.models.analytics import PostMetrics
from app.models.billing import Subscription, Invoice, BillingEvent
from app.models.privacy import DataExport, DeletionRequest, PrivacyEvent
from app.core.config import get_settings

settings = get_settings()


class PrivacyService:
    """Service for privacy and data compliance operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.export_base_path = settings.data_export_path or "/tmp/exports"
        self.ensure_export_directory()
    
    def ensure_export_directory(self):
        """Ensure export directory exists"""
        os.makedirs(self.export_base_path, exist_ok=True)
    
    def create_data_export(self, org_id: str, user_id: str, format_type: str = "json") -> Dict[str, Any]:
        """
        Create a data export request for an organization
        
        Args:
            org_id: Organization ID
            user_id: User ID requesting export
            format_type: Export format (json, csv, zip)
            
        Returns:
            Dictionary with export job details
        """
        try:
            # Generate unique export ID
            export_id = str(uuid.uuid4())
            
            # Create export record
            export_record = DataExport(
                id=export_id,
                organization_id=org_id,
                requested_by=user_id,
                format_type=format_type,
                status="pending",
                file_path=None,
                expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days retention
            )
            
            self.db.add(export_record)
            self.db.commit()
            
            # Queue Celery job for data export
            from app.workers.tasks.privacy import export_organization_data
            job = export_organization_data.delay(export_id, org_id, format_type)
            
            # Update export record with job ID
            export_record.celery_job_id = job.id
            self.db.commit()
            
            # Log privacy event
            self._log_privacy_event(
                org_id=org_id,
                user_id=user_id,
                event_type="data_export_requested",
                event_data={
                    "export_id": export_id,
                    "format_type": format_type,
                    "job_id": job.id
                }
            )
            
            return {
                "export_id": export_id,
                "job_id": job.id,
                "status": "pending",
                "format_type": format_type,
                "expires_at": export_record.expires_at.isoformat(),
                "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create data export: {str(e)}"
            )
    
    def get_export_status(self, export_id: str, org_id: str) -> Dict[str, Any]:
        """
        Get the status of a data export
        
        Args:
            export_id: Export ID
            org_id: Organization ID
            
        Returns:
            Dictionary with export status and download URL if ready
        """
        try:
            export_record = self.db.query(DataExport).filter(
                DataExport.id == export_id,
                DataExport.organization_id == org_id
            ).first()
            
            if not export_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Export not found"
                )
            
            result = {
                "export_id": export_record.id,
                "status": export_record.status,
                "format_type": export_record.format_type,
                "created_at": export_record.created_at.isoformat(),
                "expires_at": export_record.expires_at.isoformat()
            }
            
            if export_record.status == "completed" and export_record.file_path:
                # Generate signed URL for download
                download_url = self._generate_download_url(export_record.file_path)
                result["download_url"] = download_url
                result["file_size"] = self._get_file_size(export_record.file_path)
            elif export_record.status == "failed":
                result["error_message"] = export_record.error_message
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get export status: {str(e)}"
            )
    
    def create_deletion_request(self, org_id: str, user_id: str, reason: str = "") -> Dict[str, Any]:
        """
        Create a data deletion request for an organization
        
        Args:
            org_id: Organization ID
            user_id: User ID requesting deletion
            reason: Reason for deletion
            
        Returns:
            Dictionary with deletion request details
        """
        try:
            # Check if deletion request already exists
            existing_request = self.db.query(DeletionRequest).filter(
                DeletionRequest.organization_id == org_id,
                DeletionRequest.status.in_(["pending", "processing"])
            ).first()
            
            if existing_request:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Deletion request already exists"
                )
            
            # Generate unique deletion ID
            deletion_id = str(uuid.uuid4())
            
            # Create deletion request
            deletion_request = DeletionRequest(
                id=deletion_id,
                organization_id=org_id,
                requested_by=user_id,
                reason=reason,
                status="pending",
                scheduled_for=datetime.utcnow() + timedelta(hours=24)  # 24 hour grace period
            )
            
            self.db.add(deletion_request)
            self.db.commit()
            
            # Queue Celery job for data deletion
            from app.workers.tasks.privacy import process_deletion_request
            job = process_deletion_request.delay(deletion_id, org_id)
            
            # Update deletion request with job ID
            deletion_request.celery_job_id = job.id
            self.db.commit()
            
            # Log privacy event
            self._log_privacy_event(
                org_id=org_id,
                user_id=user_id,
                event_type="deletion_requested",
                event_data={
                    "deletion_id": deletion_id,
                    "reason": reason,
                    "job_id": job.id,
                    "scheduled_for": deletion_request.scheduled_for.isoformat()
                }
            )
            
            return {
                "deletion_id": deletion_id,
                "job_id": job.id,
                "status": "pending",
                "reason": reason,
                "scheduled_for": deletion_request.scheduled_for.isoformat(),
                "grace_period_hours": 24
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create deletion request: {str(e)}"
            )
    
    def get_deletion_status(self, deletion_id: str, org_id: str) -> Dict[str, Any]:
        """
        Get the status of a deletion request
        
        Args:
            deletion_id: Deletion ID
            org_id: Organization ID
            
        Returns:
            Dictionary with deletion status
        """
        try:
            deletion_request = self.db.query(DeletionRequest).filter(
                DeletionRequest.id == deletion_id,
                DeletionRequest.organization_id == org_id
            ).first()
            
            if not deletion_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Deletion request not found"
                )
            
            return {
                "deletion_id": deletion_request.id,
                "status": deletion_request.status,
                "reason": deletion_request.reason,
                "requested_at": deletion_request.created_at.isoformat(),
                "scheduled_for": deletion_request.scheduled_for.isoformat(),
                "completed_at": deletion_request.completed_at.isoformat() if deletion_request.completed_at else None,
                "error_message": deletion_request.error_message
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get deletion status: {str(e)}"
            )
    
    def cancel_deletion_request(self, deletion_id: str, org_id: str, user_id: str) -> Dict[str, Any]:
        """
        Cancel a pending deletion request
        
        Args:
            deletion_id: Deletion ID
            org_id: Organization ID
            user_id: User ID canceling deletion
            
        Returns:
            Dictionary with cancellation result
        """
        try:
            deletion_request = self.db.query(DeletionRequest).filter(
                DeletionRequest.id == deletion_id,
                DeletionRequest.organization_id == org_id,
                DeletionRequest.status == "pending"
            ).first()
            
            if not deletion_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Deletion request not found or cannot be canceled"
                )
            
            # Cancel the Celery job if it exists
            if deletion_request.celery_job_id:
                from app.workers.tasks.privacy import process_deletion_request
                process_deletion_request.AsyncResult(deletion_request.celery_job_id).revoke(terminate=True)
            
            # Update deletion request status
            deletion_request.status = "canceled"
            deletion_request.canceled_by = user_id
            deletion_request.canceled_at = datetime.utcnow()
            self.db.commit()
            
            # Log privacy event
            self._log_privacy_event(
                org_id=org_id,
                user_id=user_id,
                event_type="deletion_canceled",
                event_data={
                    "deletion_id": deletion_id,
                    "canceled_by": user_id
                }
            )
            
            return {
                "deletion_id": deletion_id,
                "status": "canceled",
                "canceled_at": deletion_request.canceled_at.isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel deletion request: {str(e)}"
            )
    
    def get_organization_data_summary(self, org_id: str) -> Dict[str, Any]:
        """
        Get a summary of organization data for privacy compliance
        
        Args:
            org_id: Organization ID
            
        Returns:
            Dictionary with data summary
        """
        try:
            # Get organization
            org = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            
            # Count various data types
            user_count = self.db.query(UserAccount).filter(UserAccount.org_id == org_id).count()
            channel_count = self.db.query(Channel).filter(Channel.org_id == org_id).count()
            post_count = self.db.query(ExternalReference).filter(ExternalReference.organization_id == org_id).count()
            analytics_count = self.db.query(PostMetrics).filter(PostMetrics.organization_id == org_id).count()
            subscription_count = self.db.query(Subscription).filter(Subscription.organization_id == org_id).count()
            invoice_count = self.db.query(Invoice).filter(Invoice.organization_id == org_id).count()
            
            # Get data retention info
            oldest_data = self.db.query(
                text("MIN(created_at) as oldest")
            ).select_from(
                text("""
                    (SELECT created_at FROM users WHERE org_id = :org_id)
                    UNION ALL
                    (SELECT created_at FROM channels WHERE org_id = :org_id)
                    UNION ALL
                    (SELECT created_at FROM external_references WHERE organization_id = :org_id)
                    UNION ALL
                    (SELECT created_at FROM analytics_events WHERE organization_id = :org_id)
                """)
            ).params(org_id=org_id).scalar()
            
            return {
                "organization_id": org_id,
                "organization_name": org.name,
                "data_summary": {
                    "users": user_count,
                    "channels": channel_count,
                    "posts": post_count,
                    "analytics_events": analytics_count,
                    "subscriptions": subscription_count,
                    "invoices": invoice_count
                },
                "oldest_data": oldest_data.isoformat() if oldest_data else None,
                "data_retention_policy": "7 years for financial records, 3 years for analytics data",
                "last_export": self._get_last_export_date(org_id),
                "last_deletion_request": self._get_last_deletion_request_date(org_id)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get data summary: {str(e)}"
            )
    
    def _generate_download_url(self, file_path: str) -> str:
        """Generate a signed download URL for the export file"""
        # In a real implementation, this would generate a signed S3 URL
        # For now, we'll return a local file URL
        file_name = os.path.basename(file_path)
        return f"/api/v1/privacy/download/{file_name}"
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def _get_last_export_date(self, org_id: str) -> Optional[str]:
        """Get the date of the last export for the organization"""
        last_export = self.db.query(DataExport).filter(
            DataExport.organization_id == org_id,
            DataExport.status == "completed"
        ).order_by(DataExport.completed_at.desc()).first()
        
        return last_export.completed_at.isoformat() if last_export and last_export.completed_at else None
    
    def _get_last_deletion_request_date(self, org_id: str) -> Optional[str]:
        """Get the date of the last deletion request for the organization"""
        last_deletion = self.db.query(DeletionRequest).filter(
            DeletionRequest.organization_id == org_id
        ).order_by(DeletionRequest.created_at.desc()).first()
        
        return last_deletion.created_at.isoformat() if last_deletion else None
    
    def _log_privacy_event(self, org_id: str, user_id: str, event_type: str, event_data: Dict[str, Any]):
        """Log privacy-related events for audit trail"""
        privacy_event = PrivacyEvent(
            organization_id=org_id,
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=datetime.utcnow()
        )
        self.db.add(privacy_event)
        self.db.commit()
    
    def download_export_file(self, file_name: str, org_id: str) -> str:
        """
        Get the file path for download (with security checks)
        
        Args:
            file_name: Name of the file to download
            org_id: Organization ID (for security)
            
        Returns:
            File path if valid and accessible
        """
        try:
            # Verify the file belongs to the organization
            export_record = self.db.query(DataExport).filter(
                DataExport.file_path.like(f"%{file_name}"),
                DataExport.organization_id == org_id,
                DataExport.status == "completed"
            ).first()
            
            if not export_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or access denied"
                )
            
            # Check if file has expired
            if export_record.expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="File has expired"
                )
            
            # Verify file exists
            if not os.path.exists(export_record.file_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File no longer exists"
                )
            
            return export_record.file_path
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get download file: {str(e)}"
            )
