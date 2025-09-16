from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets

from app.db.session import get_db
from app.models.billing import OrganizationBilling, Coupon, BillingHistory, PlanTier, BillingStatus
from app.models.entities import Organization
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()


class TrialStartRequest(BaseModel):
    days: int = 14


class CouponApplyRequest(BaseModel):
    code: str


class PlanUpgradeRequest(BaseModel):
    plan: str
    coupon_code: Optional[str] = None


class BillingStatusResponse(BaseModel):
    org_id: str
    plan: str
    status: str
    is_trial_active: bool
    trial_days_remaining: Optional[int]
    days_until_renewal: Optional[int]
    current_period_start: Optional[str]
    current_period_end: Optional[str]
    coupon_code: Optional[str]
    coupon_discount_percent: Optional[int]
    coupon_discount_amount_cents: Optional[int]
    last_payment_date: Optional[str]
    last_payment_amount_cents: Optional[int]
    next_payment_date: Optional[str]
    next_payment_amount_cents: Optional[int]

    class Config:
        from_attributes = True


class CouponResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    discount_type: str
    discount_value: int
    valid_from: str
    valid_until: Optional[str]
    max_uses: Optional[int]
    used_count: int
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class BillingHistoryResponse(BaseModel):
    id: str
    amount_cents: int
    currency: str
    description: str
    plan: str
    status: str
    coupon_code: Optional[str]
    discount_amount_cents: Optional[int]
    created_at: str
    processed_at: Optional[str]

    class Config:
        from_attributes = True


@router.get("/billing/status", response_model=BillingStatusResponse)
async def get_billing_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current billing status for the organization."""
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.org_id == current_user["org_id"]
    ).first()
    
    if not billing:
        # Create default billing record
        billing = OrganizationBilling(
            id=secrets.token_urlsafe(16),
            org_id=current_user["org_id"],
            plan=PlanTier.STARTER,
            status=BillingStatus.ACTIVE
        )
        db.add(billing)
        db.commit()
        db.refresh(billing)
    
    return BillingStatusResponse(
        org_id=billing.org_id,
        plan=billing.plan.value,
        status=billing.status.value,
        is_trial_active=billing.is_trial_active(),
        trial_days_remaining=billing.days_until_trial_end(),
        days_until_renewal=billing.days_until_renewal(),
        current_period_start=billing.current_period_start.isoformat() if billing.current_period_start else None,
        current_period_end=billing.current_period_end.isoformat() if billing.current_period_end else None,
        coupon_code=billing.coupon_code,
        coupon_discount_percent=billing.coupon_discount_percent,
        coupon_discount_amount_cents=billing.coupon_discount_amount_cents,
        last_payment_date=billing.last_payment_date.isoformat() if billing.last_payment_date else None,
        last_payment_amount_cents=billing.last_payment_amount_cents,
        next_payment_date=billing.next_payment_date.isoformat() if billing.next_payment_date else None,
        next_payment_amount_cents=billing.next_payment_amount_cents
    )


@router.post("/billing/trial/start")
async def start_trial(
    trial_data: TrialStartRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start a trial period for the organization."""
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.org_id == current_user["org_id"]
    ).first()
    
    if not billing:
        billing = OrganizationBilling(
            id=secrets.token_urlsafe(16),
            org_id=current_user["org_id"],
            plan=PlanTier.STARTER,
            status=BillingStatus.ACTIVE
        )
        db.add(billing)
    
    if billing.trial_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trial period has already been used for this organization"
        )
    
    billing.start_trial(trial_data.days)
    db.commit()
    
    return {
        "message": f"Trial started for {trial_data.days} days",
        "trial_end": billing.trial_end.isoformat(),
        "days_remaining": billing.days_until_trial_end()
    }


@router.get("/billing/coupons", response_model=List[CouponResponse])
async def list_available_coupons(
    plan: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List available coupons for the organization."""
    query = db.query(Coupon).filter(Coupon.is_active == True)
    
    if plan:
        try:
            plan_enum = PlanTier(plan)
            # Filter by applicable plans
            query = query.filter(
                Coupon.applicable_plans.is_(None) | 
                Coupon.applicable_plans.contains(f'"{plan}"')
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan. Must be one of: {[p.value for p in PlanTier]}"
            )
    
    coupons = query.filter(Coupon.valid_from <= datetime.utcnow()).all()
    
    # Filter by validity
    valid_coupons = [c for c in coupons if c.is_valid()]
    
    return [
        CouponResponse(
            id=coupon.id,
            code=coupon.code,
            name=coupon.name,
            description=coupon.description,
            discount_type=coupon.discount_type,
            discount_value=coupon.discount_value,
            valid_from=coupon.valid_from.isoformat(),
            valid_until=coupon.valid_until.isoformat() if coupon.valid_until else None,
            max_uses=coupon.max_uses,
            used_count=coupon.used_count,
            is_active=coupon.is_active,
            created_at=coupon.created_at.isoformat()
        )
        for coupon in valid_coupons
    ]


@router.post("/billing/coupons/apply")
async def apply_coupon(
    coupon_data: CouponApplyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Apply a coupon to the organization's billing."""
    # Get coupon
    coupon = db.query(Coupon).filter(
        Coupon.code == coupon_data.code,
        Coupon.is_active == True
    ).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    if not coupon.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon is not valid or has expired"
        )
    
    # Get billing record
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.org_id == current_user["org_id"]
    ).first()
    
    if not billing:
        billing = OrganizationBilling(
            id=secrets.token_urlsafe(16),
            org_id=current_user["org_id"],
            plan=PlanTier.STARTER,
            status=BillingStatus.ACTIVE
        )
        db.add(billing)
    
    # Check if coupon can be used
    if not coupon.can_be_used(billing.plan, 0):  # We'll calculate amount later
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon cannot be used with your current plan"
        )
    
    # Apply coupon
    billing.apply_coupon(
        code=coupon.code,
        discount_percent=coupon.discount_value if coupon.discount_type == "percent" else None,
        discount_amount_cents=coupon.discount_value if coupon.discount_type == "amount" else None,
        expires_at=coupon.valid_until
    )
    
    db.commit()
    
    return {
        "message": "Coupon applied successfully",
        "coupon_code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value
    }


