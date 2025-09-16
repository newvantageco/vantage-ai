from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import json

from app.db.session import get_db
from app.models.webhooks import Webhook, WebhookDelivery, WebhookEvent, WEBHOOK_EVENTS
from app.models.entities import Organization
from app.api.deps import get_current_user
from workers.webhook_worker import send_webhook
from pydantic import BaseModel

router = APIRouter()


class WebhookCreate(BaseModel):
    target_url: str
    name: str
    description: Optional[str] = None
    events: List[str]
    retry_count: int = 3
    timeout_seconds: int = 30
    headers: Optional[Dict[str, str]] = None


class WebhookResponse(BaseModel):
    id: str
    target_url: str
    name: str
    description: Optional[str]
    events: List[str]
    is_active: bool
    retry_count: int
    timeout_seconds: int
    headers: Dict[str, str]
    created_at: str
    updated_at: str
    last_triggered_at: Optional[str]

    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    id: str
    webhook_id: str
    event_type: str
    status: str
    attempt_count: int
    response_status: Optional[int]
    error_message: Optional[str]
    started_at: str
    completed_at: Optional[str]
    next_retry_at: Optional[str]

    class Config:
        from_attributes = True


@router.post("/webhooks", response_model=WebhookResponse)
async def create_webhook(
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new webhook."""
    
    # Validate events
    available_events = list(WEBHOOK_EVENTS.keys())
    invalid_events = [event for event in webhook_data.events if event not in available_events]
    if invalid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid events: {invalid_events}. Available events: {available_events}"
        )
    
    # Create webhook
    webhook = Webhook(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        target_url=webhook_data.target_url,
        name=webhook_data.name,
        description=webhook_data.description,
        events=json.dumps(webhook_data.events),
        secret=Webhook.generate_secret(),
        retry_count=webhook_data.retry_count,
        timeout_seconds=webhook_data.timeout_seconds,
        headers=json.dumps(webhook_data.headers or {})
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    
    return WebhookResponse(
        id=webhook.id,
        target_url=webhook.target_url,
        name=webhook.name,
        description=webhook.description,
        events=webhook.get_events(),
        is_active=webhook.is_active,
        retry_count=webhook.retry_count,
        timeout_seconds=webhook.timeout_seconds,
        headers=webhook.get_headers(),
        created_at=webhook.created_at.isoformat(),
        updated_at=webhook.updated_at.isoformat(),
        last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None
    )


@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List webhooks for the organization."""
    webhooks = db.query(Webhook).filter(Webhook.org_id == current_user["org_id"]).all()
    
    return [
        WebhookResponse(
            id=webhook.id,
            target_url=webhook.target_url,
            name=webhook.name,
            description=webhook.description,
            events=webhook.get_events(),
            is_active=webhook.is_active,
            retry_count=webhook.retry_count,
            timeout_seconds=webhook.timeout_seconds,
            headers=webhook.get_headers(),
            created_at=webhook.created_at.isoformat(),
            updated_at=webhook.updated_at.isoformat(),
            last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None
        )
        for webhook in webhooks
    ]


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user["org_id"]
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return WebhookResponse(
        id=webhook.id,
        target_url=webhook.target_url,
        name=webhook.name,
        description=webhook.description,
        events=webhook.get_events(),
        is_active=webhook.is_active,
        retry_count=webhook.retry_count,
        timeout_seconds=webhook.timeout_seconds,
        headers=webhook.get_headers(),
        created_at=webhook.created_at.isoformat(),
        updated_at=webhook.updated_at.isoformat(),
        last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None
    )


@router.put("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user["org_id"]
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Validate events
    available_events = list(WEBHOOK_EVENTS.keys())
    invalid_events = [event for event in webhook_data.events if event not in available_events]
    if invalid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid events: {invalid_events}. Available events: {available_events}"
        )
    
    # Update fields
    webhook.target_url = webhook_data.target_url
    webhook.name = webhook_data.name
    webhook.description = webhook_data.description
    webhook.events = json.dumps(webhook_data.events)
    webhook.retry_count = webhook_data.retry_count
    webhook.timeout_seconds = webhook_data.timeout_seconds
    webhook.headers = json.dumps(webhook_data.headers or {})
    
    db.commit()
    db.refresh(webhook)
    
    return WebhookResponse(
        id=webhook.id,
        target_url=webhook.target_url,
        name=webhook.name,
        description=webhook.description,
        events=webhook.get_events(),
        is_active=webhook.is_active,
        retry_count=webhook.retry_count,
        timeout_seconds=webhook.timeout_seconds,
        headers=webhook.get_headers(),
        created_at=webhook.created_at.isoformat(),
        updated_at=webhook.updated_at.isoformat(),
        last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None
    )


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user["org_id"]
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    db.delete(webhook)
    db.commit()
    
    return {"message": "Webhook deleted successfully"}


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    event_type: str = "POSTED",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Test a webhook with sample data."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user["org_id"]
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Create test payload
    test_payload = {
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "test": True,
            "webhook_id": webhook_id,
            "message": "This is a test webhook delivery"
        }
    }
    
    # Create delivery record
    delivery = WebhookDelivery(
        id=secrets.token_urlsafe(16),
        webhook_id=webhook_id,
        org_id=current_user["org_id"],
        event_type=event_type,
        payload=json.dumps(test_payload),
        status="pending"
    )
    
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    
    # Send webhook in background
    if background_tasks:
        background_tasks.add_task(send_webhook, delivery.id)
    
    return {
        "message": "Test webhook sent",
        "delivery_id": delivery.id,
        "payload": test_payload
    }


