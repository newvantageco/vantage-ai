"""
Rate limiting middleware using slowapi.
"""

import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.rate_limiting import (
    RateLimit, RateLimitUsage, RateLimitViolation, IPAllowlist,
    RateLimitScopes, DEFAULT_RATE_LIMITS
)
from app.core.security import get_current_user_optional


class CustomLimiter(Limiter):
    """Custom rate limiter that integrates with database."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rate_limit_exceeded_handler = self.custom_rate_limit_exceeded_handler
    
    def custom_rate_limit_exceeded_handler(self, request: Request, exc: RateLimitExceeded):
        """Custom handler for rate limit exceeded."""
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": str(exc.detail),
                "retry_after": exc.retry_after
            }
        )


# Create limiter instance
limiter = CustomLimiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"]
)


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key based on user, org, or IP."""
    try:
        # Try to get current user
        current_user = get_current_user_optional(request)
        if current_user:
            return f"user:{current_user['user_id']}"
    except:
        pass
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


def check_ip_allowlist(request: Request, org_id: str) -> bool:
    """Check if IP is in allowlist for organization."""
    try:
        db = next(get_db())
        
        # Get active allowlists for org
        allowlists = db.query(IPAllowlist).filter(
            IPAllowlist.org_id == org_id,
            IPAllowlist.is_active == True
        ).all()
        
        if not allowlists:
            return True  # No allowlist means all IPs allowed
        
        # Check if IP is in any allowlist
        ip_address = get_remote_address(request)
        for allowlist in allowlists:
            if allowlist.is_ip_allowed(ip_address):
                return True
        
        return False
        
    except Exception as e:
        print(f"Error checking IP allowlist: {e}")
        return True  # Allow on error
    finally:
        db.close()


def get_rate_limits_for_org(org_id: str, db: Session) -> Dict[str, Any]:
    """Get rate limits for organization."""
    try:
        # Get custom rate limits for org
        custom_limits = db.query(RateLimit).filter(
            RateLimit.org_id == org_id,
            RateLimit.is_active == True
        ).all()
        
        if custom_limits:
            # Use custom limits
            limits = {}
            for limit in custom_limits:
                scope_key = f"{limit.scope}:{limit.scope_value or 'default'}"
                limits[scope_key] = {
                    "requests_per_minute": limit.requests_per_minute,
                    "requests_per_hour": limit.requests_per_hour,
                    "requests_per_day": limit.requests_per_day
                }
            return limits
        
        # Use default limits based on plan (this would need to be implemented)
        # For now, return default limits
        return DEFAULT_RATE_LIMITS.get("pro", DEFAULT_RATE_LIMITS["free"])
        
    except Exception as e:
        print(f"Error getting rate limits: {e}")
        return DEFAULT_RATE_LIMITS["free"]


def track_rate_limit_usage(
    org_id: str,
    scope_key: str,
    rate_limit_id: str,
    window_start: time.time,
    window_end: time.time,
    db: Session
) -> bool:
    """Track rate limit usage and return True if within limits."""
    try:
        # Get or create usage record
        usage = db.query(RateLimitUsage).filter(
            RateLimitUsage.org_id == org_id,
            RateLimitUsage.rate_limit_id == rate_limit_id,
            RateLimitUsage.scope_key == scope_key,
            RateLimitUsage.window_start == datetime.fromtimestamp(window_start),
            RateLimitUsage.window_end == datetime.fromtimestamp(window_end)
        ).first()
        
        if not usage:
            usage = RateLimitUsage(
                id=f"usage_{int(time.time())}_{hash(scope_key)}",
                org_id=org_id,
                rate_limit_id=rate_limit_id,
                scope_key=scope_key,
                window_start=datetime.fromtimestamp(window_start),
                window_end=datetime.fromtimestamp(window_end),
                requests_count=0
            )
            db.add(usage)
        
        # Get rate limit configuration
        rate_limit = db.query(RateLimit).filter(RateLimit.id == rate_limit_id).first()
        if not rate_limit:
            return True  # No rate limit configured
        
        # Check if within limits
        usage.requests_count += 1
        
        # Determine which limit to check based on window duration
        window_duration = window_end - window_start
        
        if window_duration <= 60:  # 1 minute
            limit = rate_limit.requests_per_minute
        elif window_duration <= 3600:  # 1 hour
            limit = rate_limit.requests_per_hour
        else:  # 1 day
            limit = rate_limit.requests_per_day
        
        if usage.requests_count > limit:
            # Record violation
            violation = RateLimitViolation(
                id=f"violation_{int(time.time())}_{hash(scope_key)}",
                org_id=org_id,
                rate_limit_id=rate_limit_id,
                scope_key=scope_key,
                requests_count=usage.requests_count,
                limit_exceeded=usage.requests_count - limit,
                window_start=datetime.fromtimestamp(window_start),
                window_end=datetime.fromtimestamp(window_end)
            )
            db.add(violation)
            db.commit()
            return False
        
        db.commit()
        return True
        
    except Exception as e:
        print(f"Error tracking rate limit usage: {e}")
        db.rollback()
        return True  # Allow on error


def create_rate_limit_middleware():
    """Create rate limiting middleware."""
    return SlowAPIMiddleware


# Rate limit decorators
def rate_limit_by_user(limit: str):
    """Rate limit by user."""
    def decorator(func):
        return limiter.limit(limit, key_func=lambda request: f"user:{get_current_user_optional(request)['user_id']}")(func)
    return decorator


def rate_limit_by_org(limit: str):
    """Rate limit by organization."""
    def decorator(func):
        return limiter.limit(limit, key_func=lambda request: f"org:{get_current_user_optional(request)['org_id']}")(func)
    return decorator


def rate_limit_by_ip(limit: str):
    """Rate limit by IP address."""
    def decorator(func):
        return limiter.limit(limit, key_func=get_remote_address)(func)
    return decorator


def rate_limit_by_endpoint(limit: str):
    """Rate limit by endpoint."""
    def decorator(func):
        return limiter.limit(limit, key_func=lambda request: f"endpoint:{request.url.path}")(func)
    return decorator


# Example usage in routes:
# @rate_limit_by_user("10/minute")
# @rate_limit_by_org("1000/hour")
# @rate_limit_by_ip("100/minute")
# @rate_limit_by_endpoint("50/minute")
