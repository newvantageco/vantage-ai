# pyright: reportMissingImports=false
from __future__ import annotations
import os
from typing import Any, Optional

def _load_stripe() -> Any:
    try:
        import stripe  # type: ignore
        return stripe
    except Exception as e:
        raise RuntimeError(
            "Stripe SDK not available. Activate your venv and install:\n"
            "  python -m venv .venv && source .venv/bin/activate && pip install 'stripe>=9,<11'"
        ) from e

class StripeClient:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self._stripe = _load_stripe()
        key = api_key or os.getenv("STRIPE_SECRET_KEY")
        if not key:
            raise RuntimeError("STRIPE_SECRET_KEY is missing. Set it in Secrets Admin or .env.")
        self._stripe.api_key = key
        self._stripe.set_app_info("Vantage AI", version="0.1.0")

    def create_checkout_session(self, price_id: str, success_url: str, cancel_url: str) -> dict[str, Any]:
        s = self._stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return {"id": s["id"], "url": s["url"]}

    def create_customer(self, email: str, name: str, org_id: str) -> dict[str, Any]:
        customer = self._stripe.Customer.create(
            email=email,
            name=name,
            metadata={"org_id": org_id}
        )
        return {"id": customer["id"]}

    def create_portal_session(self, customer_id: str, return_url: str) -> dict[str, Any]:
        session = self._stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return {"url": session["url"]}

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Any:
        return self._stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET", "")
        )

    def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        subscription = self._stripe.Subscription.retrieve(subscription_id)
        return {
            "id": subscription["id"],
            "status": subscription["status"],
            "current_period_start": subscription["current_period_start"],
            "current_period_end": subscription["current_period_end"],
        }

# Functional helpers (backwards compatible)
def get_client() -> StripeClient:
    return StripeClient()

def get_stripe() -> StripeClient:
    """Alias for get_client() for consistency with imports"""
    return StripeClient()

def create_checkout_session(price_id: str, success_url: str, cancel_url: str) -> dict[str, Any]:
    return get_client().create_checkout_session(price_id, success_url, cancel_url)

# Define PlanTier enum for compatibility
from enum import Enum

class PlanTier(str, Enum):
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"