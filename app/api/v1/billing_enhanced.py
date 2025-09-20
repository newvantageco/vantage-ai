"""
Enhanced Billing API endpoints
Handles Stripe checkout sessions, portal links, and subscription management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import stripe

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_user_mock
from app.services.billing_service import BillingService
from app.models.billing import Plan, SubscriptionStatus
from app.models.entities import Organization

router = APIRouter()


class CheckoutSessionRequest(BaseModel):
    plan: str
    success_url: str
    cancel_url: str
    customer_email: Optional[str] = None


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
    plan: str
    amount: int
    currency: str


class PortalSessionRequest(BaseModel):
    return_url: str


class PortalSessionResponse(BaseModel):
    portal_url: str
    session_id: str


class BillingStatusResponse(BaseModel):
    has_subscription: bool
    plan: Optional[Dict[str, Any]]
    subscription: Optional[Dict[str, Any]]
    usage: Dict[str, Any]
    can_upgrade: bool
    can_downgrade: bool


class WebhookResponse(BaseModel):
    status: str
    event_type: Optional[str] = None
    error: Optional[str] = None


@router.post("/billing/checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Create Stripe checkout session for plan upgrade"""
    try:
        # Validate plan
        if request.plan not in ['growth', 'pro']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan. Must be 'growth' or 'pro'"
            )
        
        billing_service = BillingService(db)
        
        # Create checkout session
        result = billing_service.create_checkout_session(
            org_id=current_user["org_id"],
            plan_type=request.plan,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            customer_email=request.customer_email
        )
        
        return CheckoutSessionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/billing/portal-link", response_model=PortalSessionResponse)
