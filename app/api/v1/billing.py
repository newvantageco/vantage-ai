from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_bearer_token
from app.core.security import verify_clerk_jwt
from app.db.session import get_db
from app.models.billing import OrganizationBilling, PlanTier, BillingStatus
from app.billing.stripe_client import get_client, PlanTier as StripePlanTier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: PlanTier
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class PortalResponse(BaseModel):
    portal_url: str


class BillingInfo(BaseModel):
    org_id: str
    plan: PlanTier
    status: BillingStatus
    current_period_end: Optional[str] = None
    days_until_renewal: Optional[int] = None
    stripe_customer_id: Optional[str] = None


async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return await verify_clerk_jwt(token)


def get_or_create_billing_record(db: Session, org_id: str) -> OrganizationBilling:
    """Get existing billing record or create a new one."""
    billing = db.query(OrganizationBilling).filter(OrganizationBilling.org_id == org_id).first()
    
    if not billing:
        billing = OrganizationBilling(
            id=str(uuid4()),
            org_id=org_id,
            plan=PlanTier.STARTER,
            status=BillingStatus.ACTIVE
        )
        db.add(billing)
        db.commit()
        db.refresh(billing)
    
    return billing


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Create a Stripe checkout session for subscription upgrade."""
    org_id = claims.get("org_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization ID not found in token"
        )
    
    # Get or create billing record
    billing = get_or_create_billing_record(db, org_id)
    
    # If no Stripe customer ID, create one
    if not billing.stripe_customer_id:
        user_email = claims.get("email", "user@example.com")
        user_name = claims.get("name", "User")
        customer = await get_client().create_customer(
            email=user_email,
            name=user_name,
            org_id=org_id
        )
        billing.stripe_customer_id = customer["id"]
        db.commit()
    
    # Create checkout session
    session = await get_client().create_checkout_session(
        customer_id=billing.stripe_customer_id,
        plan=StripePlanTier(request.plan.value),
        success_url=request.success_url,
        cancel_url=request.cancel_url
    )
    
    return CheckoutResponse(
        checkout_url=session["url"],
        session_id=session["id"]
    )


@router.get("/portal", response_model=PortalResponse)
async def create_portal_session(
    return_url: str = Query(..., description="URL to return to after portal session"),
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Create a Stripe customer portal session for billing management."""
    org_id = claims.get("org_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization ID not found in token"
        )
    
    billing = db.query(OrganizationBilling).filter(OrganizationBilling.org_id == org_id).first()
    if not billing or not billing.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No billing account found"
        )
    
    session = await get_client().create_portal_session(
        customer_id=billing.stripe_customer_id,
        return_url=return_url
    )
    
    return PortalResponse(portal_url=session["url"])


@router.get("/info", response_model=BillingInfo)
async def get_billing_info(
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Get current billing information for the organization."""
    org_id = claims.get("org_id", "demo-org")  # TODO: Get from auth context
    
    billing = db.query(OrganizationBilling).filter(OrganizationBilling.org_id == org_id).first()
    if not billing:
        # Create default billing record
        billing = get_or_create_billing_record(db, org_id)
    
    return BillingInfo(
        org_id=billing.org_id,
        plan=billing.plan,
        status=billing.status,
        current_period_end=billing.current_period_end.isoformat() if billing.current_period_end else None,
        days_until_renewal=billing.days_until_renewal(),
        stripe_customer_id=billing.stripe_customer_id
    )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing stripe-signature header")
    
    try:
        event = get_client().construct_webhook_event(payload, sig_header)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    
    # Handle different event types
    if event["type"] == "checkout.session.completed":
        await handle_checkout_completed(event, db)
    elif event["type"] == "customer.subscription.updated":
        await handle_subscription_updated(event, db)
    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_deleted(event, db)
    else:
        logger.info(f"Unhandled webhook event type: {event['type']}")
    
    return {"status": "success"}


async def handle_checkout_completed(event: dict, db: Session):
    """Handle checkout.session.completed webhook."""
    session = event["data"]["object"]
    customer_id = session["customer"]
    subscription_id = session.get("subscription")
    
    if not subscription_id:
        logger.warning("No subscription ID in checkout session")
        return
    
    # Find billing record by customer ID
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_customer_id == customer_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for customer: {customer_id}")
        return
    
    # Get subscription details
    subscription = await get_client().get_subscription(subscription_id)
    
    # Update billing record
    billing.stripe_subscription_id = subscription_id
    billing.status = BillingStatus(subscription["status"])
    billing.current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
    billing.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
    
    # Update plan based on subscription
    # TODO: Map subscription price to plan tier
    billing.plan = PlanTier.GROWTH  # Default for now
    
    db.commit()
    logger.info(f"Updated billing for org {billing.org_id} with subscription {subscription_id}")


async def handle_subscription_updated(event: dict, db: Session):
    """Handle customer.subscription.updated webhook."""
    subscription = event["data"]["object"]
    subscription_id = subscription["id"]
    
    # Find billing record by subscription ID
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_subscription_id == subscription_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for subscription: {subscription_id}")
        return
    
    # Update billing record
    billing.status = BillingStatus(subscription["status"])
    billing.current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
    billing.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
    
    db.commit()
    logger.info(f"Updated subscription {subscription_id} for org {billing.org_id}")


async def handle_subscription_deleted(event: dict, db: Session):
    """Handle customer.subscription.deleted webhook."""
    subscription = event["data"]["object"]
    subscription_id = subscription["id"]
    
    # Find billing record by subscription ID
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_subscription_id == subscription_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for subscription: {subscription_id}")
        return
    
    # Update billing record
    billing.status = BillingStatus.CANCELED
    billing.stripe_subscription_id = None
    
    db.commit()
    logger.info(f"Canceled subscription {subscription_id} for org {billing.org_id}")
