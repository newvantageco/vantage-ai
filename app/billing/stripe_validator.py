"""
Stripe Validation and Error Handling
Provides comprehensive validation and error handling for Stripe operations
"""

import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class StripeErrorType(str, Enum):
    """Types of Stripe errors"""
    CARD_ERROR = "card_error"
    INVALID_REQUEST_ERROR = "invalid_request_error"
    API_ERROR = "api_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_ERROR = "permission_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    VALIDATION_ERROR = "validation_error"
    CONNECTION_ERROR = "connection_error"
    UNKNOWN_ERROR = "unknown_error"


class StripeValidationError(Exception):
    """Custom exception for Stripe validation errors"""
    def __init__(self, message: str, error_type: StripeErrorType, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


class StripeValidator:
    """Validator for Stripe operations and data"""
    
    @staticmethod
    def validate_price_id(price_id: str) -> bool:
        """Validate Stripe price ID format"""
        if not price_id:
            raise StripeValidationError(
                "Price ID is required",
                StripeErrorType.VALIDATION_ERROR
            )
        
        if not price_id.startswith("price_"):
            raise StripeValidationError(
                "Invalid price ID format",
                StripeErrorType.VALIDATION_ERROR,
                {"price_id": price_id}
            )
        
        return True
    
    @staticmethod
    def validate_customer_id(customer_id: str) -> bool:
        """Validate Stripe customer ID format"""
        if not customer_id:
            raise StripeValidationError(
                "Customer ID is required",
                StripeErrorType.VALIDATION_ERROR
            )
        
        if not customer_id.startswith("cus_"):
            raise StripeValidationError(
                "Invalid customer ID format",
                StripeErrorType.VALIDATION_ERROR,
                {"customer_id": customer_id}
            )
        
        return True
    
    @staticmethod
    def validate_subscription_id(subscription_id: str) -> bool:
        """Validate Stripe subscription ID format"""
        if not subscription_id:
            raise StripeValidationError(
                "Subscription ID is required",
                StripeErrorType.VALIDATION_ERROR
            )
        
        if not subscription_id.startswith("sub_"):
            raise StripeValidationError(
                "Invalid subscription ID format",
                StripeErrorType.VALIDATION_ERROR,
                {"subscription_id": subscription_id}
            )
        
        return True
    
    @staticmethod
    def validate_checkout_session_data(data: Dict[str, Any]) -> bool:
        """Validate checkout session creation data"""
        required_fields = ["success_url", "cancel_url"]
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise StripeValidationError(
                    f"Missing required field: {field}",
                    StripeErrorType.VALIDATION_ERROR
                )
        
        # Validate URLs
        if not data["success_url"].startswith(("http://", "https://")):
            raise StripeValidationError(
                "Invalid success URL format",
                StripeErrorType.VALIDATION_ERROR
            )
        
        if not data["cancel_url"].startswith(("http://", "https://")):
            raise StripeValidationError(
                "Invalid cancel URL format",
                StripeErrorType.VALIDATION_ERROR
            )
        
        return True
    
    @staticmethod
    def validate_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Validate Stripe webhook signature"""
        if not signature:
            raise StripeValidationError(
                "Missing webhook signature",
                StripeErrorType.VALIDATION_ERROR
            )
        
        if not secret:
            raise StripeValidationError(
                "Missing webhook secret",
                StripeErrorType.VALIDATION_ERROR
            )
        
        try:
            stripe.Webhook.construct_event(payload, signature, secret)
            return True
        except ValueError as e:
            raise StripeValidationError(
                f"Invalid webhook payload: {str(e)}",
                StripeErrorType.VALIDATION_ERROR
            )
        except stripe.error.SignatureVerificationError as e:
            raise StripeValidationError(
                f"Invalid webhook signature: {str(e)}",
                StripeErrorType.AUTHENTICATION_ERROR
            )
    
    @staticmethod
    def validate_plan_data(plan_data: Dict[str, Any]) -> bool:
        """Validate plan data for Stripe operations"""
        required_fields = ["name", "price"]
        
        for field in required_fields:
            if field not in plan_data:
                raise StripeValidationError(
                    f"Missing required field: {field}",
                    StripeErrorType.VALIDATION_ERROR
                )
        
        # Validate price
        if not isinstance(plan_data["price"], (int, float)) or plan_data["price"] <= 0:
            raise StripeValidationError(
                "Price must be a positive number",
                StripeErrorType.VALIDATION_ERROR
            )
        
        # Validate currency
        if "currency" in plan_data and plan_data["currency"] not in ["usd", "eur", "gbp"]:
            raise StripeValidationError(
                "Unsupported currency",
                StripeErrorType.VALIDATION_ERROR
            )
        
        return True


class StripeErrorHandler:
    """Handler for Stripe errors with proper categorization and logging"""
    
    @staticmethod
    def handle_stripe_error(error: stripe.error.StripeError) -> StripeValidationError:
        """Convert Stripe error to our custom validation error"""
        error_type = StripeErrorHandler._categorize_error(error)
        
        # Log the error
        logger.error(f"Stripe error: {error_type.value} - {str(error)}")
        
        # Create custom error with appropriate message
        message = StripeErrorHandler._get_user_friendly_message(error, error_type)
        
        return StripeValidationError(
            message=message,
            error_type=error_type,
            details={
                "stripe_error_type": error.__class__.__name__,
                "stripe_error_code": getattr(error, "code", None),
                "stripe_error_param": getattr(error, "param", None),
                "stripe_error_decline_code": getattr(error, "decline_code", None)
            }
        )
    
    @staticmethod
    def _categorize_error(error: stripe.error.StripeError) -> StripeErrorType:
        """Categorize Stripe error by type"""
        if isinstance(error, stripe.error.CardError):
            return StripeErrorType.CARD_ERROR
        elif isinstance(error, stripe.error.InvalidRequestError):
            return StripeErrorType.INVALID_REQUEST_ERROR
        elif isinstance(error, stripe.error.APIError):
            return StripeErrorType.API_ERROR
        elif isinstance(error, stripe.error.AuthenticationError):
            return StripeErrorType.AUTHENTICATION_ERROR
        elif isinstance(error, stripe.error.PermissionError):
            return StripeErrorType.PERMISSION_ERROR
        elif isinstance(error, stripe.error.RateLimitError):
            return StripeErrorType.RATE_LIMIT_ERROR
        else:
            return StripeErrorType.UNKNOWN_ERROR
    
    @staticmethod
    def _get_user_friendly_message(error: stripe.error.StripeError, error_type: StripeErrorType) -> str:
        """Get user-friendly error message based on error type"""
        if error_type == StripeErrorType.CARD_ERROR:
            return "There was a problem with your payment method. Please check your card details and try again."
        elif error_type == StripeErrorType.INVALID_REQUEST_ERROR:
            return "Invalid request. Please check your input and try again."
        elif error_type == StripeErrorType.API_ERROR:
            return "A temporary error occurred. Please try again in a few moments."
        elif error_type == StripeErrorType.AUTHENTICATION_ERROR:
            return "Authentication failed. Please check your API keys."
        elif error_type == StripeErrorType.PERMISSION_ERROR:
            return "You don't have permission to perform this action."
        elif error_type == StripeErrorType.RATE_LIMIT_ERROR:
            return "Too many requests. Please wait a moment and try again."
        else:
            return "An unexpected error occurred. Please try again later."


class StripeRetryHandler:
    """Handler for retrying Stripe operations with exponential backoff"""
    
    @staticmethod
    def should_retry(error: stripe.error.StripeError) -> bool:
        """Determine if an operation should be retried"""
        # Retry on rate limit errors and temporary API errors
        if isinstance(error, stripe.error.RateLimitError):
            return True
        
        if isinstance(error, stripe.error.APIError):
            # Retry on 5xx errors
            if hasattr(error, "http_status") and error.http_status >= 500:
                return True
        
        return False
    
    @staticmethod
    def get_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
        """Calculate retry delay with exponential backoff"""
        return base_delay * (2 ** attempt)
    
    @staticmethod
    def get_max_retries() -> int:
        """Get maximum number of retries"""
        return 3


class StripeOperationWrapper:
    """Wrapper for Stripe operations with validation and error handling"""
    
    def __init__(self, validator: StripeValidator, error_handler: StripeErrorHandler):
        self.validator = validator
        self.error_handler = error_handler
    
    def create_checkout_session(self, **kwargs) -> Dict[str, Any]:
        """Create checkout session with validation and error handling"""
        try:
            # Validate input data
            self.validator.validate_checkout_session_data(kwargs)
            if "price" in kwargs:
                self.validator.validate_price_id(kwargs["price"])
            
            # Create session
            session = stripe.checkout.Session.create(**kwargs)
            
            # Validate response
            if not session or not session.get("id"):
                raise StripeValidationError(
                    "Failed to create checkout session",
                    StripeErrorType.API_ERROR
                )
            
            return {
                "id": session["id"],
                "url": session["url"],
                "expires_at": session["expires_at"]
            }
            
        except stripe.error.StripeError as e:
            raise self.error_handler.handle_stripe_error(e)
        except StripeValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating checkout session: {str(e)}")
            raise StripeValidationError(
                "An unexpected error occurred",
                StripeErrorType.UNKNOWN_ERROR
            )
    
    def create_customer(self, **kwargs) -> Dict[str, Any]:
        """Create customer with validation and error handling"""
        try:
            # Validate required fields
            if "email" not in kwargs or not kwargs["email"]:
                raise StripeValidationError(
                    "Email is required for customer creation",
                    StripeErrorType.VALIDATION_ERROR
                )
            
            # Create customer
            customer = stripe.Customer.create(**kwargs)
            
            # Validate response
            if not customer or not customer.get("id"):
                raise StripeValidationError(
                    "Failed to create customer",
                    StripeErrorType.API_ERROR
                )
            
            return {
                "id": customer["id"],
                "email": customer.get("email"),
                "created": customer.get("created")
            }
            
        except stripe.error.StripeError as e:
            raise self.error_handler.handle_stripe_error(e)
        except StripeValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating customer: {str(e)}")
            raise StripeValidationError(
                "An unexpected error occurred",
                StripeErrorType.UNKNOWN_ERROR
            )
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription with validation and error handling"""
        try:
            # Validate subscription ID
            self.validator.validate_subscription_id(subscription_id)
            
            # Get subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Validate response
            if not subscription or not subscription.get("id"):
                raise StripeValidationError(
                    "Subscription not found",
                    StripeErrorType.INVALID_REQUEST_ERROR
                )
            
            return {
                "id": subscription["id"],
                "status": subscription["status"],
                "current_period_start": subscription["current_period_start"],
                "current_period_end": subscription["current_period_end"],
                "customer": subscription["customer"]
            }
            
        except stripe.error.StripeError as e:
            raise self.error_handler.handle_stripe_error(e)
        except StripeValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting subscription: {str(e)}")
            raise StripeValidationError(
                "An unexpected error occurred",
                StripeErrorType.UNKNOWN_ERROR
            )
    
    def cancel_subscription(self, subscription_id: str, immediately: bool = False) -> Dict[str, Any]:
        """Cancel subscription with validation and error handling"""
        try:
            # Validate subscription ID
            self.validator.validate_subscription_id(subscription_id)
            
            # Cancel subscription
            if immediately:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            # Validate response
            if not subscription or not subscription.get("id"):
                raise StripeValidationError(
                    "Failed to cancel subscription",
                    StripeErrorType.API_ERROR
                )
            
            return {
                "id": subscription["id"],
                "status": subscription["status"],
                "canceled_at": subscription.get("canceled_at"),
                "cancel_at_period_end": subscription.get("cancel_at_period_end")
            }
            
        except stripe.error.StripeError as e:
            raise self.error_handler.handle_stripe_error(e)
        except StripeValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error canceling subscription: {str(e)}")
            raise StripeValidationError(
                "An unexpected error occurred",
                StripeErrorType.UNKNOWN_ERROR
            )


# Global instances
validator = StripeValidator()
error_handler = StripeErrorHandler()
stripe_wrapper = StripeOperationWrapper(validator, error_handler)
