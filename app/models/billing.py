from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BillingStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"


class PlanTier(str, Enum):
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"


class OrganizationBilling(Base):
    """Organization billing information and subscription status."""
    __tablename__ = "organization_billing"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, unique=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    plan: Mapped[PlanTier] = mapped_column(SAEnum(PlanTier, name="plan_tier"), default=PlanTier.STARTER, nullable=False)
    status: Mapped[BillingStatus] = mapped_column(SAEnum(BillingStatus, name="billing_status"), default=BillingStatus.ACTIVE, nullable=False)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Trial information
    trial_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    trial_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Coupon information
    coupon_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    coupon_discount_percent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    coupon_discount_amount_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    coupon_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Billing history
    last_payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_payment_amount_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    next_payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_payment_amount_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to organization
    organization: Mapped["Organization"] = relationship(back_populates="billing")  # type: ignore[name-defined]

    def is_active(self) -> bool:
        """Check if the subscription is currently active."""
        return self.status in [BillingStatus.ACTIVE, BillingStatus.TRIALING]
    
    def is_past_due(self) -> bool:
        """Check if the subscription is past due."""
        return self.status == BillingStatus.PAST_DUE
    
    def is_trial_active(self) -> bool:
        """Check if the organization is currently in trial period."""
        if not self.trial_end or self.trial_used:
            return False
        return datetime.utcnow() < self.trial_end
    
    def days_until_renewal(self) -> Optional[int]:
        """Get days until the next billing period."""
        if not self.current_period_end:
            return None
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    def days_until_trial_end(self) -> Optional[int]:
        """Get days until trial ends."""
        if not self.trial_end or self.trial_used:
            return None
        delta = self.trial_end - datetime.utcnow()
        return max(0, delta.days)
    
    def start_trial(self, days: int = 14) -> None:
        """Start a trial period for the organization."""
        self.trial_start = datetime.utcnow()
        self.trial_end = self.trial_start + timedelta(days=days)
        self.trial_used = True
        self.status = BillingStatus.TRIALING
    
    def apply_coupon(self, code: str, discount_percent: Optional[int] = None, 
                    discount_amount_cents: Optional[int] = None, expires_at: Optional[datetime] = None) -> None:
        """Apply a coupon to the subscription."""
        self.coupon_code = code
        self.coupon_discount_percent = discount_percent
        self.coupon_discount_amount_cents = discount_amount_cents
        self.coupon_expires_at = expires_at
    
    def remove_coupon(self) -> None:
        """Remove the current coupon."""
        self.coupon_code = None
        self.coupon_discount_percent = None
        self.coupon_discount_amount_cents = None
        self.coupon_expires_at = None


class Coupon(Base):
    """Coupon codes for discounts."""
    __tablename__ = "coupons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Discount details
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)  # percent, amount
    discount_value: Mapped[int] = mapped_column(Integer, nullable=False)  # percentage or cents
    
    # Validity
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    max_uses: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Applicability
    applicable_plans: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    min_amount_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_valid(self) -> bool:
        """Check if the coupon is currently valid."""
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        
        return True
    
    def can_be_used(self, plan: PlanTier, amount_cents: int) -> bool:
        """Check if the coupon can be used for a specific plan and amount."""
        if not self.is_valid():
            return False
        
        # Check plan applicability
        if self.applicable_plans:
            import json
            try:
                plans = json.loads(self.applicable_plans)
                if plan.value not in plans:
                    return False
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Check minimum amount
        if self.min_amount_cents and amount_cents < self.min_amount_cents:
            return False
        
        return True
    
    def calculate_discount(self, amount_cents: int) -> int:
        """Calculate the discount amount in cents."""
        if self.discount_type == "percent":
            return int(amount_cents * self.discount_value / 100)
        elif self.discount_type == "amount":
            return min(self.discount_value, amount_cents)
        else:
            return 0
    
    def use_coupon(self) -> None:
        """Mark the coupon as used."""
        self.used_count += 1


class BillingHistory(Base):
    """Billing history for organizations."""
    __tablename__ = "billing_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Transaction details
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    
    # Description
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    plan: Mapped[PlanTier] = mapped_column(SAEnum(PlanTier, name="plan_tier"), nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # succeeded, failed, pending, refunded
    
    # Coupon information
    coupon_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    discount_amount_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
