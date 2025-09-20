"""
Billing Models
Handles Stripe integration, subscriptions, and payment processing
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class PlanType(str, enum.Enum):
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"


class SubscriptionStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Stripe details
    stripe_subscription_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_customer_id = Column(String(255), nullable=False, index=True)
    
    # Plan details
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    
    # Pricing
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), default="USD")
    interval = Column(String(20), default="month")  # month, year
    
    # Trial
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    
    # Billing dates
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage limits
    monthly_posts_limit = Column(Integer, nullable=True)
    monthly_ai_requests_limit = Column(Integer, nullable=True)
    team_members_limit = Column(Integer, nullable=True)
    integrations_limit = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    plan = relationship("Plan", back_populates="subscriptions")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    
    # Stripe details
    stripe_invoice_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    
    # Invoice details
    invoice_number = Column(String(100), nullable=True)
    amount_due = Column(Integer, nullable=False)  # Amount in cents
    amount_paid = Column(Integer, default=0)  # Amount paid in cents
    currency = Column(String(3), default="USD")
    
    # Status
    status = Column(String(20), default="draft")  # draft, open, paid, void, uncollectible
    paid = Column(Boolean, default=False)
    
    # Dates
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # PDF
    invoice_pdf_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    subscription = relationship("Subscription")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Stripe details
    stripe_payment_method_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Payment method details
    type = Column(String(50), nullable=False)  # card, bank_account, etc.
    brand = Column(String(50), nullable=True)  # visa, mastercard, etc.
    last4 = Column(String(4), nullable=True)
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Usage period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Usage metrics
    posts_used = Column(Integer, default=0)
    ai_requests_used = Column(Integer, default=0)
    team_members_used = Column(Integer, default=0)
    integrations_used = Column(Integer, default=0)
    
    # Overage charges
    posts_overage = Column(Integer, default=0)
    ai_requests_overage = Column(Integer, default=0)
    overage_amount = Column(Integer, default=0)  # Overage charges in cents
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    subscription = relationship("Subscription")


class BillingEvent(Base):
    __tablename__ = "billing_events"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # subscription.created, invoice.paid, etc.
    stripe_event_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # Event data
    data = Column(JSON, nullable=False)
    
    # Processing status
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")


class OrganizationBilling(Base):
    """Organization billing information"""
    __tablename__ = "organization_billing"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    stripe_customer_id = Column(String, unique=True, nullable=True)
    billing_email = Column(String, nullable=True)
    billing_address = Column(JSON, nullable=True)
    payment_method_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")


class Coupon(Base):
    """Discount coupons"""
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    discount_type = Column(String, nullable=False)  # "percentage", "fixed"
    discount_value = Column(Float, nullable=False)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BillingHistory(Base):
    """Billing history for organizations"""
    __tablename__ = "billing_history"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    stripe_invoice_id = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String, default="usd")
    status = Column(String, nullable=False)  # "paid", "pending", "failed"
    invoice_url = Column(String, nullable=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")


class Plan(Base):
    """Subscription plans"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)  # growth, pro
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Price in cents
    currency = Column(String(3), default="USD")
    billing_interval = Column(String(20), default="month")  # month, year
    stripe_price_id = Column(String(255), nullable=True, unique=True)
    
    # Features and limits
    features = Column(JSON, nullable=True)  # List of features
    ai_request_limit = Column(Integer, nullable=True)
    ai_token_limit = Column(Integer, nullable=True)
    content_post_limit = Column(Integer, nullable=True)
    team_member_limit = Column(Integer, nullable=True)
    integration_limit = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class PlanTier(str, enum.Enum):
    """Subscription plan tiers"""
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"


class BillingStatus(Base):
    """Billing status tracking"""
    __tablename__ = "billing_status"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    status = Column(String, nullable=False)  # "active", "trial", "past_due", "canceled"
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    last_payment_at = Column(DateTime(timezone=True), nullable=True)
    next_payment_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")