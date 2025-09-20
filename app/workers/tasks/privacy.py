"""
Privacy Celery Tasks
Handles data export and deletion operations asynchronously
"""

from celery import Celery
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json
import csv
import zipfile
import io
import os
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.models.entities import Organization, UserAccount, Channel
from app.models.publishing import ExternalReference, PublishingJob
from app.models.analytics import AnalyticsEvent
from app.models.billing import Subscription, Invoice, BillingEvent
from app.models.privacy import DataExport, DeletionRequest, ExportStatus, DeletionStatus
from app.core.config import get_settings

settings = get_settings()

# Initialize Celery app
celery_app = Celery(
    "privacy_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def export_organization_data(self, export_id: str, org_id: str, format_type: str = "json"):
    """
    Export organization data to specified format
    
    Args:
        export_id: Export ID
        org_id: Organization ID
        format_type: Export format (json, csv, zip)
    """
    db = SessionLocal()
    try:
        # Get export record
        export_record = db.query(DataExport).filter(DataExport.id == export_id).first()
        if not export_record:
            raise Exception(f"Export record {export_id} not found")
        
        # Update status to processing
        export_record.status = ExportStatus.PROCESSING
        db.commit()
        
        # Get organization data
        organization_data = _collect_organization_data(db, org_id)
        
        # Generate export file
        file_path = _generate_export_file(export_id, organization_data, format_type)
        
        # Update export record
        export_record.status = ExportStatus.COMPLETED
        export_record.file_path = file_path
        export_record.file_size = os.path.getsize(file_path)
        export_record.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"Export {export_id} completed successfully")
        
    except Exception as e:
        print(f"Export {export_id} failed: {str(e)}")
        
        # Update export record with error
        if 'export_record' in locals():
            export_record.status = ExportStatus.FAILED
            export_record.error_message = str(e)
            db.commit()
        
        # Retry if not max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        else:
            raise e
    
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def process_deletion_request(self, deletion_id: str, org_id: str):
    """
    Process organization data deletion request
    
    Args:
        deletion_id: Deletion request ID
        org_id: Organization ID
    """
    db = SessionLocal()
    try:
        # Get deletion request
        deletion_request = db.query(DeletionRequest).filter(DeletionRequest.id == deletion_id).first()
        if not deletion_request:
            raise Exception(f"Deletion request {deletion_id} not found")
        
        # Update status to processing
        deletion_request.status = DeletionStatus.PROCESSING
        db.commit()
        
        # Wait for grace period if not yet reached
        if deletion_request.scheduled_for > datetime.utcnow():
            remaining_seconds = (deletion_request.scheduled_for - datetime.utcnow()).total_seconds()
            print(f"Waiting {remaining_seconds} seconds for grace period to complete")
            return
        
        # Perform data deletion
        _delete_organization_data(db, org_id)
        
        # Update deletion request
        deletion_request.status = DeletionStatus.COMPLETED
        deletion_request.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"Deletion {deletion_id} completed successfully")
        
    except Exception as e:
        print(f"Deletion {deletion_id} failed: {str(e)}")
        
        # Update deletion request with error
        if 'deletion_request' in locals():
            deletion_request.status = DeletionStatus.FAILED
            deletion_request.error_message = str(e)
            db.commit()
        
        # Retry if not max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        else:
            raise e
    
    finally:
        db.close()