async def create_portal_session(
    request: PortalSessionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Create Stripe customer portal session"""
    try:
        billing_service = BillingService(db)
        
        # Create portal session
        result = billing_service.create_portal_session(
            org_id=current_user["org_id"],
            return_url=request.return_url
        )
        
        return PortalSessionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create portal session: {str(e)}"
        )


@router.get("/billing/status", response_model=BillingStatusResponse)
async def get_billing_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Get organization's billing status and usage"""
    try:
        billing_service = BillingService(db)
        
        # Get subscription and plan
        subscription = billing_service.get_organization_subscription(current_user["org_id"])
        plan = billing_service.get_organization_plan(current_user["org_id"])
        
        # Get usage data
        usage = billing_service.get_organization_usage(current_user["org_id"])
        
        # Determine upgrade/downgrade options
        can_upgrade = not subscription or (plan and plan.name == 'growth')
        can_downgrade = subscription and plan and plan.name == 'pro'
        
        # Format response
        plan_data = None
        if plan:
            plan_data = {
                "id": plan.id,
                "name": plan.name,
                "display_name": plan.display_name,
                "description": plan.description,
                "price": plan.price,
                "currency": plan.currency,
                "billing_interval": plan.billing_interval,
                "features": plan.features,
                "limits": {
                    "ai_requests": plan.ai_request_limit,
                    "ai_tokens": plan.ai_token_limit,
                    "content_posts": plan.content_post_limit
                }
            }
        
        subscription_data = None
        if subscription:
            subscription_data = {
                "id": subscription.id,
                "status": subscription.status.value,
                "current_period_start": subscription.current_period_start.isoformat(),
                "current_period_end": subscription.current_period_end.isoformat(),
                "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None
            }
        
        return BillingStatusResponse(
            has_subscription=subscription is not None,
            plan=plan_data,
            subscription=subscription_data,
            usage=usage,
            can_upgrade=can_upgrade,
            can_downgrade=can_downgrade
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing status: {str(e)}"
        )


@router.get("/billing/plans")
async def get_available_plans(
    db: Session = Depends(get_db)
):
    """Get available billing plans"""
    try:
        plans = db.query(Plan).filter(Plan.is_active == True).all()
        
        return {
            "plans": [
                {
                    "id": plan.id,
                    "name": plan.name,
                    "display_name": plan.display_name,
                    "description": plan.description,
                    "price": plan.price,
                    "currency": plan.currency,
                    "billing_interval": plan.billing_interval,
                    "features": plan.features,
                    "limits": {
                        "ai_requests": plan.ai_request_limit,
                        "ai_tokens": plan.ai_token_limit,
                        "content_posts": plan.content_post_limit
                    },
                    "stripe_price_id": plan.stripe_price_id
                }
                for plan in plans
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plans: {str(e)}"
        )


@router.post("/billing/webhook")
async def handle_stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    try:
        # Get the raw body and signature
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        if not sig_header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing stripe-signature header"
            )
        
        # Verify webhook signature
        from app.core.config import get_settings
        settings = get_settings()
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        
        # Process the event
        billing_service = BillingService(db)
        result = billing_service.handle_webhook_event(event)
        
        return WebhookResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/billing/usage")
async def get_usage_details(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Get detailed usage information"""
    try:
        billing_service = BillingService(db)
        
        # Parse month if provided
        month_date = None
        if month:
            try:
                month_date = datetime.strptime(month, "%Y-%m")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid month format. Use YYYY-MM"
                )
        
        usage = billing_service.get_organization_usage(
            org_id=current_user["org_id"],
            month=month_date
        )
        
        return usage
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage details: {str(e)}"
        )


@router.get("/billing/invoices")
async def get_invoices(
    limit: int = Query(10, ge=1, le=100, description="Number of invoices to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Get organization's invoices from Stripe"""
    try:
        billing_service = BillingService(db)
        
        # Get organization
        org = db.query(Organization).filter(Organization.id == current_user["org_id"]).first()
        if not org or not org.stripe_customer_id:
            return {"invoices": []}
        
        # Get invoices from Stripe
        invoices = stripe.Invoice.list(
            customer=org.stripe_customer_id,
            limit=limit
        )
        
        return {
            "invoices": [
                {
                    "id": invoice.id,
                    "number": invoice.number,
                    "status": invoice.status,
                    "amount_paid": invoice.amount_paid,
                    "amount_due": invoice.amount_due,
                    "currency": invoice.currency,
                    "created": datetime.fromtimestamp(invoice.created).isoformat(),
                    "period_start": datetime.fromtimestamp(invoice.period_start).isoformat(),
                    "period_end": datetime.fromtimestamp(invoice.period_end).isoformat(),
                    "invoice_pdf": invoice.invoice_pdf,
                    "hosted_invoice_url": invoice.hosted_invoice_url
                }
                for invoice in invoices.data
            ]
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoices: {str(e)}"
        )


@router.post("/billing/cancel-subscription")
async def cancel_subscription(
    immediately: bool = Query(False, description="Cancel immediately or at period end"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Cancel organization's subscription"""
    try:
        billing_service = BillingService(db)
        
        result = billing_service.cancel_subscription(
            org_id=current_user["org_id"],
            immediately=immediately
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.post("/billing/upgrade-subscription")
async def upgrade_subscription(
    new_plan: str = Query(..., description="New plan type (growth, pro)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Upgrade organization's subscription"""
    try:
        billing_service = BillingService(db)
        
        result = billing_service.upgrade_subscription(
            org_id=current_user["org_id"],
            new_plan_type=new_plan
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade subscription: {str(e)}"
        )


@router.post("/billing/update-usage")
async def update_usage(
    usage_type: str = Query(..., description="Type of usage (ai_requests, content_posts, etc.)"),
    amount: int = Query(1, ge=1, description="Amount to add to usage"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Update organization's usage (internal API)"""
    try:
        billing_service = BillingService(db)
        
        success = billing_service.update_usage(
            org_id=current_user["org_id"],
            usage_type=usage_type,
            amount=amount
        )
        
        return {
            "success": success,
            "usage_type": usage_type,
            "amount": amount
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update usage: {str(e)}"
        )


@router.get("/billing/analytics")
async def get_billing_analytics(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Get billing analytics for the organization"""
    try:
        billing_service = BillingService(db)
        
        # Get usage data for the last N months
        analytics_data = {
            "months": [],
            "total_usage": {
                "ai_requests": 0,
                "content_posts": 0,
                "overage_charges": 0
            },
            "trends": {
                "ai_requests": [],
                "content_posts": [],
                "overage_charges": []
            }
        }
        
        for i in range(months):
            month_date = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
            usage = billing_service.get_organization_usage(
                org_id=current_user["org_id"],
                month=month_date
            )
            
            analytics_data["months"].append(usage["month"])
            analytics_data["total_usage"]["ai_requests"] += usage["ai_requests"]
            analytics_data["total_usage"]["content_posts"] += usage["content_posts"]
            analytics_data["total_usage"]["overage_charges"] += usage["overage"]["amount"]
            
            analytics_data["trends"]["ai_requests"].append(usage["ai_requests"])
            analytics_data["trends"]["content_posts"].append(usage["content_posts"])
            analytics_data["trends"]["overage_charges"].append(usage["overage"]["amount"])
        
        return analytics_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing analytics: {str(e)}"
        )


@router.get("/billing/health")
async def billing_health_check(
    db: Session = Depends(get_db)
):
    """Health check for billing service"""
    try:
        # Test Stripe connection
        stripe.Account.retrieve()
        
        # Test database connection
        db.query(Plan).first()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "stripe_connected": True,
            "database_connected": True
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "stripe_connected": False,
            "database_connected": False
        }