@router.delete("/billing/coupons/remove")
async def remove_coupon(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Remove the current coupon from the organization's billing."""
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.org_id == current_user["org_id"]
    ).first()
    
    if not billing or not billing.coupon_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No coupon applied"
        )
    
    billing.remove_coupon()
    db.commit()
    
    return {"message": "Coupon removed successfully"}


@router.post("/billing/upgrade")
async def upgrade_plan(
    upgrade_data: PlanUpgradeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upgrade the organization's plan."""
    try:
        new_plan = PlanTier(upgrade_data.plan)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {[p.value for p in PlanTier]}"
        )
    
    # Get billing record
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.org_id == current_user["org_id"]
    ).first()
    
    if not billing:
        billing = OrganizationBilling(
            id=secrets.token_urlsafe(16),
            org_id=current_user["org_id"],
            plan=PlanTier.STARTER,
            status=BillingStatus.ACTIVE
        )
        db.add(billing)
    
    # Check if upgrading
    if billing.plan == new_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already on this plan"
        )
    
    # Apply coupon if provided
    if upgrade_data.coupon_code:
        coupon = db.query(Coupon).filter(
            Coupon.code == upgrade_data.coupon_code,
            Coupon.is_active == True
        ).first()
        
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found"
            )
        
        if not coupon.is_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon is not valid or has expired"
            )
        
        if not coupon.can_be_used(new_plan, 0):  # We'll calculate amount later
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon cannot be used with this plan"
            )
        
        billing.apply_coupon(
            code=coupon.code,
            discount_percent=coupon.discount_value if coupon.discount_type == "percent" else None,
            discount_amount_cents=coupon.discount_value if coupon.discount_type == "amount" else None,
            expires_at=coupon.valid_until
        )
    
    # Update plan
    billing.plan = new_plan
    billing.status = BillingStatus.ACTIVE
    
    # Set billing period
    now = datetime.utcnow()
    billing.current_period_start = now
    billing.current_period_end = now + timedelta(days=30)  # Monthly billing
    
    db.commit()
    
    return {
        "message": f"Plan upgraded to {new_plan.value}",
        "new_plan": new_plan.value,
        "billing_period_start": billing.current_period_start.isoformat(),
        "billing_period_end": billing.current_period_end.isoformat()
    }


@router.get("/billing/history", response_model=List[BillingHistoryResponse])
async def get_billing_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get billing history for the organization."""
    history = db.query(BillingHistory).filter(
        BillingHistory.org_id == current_user["org_id"]
    ).order_by(BillingHistory.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        BillingHistoryResponse(
            id=entry.id,
            amount_cents=entry.amount_cents,
            currency=entry.currency,
            description=entry.description,
            plan=entry.plan.value,
            status=entry.status,
            coupon_code=entry.coupon_code,
            discount_amount_cents=entry.discount_amount_cents,
            created_at=entry.created_at.isoformat(),
            processed_at=entry.processed_at.isoformat() if entry.processed_at else None
        )
        for entry in history
    ]


@router.get("/billing/plans")
async def get_available_plans():
    """Get available billing plans."""
    return {
        "plans": [
            {
                "tier": "starter",
                "name": "Starter",
                "price_cents": 0,
                "billing_interval": "month",
                "features": [
                    "50 posts per month",
                    "3 social channels",
                    "2 team members",
                    "5 campaigns",
                    "100 content items",
                    "200 AI generations"
                ]
            },
            {
                "tier": "growth",
                "name": "Growth",
                "price_cents": 2900,  # $29
                "billing_interval": "month",
                "features": [
                    "200 posts per month",
                    "10 social channels",
                    "5 team members",
                    "20 campaigns",
                    "500 content items",
                    "1000 AI generations"
                ]
            },
            {
                "tier": "pro",
                "name": "Pro",
                "price_cents": 9900,  # $99
                "billing_interval": "month",
                "features": [
                    "1000 posts per month",
                    "50 social channels",
                    "25 team members",
                    "100 campaigns",
                    "2500 content items",
                    "5000 AI generations"
                ]
            }
        ]
    }


@router.get("/billing/trial/status")
async def get_trial_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get trial status for the organization."""
    billing = db.query(OrganizationBilling).filter(
        OrganizationBilling.org_id == current_user["org_id"]
    ).first()
    
    if not billing:
        return {
            "has_trial": False,
            "trial_used": False,
            "can_start_trial": True
        }
    
    return {
        "has_trial": billing.trial_end is not None,
        "trial_used": billing.trial_used,
        "trial_active": billing.is_trial_active(),
        "trial_days_remaining": billing.days_until_trial_end(),
        "can_start_trial": not billing.trial_used
    }
