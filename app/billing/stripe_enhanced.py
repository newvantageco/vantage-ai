import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.core.config import get_settings
from app.models.billing import OrganizationBilling, Coupon, BillingHistory, PlanTier, BillingStatus

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = get_settings().stripe_secret_key


class StripeEnhancedClient:
    """Enhanced Stripe client for billing operations."""
    
    def __init__(self):
        self.webhook_secret = get_settings().stripe_webhook_secret
    
    def create_customer(self, org_id: str, email: str, name: str) -> str:
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "org_id": org_id
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise
    
    def create_subscription(
        self, 
        customer_id: str, 
        price_id: str, 
        coupon_id: Optional[str] = None,
        trial_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a Stripe subscription."""
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"]
            }
            
            if coupon_id:
                subscription_data["coupon"] = coupon_id
            
            if trial_days:
                subscription_data["trial_period_days"] = trial_days
            
            subscription = stripe.Subscription.create(**subscription_data)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe subscription: {e}")
            raise
    
    def create_price(
        self, 
        product_id: str, 
        amount_cents: int, 
        currency: str = "usd",
        interval: str = "month"
    ) -> str:
        """Create a Stripe price."""
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_cents,
                currency=currency,
                recurring={"interval": interval}
            )
            return price.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe price: {e}")
            raise
    
    def create_product(self, name: str, description: str) -> str:
        """Create a Stripe product."""
        try:
            product = stripe.Product.create(
                name=name,
                description=description
            )
            return product.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe product: {e}")
            raise
    
    def create_coupon(
        self, 
        code: str, 
        discount_type: str, 
        discount_value: int,
        duration: str = "once",
        max_redemptions: Optional[int] = None,
        redeem_by: Optional[datetime] = None
    ) -> str:
        """Create a Stripe coupon."""
        try:
            coupon_data = {
                "id": code,
                "duration": duration
            }
            
            if discount_type == "percent":
                coupon_data["percent_off"] = discount_value
            else:
                coupon_data["amount_off"] = discount_value
                coupon_data["currency"] = "usd"
            
            if max_redemptions:
                coupon_data["max_redemptions"] = max_redemptions
            
            if redeem_by:
                coupon_data["redeem_by"] = int(redeem_by.timestamp())
            
            coupon = stripe.Coupon.create(**coupon_data)
            return coupon.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe coupon: {e}")
            raise
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get a Stripe subscription."""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe subscription: {e}")
            raise
    
    def cancel_subscription(self, subscription_id: str, immediately: bool = False) -> Dict[str, Any]:
        """Cancel a Stripe subscription."""
        try:
            if immediately:
                return stripe.Subscription.delete(subscription_id)
            else:
                return stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel Stripe subscription: {e}")
            raise
    
    def update_subscription(
        self, 
        subscription_id: str, 
        price_id: str,
        proration_behavior: str = "create_prorations"
    ) -> Dict[str, Any]:
        """Update a Stripe subscription."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0]["id"],
                    "price": price_id
                }],
                proration_behavior=proration_behavior
            )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update Stripe subscription: {e}")
            raise
    
    def create_payment_intent(
        self, 
        amount_cents: int, 
        customer_id: str,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a payment intent for one-time payments."""
        try:
            intent_data = {
                "amount": amount_cents,
                "currency": currency,
                "customer": customer_id,
                "automatic_payment_methods": {"enabled": True}
            }
            
            if metadata:
                intent_data["metadata"] = metadata
            
            return stripe.PaymentIntent.create(**intent_data)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise
    
    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        coupon_id: Optional[str] = None,
        trial_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a Stripe checkout session."""
        try:
            session_data = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [{
                    "price": price_id,
                    "quantity": 1
                }],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url
            }
            
            if coupon_id:
                session_data["discounts"] = [{"coupon": coupon_id}]
            
            if trial_days:
                session_data["subscription_data"] = {
                    "trial_period_days": trial_days
                }
            
            return stripe.checkout.Session.create(**session_data)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get a Stripe customer."""
        try:
            return stripe.Customer.retrieve(customer_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe customer: {e}")
            raise
    
    def list_customer_subscriptions(self, customer_id: str) -> List[Dict[str, Any]]:
        """List subscriptions for a customer."""
        try:
            subscriptions = stripe.Subscription.list(customer=customer_id)
            return subscriptions.data
        except stripe.error.StripeError as e:
            logger.error(f"Failed to list customer subscriptions: {e}")
            raise
    
    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Construct and verify a webhook event."""
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise


class BillingPlanManager:
    """Manager for billing plans and pricing."""
    
    def __init__(self, stripe_client: StripeEnhancedClient):
        self.stripe = stripe_client
        self.plan_configs = {
            PlanTier.STARTER: {
                "name": "Starter",
                "description": "Perfect for small businesses getting started",
                "price_cents": 0,
                "features": [
                    "50 posts per month",
                    "3 social channels",
                    "2 team members",
                    "5 campaigns",
                    "100 content items",
                    "200 AI generations"
                ]
            },
            PlanTier.GROWTH: {
                "name": "Growth",
                "description": "For growing businesses that need more reach",
                "price_cents": 2900,  # $29
                "features": [
                    "200 posts per month",
                    "10 social channels",
                    "5 team members",
                    "20 campaigns",
                    "500 content items",
                    "1000 AI generations"
                ]
            },
            PlanTier.PRO: {
                "name": "Pro",
                "description": "For established businesses with high volume needs",
                "price_cents": 9900,  # $99
                "features": [
                    "1000 posts per month",
                    "50 social channels",
                    "25 team members",
                    "100 campaigns",
                    "2500 content items",
                    "5000 AI generations"
                ]
            }
        }
    
    def get_plan_config(self, plan: PlanTier) -> Dict[str, Any]:
        """Get configuration for a plan."""
        return self.plan_configs.get(plan, {})
    
    def create_stripe_products_and_prices(self) -> Dict[PlanTier, str]:
        """Create Stripe products and prices for all plans."""
        price_ids = {}
        
        for plan, config in self.plan_configs.items():
            if config["price_cents"] > 0:  # Only create paid plans
                # Create product
                product_id = self.stripe.create_product(
                    name=config["name"],
                    description=config["description"]
                )
                
                # Create price
                price_id = self.stripe.create_price(
                    product_id=product_id,
                    amount_cents=config["price_cents"],
                    currency="usd",
                    interval="month"
                )
                
                price_ids[plan] = price_id
        
        return price_ids
    
    def sync_coupons_to_stripe(self, coupons: List[Coupon]) -> Dict[str, str]:
        """Sync local coupons to Stripe."""
        stripe_coupon_ids = {}
        
        for coupon in coupons:
            if coupon.is_active and coupon.is_valid():
                try:
                    stripe_coupon_id = self.stripe.create_coupon(
                        code=coupon.code,
                        discount_type=coupon.discount_type,
                        discount_value=coupon.discount_value,
                        duration="once",
                        max_redemptions=coupon.max_uses,
                        redeem_by=coupon.valid_until
                    )
                    stripe_coupon_ids[coupon.code] = stripe_coupon_id
                except Exception as e:
                    logger.error(f"Failed to sync coupon {coupon.code} to Stripe: {e}")
        
        return stripe_coupon_ids


# Global instances
stripe_client = StripeEnhancedClient()
billing_plan_manager = BillingPlanManager(stripe_client)
