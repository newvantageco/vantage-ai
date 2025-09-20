"""
Enhanced Stripe Client with Clean Configuration

This client uses the new Pydantic-based configuration and provides
a clean interface for Stripe operations.
"""

import stripe
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.billing.stripe_config import get_stripe, get_webhook_secret, is_dry_run, get_price_id

logger = logging.getLogger(__name__)


class StripeClientEnhanced:
    """Enhanced Stripe client with clean configuration."""
    
    def __init__(self):
        self._stripe = get_stripe()
        self._webhook_secret = get_webhook_secret()
        self._dry_run = is_dry_run()
    
    def create_checkout_session(
        self, 
        price_id: str, 
        success_url: str, 
        cancel_url: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a Stripe checkout session."""
        if self._dry_run:
            logger.info(f"DRY RUN: Would create checkout session for price {price_id}")
            return {
                "id": "cs_dry_run",
                "url": f"{success_url}?dry_run=true"
            }
        
        try:
            session_data = {
                "mode": "subscription",
                "line_items": [{"price": price_id, "quantity": 1}],
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
            
            if customer_email:
                session_data["customer_email"] = customer_email
            
            if metadata:
                session_data["metadata"] = metadata
            
            session = self._stripe.checkout.Session.create(**session_data)
            return {"id": session["id"], "url": session["url"]}
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise
    
    def create_customer(
        self, 
        email: str, 
        name: str, 
        org_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a Stripe customer."""
        if self._dry_run:
            logger.info(f"DRY RUN: Would create customer for {email}")
            return {"id": "cus_dry_run"}
        
        try:
            customer_data = {
                "email": email,
                "name": name,
                "metadata": {"org_id": org_id}
            }
            
            if metadata:
                customer_data["metadata"].update(metadata)
            
            customer = self._stripe.Customer.create(**customer_data)
            return {"id": customer["id"]}
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create customer: {e}")
            raise
    
    def create_portal_session(self, customer_id: str, return_url: str) -> Dict[str, Any]:
        """Create a Stripe billing portal session."""
        if self._dry_run:
            logger.info(f"DRY RUN: Would create portal session for customer {customer_id}")
            return {"url": f"{return_url}?dry_run=true"}
        
        try:
            session = self._stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return {"url": session["url"]}
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create portal session: {e}")
            raise
    
    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Any:
        """Construct webhook event with proper signature verification."""
        try:
            return self._stripe.Webhook.construct_event(
                payload, sig_header, self._webhook_secret
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to construct webhook event: {e}")
            raise
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details."""
        if self._dry_run:
            logger.info(f"DRY RUN: Would retrieve subscription {subscription_id}")
            return {
                "id": subscription_id,
                "status": "active",
                "current_period_start": int(datetime.now().timestamp()),
                "current_period_end": int(datetime.now().timestamp()) + 2592000,  # 30 days
            }
        
        try:
            subscription = self._stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription["id"],
                "status": subscription["status"],
                "current_period_start": subscription["current_period_start"],
                "current_period_end": subscription["current_period_end"],
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription: {e}")
            raise
    
    def get_price_id_for_plan(self, plan_type: str) -> str:
        """Get price ID for a plan type."""
        return get_price_id(plan_type)
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription."""
        if self._dry_run:
            logger.info(f"DRY RUN: Would cancel subscription {subscription_id}")
            return {"id": subscription_id, "status": "canceled"}
        
        try:
            subscription = self._stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return {
                "id": subscription["id"],
                "status": subscription["status"],
                "cancel_at_period_end": subscription["cancel_at_period_end"]
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise


# Global client instance
def get_stripe_client() -> StripeClientEnhanced:
    """Get the global Stripe client instance."""
    return StripeClientEnhanced()


# Backward compatibility functions
def create_checkout_session(price_id: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    client = get_stripe_client()
    return client.create_checkout_session(price_id, success_url, cancel_url)


def create_customer(email: str, name: str, org_id: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    client = get_stripe_client()
    return client.create_customer(email, name, org_id)


def create_portal_session(customer_id: str, return_url: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    client = get_stripe_client()
    return client.create_portal_session(customer_id, return_url)