@router.get("/webhooks/{webhook_id}/deliveries", response_model=List[WebhookDeliveryResponse])
async def list_webhook_deliveries(
    webhook_id: str,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List webhook deliveries."""
    # Verify webhook belongs to org
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user["org_id"]
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    query = db.query(WebhookDelivery).filter(WebhookDelivery.webhook_id == webhook_id)
    
    if status:
        query = query.filter(WebhookDelivery.status == status)
    
    deliveries = query.order_by(WebhookDelivery.started_at.desc()).offset(offset).limit(limit).all()
    
    return [
        WebhookDeliveryResponse(
            id=delivery.id,
            webhook_id=delivery.webhook_id,
            event_type=delivery.event_type,
            status=delivery.status,
            attempt_count=delivery.attempt_count,
            response_status=delivery.response_status,
            error_message=delivery.error_message,
            started_at=delivery.started_at.isoformat(),
            completed_at=delivery.completed_at.isoformat() if delivery.completed_at else None,
            next_retry_at=delivery.next_retry_at.isoformat() if delivery.next_retry_at else None
        )
        for delivery in deliveries
    ]


@router.get("/webhooks/events")
async def get_available_events():
    """Get available webhook events."""
    return {
        "events": [
            {
                "id": event_id,
                "name": event_data["name"],
                "description": event_data["description"],
                "schema": event_data["schema"]
            }
            for event_id, event_data in WEBHOOK_EVENTS.items()
        ]
    }


@router.get("/webhooks/{webhook_id}/secret")
async def get_webhook_secret(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get webhook secret for signature verification."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user["org_id"]
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return {
        "webhook_id": webhook_id,
        "secret": webhook.secret,
        "signature_header": "X-Vantage-Signature",
        "example_signature": webhook.generate_signature('{"test": "payload"}')
    }


@router.post("/webhooks/{webhook_id}/regenerate-secret")
async def regenerate_webhook_secret(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Regenerate webhook secret."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user["org_id"]
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Generate new secret
    webhook.secret = Webhook.generate_secret()
    db.commit()
    
    return {
        "message": "Webhook secret regenerated successfully",
        "secret": webhook.secret
    }
