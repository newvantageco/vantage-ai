"""
Platform Webhook Endpoints
Handles incoming webhooks from external platforms (Meta, LinkedIn, Google, TikTok, WhatsApp, Stripe)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import json
import hmac
import hashlib
import secrets

from app.db.session import get_db
from app.models.publishing import PlatformIntegration, ExternalReference, PublishingStatus
from app.models.entities import Organization
from app.workers.tasks import process_platform_webhook
from pydantic import BaseModel

router = APIRouter()


class WebhookResponse(BaseModel):
    success: bool
    message: str
    processed_at: str


def verify_meta_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify Meta webhook signature"""
    if not signature or not secret:
        return False
    
    # Remove 'sha256=' prefix if present
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def verify_linkedin_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify LinkedIn webhook signature"""
    if not signature or not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def verify_google_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify Google webhook signature"""
    if not signature or not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def verify_tiktok_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify TikTok webhook signature"""
    if not signature or not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def verify_whatsapp_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify WhatsApp webhook signature"""
    if not signature or not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def verify_stripe_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify Stripe webhook signature"""
    if not signature or not secret:
        return False
    
    # Stripe uses a different signature format
    try:
        import stripe
        stripe.Webhook.construct_event(payload, signature, secret)
        return True
    except Exception:
        return False


@router.post("/webhooks/meta", response_model=WebhookResponse)
async def meta_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Meta (Facebook/Instagram) webhooks"""
    try:
        # Get raw body
        body = await request.body()
        payload = body.decode('utf-8')
        
        # Get signature
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        # Get webhook secret from environment or database
        # TODO: Implement proper secret retrieval from database
        webhook_secret = "your_meta_webhook_secret"  # This should come from config
        
        # Verify signature
        if not verify_meta_signature(payload, signature, webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        # Parse payload
        data = json.loads(payload)
        
        # Store webhook payload
        webhook_id = secrets.token_urlsafe(16)
        
        # Enqueue background task to process webhook
        background_tasks.add_task(
            process_platform_webhook,
            webhook_id=webhook_id,
            platform="meta",
            payload=data,
            signature=signature
        )
        
        return WebhookResponse(
            success=True,
            message="Meta webhook processed successfully",
            processed_at=datetime.utcnow().isoformat()
        )
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.post("/webhooks/linkedin", response_model=WebhookResponse)
async def linkedin_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle LinkedIn webhooks"""
    try:
        body = await request.body()
        payload = body.decode('utf-8')
        signature = request.headers.get('X-LinkedIn-Signature', '')
        
        webhook_secret = "your_linkedin_webhook_secret"
        
        if not verify_linkedin_signature(payload, signature, webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        data = json.loads(payload)
        webhook_id = secrets.token_urlsafe(16)
        
        background_tasks.add_task(
            process_platform_webhook,
            webhook_id=webhook_id,
            platform="linkedin",
            payload=data,
            signature=signature
        )
        
        return WebhookResponse(
            success=True,
            message="LinkedIn webhook processed successfully",
            processed_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LinkedIn webhook processing failed: {str(e)}"
        )


@router.post("/webhooks/google", response_model=WebhookResponse)
async def google_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Google (My Business, Ads) webhooks"""
    try:
        body = await request.body()
        payload = body.decode('utf-8')
        signature = request.headers.get('X-Google-Signature', '')
        
        webhook_secret = "your_google_webhook_secret"
        
        if not verify_google_signature(payload, signature, webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        data = json.loads(payload)
        webhook_id = secrets.token_urlsafe(16)
        
        background_tasks.add_task(
            process_platform_webhook,
            webhook_id=webhook_id,
            platform="google",
            payload=data,
            signature=signature
        )
        
        return WebhookResponse(
            success=True,
            message="Google webhook processed successfully",
            processed_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google webhook processing failed: {str(e)}"
        )


@router.post("/webhooks/tiktok", response_model=WebhookResponse)
async def tiktok_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle TikTok webhooks"""
    try:
        body = await request.body()
        payload = body.decode('utf-8')
        signature = request.headers.get('X-TikTok-Signature', '')
        
        webhook_secret = "your_tiktok_webhook_secret"
        
        if not verify_tiktok_signature(payload, signature, webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        data = json.loads(payload)
        webhook_id = secrets.token_urlsafe(16)
        
        background_tasks.add_task(
            process_platform_webhook,
            webhook_id=webhook_id,
            platform="tiktok",
            payload=data,
            signature=signature
        )
        
        return WebhookResponse(
            success=True,
            message="TikTok webhook processed successfully",
            processed_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TikTok webhook processing failed: {str(e)}"
        )


@router.post("/webhooks/whatsapp", response_model=WebhookResponse)
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle WhatsApp Business webhooks"""
    try:
        body = await request.body()
        payload = body.decode('utf-8')
        signature = request.headers.get('X-WhatsApp-Signature', '')
        
        webhook_secret = "your_whatsapp_webhook_secret"
        
        if not verify_whatsapp_signature(payload, signature, webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        data = json.loads(payload)
        webhook_id = secrets.token_urlsafe(16)
        
        background_tasks.add_task(
            process_platform_webhook,
            webhook_id=webhook_id,
            platform="whatsapp",
            payload=data,
            signature=signature
        )
        
        return WebhookResponse(
            success=True,
            message="WhatsApp webhook processed successfully",
            processed_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WhatsApp webhook processing failed: {str(e)}"
        )


@router.post("/webhooks/stripe", response_model=WebhookResponse)
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        payload = body.decode('utf-8')
        signature = request.headers.get('Stripe-Signature', '')
        
        webhook_secret = "your_stripe_webhook_secret"
        
        if not verify_stripe_signature(payload, signature, webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        data = json.loads(payload)
        webhook_id = secrets.token_urlsafe(16)
        
        background_tasks.add_task(
            process_platform_webhook,
            webhook_id=webhook_id,
            platform="stripe",
            payload=data,
            signature=signature
        )
        
        return WebhookResponse(
            success=True,
            message="Stripe webhook processed successfully",
            processed_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe webhook processing failed: {str(e)}"
        )


@router.get("/webhooks/health")
async def webhooks_health():
    """Health check for webhook endpoints"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "supported_platforms": [
            "meta", "linkedin", "google", "tiktok", "whatsapp", "stripe"
        ]
    }
