from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import secrets

from app.db.session import get_db
from app.billing.stripe_enhanced import stripe_client
from app.models.billing import OrganizationBilling, BillingHistory, BillingStatus, PlanTier

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    try:
        event = stripe_client.construct_webhook_event(payload, sig_header)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    try:
        if event["type"] == "customer.subscription.created":
            await handle_subscription_created(event, db)
        elif event["type"] == "customer.subscription.updated":
            await handle_subscription_updated(event, db)
        elif event["type"] == "customer.subscription.deleted":
            await handle_subscription_deleted(event, db)
        elif event["type"] == "invoice.payment_succeeded":
            await handle_payment_succeeded(event, db)
        elif event["type"] == "invoice.payment_failed":
            await handle_payment_failed(event, db)
        elif event["type"] == "customer.subscription.trial_will_end":
            await handle_trial_will_end(event, db)
        else:
            logger.info(f"Unhandled event type: {event['type']}")
    
    except Exception as e:
        logger.error(f"Error processing webhook event {event['id']}: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    return {"status": "success"}


async def handle_subscription_created(event: dict, db: Session):
    """Handle subscription created event."""
    subscription = event["data"]["object"]
    customer_id = subscription["customer"]
    
    # Find organization by Stripe customer ID
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_customer_id == customer_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for customer {customer_id}")
        return
    
    # Update billing record
    billing.stripe_subscription_id = subscription["id"]
    billing.status = BillingStatus.ACTIVE
    billing.current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
    billing.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
    
    # Set plan based on price
    price_id = subscription["items"]["data"][0]["price"]["id"]
    # You would need to map price_id to PlanTier here
    # For now, default to GROWTH
    billing.plan = PlanTier.GROWTH
    
    db.commit()
    logger.info(f"Subscription created for org {billing.org_id}")


async def handle_subscription_updated(event: dict, db: Session):
    """Handle subscription updated event."""
    subscription = event["data"]["object"]
    subscription_id = subscription["id"]
    
    # Find billing record
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_subscription_id == subscription_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for subscription {subscription_id}")
        return
    
    # Update billing record
    billing.current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
    billing.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
    
    if subscription["status"] == "active":
        billing.status = BillingStatus.ACTIVE
    elif subscription["status"] == "past_due":
        billing.status = BillingStatus.PAST_DUE
    elif subscription["status"] == "canceled":
        billing.status = BillingStatus.CANCELED
    
    db.commit()
    logger.info(f"Subscription updated for org {billing.org_id}")


async def handle_subscription_deleted(event: dict, db: Session):
    """Handle subscription deleted event."""
    subscription = event["data"]["object"]
    subscription_id = subscription["id"]
    
    # Find billing record
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_subscription_id == subscription_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for subscription {subscription_id}")
        return
    
    # Update billing record
    billing.status = BillingStatus.CANCELED
    billing.stripe_subscription_id = None
    
    db.commit()
    logger.info(f"Subscription canceled for org {billing.org_id}")


async def handle_payment_succeeded(event: dict, db: Session):
    """Handle successful payment event."""
    invoice = event["data"]["object"]
    customer_id = invoice["customer"]
    
    # Find billing record
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_customer_id == customer_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for customer {customer_id}")
        return
    
    # Create billing history entry
    history_entry = BillingHistory(
        id=secrets.token_urlsafe(16),
        org_id=billing.org_id,
        stripe_payment_intent_id=invoice.get("payment_intent"),
        amount_cents=invoice["amount_paid"],
        currency=invoice["currency"],
        description=f"Payment for {billing.plan.value} plan",
        plan=billing.plan,
        status="succeeded",
        created_at=datetime.utcnow(),
        processed_at=datetime.utcnow()
    )
    
    db.add(history_entry)
    
    # Update billing record
    billing.last_payment_date = datetime.utcnow()
    billing.last_payment_amount_cents = invoice["amount_paid"]
    billing.next_payment_date = datetime.fromtimestamp(invoice["period_end"])
    billing.next_payment_amount_cents = invoice["amount_due"]
    
    db.commit()
    logger.info(f"Payment succeeded for org {billing.org_id}")


async def handle_payment_failed(event: dict, db: Session):
    """Handle failed payment event."""
    invoice = event["data"]["object"]
    customer_id = invoice["customer"]
    
    # Find billing record
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_customer_id == customer_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for customer {customer_id}")
        return
    
    # Create billing history entry
    history_entry = BillingHistory(
        id=secrets.token_urlsafe(16),
        org_id=billing.org_id,
        stripe_payment_intent_id=invoice.get("payment_intent"),
        amount_cents=invoice["amount_due"],
        currency=invoice["currency"],
        description=f"Failed payment for {billing.plan.value} plan",
        plan=billing.plan,
        status="failed",
        created_at=datetime.utcnow(),
        processed_at=datetime.utcnow()
    )
    
    db.add(history_entry)
    
    # Update billing status
    billing.status = BillingStatus.PAST_DUE
    
    db.commit()
    logger.info(f"Payment failed for org {billing.org_id}")


async def handle_trial_will_end(event: dict, db: Session):
    """Handle trial will end event."""
    subscription = event["data"]["object"]
    customer_id = subscription["customer"]
    
    # Find billing record
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.stripe_customer_id == customer_id
    ).first()
    
    if not billing:
        logger.error(f"No billing record found for customer {customer_id}")
        return
    
    # You could send a notification here
    logger.info(f"Trial will end for org {billing.org_id}")
    
    # Update trial status if needed
    if billing.trial_end and datetime.utcnow() >= billing.trial_end:
        billing.trial_used = True
        db.commit()
