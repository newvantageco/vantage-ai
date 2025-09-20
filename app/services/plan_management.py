"""
Plan Management Service
Handles subscription plan management, migrations, and feature management
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.models.billing import Plan, Subscription, SubscriptionStatus, PlanTier
from app.models.entities import Organization
from app.billing.stripe_validator import StripeOperationWrapper, StripeValidationError
from app.billing.stripe_enhanced import StripeEnhancedClient

logger = logging.getLogger(__name__)


class PlanManagementService:
    """Service for managing subscription plans and migrations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stripe_client = StripeEnhancedClient()
        self.stripe_wrapper = StripeOperationWrapper(
            validator=None,  # Will be set in __init__
            error_handler=None
        )
    
    def create_plan(
        self, 
        name: str, 
        display_name: str, 
        description: str, 
        price_cents: int, 
        currency: str = "USD",
        billing_interval: str = "month",
        features: List[str] = None,
        limits: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Create a new subscription plan
        
        Args:
            name: Plan name (e.g., "starter", "growth", "pro")
            display_name: Human-readable plan name
            description: Plan description
            price_cents: Price in cents
            currency: Currency code
            billing_interval: Billing interval (month, year)
            features: List of plan features
            limits: Plan limits (ai_requests, content_posts, etc.)
            
        Returns:
            Dictionary with created plan details
        """
        try:
            # Validate plan data
            if not name or not display_name or price_cents <= 0:
                raise ValueError("Invalid plan data")
            
            # Check if plan already exists
            existing_plan = self.db.query(Plan).filter(Plan.name == name).first()
            if existing_plan:
                raise ValueError(f"Plan '{name}' already exists")
            
            # Create Stripe product and price
            stripe_product_id = self.stripe_client.create_product(
                name=display_name,
                description=description
            )
            
            stripe_price_id = self.stripe_client.create_price(
                product_id=stripe_product_id,
                amount_cents=price_cents,
                currency=currency,
                interval=billing_interval
            )
            
            # Create plan in database
            plan = Plan(
                name=name,
                display_name=display_name,
                description=description,
                price=price_cents,
                currency=currency,
                billing_interval=billing_interval,
                stripe_price_id=stripe_price_id,
                features=features or [],
                ai_request_limit=limits.get("ai_requests") if limits else None,
                ai_token_limit=limits.get("ai_tokens") if limits else None,
                content_post_limit=limits.get("content_posts") if limits else None,
                team_member_limit=limits.get("team_members") if limits else None,
                integration_limit=limits.get("integrations") if limits else None,
                is_active=True
            )
            
            self.db.add(plan)
            self.db.commit()
            
            logger.info(f"Created plan '{name}' with Stripe price ID {stripe_price_id}")
            
            return {
                "id": plan.id,
                "name": plan.name,
                "display_name": plan.display_name,
                "price": plan.price,
                "currency": plan.currency,
                "billing_interval": plan.billing_interval,
                "stripe_price_id": plan.stripe_price_id,
                "features": plan.features,
                "limits": {
                    "ai_requests": plan.ai_request_limit,
                    "ai_tokens": plan.ai_token_limit,
                    "content_posts": plan.content_post_limit,
                    "team_members": plan.team_member_limit,
                    "integrations": plan.integration_limit
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create plan '{name}': {str(e)}")
            raise
    
    def update_plan(self, plan_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing plan
        
        Args:
            plan_id: Plan ID to update
            updates: Dictionary of fields to update
            
        Returns:
            Dictionary with updated plan details
        """
        try:
            plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                raise ValueError(f"Plan with ID {plan_id} not found")
            
            # Update allowed fields
            allowed_fields = [
                "display_name", "description", "features", 
                "ai_request_limit", "ai_token_limit", "content_post_limit",
                "team_member_limit", "integration_limit", "is_active"
            ]
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(plan, field):
                    setattr(plan, field, value)
            
            plan.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated plan '{plan.name}'")
            
            return {
                "id": plan.id,
                "name": plan.name,
                "display_name": plan.display_name,
                "price": plan.price,
                "currency": plan.currency,
                "billing_interval": plan.billing_interval,
                "features": plan.features,
                "limits": {
                    "ai_requests": plan.ai_request_limit,
                    "ai_tokens": plan.ai_token_limit,
                    "content_posts": plan.content_post_limit,
                    "team_members": plan.team_member_limit,
                    "integrations": plan.integration_limit
                },
                "is_active": plan.is_active
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update plan {plan_id}: {str(e)}")
            raise
    
    def deactivate_plan(self, plan_id: int) -> bool:
        """
        Deactivate a plan (soft delete)
        
        Args:
            plan_id: Plan ID to deactivate
            
        Returns:
            True if successful
        """
        try:
            plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                raise ValueError(f"Plan with ID {plan_id} not found")
            
            # Check if plan has active subscriptions
            active_subscriptions = self.db.query(Subscription).filter(
                and_(
                    Subscription.plan_id == plan_id,
                    Subscription.status.in_(["active", "trialing"])
                )
            ).count()
            
            if active_subscriptions > 0:
                raise ValueError(f"Cannot deactivate plan with {active_subscriptions} active subscriptions")
            
            plan.is_active = False
            plan.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deactivated plan '{plan.name}'")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to deactivate plan {plan_id}: {str(e)}")
            raise
    
    def get_available_plans(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all available plans
        
        Args:
            include_inactive: Whether to include inactive plans
            
        Returns:
            List of plan dictionaries
        """
        query = self.db.query(Plan)
        if not include_inactive:
            query = query.filter(Plan.is_active == True)
        
        plans = query.order_by(Plan.price).all()
        
        return [
            {
                "id": plan.id,
                "name": plan.name,
                "display_name": plan.display_name,
                "description": plan.description,
                "price": plan.price,
                "currency": plan.currency,
                "billing_interval": plan.billing_interval,
                "stripe_price_id": plan.stripe_price_id,
                "features": plan.features,
                "limits": {
                    "ai_requests": plan.ai_request_limit,
                    "ai_tokens": plan.ai_token_limit,
                    "content_posts": plan.content_post_limit,
                    "team_members": plan.team_member_limit,
                    "integrations": plan.integration_limit
                },
                "is_active": plan.is_active,
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
            }
            for plan in plans
        ]
    
    def migrate_subscription(
        self, 
        subscription_id: int, 
        new_plan_id: int, 
        proration_behavior: str = "create_prorations"
    ) -> Dict[str, Any]:
        """
        Migrate a subscription to a new plan
        
        Args:
            subscription_id: Subscription ID to migrate
            new_plan_id: New plan ID
            proration_behavior: How to handle proration (create_prorations, none, always_invoice)
            
        Returns:
            Dictionary with migration result
        """
        try:
            # Get subscription and new plan
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            
            new_plan = self.db.query(Plan).filter(Plan.id == new_plan_id).first()
            
            if not subscription:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            if not new_plan:
                raise ValueError(f"Plan {new_plan_id} not found")
            
            if not new_plan.is_active:
                raise ValueError(f"Plan '{new_plan.name}' is not active")
            
            # Update subscription in Stripe
            stripe_subscription = self.stripe_client.update_subscription(
                subscription_id=subscription.stripe_subscription_id,
                price_id=new_plan.stripe_price_id,
                proration_behavior=proration_behavior
            )
            
            # Update local subscription
            old_plan_id = subscription.plan_id
            subscription.plan_id = new_plan_id
            subscription.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Migrated subscription {subscription_id} from plan {old_plan_id} to {new_plan_id}")
            
            return {
                "success": True,
                "subscription_id": subscription_id,
                "old_plan_id": old_plan_id,
                "new_plan_id": new_plan_id,
                "proration_behavior": proration_behavior,
                "stripe_subscription_id": stripe_subscription["id"]
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to migrate subscription {subscription_id}: {str(e)}")
            raise
    
    def get_migration_options(self, current_plan_id: int) -> List[Dict[str, Any]]:
        """
        Get available migration options for a plan
        
        Args:
            current_plan_id: Current plan ID
            
        Returns:
            List of migration options
        """
        current_plan = self.db.query(Plan).filter(Plan.id == current_plan_id).first()
        if not current_plan:
            return []
        
        # Get all other active plans
        other_plans = self.db.query(Plan).filter(
            and_(
                Plan.id != current_plan_id,
                Plan.is_active == True
            )
        ).order_by(Plan.price).all()
        
        migration_options = []
        
        for plan in other_plans:
            # Determine migration type
            if plan.price > current_plan.price:
                migration_type = "upgrade"
                proration_behavior = "create_prorations"
            elif plan.price < current_plan.price:
                migration_type = "downgrade"
                proration_behavior = "none"  # No proration for downgrades
            else:
                migration_type = "lateral"
                proration_behavior = "none"
            
            migration_options.append({
                "plan_id": plan.id,
                "plan_name": plan.name,
                "display_name": plan.display_name,
                "price": plan.price,
                "currency": plan.currency,
                "billing_interval": plan.billing_interval,
                "migration_type": migration_type,
                "proration_behavior": proration_behavior,
                "price_difference": plan.price - current_plan.price,
                "features": plan.features,
                "limits": {
                    "ai_requests": plan.ai_request_limit,
                    "ai_tokens": plan.ai_token_limit,
                    "content_posts": plan.content_post_limit,
                    "team_members": plan.team_member_limit,
                    "integrations": plan.integration_limit
                }
            })
        
        return migration_options
    
    def get_plan_usage_stats(self, plan_id: int) -> Dict[str, Any]:
        """
        Get usage statistics for a plan
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Dictionary with usage statistics
        """
        plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        # Get active subscriptions for this plan
        active_subscriptions = self.db.query(Subscription).filter(
            and_(
                Subscription.plan_id == plan_id,
                Subscription.status.in_(["active", "trialing"])
            )
        ).all()
        
        # Get total revenue from this plan
        total_revenue = sum(sub.amount for sub in active_subscriptions)
        
        # Get subscription count by status
        status_counts = {}
        for status in SubscriptionStatus:
            count = self.db.query(Subscription).filter(
                and_(
                    Subscription.plan_id == plan_id,
                    Subscription.status == status
                )
            ).count()
            status_counts[status.value] = count
        
        return {
            "plan_id": plan_id,
            "plan_name": plan.name,
            "display_name": plan.display_name,
            "active_subscriptions": len(active_subscriptions),
            "total_revenue": total_revenue,
            "status_breakdown": status_counts,
            "average_revenue_per_subscription": total_revenue / len(active_subscriptions) if active_subscriptions else 0
        }
    
    def sync_plans_with_stripe(self) -> Dict[str, Any]:
        """
        Sync local plans with Stripe products and prices
        
        Returns:
            Dictionary with sync results
        """
        try:
            sync_results = {
                "created": [],
                "updated": [],
                "errors": []
            }
            
            # Get all active plans
            plans = self.db.query(Plan).filter(Plan.is_active == True).all()
            
            for plan in plans:
                try:
                    # Check if Stripe price exists
                    if plan.stripe_price_id:
                        try:
                            stripe.Price.retrieve(plan.stripe_price_id)
                            # Price exists, no action needed
                            continue
                        except stripe.error.InvalidRequestError:
                            # Price doesn't exist, create new one
                            pass
                    
                    # Create Stripe product and price
                    stripe_product_id = self.stripe_client.create_product(
                        name=plan.display_name,
                        description=plan.description
                    )
                    
                    stripe_price_id = self.stripe_client.create_price(
                        product_id=stripe_product_id,
                        amount_cents=plan.price,
                        currency=plan.currency,
                        interval=plan.billing_interval
                    )
                    
                    # Update plan with new Stripe IDs
                    plan.stripe_price_id = stripe_price_id
                    plan.updated_at = datetime.utcnow()
                    
                    sync_results["created"].append({
                        "plan_id": plan.id,
                        "plan_name": plan.name,
                        "stripe_price_id": stripe_price_id
                    })
                    
                except Exception as e:
                    sync_results["errors"].append({
                        "plan_id": plan.id,
                        "plan_name": plan.name,
                        "error": str(e)
                    })
            
            self.db.commit()
            
            logger.info(f"Synced {len(plans)} plans with Stripe")
            
            return sync_results
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to sync plans with Stripe: {str(e)}")
            raise
