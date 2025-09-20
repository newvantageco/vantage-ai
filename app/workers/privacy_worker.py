from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4

import httpx
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.retention import PrivacyJob, OrgRetention
from app.models.entities import Organization, UserAccount, Channel
from app.models.content import ContentItem, Campaign, Schedule, BrandGuide
from app.models.conversations import Conversation, Message
from app.models.post_metrics import PostMetrics
from app.models.external_refs import ScheduleExternal

logger = logging.getLogger(__name__)

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1")


class PrivacyWorker:
    """Handles privacy-related background jobs like data export and deletion."""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    async def process_export_job(self, job_id: str, include_media: bool, format: str) -> None:
        """Process a data export job."""
        try:
            job = self.db.query(PrivacyJob).filter(PrivacyJob.id == job_id).first()
            if not job:
                logger.error(f"Export job {job_id} not found")
                return
            
            job.status = "processing"
            self.db.commit()
            
            logger.info(f"Starting export job {job_id} for org {job.org_id}")
            
            # Create temporary directory for export
            with tempfile.TemporaryDirectory() as temp_dir:
                export_data = await self._collect_org_data(job.org_id, include_media)
                
                # Generate files based on format
                files_created = []
                
                if format in ["json", "both"]:
                    json_file = os.path.join(temp_dir, f"export_{job.org_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                    with open(json_file, 'w') as f:
                        json.dump(export_data, f, indent=2, default=str)
                    files_created.append(json_file)
                
                if format in ["csv", "both"]:
                    csv_files = await self._generate_csv_files(export_data, temp_dir)
                    files_created.extend(csv_files)
                
                # Create zip file
                zip_file = os.path.join(temp_dir, f"export_{job.org_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
                with zipfile.ZipFile(zip_file, 'w') as zf:
                    for file_path in files_created:
                        zf.write(file_path, os.path.basename(file_path))
                
                # Upload to storage (in production, this would be S3/R2)
                file_url = await self._upload_export_file(zip_file, job.org_id)
                
                # Update job status
                job.status = "completed"
                job.file_url = file_url
                job.completed_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Export job {job_id} completed successfully")
                
        except Exception as e:
            logger.error(f"Export job {job_id} failed: {e}")
            job = self.db.query(PrivacyJob).filter(PrivacyJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                self.db.commit()
    
    async def process_delete_job(self, job_id: str, delete_media: bool, grace_period_days: int) -> None:
        """Process a data deletion job."""
        try:
            job = self.db.query(PrivacyJob).filter(PrivacyJob.id == job_id).first()
            if not job:
                logger.error(f"Delete job {job_id} not found")
                return
            
            job.status = "processing"
            self.db.commit()
            
            logger.info(f"Starting delete job {job_id} for org {job.org_id}")
            
            # Wait for grace period - schedule for later instead of blocking
            if grace_period_days > 0:
                logger.info(f"Scheduling delete job {job_id} for {grace_period_days} days from now")
                # Instead of blocking, schedule the job for later execution
                from app.workers.celery_app import celery_app
                celery_app.send_task(
                    'app.workers.privacy_worker.execute_delayed_deletion',
                    args=[job_id],
                    countdown=grace_period_days * 24 * 3600  # Schedule for later
                )
                return {"status": "scheduled", "job_id": job_id, "grace_period_days": grace_period_days}
            
            # Perform data deletion
            await self._delete_org_data(job.org_id, delete_media)
            
            # Update job status
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Delete job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Delete job {job_id} failed: {e}")
            job = self.db.query(PrivacyJob).filter(PrivacyJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                self.db.commit()
    
    async def _collect_org_data(self, org_id: str, include_media: bool) -> Dict[str, Any]:
        """Collect all organization data for export."""
        data = {
            "export_info": {
                "org_id": org_id,
                "exported_at": datetime.utcnow().isoformat(),
                "include_media": include_media
            },
            "organization": {},
            "users": [],
            "channels": [],
            "campaigns": [],
            "content_items": [],
            "schedules": [],
            "brand_guide": {},
            "conversations": [],
            "messages": [],
            "post_metrics": [],
            "external_refs": []
        }
        
        # Organization info
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if org:
            data["organization"] = {
                "id": org.id,
                "name": org.name,
                "created_at": org.created_at.isoformat()
            }
        
        # Users
        users = self.db.query(UserAccount).filter(UserAccount.org_id == org_id).all()
        for user in users:
            data["users"].append({
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat()
            })
        
        # Channels
        channels = self.db.query(Channel).filter(Channel.org_id == org_id).all()
        for channel in channels:
            data["channels"].append({
                "id": channel.id,
                "provider": channel.provider,
                "account_ref": channel.account_ref,
                "created_at": channel.created_at.isoformat()
                # Note: Not including tokens for security
            })
        
        # Campaigns
        campaigns = self.db.query(Campaign).filter(Campaign.org_id == org_id).all()
        for campaign in campaigns:
            data["campaigns"].append({
                "id": campaign.id,
                "name": campaign.name,
                "objective": campaign.objective,
                "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
                "created_at": campaign.created_at.isoformat()
            })
        
        # Content items
        content_items = self.db.query(ContentItem).filter(ContentItem.org_id == org_id).all()
        for item in content_items:
            data["content_items"].append({
                "id": item.id,
                "campaign_id": item.campaign_id,
                "title": item.title,
                "caption": item.caption,
                "alt_text": item.alt_text,
                "first_comment": item.first_comment,
                "hashtags": item.hashtags,
                "status": item.status,
                "created_at": item.created_at.isoformat()
            })
        
        # Schedules
        schedules = self.db.query(Schedule).filter(Schedule.org_id == org_id).all()
        for schedule in schedules:
            data["schedules"].append({
                "id": schedule.id,
                "content_item_id": schedule.content_item_id,
                "channel_id": schedule.channel_id,
                "scheduled_at": schedule.scheduled_at.isoformat(),
                "status": schedule.status,
                "error_message": schedule.error_message,
                "created_at": schedule.created_at.isoformat()
            })
        
        # Brand guide
        brand_guide = self.db.query(BrandGuide).filter(BrandGuide.org_id == org_id).first()
        if brand_guide:
            data["brand_guide"] = {
                "id": brand_guide.id,
                "voice": brand_guide.voice,
                "audience": brand_guide.audience,
                "pillars": brand_guide.pillars,
                "created_at": brand_guide.created_at.isoformat()
            }
        
        # Conversations and messages
        conversations = self.db.query(Conversation).filter(Conversation.org_id == org_id).all()
        for conv in conversations:
            data["conversations"].append({
                "id": conv.id,
                "channel": conv.channel,
                "peer_id": conv.peer_id,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "created_at": conv.created_at.isoformat()
            })
            
            # Messages for this conversation
            messages = self.db.query(Message).filter(Message.conversation_id == conv.id).all()
            for msg in messages:
                data["messages"].append({
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "direction": msg.direction,
                    "text": msg.text,
                    "media_url": msg.media_url if include_media else None,
                    "created_at": msg.created_at.isoformat()
                })
        
        # Post metrics
        schedule_ids = [s["id"] for s in data["schedules"]]
        if schedule_ids:
            metrics = self.db.query(PostMetrics).filter(PostMetrics.schedule_id.in_(schedule_ids)).all()
            for metric in metrics:
                data["post_metrics"].append({
                    "id": metric.id,
                    "schedule_id": metric.schedule_id,
                    "impressions": metric.impressions,
                    "reach": metric.reach,
                    "likes": metric.likes,
                    "comments": metric.comments,
                    "shares": metric.shares,
                    "clicks": metric.clicks,
                    "video_views": metric.video_views,
                    "saves": metric.saves,
                    "cost_cents": metric.cost_cents,
                    "fetched_at": metric.fetched_at.isoformat(),
                    "created_at": metric.created_at.isoformat()
                })
        
        # External references
        if schedule_ids:
            external_refs = self.db.query(ScheduleExternal).filter(ScheduleExternal.schedule_id.in_(schedule_ids)).all()
            for ref in external_refs:
                data["external_refs"].append({
                    "id": ref.id,
                    "schedule_id": ref.schedule_id,
                    "ref_id": ref.ref_id,
                    "ref_url": ref.ref_url,
                    "provider": ref.provider,
                    "created_at": ref.created_at.isoformat()
                })
        
        return data
    
    async def _generate_csv_files(self, data: Dict[str, Any], temp_dir: str) -> List[str]:
        """Generate CSV files from export data."""
        import csv
        
        csv_files = []
        
        # Users CSV
        if data["users"]:
            users_file = os.path.join(temp_dir, "users.csv")
            with open(users_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["id", "email", "role", "created_at"])
                writer.writeheader()
                writer.writerows(data["users"])
            csv_files.append(users_file)
        
        # Content items CSV
        if data["content_items"]:
            content_file = os.path.join(temp_dir, "content_items.csv")
            with open(content_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["id", "campaign_id", "title", "caption", "status", "created_at"])
                writer.writeheader()
                writer.writerows(data["content_items"])
            csv_files.append(content_file)
        
        # Schedules CSV
        if data["schedules"]:
            schedules_file = os.path.join(temp_dir, "schedules.csv")
            with open(schedules_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["id", "content_item_id", "channel_id", "scheduled_at", "status", "created_at"])
                writer.writeheader()
                writer.writerows(data["schedules"])
            csv_files.append(schedules_file)
        
        return csv_files
    
    async def _upload_export_file(self, file_path: str, org_id: str) -> str:
        """Upload export file to storage and return signed URL."""
        # In production, this would upload to S3/R2 and return a signed URL
        # For now, we'll simulate this with a placeholder URL
        file_name = os.path.basename(file_path)
        signed_url = f"https://storage.example.com/exports/{org_id}/{file_name}?expires=86400"  # 24h expiry
        
        logger.info(f"Export file uploaded: {signed_url}")
        return signed_url
    
    async def _delete_org_data(self, org_id: str, delete_media: bool) -> None:
        """Delete organization data according to privacy requirements."""
        logger.info(f"Starting data deletion for org {org_id}")
        
        # 1. Mask/anonymize PII in user accounts
        users = self.db.query(UserAccount).filter(UserAccount.org_id == org_id).all()
        for user in users:
            user.email = f"deleted_{user.id[:8]}@example.com"
            user.id = f"deleted_{user.id[:8]}"
        
        # 2. Revoke OAuth tokens in channels
        channels = self.db.query(Channel).filter(Channel.org_id == org_id).all()
        for channel in channels:
            channel.access_token = None
            channel.refresh_token = None
            channel.account_ref = f"deleted_{channel.id[:8]}"
        
        # 3. Anonymize conversation data
        conversations = self.db.query(Conversation).filter(Conversation.org_id == org_id).all()
        for conv in conversations:
            conv.peer_id = f"deleted_{conv.id[:8]}"
        
        # 4. Clear message content
        messages = self.db.query(Message).filter(
            Message.conversation_id.in_([c.id for c in conversations])
        ).all()
        for msg in messages:
            msg.text = "[Content deleted for privacy]"
            if not delete_media:
                msg.media_url = None
        
        # 5. Anonymize content items
        content_items = self.db.query(ContentItem).filter(ContentItem.org_id == org_id).all()
        for item in content_items:
            item.title = f"[Deleted Content {item.id[:8]}]"
            item.caption = "[Content deleted for privacy]"
            item.alt_text = "[Content deleted for privacy]"
            item.first_comment = "[Content deleted for privacy]"
            item.hashtags = None
        
        # 6. Clear brand guide
        brand_guides = self.db.query(BrandGuide).filter(BrandGuide.org_id == org_id).all()
        for guide in brand_guides:
            guide.voice = "[Deleted for privacy]"
            guide.audience = "[Deleted for privacy]"
            guide.pillars = "[Deleted for privacy]"
        
        # 7. Anonymize organization name
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if org:
            org.name = f"Deleted Organization {org.id[:8]}"
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"Data deletion completed for org {org_id}")
    
    async def cleanup_expired_data(self) -> None:
        """Clean up data based on retention policies."""
        logger.info("Starting retention policy cleanup")
        
        retention_policies = self.db.query(OrgRetention).all()
        
        for policy in retention_policies:
            cutoff_date = datetime.utcnow() - timedelta(days=policy.messages_days)
            
            # Clean up old messages
            old_messages = self.db.query(Message).filter(
                Message.conversation_id.in_(
                    self.db.query(Conversation.id).filter(Conversation.org_id == policy.org_id)
                ),
                Message.created_at < cutoff_date
            ).all()
            
            for msg in old_messages:
                msg.text = "[Content expired per retention policy]"
                msg.media_url = None
            
            # Clean up old audit logs (if you have an audit log table)
            # This would be implemented based on your audit logging system
            
            logger.info(f"Cleaned up {len(old_messages)} old messages for org {policy.org_id}")
        
        self.db.commit()
        logger.info("Retention policy cleanup completed")


# Background task functions for FastAPI
async def process_export_job(job_id: str, include_media: bool, format: str) -> None:
    """Background task wrapper for export job."""
    worker = PrivacyWorker()
    await worker.process_export_job(job_id, include_media, format)


async def process_delete_job(job_id: str, delete_media: bool, grace_period_days: int) -> None:
    """Background task wrapper for delete job."""
    worker = PrivacyWorker()
    await worker.process_delete_job(job_id, delete_media, grace_period_days)


async def cleanup_expired_data() -> None:
    """Background task wrapper for retention cleanup."""
    worker = PrivacyWorker()
    await worker.cleanup_expired_data()
