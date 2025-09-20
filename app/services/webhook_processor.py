"""
Webhook Processing Service
Handles Stripe webhook events with retry logic and error handling
"""

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
import stripe

from app.models.billing import BillingEvent, Subscription, Invoice, Organization
from app.billing.stripe_validator import StripeValidationError, StripeErrorHandler
from app.services.billing_service import BillingService

logger = logging.getLogger(__name__)


class WebhookProcessingResult:
    """Result of webhook processing"""
    
    def __init__(self, success: bool, event_type: str, error: Optional[str] = None, retry_after: Optional[int] = None):
        self.success = success
        self.event_type = event_type
        self.error = error
        self.retry_after = retry_after
        self.processed_at = datetime.utcnow()


class WebhookProcessor:
    """Processes Stripe webhook events with retry logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.billing_service = BillingService(db)
        self.error_handler = StripeErrorHandler()
        self.max_retries = 3
        self.retry_delays = [60, 300, 900]  # 1 min, 5 min, 15 min
    
    def process_webhook_event(self, event_data: Dict[str, Any]) -> WebhookProcessingResult:
        """
        Process a Stripe webhook event
        
        Args:
            event_data: Stripe webhook event data
            
        Returns:
            WebhookProcessingResult
        """
        event_type = event_data.get("type")
        event_id = event_data.get("id")
        
        logger.info(f"Processing webhook event: {event_type} (ID: {event_id})")
        
        try:
            # Check if event was already processed
            existing_event = self.db.query(BillingEvent).filter(
                BillingEvent.stripe_event_id == event_id
            ).first()
            
            if existing_event and existing_event.processed:
                logger.info(f"Event {event_id} already processed, skipping")
                return WebhookProcessingResult(
                    success=True,
                    event_type=event_type,
                    error="Already processed"
                )
            
            # Process the event
            result = self._process_event_by_type(event_data)
            
            # Log the event
            self._log_webhook_event(event_data, success=True)
            
            logger.info(f"Successfully processed webhook event: {event_type}")
            return WebhookProcessingResult(
                success=True,
                event_type=event_type
            )
            
        except Exception as e:
            logger.error(f"Failed to process webhook event {event_type}: {str(e)}")
            
            # Log the error
            self._log_webhook_event(event_data, success=False, error=str(e))
            
            # Determine if we should retry
            retry_after = self._should_retry(event_data, str(e))
            
            return WebhookProcessingResult(
                success=False,
                event_type=event_type,
                error=str(e),
                retry_after=retry_after
            )
    
    def _process_event_by_type(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process event based on its type"""
        event_type = event_data.get("type")
        
        # Map event types to handlers
        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
            "invoice.payment_action_required": self._handle_payment_action_required,
            "customer.subscription.trial_will_end": self._handle_trial_will_end,
            "customer.subscription.trial_ended": self._handle_trial_ended,
            "payment_method.attached": self._handle_payment_method_attached,
            "payment_method.detached": self._handle_payment_method_detached,
        }
        
        handler = handlers.get(event_type)
        if not handler:
            logger.warning(f"No handler for event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}
        
        return handler(event_data)
    
    def _handle_checkout_completed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checkout session completed event"""
        session = event_data["data"]["object"]
        org_id = int(session["metadata"]["organization_id"])
        plan_type = session["metadata"]["plan_type"]
        
        # Get organization and update Stripe customer ID
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if org and not org.stripe_customer_id:
            org.stripe_customer_id = session["customer"]
            self.db.commit()
        
        return {"status": "processed", "event_type": "checkout.session.completed"}
    
    def _handle_subscription_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription created event"""
        subscription = event_data["data"]["object"]
        org_id = int(subscription["metadata"]["organization_id"])
        plan_type = subscription["metadata"]["plan_type"]
        
        # Get organization and plan
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")
        
        # Update organization's Stripe customer ID
        if not org.stripe_customer_id:
            org.stripe_customer_id = subscription["customer"]
            self.db.commit()
        
        # Get plan
        from app.models.billing import Plan
        plan = self.db.query(Plan).filter(Plan.name == plan_type).first()
        if not plan:
            raise ValueError(f"Plan '{plan_type}' not found")
        
        # Create subscription record
        subscription_record = Subscription(
            organization_id=org_id,
            stripe_subscription_id=subscription["id"],
            stripe_customer_id=subscription["customer"],
            plan_id=plan.id,
            status=subscription["status"],
            current_period_start=datetime.fromtimestamp(subscription["current_period_start"]),
            current_period_end=datetime.fromtimestamp(subscription["current_period_end"]),
            amount=subscription["items"]["data"][0]["price"]["unit_amount"],
            currency=subscription["currency"]
        )
        
        self.db.add(subscription_record)
        self.db.commit()
        
        return {"status": "processed", "event_type": "customer.subscription.created"}
    
    def _handle_subscription_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updated event"""
        subscription = event_data["data"]["object"]
        stripe_subscription_id = subscription["id"]
        
        # Find existing subscription
        subscription_record = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if not subscription_record:
            raise ValueError(f"Subscription {stripe_subscription_id} not found")
        
        # Update subscription
        subscription_record.status = subscription["status"]
        subscription_record.current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
        subscription_record.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
        subscription_record.cancel_at_period_end = subscription.get("cancel_at_period_end", False)
        
        if subscription.get("canceled_at"):
            subscription_record.canceled_at = datetime.fromtimestamp(subscription["canceled_at"])
        
        self.db.commit()
        
        return {"status": "processed", "event_type": "customer.subscription.updated"}
    
    def _handle_subscription_deleted(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deleted event"""
        subscription = event_data["data"]["object"]
        stripe_subscription_id = subscription["id"]
        
        # Find and update subscription
        subscription_record = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if subscription_record:
            subscription_record.status = "canceled"
            subscription_record.canceled_at = datetime.utcnow()
            self.db.commit()
        
        return {"status": "processed", "event_type": "customer.subscription.deleted"}
    
    def _handle_payment_succeeded(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment succeeded event"""
        invoice = event_data["data"]["object"]
        customer_id = invoice["customer"]
        
        # Find organization by Stripe customer ID
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            # Create invoice record
            invoice_record = Invoice(
                organization_id=org.id,
                stripe_invoice_id=invoice["id"],
                amount_due=invoice["amount_due"],
                amount_paid=invoice["amount_paid"],
                currency=invoice["currency"],
                status=invoice["status"],
                paid=True,
                paid_at=datetime.fromtimestamp(invoice["created"]),
                invoice_pdf_url=invoice.get("invoice_pdf")
            )
            
            self.db.add(invoice_record)
            self.db.commit()
        
        return {"status": "processed", "event_type": "invoice.payment_succeeded"}
    
    def _handle_payment_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failed event"""
        invoice = event_data["data"]["object"]
        customer_id = invoice["customer"]
        
        # Find organization by Stripe customer ID
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            # Update subscription status to past_due
            subscription = self.db.query(Subscription).filter(
                Subscription.organization_id == org.id,
                Subscription.status.in_(["active", "trialing"])
            ).first()
            
            if subscription:
                subscription.status = "past_due"
                self.db.commit()
        
        return {"status": "processed", "event_type": "invoice.payment_failed"}
    
    def _handle_payment_action_required(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment action required event"""
        invoice = event_data["data"]["object"]
        customer_id = invoice["customer"]
        
        # Find organization and update subscription status
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            subscription = self.db.query(Subscription).filter(
                Subscription.organization_id == org.id,
                Subscription.status.in_(["active", "trialing"])
            ).first()
            
            if subscription:
                subscription.status = "incomplete"
                self.db.commit()
        
        return {"status": "processed", "event_type": "invoice.payment_action_required"}
    
    def _handle_trial_will_end(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trial will end event"""
        subscription = event_data["data"]["object"]
        customer_id = subscription["customer"]
        
        # Find organization and send notification
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            # TODO: Send trial ending notification
            logger.info(f"Trial ending for organization {org.id}")
        
        return {"status": "processed", "event_type": "customer.subscription.trial_will_end"}
    
    def _handle_trial_ended(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trial ended event"""
        subscription = event_data["data"]["object"]
        customer_id = subscription["customer"]
        
        # Find organization and update subscription
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            subscription_record = self.db.query(Subscription).filter(
                Subscription.organization_id == org.id,
                Subscription.stripe_subscription_id == subscription["id"]
            ).first()
            
            if subscription_record:
                subscription_record.status = subscription["status"]
                self.db.commit()
        
        return {"status": "processed", "event_type": "customer.subscription.trial_ended"}
    
    def _handle_payment_method_attached(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment method attached event"""
        payment_method = event_data["data"]["object"]
        customer_id = payment_method["customer"]
        
        # Find organization and update payment method
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            # TODO: Update payment method in database
            logger.info(f"Payment method attached for organization {org.id}")
        
        return {"status": "processed", "event_type": "payment_method.attached"}
    
    def _handle_payment_method_detached(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment method detached event"""
        payment_method = event_data["data"]["object"]
        customer_id = payment_method["customer"]
        
        # Find organization and update payment method
        org = self.db.query(Organization).filter(
            Organization.stripe_customer_id == customer_id
        ).first()
        
        if org:
            # TODO: Update payment method in database
            logger.info(f"Payment method detached for organization {org.id}")
        
        return {"status": "processed", "event_type": "payment_method.detached"}
    
    def _log_webhook_event(self, event_data: Dict[str, Any], success: bool, error: Optional[str] = None):
        """Log webhook event to database"""
        try:
            billing_event = BillingEvent(
                organization_id=0,  # Will be updated if we can determine it
                event_type=event_data.get("type"),
                stripe_event_id=event_data.get("id"),
                data=event_data,
                processed=success,
                processed_at=datetime.utcnow() if success else None,
                error_message=error
            )
            
            # Try to determine organization ID
            if "data" in event_data and "object" in event_data["data"]:
                obj = event_data["data"]["object"]
                if "customer" in obj:
                    org = self.db.query(Organization).filter(
                        Organization.stripe_customer_id == obj["customer"]
                    ).first()
                    if org:
                        billing_event.organization_id = org.id
            
            self.db.add(billing_event)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log webhook event: {str(e)}")
    
    def _should_retry(self, event_data: Dict[str, Any], error: str) -> Optional[int]:
        """Determine if event should be retried and when"""
        event_type = event_data.get("type")
        
        # Don't retry certain event types
        non_retryable_events = [
            "customer.subscription.deleted",
            "invoice.payment_succeeded",
            "invoice.payment_failed"
        ]
        
        if event_type in non_retryable_events:
            return None
        
        # Check if we've already retried this event
        event_id = event_data.get("id")
        retry_count = self.db.query(BillingEvent).filter(
            and_(
                BillingEvent.stripe_event_id == event_id,
                BillingEvent.processed == False
            )
        ).count()
        
        if retry_count >= self.max_retries:
            return None
        
        # Return retry delay
        return self.retry_delays[min(retry_count, len(self.retry_delays) - 1)]
    
    def retry_failed_events(self) -> Dict[str, Any]:
        """Retry failed webhook events"""
        try:
            # Find events that failed and should be retried
            failed_events = self.db.query(BillingEvent).filter(
                and_(
                    BillingEvent.processed == False,
                    BillingEvent.created_at > datetime.utcnow() - timedelta(hours=24)
                )
            ).all()
            
            retry_results = {
                "total": len(failed_events),
                "successful": 0,
                "failed": 0,
                "skipped": 0
            }
            
            for event in failed_events:
                try:
                    # Check if enough time has passed since last attempt
                    if event.processed_at:
                        time_since_last_attempt = datetime.utcnow() - event.processed_at
                        if time_since_last_attempt.total_seconds() < 300:  # 5 minutes
                            retry_results["skipped"] += 1
                            continue
                    
                    # Retry the event
                    result = self.process_webhook_event(event.data)
                    
                    if result.success:
                        retry_results["successful"] += 1
                    else:
                        retry_results["failed"] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to retry event {event.stripe_event_id}: {str(e)}")
                    retry_results["failed"] += 1
            
            logger.info(f"Retry completed: {retry_results}")
            return retry_results
            
        except Exception as e:
            logger.error(f"Failed to retry events: {str(e)}")
            raise
    
    def get_webhook_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get webhook processing statistics"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        total_events = self.db.query(BillingEvent).filter(
            BillingEvent.created_at >= since
        ).count()
        
        successful_events = self.db.query(BillingEvent).filter(
            and_(
                BillingEvent.created_at >= since,
                BillingEvent.processed == True
            )
        ).count()
        
        failed_events = self.db.query(BillingEvent).filter(
            and_(
                BillingEvent.created_at >= since,
                BillingEvent.processed == False
            )
        ).count()
        
        # Get events by type
        events_by_type = {}
        for event in self.db.query(BillingEvent).filter(
            BillingEvent.created_at >= since
        ).all():
            event_type = event.event_type
            if event_type not in events_by_type:
                events_by_type[event_type] = {"total": 0, "successful": 0, "failed": 0}
            
            events_by_type[event_type]["total"] += 1
            if event.processed:
                events_by_type[event_type]["successful"] += 1
            else:
                events_by_type[event_type]["failed"] += 1
        
        return {
            "period_hours": hours,
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": (successful_events / total_events * 100) if total_events > 0 else 0,
            "events_by_type": events_by_type
        }
