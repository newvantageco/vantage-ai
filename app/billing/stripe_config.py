"""
Stripe Configuration and Client Factory

This module provides a clean, type-safe way to configure and access Stripe
using Pydantic settings with proper error handling.
"""

import stripe
from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StripeSettings(BaseSettings):
    """Stripe configuration settings."""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }
    
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_DRY_RUN: bool = True
    
    # Stripe Price IDs for each plan
    STRIPE_PRICE_STARTER: Optional[str] = None
    STRIPE_PRICE_GROWTH: Optional[str] = None
    STRIPE_PRICE_PRO: Optional[str] = None


# Global settings instance
settings = StripeSettings()


def get_stripe():
    """Get configured Stripe client with proper error handling."""
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("Missing STRIPE_SECRET_KEY")
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe.set_app_info("Vantage AI", version="0.1.0")
    
    return stripe


def get_webhook_secret() -> str:
    """Get Stripe webhook secret with proper error handling."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("Missing STRIPE_WEBHOOK_SECRET")
    
    return settings.STRIPE_WEBHOOK_SECRET


def is_dry_run() -> bool:
    """Check if Stripe is in dry-run mode."""
    return settings.STRIPE_DRY_RUN


def get_price_id(plan_type: str) -> str:
    """Get Stripe price ID for a plan type."""
    price_mapping = {
        "starter": settings.STRIPE_PRICE_STARTER,
        "growth": settings.STRIPE_PRICE_GROWTH,
        "pro": settings.STRIPE_PRICE_PRO,
    }
    
    price_id = price_mapping.get(plan_type.lower())
    if not price_id:
        raise ValueError(f"Unknown plan type: {plan_type}")
    
    return price_id


# Convenience function for backward compatibility
def configure_stripe():
    """Configure Stripe with current settings (for backward compatibility)."""
    try:
        get_stripe()
        logger.info("Stripe configured successfully")
    except RuntimeError as e:
        logger.warning(f"Stripe configuration failed: {e}")
        if not settings.STRIPE_DRY_RUN:
            raise
