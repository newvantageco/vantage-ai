"""
Billing API Router
Handles Stripe integration, subscriptions, and payment processing
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import stripe
import os

from app.api.deps import get_db, get_current_user
from app.schemas.billing import (
    CheckoutSessionResponse, PortalLinkResponse,
    SubscriptionResponse, InvoiceResponse, PaymentMethodResponse,
    UsageRecordResponse, BillingEventResponse
)
from app.models.billing import (
    Subscription, Invoice, PaymentMethod, UsageRecord, BillingEvent
)
from app.models.cms import UserAccount, Organization
from app.services.billing_service import BillingService

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")

# Initialize billing service (will be created per request)
# billing_service = BillingService()


@router.post("/billing/checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> CheckoutSessionResponse:
    """
    Create a Stripe checkout session for subscription.
    """
    try:
        billing_service = BillingService(db)
        # Get or create Stripe customer
        customer_id = await billing_service.get_or_create_customer(
            current_user.organization_id, 
            current_user.email,
            current_user.first_name,
            current_user.last_name
        )
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'organization_id': str(current_user.organization_id),
                'user_id': str(current_user.id)
            }
        )
        
        return CheckoutSessionResponse(
            session_id=checkout_session.id,
            url=checkout_session.url,
            expires_at=datetime.fromtimestamp(checkout_session.expires_at)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Checkout session creation failed: {str(e)}"
        )


@router.post("/billing/portal-link", response_model=PortalLinkResponse)
async def create_portal_link(
    return_url: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> PortalLinkResponse:
    """
    Create a Stripe customer portal link.
    """
    try:
        # Get organization's Stripe customer ID
        organization = db.query(Organization).filter(
            Organization.id == current_user.organization_id
        ).first()
        
        if not organization or not organization.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Stripe customer found for this organization"
            )
        
        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=organization.stripe_customer_id,
            return_url=return_url
        )
        
        return PortalLinkResponse(
            url=portal_session.url,
            expires_at=datetime.fromtimestamp(portal_session.expires_at)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portal link creation failed: {str(e)}"
        )


@router.get("/billing/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> SubscriptionResponse:
    """
    Get current organization's subscription.
    """
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == current_user.organization_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    return SubscriptionResponse.from_orm(subscription)


@router.get("/billing/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[InvoiceResponse]:
    """
    List invoices for the current organization.
    """
    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id
    ).order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    
    return [InvoiceResponse.from_orm(invoice) for invoice in invoices]


@router.get("/billing/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> InvoiceResponse:
    """
    Get a specific invoice.
    """
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return InvoiceResponse.from_orm(invoice)


@router.get("/billing/payment-methods", response_model=List[PaymentMethodResponse])
async def list_payment_methods(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[PaymentMethodResponse]:
    """
    List payment methods for the current organization.
    """
    payment_methods = db.query(PaymentMethod).filter(
        PaymentMethod.organization_id == current_user.organization_id
    ).all()
    
    return [PaymentMethodResponse.from_orm(pm) for pm in payment_methods]


@router.post("/billing/payment-methods/{payment_method_id}/set-default", status_code=status.HTTP_200_OK)
async def set_default_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Set a payment method as default.
    """
    # Get payment method
    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id,
        PaymentMethod.organization_id == current_user.organization_id
    ).first()
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    # Remove default from all payment methods
    db.query(PaymentMethod).filter(
        PaymentMethod.organization_id == current_user.organization_id
    ).update({"is_default": False})
    
    # Set this one as default
    payment_method.is_default = True
    db.commit()
    
    return {"status": "success", "message": "Default payment method updated"}