def _collect_organization_data(db: Session, org_id: str) -> Dict[str, Any]:
    """Collect all organization data for export"""
    
    # Get organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise Exception(f"Organization {org_id} not found")
    
    # Collect users
    users = db.query(UserAccount).filter(UserAccount.org_id == org_id).all()
    users_data = [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]
    
    # Collect channels
    channels = db.query(Channel).filter(Channel.org_id == org_id).all()
    channels_data = [
        {
            "id": channel.id,
            "provider": channel.provider,
            "account_ref": channel.account_ref,
            "created_at": channel.created_at.isoformat(),
            "metadata": channel.metadata_json
        }
        for channel in channels
    ]
    
    # Collect external references (posts)
    posts = db.query(ExternalReference).filter(ExternalReference.organization_id == org_id).all()
    posts_data = [
        {
            "id": post.id,
            "platform": post.platform.value,
            "external_id": post.external_id,
            "url": post.url,
            "status": post.status.value,
            "created_at": post.created_at.isoformat(),
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "platform_data": post.platform_data
        }
        for post in posts
    ]
    
    # Collect analytics events
    analytics_events = db.query(AnalyticsEvent).filter(AnalyticsEvent.organization_id == org_id).all()
    analytics_data = [
        {
            "id": event.id,
            "platform": event.platform.value,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "event_data": event.event_data
        }
        for event in analytics_events
    ]
    
    # Collect billing data
    subscriptions = db.query(Subscription).filter(Subscription.organization_id == org_id).all()
    subscriptions_data = [
        {
            "id": sub.id,
            "stripe_subscription_id": sub.stripe_subscription_id,
            "status": sub.status.value,
            "amount": sub.amount,
            "currency": sub.currency,
            "created_at": sub.created_at.isoformat(),
            "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None
        }
        for sub in subscriptions
    ]
    
    invoices = db.query(Invoice).filter(Invoice.organization_id == org_id).all()
    invoices_data = [
        {
            "id": invoice.id,
            "stripe_invoice_id": invoice.stripe_invoice_id,
            "amount_due": invoice.amount_due,
            "amount_paid": invoice.amount_paid,
            "currency": invoice.currency,
            "status": invoice.status,
            "created_at": invoice.created_at.isoformat(),
            "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None
        }
        for invoice in invoices
    ]
    
    # Compile organization data
    organization_data = {
        "export_info": {
            "export_id": f"export_{org_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "organization_id": org_id,
            "exported_at": datetime.utcnow().isoformat(),
            "data_retention_policy": "7 years for financial records, 3 years for analytics data"
        },
        "organization": {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "created_at": org.created_at.isoformat(),
            "is_active": org.is_active
        },
        "users": users_data,
        "channels": channels_data,
        "posts": posts_data,
        "analytics_events": analytics_data,
        "subscriptions": subscriptions_data,
        "invoices": invoices_data
    }
    
    return organization_data


