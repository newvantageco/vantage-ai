# pyright: reportMissingImports=false
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import stripe as _stripe  # for type hints only

def _get_stripe() -> "Any":
    """
    Lazy-import stripe to avoid hard failures when the package isn't installed
    in some environments (e.g., front-end-only dev). Raises a clear error at runtime
    if used without proper installation/config.
    """
    try:
        import stripe  # type: ignore
        return stripe
    except Exception as e:
        raise RuntimeError(
            "Stripe SDK not available. Install it in your current venv:\n"
            "  python -m venv .venv && source .venv/bin/activate && pip install 'stripe>=9,<11'"
        ) from e

def get_client() -> "Any":
    stripe = _get_stripe()
    api_key = os.getenv("STRIPE_SECRET_KEY")
    if not api_key:
        raise RuntimeError("STRIPE_SECRET_KEY is missing. Set it in your Secrets Admin or .env.")
    stripe.api_key = api_key
    # Optional: set app info for Stripe dashboard
    stripe.set_app_info("Vantage AI", version="0.1.0")
    return stripe

def create_checkout_session(price_id: str, success_url: str, cancel_url: str) -> dict[str, Any]:
    stripe = get_client()
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {"id": session["id"], "url": session["url"]}