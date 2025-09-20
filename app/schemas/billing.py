"""
Billing Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlanType(str, Enum):
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"


class SubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


# Checkout Session Schemas
class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str
    expires_at: datetime


class CheckoutSessionRequest(BaseModel):
    price_id: str = Field(..., description="Stripe price ID")
    success_url: str = Field(..., description="Success redirect URL")
    cancel_url: str = Field(..., description="Cancel redirect URL")


# Portal Link Schemas
class PortalLinkResponse(BaseModel):
    url: str
    expires_at: datetime


class PortalLinkRequest(BaseModel):
    return_url: str = Field(..., description="Return URL after portal session")


# Subscription Schemas
class SubscriptionResponse(BaseModel):
    id: int
    organization_id: int
    stripe_subscription_id: Optional[str]
    stripe_customer_id: str
    plan: PlanType
    status: SubscriptionStatus
    amount: int
    currency: str
    interval: str
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    canceled_at: Optional[datetime]
    monthly_posts_limit: Optional[int]
    monthly_ai_requests_limit: Optional[int]
    team_members_limit: Optional[int]
    integrations_limit: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceResponse(BaseModel):
    id: int
    organization_id: int
    subscription_id: Optional[int]
    stripe_invoice_id: Optional[str]
    stripe_payment_intent_id: Optional[str]
    invoice_number: Optional[str]
    amount_due: int
    amount_paid: int
    currency: str
    status: InvoiceStatus
    paid: bool
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
    invoice_pdf_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Payment Method Schemas
class PaymentMethodResponse(BaseModel):
    id: int
    organization_id: int
    stripe_payment_method_id: str
    type: str
    brand: Optional[str]
    last4: Optional[str]
    exp_month: Optional[int]
    exp_year: Optional[int]
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Usage Record Schemas
class UsageRecordResponse(BaseModel):
    id: int
    organization_id: int
    subscription_id: int
    period_start: datetime
    period_end: datetime
    posts_used: int
    ai_requests_used: int
    team_members_used: int
    integrations_used: int
    posts_overage: int
    ai_requests_overage: int
    overage_amount: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Billing Event Schemas
class BillingEventResponse(BaseModel):
    id: int
    organization_id: int
    event_type: str
    stripe_event_id: Optional[str]
    data: Dict[str, Any]
    processed: bool
    processed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Plan Schemas
class PlanFeature(BaseModel):
    name: str
    included: bool
    limit: Optional[int] = None


class PlanResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: int
    currency: str
    interval: str
    features: List[PlanFeature]
    limits: Dict[str, int]
    is_popular: bool = False
    trial_days: Optional[int] = None


# Billing Summary Schemas
class BillingSummaryResponse(BaseModel):
    subscription: SubscriptionResponse
    current_usage: Dict[str, Any]
    next_invoice: Optional[InvoiceResponse]
    payment_methods: List[PaymentMethodResponse]
    recent_invoices: List[InvoiceResponse]


# Usage Analytics Schemas
class UsageAnalyticsResponse(BaseModel):
    current_period: UsageRecordResponse
    previous_period: Optional[UsageRecordResponse]
    trends: Dict[str, float]  # Percentage changes
    projections: Dict[str, int]  # Projected usage for current period


# Billing Alerts Schemas
class BillingAlertResponse(BaseModel):
    id: int
    organization_id: int
    alert_type: str
    message: str
    is_active: bool
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# Payment Intent Schemas
class PaymentIntentResponse(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    client_secret: str
    created_at: datetime


# Subscription Update Schemas
class SubscriptionUpdateRequest(BaseModel):
    plan: Optional[PlanType] = None
    cancel_at_period_end: Optional[bool] = None


class SubscriptionUpdateResponse(BaseModel):
    subscription: SubscriptionResponse
    message: str


# Invoice Payment Schemas
class InvoicePaymentRequest(BaseModel):
    payment_method_id: str
    invoice_id: int


class InvoicePaymentResponse(BaseModel):
    success: bool
    message: str
    payment_intent_id: Optional[str] = None


# Billing Settings Schemas
class BillingSettingsResponse(BaseModel):
    organization_id: int
    auto_pay: bool
    invoice_email: Optional[str]
    billing_address: Optional[Dict[str, Any]]
    tax_settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class BillingSettingsUpdate(BaseModel):
    auto_pay: Optional[bool] = None
    invoice_email: Optional[str] = None
    billing_address: Optional[Dict[str, Any]] = None
    tax_settings: Optional[Dict[str, Any]] = None


# Webhook Event Schemas
class WebhookEventRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]
    signature: str


class WebhookEventResponse(BaseModel):
    processed: bool
    message: str
    event_id: Optional[str] = None
