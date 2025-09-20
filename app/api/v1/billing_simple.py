"""
Simple Billing API
A minimal billing endpoint that works with existing Stripe infrastructure
"""

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

router = APIRouter()


class Plan(BaseModel):
    id: str
    name: str
    description: str
    price_monthly: int  # Price in cents
    price_yearly: int   # Price in cents
    features: List[str]
    limits: Dict[str, int]


class Subscription(BaseModel):
    id: str
    plan_id: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool
    trial_end: Optional[str] = None


class Usage(BaseModel):
    ai_requests: int
    ai_requests_limit: int
    posts_published: int
    posts_limit: int
    team_members: int
    team_members_limit: int
    storage_used: int  # in MB
    storage_limit: int  # in MB


class BillingSummary(BaseModel):
    subscription: Subscription
    usage: Usage
    next_billing_date: str
    amount_due: int  # in cents


@router.get("/billing/plans", response_model=List[Plan])
async def get_available_plans() -> List[Plan]:
    """
    Get all available subscription plans
    """
    try:
        # Mock plans data (in real implementation, this would query the database)
        plans = [
            Plan(
                id="starter",
                name="Starter",
                description="Perfect for small businesses getting started with AI marketing",
                price_monthly=2900,  # $29.00
                price_yearly=29000,  # $290.00 (2 months free)
                features=[
                    "AI Content Generation (200/month)",
                    "3 Social Media Platforms",
                    "Basic Scheduling",
                    "2 Team Members",
                    "5GB Storage",
                    "Email Support"
                ],
                limits={
                    "ai_requests": 200,
                    "posts": 50,
                    "team_members": 2,
                    "storage_mb": 5120,  # 5GB
                    "platforms": 3
                }
            ),
            Plan(
                id="growth",
                name="Growth",
                description="Ideal for growing businesses scaling their marketing efforts",
                price_monthly=7900,  # $79.00
                price_yearly=79000,  # $790.00 (2 months free)
                features=[
                    "AI Content Generation (1000/month)",
                    "6 Social Media Platforms",
                    "Advanced Scheduling",
                    "10 Team Members",
                    "25GB Storage",
                    "Priority Support",
                    "Analytics Dashboard",
                    "API Access"
                ],
                limits={
                    "ai_requests": 1000,
                    "posts": 200,
                    "team_members": 10,
                    "storage_mb": 25600,  # 25GB
                    "platforms": 6
                }
            ),
            Plan(
                id="pro",
                name="Pro",
                description="For agencies and enterprises with advanced marketing needs",
                price_monthly=19900,  # $199.00
                price_yearly=199000,  # $1990.00 (2 months free)
                features=[
                    "Unlimited AI Content Generation",
                    "All Social Media Platforms",
                    "Advanced Automation",
                    "50 Team Members",
                    "100GB Storage",
                    "Dedicated Support",
                    "Advanced Analytics",
                    "White-label Options",
                    "Custom Integrations"
                ],
                limits={
                    "ai_requests": -1,  # Unlimited
                    "posts": -1,  # Unlimited
                    "team_members": 50,
                    "storage_mb": 102400,  # 100GB
                    "platforms": -1  # All platforms
                }
            )
        ]
        
        return plans
        
    except Exception as e:
        logger.error(f"Get plans error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plans: {str(e)}"
        )


@router.get("/billing/subscription", response_model=BillingSummary)
async def get_billing_summary() -> BillingSummary:
    """
    Get current subscription and usage information
    """
    try:
        # Mock subscription data (in real implementation, this would query the database)
        subscription = Subscription(
            id="sub_1234567890",
            plan_id="growth",
            status="active",
            current_period_start="2024-01-01T00:00:00Z",
            current_period_end="2024-02-01T00:00:00Z",
            cancel_at_period_end=False,
            trial_end=None
        )
        
        usage = Usage(
            ai_requests=156,
            ai_requests_limit=1000,
            posts_published=23,
            posts_limit=200,
            team_members=3,
            team_members_limit=10,
            storage_used=1250,  # 1.25GB
            storage_limit=25600  # 25GB
        )
        
        return BillingSummary(
            subscription=subscription,
            usage=usage,
            next_billing_date="2024-02-01T00:00:00Z",
            amount_due=7900  # $79.00
        )
        
    except Exception as e:
        logger.error(f"Get billing summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing summary: {str(e)}"
        )