def _generate_export_file(export_id: str, data: Dict[str, Any], format_type: str) -> str:
    """Generate export file in specified format"""
    
    export_dir = settings.data_export_path or "/tmp/exports"
    os.makedirs(export_dir, exist_ok=True)
    
    if format_type == "json":
        file_path = os.path.join(export_dir, f"{export_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    elif format_type == "csv":
        file_path = os.path.join(export_dir, f"{export_id}.zip")
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Create CSV files for each data type
            for data_type, records in data.items():
                if isinstance(records, list) and records:
                    csv_buffer = io.StringIO()
                    writer = csv.DictWriter(csv_buffer, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)
                    zipf.writestr(f"{data_type}.csv", csv_buffer.getvalue())
            
            # Add organization info as JSON
            org_info = {k: v for k, v in data.items() if k == "organization" or k == "export_info"}
            zipf.writestr("organization_info.json", json.dumps(org_info, indent=2))
    
    elif format_type == "zip":
        file_path = os.path.join(export_dir, f"{export_id}.zip")
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add JSON file
            zipf.writestr("data_export.json", json.dumps(data, indent=2, ensure_ascii=False))
            
            # Add individual CSV files
            for data_type, records in data.items():
                if isinstance(records, list) and records:
                    csv_buffer = io.StringIO()
                    writer = csv.DictWriter(csv_buffer, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)
                    zipf.writestr(f"{data_type}.csv", csv_buffer.getvalue())
    
    else:
        raise ValueError(f"Unsupported format type: {format_type}")
    
    return file_path


def _delete_organization_data(db: Session, org_id: str):
    """Delete all organization data (PII scrubbing)"""
    
    print(f"Starting data deletion for organization {org_id}")
    
    # Delete analytics events
    analytics_count = db.query(AnalyticsEvent).filter(AnalyticsEvent.organization_id == org_id).count()
    db.query(AnalyticsEvent).filter(AnalyticsEvent.organization_id == org_id).delete()
    print(f"Deleted {analytics_count} analytics events")
    
    # Delete external references (posts)
    posts_count = db.query(ExternalReference).filter(ExternalReference.organization_id == org_id).count()
    db.query(ExternalReference).filter(ExternalReference.organization_id == org_id).delete()
    print(f"Deleted {posts_count} external references")
    
    # Delete publishing jobs
    jobs_count = db.query(PublishingJob).filter(PublishingJob.organization_id == org_id).count()
    db.query(PublishingJob).filter(PublishingJob.organization_id == org_id).delete()
    print(f"Deleted {jobs_count} publishing jobs")
    
    # Delete billing events
    billing_events_count = db.query(BillingEvent).filter(BillingEvent.organization_id == org_id).count()
    db.query(BillingEvent).filter(BillingEvent.organization_id == org_id).delete()
    print(f"Deleted {billing_events_count} billing events")
    
    # Delete invoices
    invoices_count = db.query(Invoice).filter(Invoice.organization_id == org_id).count()
    db.query(Invoice).filter(Invoice.organization_id == org_id).delete()
    print(f"Deleted {invoices_count} invoices")
    
    # Delete subscriptions
    subscriptions_count = db.query(Subscription).filter(Subscription.organization_id == org_id).count()
    db.query(Subscription).filter(Subscription.organization_id == org_id).delete()
    print(f"Deleted {subscriptions_count} subscriptions")
    
    # Delete channels
    channels_count = db.query(Channel).filter(Channel.org_id == org_id).count()
    db.query(Channel).filter(Channel.org_id == org_id).delete()
    print(f"Deleted {channels_count} channels")
    
    # Delete users
    users_count = db.query(UserAccount).filter(UserAccount.org_id == org_id).count()
    db.query(UserAccount).filter(UserAccount.org_id == org_id).delete()
    print(f"Deleted {users_count} users")
    
    # Deactivate organization (soft delete)
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org:
        org.is_active = False
        print(f"Deactivated organization {org_id}")
    
    # Commit all changes
    db.commit()
    
    print(f"Data deletion completed for organization {org_id}")


@celery_app.task
def cleanup_expired_exports():
    """Clean up expired export files"""
    db = SessionLocal()
    try:
        # Find expired exports
        expired_exports = db.query(DataExport).filter(
            DataExport.expires_at < datetime.utcnow(),
            DataExport.status == ExportStatus.COMPLETED
        ).all()
        
        for export_record in expired_exports:
            # Delete file if it exists
            if export_record.file_path and os.path.exists(export_record.file_path):
                os.remove(export_record.file_path)
                print(f"Deleted expired export file: {export_record.file_path}")
            
            # Update status
            export_record.status = ExportStatus.EXPIRED
            print(f"Marked export {export_record.id} as expired")
        
        db.commit()
        print(f"Cleaned up {len(expired_exports)} expired exports")
        
    except Exception as e:
        print(f"Error cleaning up expired exports: {str(e)}")
    finally:
        db.close()


@celery_app.task
def process_scheduled_deletions():
    """Process scheduled deletion requests"""
    db = SessionLocal()
    try:
        # Find deletion requests that are ready to process
        ready_deletions = db.query(DeletionRequest).filter(
            DeletionRequest.status == DeletionStatus.PENDING,
            DeletionRequest.scheduled_for <= datetime.utcnow()
        ).all()
        
        for deletion_request in ready_deletions:
            # Queue the deletion job
            process_deletion_request.delay(deletion_request.id, deletion_request.organization_id)
            print(f"Queued deletion request {deletion_request.id}")
        
        print(f"Queued {len(ready_deletions)} deletion requests")
        
    except Exception as e:
        print(f"Error processing scheduled deletions: {str(e)}")
    finally:
        db.close()
