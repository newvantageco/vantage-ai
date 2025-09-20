"""
Billing Service
Handles Stripe integration, subscription management, and billing operations
"""

import stripe
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.billing import Subscription, Plan, SubscriptionStatus, BillingEvent
from app.models.entities import Organization
from app.core.config import get_settings

settings = get_settings()

# Configure Stripe
stripe.api_key = settings.stripe_secret_key


class BillingService:
    """Service for billing and subscription management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_organization_subscription(self, org_id: int) -> Optional[Subscription]:
        """Get organization's current subscription"""
        return self.db.query(Subscription).filter(
            Subscription.organization_id == org_id,
            Subscription.status.in_([
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIALING,
                SubscriptionStatus.PAST_DUE
            ])
        ).first()
    
    def get_organization_plan(self, org_id: int) -> Optional[Plan]:
        """Get organization's current plan"""
        subscription = self.get_organization_subscription(org_id)
        if subscription:
            return subscription.plan
        return None
    
    async def create_checkout_session(
        self, 
        org_id: int, 
        plan_type: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Stripe checkout session for plan upgrade
        
        Args:
            org_id: Organization ID
            plan_type: Plan type (growth, pro)
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
            customer_email: Customer email (optional)
            
        Returns:
            Dictionary with checkout session URL and details
        """
        try:
            # Get organization
            org = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            
            # Get plan details
            plan = self.db.query(Plan).filter(Plan.name == plan_type).first()
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plan '{plan_type}' not found"
                )
            
            # Get or create Stripe customer
            customer_id = await self._get_or_create_stripe_customer(org, customer_email)
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'organization_id': str(org_id),
                    'plan_type': plan_type
                },
                subscription_data={
                    'metadata': {
                        'organization_id': str(org_id),
                        'plan_type': plan_type
                    }
                }
            )
            
            return {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "plan": plan_type,
                "amount": plan.price,
                "currency": plan.currency
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create checkout session: {str(e)}"
            )
    
    async def _get_or_create_stripe_customer(self, org: Organization, email: Optional[str] = None) -> str:
        """Get or create Stripe customer for organization"""
        # Check if organization already has a Stripe customer ID
        if org.stripe_customer_id:
            try:
                # Verify customer still exists in Stripe
                stripe.Customer.retrieve(org.stripe_customer_id)
                return org.stripe_customer_id
            except stripe.error.StripeError:
                # Customer doesn't exist, create new one
                pass
        
        # Create new Stripe customer
        customer_data = {
            'name': org.name,
            'metadata': {
                'organization_id': str(org.id),
                'organization_slug': org.slug
            }
        }
        
        if email:
            customer_data['email'] = email
        
        customer = stripe.Customer.create(**customer_data)
        
        # Update organization with Stripe customer ID
        org.stripe_customer_id = customer.id
        self.db.commit()
        
        return customer.id
    
    def create_portal_session(self, org_id: int, return_url: str) -> Dict[str, Any]:
        """
        Create Stripe customer portal session
        
        Args:
            org_id: Organization ID
            return_url: Return URL after portal session
            
        Returns:
            Dictionary with portal session URL
        """
        try:
            # Get organization
            org = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            
            if not org.stripe_customer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No active subscription found"
                )
            
            # Create portal session
            portal_session = stripe.billing_portal.Session.create(
                customer=org.stripe_customer_id,
                return_url=return_url
            )
            
            return {
                "portal_url": portal_session.url,
                "session_id": portal_session.id
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create portal session: {str(e)}"
            )
    
    def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Stripe webhook events
        
        Args:
            event_data: Stripe webhook event data
            
        Returns:
            Dictionary with processing result
        """
        try:
            event_type = event_data.get('type')
            
            if event_type == 'checkout.session.completed':
                return self._handle_checkout_completed(event_data)
            elif event_type == 'customer.subscription.created':
                return self._handle_subscription_created(event_data)
            elif event_type == 'customer.subscription.updated':
                return self._handle_subscription_updated(event_data)
            elif event_type == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event_data)
            elif event_type == 'invoice.payment_succeeded':
                return self._handle_payment_succeeded(event_data)
            elif event_type == 'invoice.payment_failed':
                return self._handle_payment_failed(event_data)
            else:
                return {"status": "ignored", "event_type": event_type}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _handle_checkout_completed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checkout session completed event"""
        session = event_data['data']['object']
        org_id = int(session['metadata']['organization_id'])
        plan_type = session['metadata']['plan_type']
        
        # Get organization and plan
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        plan = self.db.query(Plan).filter(Plan.name == plan_type).first()
        
        if not org or not plan:
            return {"status": "error", "error": "Organization or plan not found"}
        
        # Update organization's Stripe customer ID if not set
        if not org.stripe_customer_id:
            org.stripe_customer_id = session['customer']
            self.db.commit()
        
        return {"status": "processed", "event_type": "checkout.session.completed"}
    
    def _handle_subscription_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription created event"""
        subscription = event_data['data']['object']
        org_id = int(subscription['metadata']['organization_id'])
        plan_type = subscription['metadata']['plan_type']
        
        # Get organization and plan
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        plan = self.db.query(Plan).filter(Plan.name == plan_type).first()
        
        if not org or not plan:
            return {"status": "error", "error": "Organization or plan not found"}
        
        # Create subscription record
        subscription_record = Subscription(
            organization_id=org_id,
            stripe_subscription_id=subscription['id'],
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.fromtimestamp(subscription['current_period_start']),
            current_period_end=datetime.fromtimestamp(subscription['current_period_end']),
            stripe_customer_id=subscription['customer']
        )
        
        self.db.add(subscription_record)
        self.db.commit()
        
        # Log billing event
        self._log_billing_event(
            org_id=org_id,
            event_type="subscription_created",
            event_data={
                "subscription_id": subscription['id'],
                "plan": plan_type,
                "amount": subscription['items']['data'][0]['price']['unit_amount']
            }
        )
        
        return {"status": "processed", "event_type": "customer.subscription.created"}
    
    def _handle_subscription_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updated event"""
        subscription = event_data['data']['object']
        stripe_subscription_id = subscription['id']
        
        # Find existing subscription
        subscription_record = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if not subscription_record:
            return {"status": "error", "error": "Subscription not found"}
        
        # Update subscription status
        status_mapping = {
            'active': SubscriptionStatus.ACTIVE,
            'trialing': SubscriptionStatus.TRIALING,
            'past_due': SubscriptionStatus.PAST_DUE,
            'canceled': SubscriptionStatus.CANCELED,
            'unpaid': SubscriptionStatus.UNPAID
        }
        
        new_status = status_mapping.get(subscription['status'], SubscriptionStatus.ACTIVE)
        subscription_record.status = new_status
        subscription_record.current_period_start = datetime.fromtimestamp(subscription['current_period_start'])
        subscription_record.current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
        
        self.db.commit()
        
        # Log billing event
        self._log_billing_event(
            org_id=subscription_record.organization_id,
            event_type="subscription_updated",
            event_data={
                "subscription_id": stripe_subscription_id,
                "new_status": new_status.value,
                "old_status": subscription_record.status.value
            }
        )
        
        return {"status": "processed", "event_type": "customer.subscription.updated"}
    
    def _handle_subscription_deleted(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deleted event"""
        subscription = event_data['data']['object']
        stripe_subscription_id = subscription['id']
        
        # Find and update subscription
        subscription_record = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if subscription_record:
            subscription_record.status = SubscriptionStatus.CANCELED
            subscription_record.canceled_at = datetime.utcnow()
            self.db.commit()
            
            # Log billing event
            self._log_billing_event(
                org_id=subscription_record.organization_id,
                event_type="subscription_canceled",
                event_data={"subscription_id": stripe_subscription_id}
            )
        
        return {"status": "processed", "event_type": "customer.subscription.deleted"}
    
    def _handle_payment_succeeded(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment succeeded event"""
        invoice = event_data['data']['object']
        customer_id = invoice['customer']
        
        # Find organization by Stripe customer ID
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            # Log billing event
            self._log_billing_event(
                org_id=org.id,
                event_type="payment_succeeded",
                event_data={
                    "invoice_id": invoice['id'],
                    "amount": invoice['amount_paid'],
                    "currency": invoice['currency']
                }
            )
        
        return {"status": "processed", "event_type": "invoice.payment_succeeded"}
    
    def _handle_payment_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failed event"""
        invoice = event_data['data']['object']
        customer_id = invoice['customer']
        
        # Find organization by Stripe customer ID
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            # Log billing event
            self._log_billing_event(
                org_id=org.id,
                event_type="payment_failed",
                event_data={
                    "invoice_id": invoice['id'],
                    "amount": invoice['amount_due'],
                    "currency": invoice['currency']
                }
            )
        
        return {"status": "processed", "event_type": "invoice.payment_failed"}
    
    def _log_billing_event(self, org_id: int, event_type: str, event_data: Dict[str, Any]):
        """Log billing event for audit trail"""
        billing_event = BillingEvent(
            organization_id=org_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=datetime.utcnow()
        )
        self.db.add(billing_event)
        self.db.commit()
    
    def get_organization_usage(self, org_id: int, month: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get organization's AI usage for the month
        
        Args:
            org_id: Organization ID
            month: Month to get usage for (defaults to current month)
            
        Returns:
            Dictionary with usage statistics
        """
        if not month:
            month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate month boundaries
        if month.month == 12:
            next_month = month.replace(year=month.year + 1, month=1)
        else:
            next_month = month.replace(month=month.month + 1)
        
        # Get current subscription to determine limits
        subscription = self.get_organization_subscription(org_id)
        plan = subscription.plan if subscription else None
        
        # Get usage records for the month
        from app.models.billing import UsageRecord
        usage_record = self.db.query(UsageRecord).filter(
            UsageRecord.organization_id == org_id,
            UsageRecord.period_start >= month,
            UsageRecord.period_end < next_month
        ).first()
        
        # If no usage record exists, create one with zero usage
        if not usage_record:
            usage_record = UsageRecord(
                organization_id=org_id,
                subscription_id=subscription.id if subscription else None,
                period_start=month,
                period_end=next_month,
                posts_used=0,
                ai_requests_used=0,
                team_members_used=0,
                integrations_used=0
            )
            self.db.add(usage_record)
            self.db.commit()
        
        # Calculate usage percentages
        plan_limits = {
            "ai_requests": plan.ai_request_limit if plan else 0,
            "ai_tokens": plan.ai_token_limit if plan else 0,
            "content_posts": plan.content_post_limit if plan else 0,
            "team_members": plan.team_member_limit if plan else 0,
            "integrations": plan.integration_limit if plan else 0
        }
        
        usage_percentage = {}
        for key, limit in plan_limits.items():
            if limit > 0:
                used = getattr(usage_record, f"{key.replace('_', '_')}_used", 0)
                usage_percentage[key] = min(100, (used / limit) * 100)
            else:
                usage_percentage[key] = 0
        
        usage_data = {
            "month": month.strftime("%Y-%m"),
            "ai_requests": usage_record.ai_requests_used,
            "ai_tokens": 0,  # TODO: Implement token tracking
            "content_posts": usage_record.posts_used,
            "team_members": usage_record.team_members_used,
            "integrations": usage_record.integrations_used,
            "plan_limits": plan_limits,
            "usage_percentage": usage_percentage,
            "overage": {
                "posts": usage_record.posts_overage,
                "ai_requests": usage_record.ai_requests_overage,
                "amount": usage_record.overage_amount
            }
        }
        
        return usage_data
    
    def update_usage(self, org_id: int, usage_type: str, amount: int = 1) -> bool:
        """
        Update usage for an organization
        
        Args:
            org_id: Organization ID
            usage_type: Type of usage (ai_requests, content_posts, etc.)
            amount: Amount to add to usage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current month usage record
            now = datetime.utcnow()
            month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if month.month == 12:
                next_month = month.replace(year=month.year + 1, month=1)
            else:
                next_month = month.replace(month=month.month + 1)
            
            from app.models.billing import UsageRecord
            usage_record = self.db.query(UsageRecord).filter(
                UsageRecord.organization_id == org_id,
                UsageRecord.period_start >= month,
                UsageRecord.period_end < next_month
            ).first()
            
            if not usage_record:
                # Create new usage record
                subscription = self.get_organization_subscription(org_id)
                usage_record = UsageRecord(
                    organization_id=org_id,
                    subscription_id=subscription.id if subscription else None,
                    period_start=month,
                    period_end=next_month
                )
                self.db.add(usage_record)
            
            # Update the appropriate usage field
            field_name = f"{usage_type}_used"
            if hasattr(usage_record, field_name):
                current_usage = getattr(usage_record, field_name, 0)
                setattr(usage_record, field_name, current_usage + amount)
                
                # Check for overage
                self._check_usage_overage(usage_record, org_id)
                
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            return False
    
    def _check_usage_overage(self, usage_record, org_id: int):
        """Check if usage exceeds plan limits and calculate overage charges"""
        subscription = self.get_organization_subscription(org_id)
        if not subscription or not subscription.plan:
            return
        
        plan = subscription.plan
        overage_charges = 0
        
        # Check posts overage
        if plan.content_post_limit and usage_record.posts_used > plan.content_post_limit:
            overage = usage_record.posts_used - plan.content_post_limit
            usage_record.posts_overage = overage
            # $0.10 per post overage
            overage_charges += overage * 10
        
        # Check AI requests overage
        if plan.ai_request_limit and usage_record.ai_requests_used > plan.ai_request_limit:
            overage = usage_record.ai_requests_used - plan.ai_request_limit
            usage_record.ai_requests_overage = overage
            # $0.01 per AI request overage
            overage_charges += overage * 1
        
        usage_record.overage_amount = overage_charges
        
        # If there are overage charges, create an invoice
        if overage_charges > 0:
            self._create_overage_invoice(org_id, overage_charges)
    
    def _create_overage_invoice(self, org_id: int, amount_cents: int):
        """Create an invoice for overage charges"""
        try:
            from app.models.billing import Invoice
            from app.models.entities import Organization
            
            org = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not org or not org.stripe_customer_id:
                return
            
            # Create invoice in Stripe
            invoice = stripe.Invoice.create(
                customer=org.stripe_customer_id,
                auto_advance=True,
                collection_method='charge_automatically'
            )
            
            # Add overage line item
            stripe.InvoiceItem.create(
                customer=org.stripe_customer_id,
                invoice=invoice.id,
                amount=amount_cents,
                currency='usd',
                description='Overage charges'
            )
            
            # Finalize and send invoice
            stripe.Invoice.finalize_invoice(invoice.id)
            
            # Store invoice in database
            invoice_record = Invoice(
                organization_id=org_id,
                stripe_invoice_id=invoice.id,
                amount_due=amount_cents,
                currency='USD',
                status='open'
            )
            self.db.add(invoice_record)
            self.db.commit()
            
        except Exception as e:
            # Log error but don't fail the usage update
            pass
    
    def cancel_subscription(self, org_id: int, immediately: bool = False) -> Dict[str, Any]:
        """
        Cancel organization's subscription
        
        Args:
            org_id: Organization ID
            immediately: Whether to cancel immediately or at period end
            
        Returns:
            Dictionary with cancellation result
        """
        try:
            subscription = self.get_organization_subscription(org_id)
            if not subscription or not subscription.stripe_subscription_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active subscription found"
                )
            
            # Cancel in Stripe
            if immediately:
                stripe.Subscription.delete(subscription.stripe_subscription_id)
            else:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
            
            # Update local subscription
            subscription.status = SubscriptionStatus.CANCELED
            subscription.canceled_at = datetime.utcnow()
            if not immediately:
                subscription.cancel_at_period_end = True
            
            self.db.commit()
            
            # Log billing event
            self._log_billing_event(
                org_id=org_id,
                event_type="subscription_canceled",
                event_data={
                    "subscription_id": subscription.stripe_subscription_id,
                    "immediately": immediately
                }
            )
            
            return {
                "status": "success",
                "canceled_at": subscription.canceled_at.isoformat(),
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel subscription: {str(e)}"
            )
    
    def upgrade_subscription(self, org_id: int, new_plan_type: str) -> Dict[str, Any]:
        """
        Upgrade organization's subscription to a new plan
        
        Args:
            org_id: Organization ID
            new_plan_type: New plan type (growth, pro)
            
        Returns:
            Dictionary with upgrade result
        """
        try:
            subscription = self.get_organization_subscription(org_id)
            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active subscription found"
                )
            
            # Get new plan
            new_plan = self.db.query(Plan).filter(Plan.name == new_plan_type).first()
            if not new_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plan '{new_plan_type}' not found"
                )
            
            # Update subscription in Stripe
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[{
                    'id': subscription.stripe_subscription_id,
                    'price': new_plan.stripe_price_id
                }],
                proration_behavior='create_prorations'
            )
            
            # Update local subscription
            subscription.plan_id = new_plan.id
            self.db.commit()
            
            # Log billing event
            self._log_billing_event(
                org_id=org_id,
                event_type="subscription_upgraded",
                event_data={
                    "subscription_id": subscription.stripe_subscription_id,
                    "old_plan": subscription.plan.name,
                    "new_plan": new_plan_type
                }
            )
            
            return {
                "status": "success",
                "new_plan": new_plan_type,
                "prorated": True
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upgrade subscription: {str(e)}"
            )