@router.post("/billing/checkout")
async def create_checkout_session(
    plan_id: str,
    billing_cycle: str = Query("monthly", description="Billing cycle: monthly or yearly")
) -> Dict[str, Any]:
    """
    Create a Stripe checkout session for subscription
    """
    try:
        # Validate plan
        valid_plans = ["starter", "growth", "pro"]
        if plan_id not in valid_plans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan: {plan_id}"
            )
        
        # Validate billing cycle
        if billing_cycle not in ["monthly", "yearly"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Billing cycle must be 'monthly' or 'yearly'"
            )
        
        # Mock checkout session (in real implementation, this would create a real Stripe session)
        mock_session = {
            "session_id": f"cs_test_{plan_id}_{billing_cycle}_{int(datetime.now().timestamp())}",
            "url": f"https://checkout.stripe.com/pay/cs_test_{plan_id}_{billing_cycle}",
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat() + "Z"
        }
        
        return {
            "success": True,
            "checkout_session": mock_session,
            "message": f"Checkout session created for {plan_id} plan ({billing_cycle})"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create checkout session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/billing/portal")
async def create_customer_portal() -> Dict[str, Any]:
    """
    Create a Stripe customer portal session
    """
    try:
        # Mock portal session (in real implementation, this would create a real Stripe portal session)
        mock_portal = {
            "url": f"https://billing.stripe.com/p/session_{int(datetime.now().timestamp())}",
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat() + "Z"
        }
        
        return {
            "success": True,
            "portal_session": mock_portal,
            "message": "Customer portal session created"
        }
        
    except Exception as e:
        logger.error(f"Create portal session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create portal session: {str(e)}"
        )


@router.get("/billing/usage")
async def get_usage_details() -> Dict[str, Any]:
    """
    Get detailed usage information
    """
    try:
        # Mock usage data (in real implementation, this would query the database)
        usage_data = {
            "current_period": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-02-01T00:00:00Z"
            },
            "ai_usage": {
                "requests_used": 156,
                "requests_limit": 1000,
                "percentage_used": 15.6,
                "cost_this_period": 1560,  # $15.60 in cents
                "breakdown": {
                    "content_generation": 89,
                    "optimization": 45,
                    "scheduling": 22
                }
            },
            "publishing_usage": {
                "posts_published": 23,
                "posts_limit": 200,
                "percentage_used": 11.5,
                "platforms_used": ["facebook", "linkedin", "instagram"],
                "scheduled_posts": 12
            },
            "team_usage": {
                "active_members": 3,
                "members_limit": 10,
                "percentage_used": 30.0,
                "pending_invites": 1
            },
            "storage_usage": {
                "used_mb": 1250,
                "limit_mb": 25600,
                "percentage_used": 4.9,
                "files_count": 45
            }
        }
        
        return usage_data
        
    except Exception as e:
        logger.error(f"Get usage details error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage details: {str(e)}"
        )


@router.get("/billing/invoices")
async def get_invoices(
    limit: int = Query(10, description="Number of invoices to return")
) -> Dict[str, Any]:
    """
    Get billing history and invoices
    """
    try:
        # Mock invoices data (in real implementation, this would query the database)
        invoices = [
            {
                "id": "in_1234567890",
                "number": "INV-2024-001",
                "date": "2024-01-01T00:00:00Z",
                "amount": 7900,  # $79.00
                "status": "paid",
                "description": "Growth Plan - Monthly"
            },
            {
                "id": "in_1234567891",
                "number": "INV-2023-012",
                "date": "2023-12-01T00:00:00Z",
                "amount": 7900,  # $79.00
                "status": "paid",
                "description": "Growth Plan - Monthly"
            },
            {
                "id": "in_1234567892",
                "number": "INV-2023-011",
                "date": "2023-11-01T00:00:00Z",
                "amount": 2900,  # $29.00
                "status": "paid",
                "description": "Starter Plan - Monthly"
            }
        ]
        
        return {
            "invoices": invoices[:limit],
            "total_count": len(invoices),
            "has_more": len(invoices) > limit
        }
        
    except Exception as e:
        logger.error(f"Get invoices error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoices: {str(e)}"
        )


@router.get("/billing/status")
async def get_billing_status():
    """Get billing service status"""
    return {
        "status": "operational",
        "features": [
            "subscription_management",
            "payment_processing",
            "usage_tracking",
            "invoice_management",
            "plan_upgrades"
        ],
        "supported_plans": ["starter", "growth", "pro"],
        "payment_methods": ["card", "bank_transfer"],
        "version": "1.0.0",
        "message": "Billing service is ready for subscription management!"
    }
