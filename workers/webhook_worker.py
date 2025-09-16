"""
Webhook worker for sending webhook notifications.
"""

import logging
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hmac
import hashlib

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.webhooks import Webhook, WebhookDelivery

logger = logging.getLogger(__name__)


async def send_webhook(delivery_id: str):
    """Send a webhook delivery."""
    db = next(get_db())
    
    try:
        # Get the delivery record
        delivery = db.query(WebhookDelivery).filter(WebhookDelivery.id == delivery_id).first()
        if not delivery:
            logger.error(f"Webhook delivery {delivery_id} not found")
            return
        
        # Get the webhook
        webhook = db.query(Webhook).filter(Webhook.id == delivery.webhook_id).first()
        if not webhook or not webhook.is_active:
            logger.error(f"Webhook {delivery.webhook_id} not found or inactive")
            delivery.status = "failed"
            delivery.error_message = "Webhook not found or inactive"
            delivery.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # Update delivery status
        delivery.status = "retrying" if delivery.attempt_count > 1 else "pending"
        delivery.attempt_count += 1
        db.commit()
        
        logger.info(f"Sending webhook {webhook.id} (attempt {delivery.attempt_count})")
        
        # Prepare headers
        headers = webhook.get_headers().copy()
        headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Vantage-AI-Webhook/1.0",
            "X-Vantage-Event": delivery.event_type,
            "X-Vantage-Delivery": delivery.id
        })
        
        # Generate signature
        payload = delivery.payload
        signature = webhook.generate_signature(payload)
        headers["X-Vantage-Signature"] = f"sha256={signature}"
        
        # Send webhook
        success = await _send_http_request(
            webhook.target_url,
            payload,
            headers,
            webhook.timeout_seconds
        )
        
        if success["success"]:
            # Mark as delivered
            delivery.status = "delivered"
            delivery.response_status = success["status_code"]
            delivery.response_body = success.get("response_body")
            delivery.response_headers = json.dumps(success.get("response_headers", {}))
            delivery.completed_at = datetime.utcnow()
            delivery.next_retry_at = None
            
            # Update webhook last triggered
            webhook.last_triggered_at = datetime.utcnow()
            
            logger.info(f"Webhook {webhook.id} delivered successfully")
            
        else:
            # Handle failure
            delivery.status = "failed"
            delivery.error_message = success["error"]
            delivery.completed_at = datetime.utcnow()
            
            # Schedule retry if within retry limit
            if delivery.attempt_count < webhook.retry_count:
                delivery.status = "retrying"
                delivery.next_retry_at = datetime.utcnow() + timedelta(
                    minutes=2 ** delivery.attempt_count  # Exponential backoff
                )
                delivery.completed_at = None
                
                logger.info(f"Webhook {webhook.id} failed, retry scheduled for {delivery.next_retry_at}")
            else:
                logger.error(f"Webhook {webhook.id} failed after {delivery.attempt_count} attempts")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error sending webhook delivery {delivery_id}: {e}")
        
        # Mark delivery as failed
        delivery.status = "failed"
        delivery.error_message = str(e)
        delivery.completed_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()


async def _send_http_request(
    url: str,
    payload: str,
    headers: Dict[str, str],
    timeout: int
) -> Dict[str, Any]:
    """Send HTTP request to webhook URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response_body = await response.text()
                response_headers = dict(response.headers)
                
                return {
                    "success": True,
                    "status_code": response.status,
                    "response_body": response_body,
                    "response_headers": response_headers
                }
                
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": f"Request timeout after {timeout} seconds"
        }
    except aiohttp.ClientError as e:
        return {
            "success": False,
            "error": f"HTTP client error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


async def retry_failed_webhooks():
    """Retry webhooks that are scheduled for retry."""
    db = next(get_db())
    
    try:
        # Find deliveries that need retry
        now = datetime.utcnow()
        deliveries = db.query(WebhookDelivery).filter(
            WebhookDelivery.status == "retrying",
            WebhookDelivery.next_retry_at <= now
        ).all()
        
        logger.info(f"Found {len(deliveries)} webhook deliveries to retry")
        
        for delivery in deliveries:
            await send_webhook(delivery.id)
            
    except Exception as e:
        logger.error(f"Error retrying webhooks: {e}")
    finally:
        db.close()


async def cleanup_old_deliveries(days: int = 30):
    """Clean up old webhook delivery records."""
    db = next(get_db())
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old completed deliveries
        deleted_count = db.query(WebhookDelivery).filter(
            WebhookDelivery.status.in_(["delivered", "failed"]),
            WebhookDelivery.completed_at < cutoff_date
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old webhook deliveries")
        
    except Exception as e:
        logger.error(f"Error cleaning up old deliveries: {e}")
        db.rollback()
    finally:
        db.close()


def trigger_webhook(org_id: str, event_type: str, data: Dict[str, Any]):
    """Trigger webhooks for an event (called from other parts of the app)."""
    db = next(get_db())
    
    try:
        # Find active webhooks for this org that listen to this event
        webhooks = db.query(Webhook).filter(
            Webhook.org_id == org_id,
            Webhook.is_active == True
        ).all()
        
        triggered_count = 0
        
        for webhook in webhooks:
            events = webhook.get_events()
            if event_type in events:
                # Create delivery record
                payload = {
                    "event": event_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": data
                }
                
                delivery = WebhookDelivery(
                    id=f"del_{hash(f'{webhook.id}_{event_type}_{datetime.utcnow().timestamp()}')}",
                    webhook_id=webhook.id,
                    org_id=org_id,
                    event_type=event_type,
                    payload=json.dumps(payload),
                    status="pending"
                )
                
                db.add(delivery)
                triggered_count += 1
                
                # Send webhook asynchronously
                asyncio.create_task(send_webhook(delivery.id))
        
        db.commit()
        logger.info(f"Triggered {triggered_count} webhooks for event {event_type} in org {org_id}")
        
    except Exception as e:
        logger.error(f"Error triggering webhooks: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # This can be run as a standalone worker
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python webhook_worker.py <delivery_id|retry|cleanup> [days]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "retry":
        asyncio.run(retry_failed_webhooks())
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        asyncio.run(cleanup_old_deliveries(days))
    else:
        # Assume it's a delivery ID
        delivery_id = command
        asyncio.run(send_webhook(delivery_id))
