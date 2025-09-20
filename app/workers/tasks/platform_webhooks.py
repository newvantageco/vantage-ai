"""
Platform Webhook Processing Tasks
Celery tasks for processing incoming webhooks from external platforms
"""

from celery import Celery
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging

from app.db.session import SessionLocal
from app.models.publishing import PlatformIntegration, ExternalReference, PublishingStatus
from app.models.entities import Organization
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

# Initialize Celery app
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def process_platform_webhook(self, webhook_id: str, platform: str, payload: Dict[str, Any], signature: str):
    """
    Process incoming webhook from external platform
    
    Args:
        webhook_id: Unique identifier for this webhook
        platform: Platform name (meta, linkedin, google, tiktok, whatsapp, stripe)
        payload: Webhook payload data
        signature: Webhook signature for verification
    """
    try:
        db = SessionLocal()
        
        # Process based on platform
        if platform == "meta":
            result = _process_meta_webhook(db, payload)
        elif platform == "linkedin":
            result = _process_linkedin_webhook(db, payload)
        elif platform == "google":
            result = _process_google_webhook(db, payload)
        elif platform == "tiktok":
            result = _process_tiktok_webhook(db, payload)
        elif platform == "whatsapp":
            result = _process_whatsapp_webhook(db, payload)
        elif platform == "stripe":
            result = _process_stripe_webhook(db, payload)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        logger.info(f"Successfully processed {platform} webhook {webhook_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to process {platform} webhook {webhook_id}: {str(exc)}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Max retries exceeded for {platform} webhook {webhook_id}")
            raise exc
    finally:
        db.close()