@router.delete("/billing/payment-methods/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Delete a payment method.
    """
    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id,
        PaymentMethod.organization_id == current_user.organization_id
    ).first()
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    # Delete from Stripe
    try:
        stripe.PaymentMethod.detach(payment_method.stripe_payment_method_id)
    except Exception as e:
        print(f"Failed to detach payment method from Stripe: {e}")
    
    # Delete from database
    db.delete(payment_method)
    db.commit()


@router.get("/billing/usage", response_model=List[UsageRecordResponse])
async def get_usage_records(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[UsageRecordResponse]:
    """
    Get usage records for the current organization.
    """
    usage_records = db.query(UsageRecord).filter(
        UsageRecord.organization_id == current_user.organization_id
    ).order_by(UsageRecord.period_start.desc()).offset(skip).limit(limit).all()
    
    return [UsageRecordResponse.from_orm(record) for record in usage_records]


@router.get("/billing/current-usage", response_model=Dict[str, Any])
async def get_current_usage(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current month's usage.
    """
    try:
        # Get current subscription
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == current_user.organization_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # Get current period usage
        current_period_start = subscription.current_period_start
        current_period_end = subscription.current_period_end
        
        usage_record = db.query(UsageRecord).filter(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.subscription_id == subscription.id,
            UsageRecord.period_start == current_period_start,
            UsageRecord.period_end == current_period_end
        ).first()
        
        if not usage_record:
            # Create new usage record
            usage_record = UsageRecord(
                organization_id=current_user.organization_id,
                subscription_id=subscription.id,
                period_start=current_period_start,
                period_end=current_period_end
            )
            db.add(usage_record)
            db.commit()
            db.refresh(usage_record)
        
        return {
            "period_start": usage_record.period_start,
            "period_end": usage_record.period_end,
            "posts_used": usage_record.posts_used,
            "posts_limit": subscription.monthly_posts_limit,
            "ai_requests_used": usage_record.ai_requests_used,
            "ai_requests_limit": subscription.monthly_ai_requests_limit,
            "team_members_used": usage_record.team_members_used,
            "team_members_limit": subscription.team_members_limit,
            "integrations_used": usage_record.integrations_used,
            "integrations_limit": subscription.integrations_limit,
            "posts_overage": usage_record.posts_overage,
            "ai_requests_overage": usage_record.ai_requests_overage,
            "overage_amount": usage_record.overage_amount
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Current usage retrieval failed: {str(e)}"
        )


@router.post("/billing/webhooks/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    """
    try:
        # Get webhook signature
        signature = request.headers.get('stripe-signature')
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature"
            )
        
        # Get request body
        body = await request.body()
        
        # Verify webhook signature
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
        try:
            event = stripe.Webhook.construct_event(
                body, signature, webhook_secret
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payload: {e}"
            )
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid signature: {e}"
            )
        
        # Process event
        result = await billing_service.process_stripe_event(event, db)
        
        return {"status": "success", "event_id": event.id, "result": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/billing/plans", response_model=List[Dict[str, Any]])
async def get_available_plans() -> List[Dict[str, Any]]:
    """
    Get available subscription plans.
    """
    return [
        {
            "id": "starter",
            "name": "Starter",
            "price": 0,
            "currency": "USD",
            "interval": "month",
            "features": [
                "Up to 10 posts per month",
                "Basic AI content generation",
                "1 team member",
                "Basic analytics"
            ],
            "limits": {
                "monthly_posts": 10,
                "monthly_ai_requests": 50,
                "team_members": 1,
                "integrations": 2
            }
        },
        {
            "id": "growth",
            "name": "Growth",
            "price": 2900,  # $29.00 in cents
            "currency": "USD",
            "interval": "month",
            "features": [
                "Up to 100 posts per month",
                "Advanced AI content generation",
                "Up to 5 team members",
                "Advanced analytics",
                "Priority support"
            ],
            "limits": {
                "monthly_posts": 100,
                "monthly_ai_requests": 500,
                "team_members": 5,
                "integrations": 10
            }
        },
        {
            "id": "pro",
            "name": "Pro",
            "price": 9900,  # $99.00 in cents
            "currency": "USD",
            "interval": "month",
            "features": [
                "Unlimited posts",
                "Premium AI content generation",
                "Unlimited team members",
                "Advanced analytics & reporting",
                "White-label options",
                "Priority support"
            ],
            "limits": {
                "monthly_posts": -1,  # Unlimited
                "monthly_ai_requests": -1,  # Unlimited
                "team_members": -1,  # Unlimited
                "integrations": -1  # Unlimited
            }
        }
    ]