def _process_meta_webhook(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process Meta (Facebook/Instagram) webhook"""
    try:
        # Extract relevant data from Meta webhook
        entry = payload.get('entry', [])
        if not entry:
            return {"status": "no_data", "message": "No entry data in webhook"}
        
        for item in entry:
            # Process changes (likes, comments, etc.)
            changes = item.get('changes', [])
            for change in changes:
                field = change.get('field')
                value = change.get('value', {})
                
                if field == 'feed':
                    # Post engagement data
                    post_id = value.get('post_id')
                    if post_id:
                        _update_post_metrics(db, 'meta', post_id, value)
                
                elif field == 'comments':
                    # Comment data
                    _process_comment_data(db, 'meta', value)
                
                elif field == 'likes':
                    # Like data
                    _process_like_data(db, 'meta', value)
        
        return {"status": "success", "processed": len(entry)}
        
    except Exception as e:
        logger.error(f"Error processing Meta webhook: {str(e)}")
        raise


def _process_linkedin_webhook(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process LinkedIn webhook"""
    try:
        # Extract LinkedIn webhook data
        event_type = payload.get('eventType')
        resource = payload.get('resource')
        
        if event_type == 'POST_CREATED':
            # New post created
            post_id = resource.get('id')
            if post_id:
                _update_post_metrics(db, 'linkedin', post_id, resource)
        
        elif event_type == 'POST_UPDATED':
            # Post updated
            post_id = resource.get('id')
            if post_id:
                _update_post_metrics(db, 'linkedin', post_id, resource)
        
        return {"status": "success", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Error processing LinkedIn webhook: {str(e)}")
        raise


def _process_google_webhook(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process Google (My Business, Ads) webhook"""
    try:
        # Extract Google webhook data
        event_type = payload.get('eventType')
        resource = payload.get('resource')
        
        if event_type == 'POST_CREATED':
            # New Google My Business post
            post_id = resource.get('id')
            if post_id:
                _update_post_metrics(db, 'google_gbp', post_id, resource)
        
        elif event_type == 'CAMPAIGN_UPDATED':
            # Google Ads campaign update
            campaign_id = resource.get('id')
            if campaign_id:
                _update_campaign_metrics(db, 'google_ads', campaign_id, resource)
        
        return {"status": "success", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Error processing Google webhook: {str(e)}")
        raise


def _process_tiktok_webhook(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process TikTok webhook"""
    try:
        # Extract TikTok webhook data
        event_type = payload.get('eventType')
        resource = payload.get('resource')
        
        if event_type == 'CAMPAIGN_CREATED':
            # New TikTok ad campaign
            campaign_id = resource.get('id')
            if campaign_id:
                _update_campaign_metrics(db, 'tiktok_ads', campaign_id, resource)
        
        elif event_type == 'CAMPAIGN_UPDATED':
            # TikTok campaign update
            campaign_id = resource.get('id')
            if campaign_id:
                _update_campaign_metrics(db, 'tiktok_ads', campaign_id, resource)
        
        return {"status": "success", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Error processing TikTok webhook: {str(e)}")
        raise


def _process_whatsapp_webhook(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process WhatsApp Business webhook"""
    try:
        # Extract WhatsApp webhook data
        entry = payload.get('entry', [])
        
        for item in entry:
            changes = item.get('changes', [])
            for change in changes:
                field = change.get('field')
                value = change.get('value', {})
                
                if field == 'messages':
                    # Message data
                    _process_whatsapp_messages(db, value)
        
        return {"status": "success", "processed": len(entry)}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        raise


def _process_stripe_webhook(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process Stripe webhook"""
    try:
        # Extract Stripe webhook data
        event_type = payload.get('type')
        data = payload.get('data', {})
        
        if event_type == 'invoice.payment_succeeded':
            # Payment succeeded
            invoice = data.get('object', {})
            customer_id = invoice.get('customer')
            amount = invoice.get('amount_paid', 0)
            
            # Update billing information
            _update_billing_info(db, customer_id, amount, 'payment_succeeded')
        
        elif event_type == 'invoice.payment_failed':
            # Payment failed
            invoice = data.get('object', {})
            customer_id = invoice.get('customer')
            
            # Update billing information
            _update_billing_info(db, customer_id, 0, 'payment_failed')
        
        return {"status": "success", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        raise


def _update_post_metrics(db: Session, platform: str, post_id: str, data: Dict[str, Any]):
    """Update post metrics from webhook data"""
    try:
        # Find external reference
        external_ref = db.query(ExternalReference).filter(
            ExternalReference.platform == platform,
            ExternalReference.external_id == post_id
        ).first()
        
        if external_ref:
            # Update metrics in platform_data
            platform_data = external_ref.platform_data or {}
            platform_data.update({
                'last_webhook_update': datetime.utcnow().isoformat(),
                'webhook_data': data
            })
            external_ref.platform_data = platform_data
            db.commit()
            
            # Update analytics service with new metrics
            from app.services.analytics_service import AnalyticsService
            analytics_service = AnalyticsService(db)
            
            # Extract metrics from webhook data
            metrics_data = {
                'organization_id': external_ref.organization_id,
                'impressions': data.get('impressions', 0),
                'reach': data.get('reach', 0),
                'clicks': data.get('clicks', 0),
                'engagements': data.get('engagements', 0),
                'likes': data.get('likes', 0),
                'comments': data.get('comments', 0),
                'shares': data.get('shares', 0),
                'saves': data.get('saves', 0),
                'conversions': data.get('conversions', 0),
                'video_views': data.get('video_views', 0),
                'data_source': 'webhook',
                'is_estimated': data.get('is_estimated', False)
            }
            
            # Update post metrics
            analytics_service.update_post_metrics(
                external_reference_id=external_ref.id,
                platform=platform,
                external_id=post_id,
                metrics_data=metrics_data
            )
            
            logger.info(f"Updated analytics metrics for {platform} post {post_id}")
            
    except Exception as e:
        logger.error(f"Error updating post metrics: {str(e)}")


def _update_campaign_metrics(db: Session, platform: str, campaign_id: str, data: Dict[str, Any]):
    """Update campaign metrics from webhook data"""
    try:
        # Find external reference
        external_ref = db.query(ExternalReference).filter(
            ExternalReference.platform == platform,
            ExternalReference.external_id == campaign_id
        ).first()
        
        if external_ref:
            # Update metrics in platform_data
            platform_data = external_ref.platform_data or {}
            platform_data.update({
                'last_webhook_update': datetime.utcnow().isoformat(),
                'webhook_data': data
            })
            external_ref.platform_data = platform_data
            db.commit()
            
    except Exception as e:
        logger.error(f"Error updating campaign metrics: {str(e)}")


def _process_comment_data(db: Session, platform: str, data: Dict[str, Any]):
    """Process comment data from webhook"""
    try:
        comment_id = data.get('id')
        post_id = data.get('post_id')
        comment_text = data.get('message', '')
        author_name = data.get('from', {}).get('name', 'Unknown')
        created_time = data.get('created_time')
        
        if not comment_id or not post_id:
            logger.warning(f"Incomplete comment data from {platform}")
            return
        
        # Find the external reference for this post
        external_ref = db.query(ExternalReference).filter(
            ExternalReference.platform == platform,
            ExternalReference.external_id == post_id
        ).first()
        
        if external_ref:
            # Update comment count in platform_data
            platform_data = external_ref.platform_data or {}
            comments = platform_data.get('comments', [])
            
            # Add new comment
            comment_data = {
                'id': comment_id,
                'text': comment_text,
                'author': author_name,
                'created_time': created_time,
                'platform': platform
            }
            
            # Check if comment already exists
            existing_comment = next((c for c in comments if c.get('id') == comment_id), None)
            if not existing_comment:
                comments.append(comment_data)
                platform_data['comments'] = comments
                platform_data['comment_count'] = len(comments)
                platform_data['last_comment_at'] = created_time
                
                external_ref.platform_data = platform_data
                db.commit()
                
                logger.info(f"Added new comment {comment_id} to post {post_id} on {platform}")
        
    except Exception as e:
        logger.error(f"Error processing comment data: {str(e)}")


def _process_like_data(db: Session, platform: str, data: Dict[str, Any]):
    """Process like data from webhook"""
    try:
        post_id = data.get('post_id')
        like_count = data.get('like_count', 0)
        reaction_data = data.get('reactions', {})
        
        if not post_id:
            logger.warning(f"Incomplete like data from {platform}")
            return
        
        # Find the external reference for this post
        external_ref = db.query(ExternalReference).filter(
            ExternalReference.platform == platform,
            ExternalReference.external_id == post_id
        ).first()
        
        if external_ref:
            # Update like count in platform_data
            platform_data = external_ref.platform_data or {}
            platform_data.update({
                'like_count': like_count,
                'reactions': reaction_data,
                'last_engagement_update': datetime.utcnow().isoformat()
            })
            
            external_ref.platform_data = platform_data
            db.commit()
            
            logger.info(f"Updated like count for post {post_id} on {platform}: {like_count}")
        
    except Exception as e:
        logger.error(f"Error processing like data: {str(e)}")


def _process_whatsapp_messages(db: Session, data: Dict[str, Any]):
    """Process WhatsApp message data"""
    try:
        messages = data.get('messages', [])
        
        for message in messages:
            message_id = message.get('id')
            from_number = message.get('from')
            message_text = message.get('text', {}).get('body', '')
            timestamp = message.get('timestamp')
            message_type = message.get('type', 'text')
            
            if not message_id or not from_number:
                continue
            
            # Store message data (you might want to create a separate table for this)
            logger.info(f"Received WhatsApp message {message_id} from {from_number}: {message_text[:50]}...")
            
            # Here you could implement:
            # - Message threading
            # - Auto-response logic
            # - Message analytics
            # - Integration with your CRM
            
    except Exception as e:
        logger.error(f"Error processing WhatsApp messages: {str(e)}")


def _update_billing_info(db: Session, customer_id: str, amount: int, status: str):
    """Update billing information from Stripe webhook"""
    try:
        # Find organization by Stripe customer ID
        organization = db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if not organization:
            logger.warning(f"Organization not found for Stripe customer {customer_id}")
            return
        
        # Update billing status
        if status == 'payment_succeeded':
            organization.billing_status = 'active'
            organization.last_payment_amount = amount
            organization.last_payment_date = datetime.utcnow()
            logger.info(f"Payment succeeded for organization {organization.id}: ${amount/100}")
            
        elif status == 'payment_failed':
            organization.billing_status = 'past_due'
            logger.warning(f"Payment failed for organization {organization.id}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error updating billing info: {str(e)}")
