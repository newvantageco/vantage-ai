"""
Redis-backed Rate Limiting Middleware
Implements token bucket algorithm for rate limiting
"""

import time
import json
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
from app.core.config import get_settings

settings = get_settings()

# Redis connection with error handling
try:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True,
        socket_connect_timeout=5,  # Add connection timeout
        socket_timeout=5,  # Add socket timeout
        retry_on_timeout=True,
        health_check_interval=30  # Health check every 30 seconds
    )
    # Test connection
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis connection failed: {e}. Rate limiting will be disabled.")
    redis_client = None


class RateLimiter:
    """Redis-backed rate limiter using token bucket algorithm"""
    
    def __init__(self, redis_client: redis.Redis = None):
        self.redis = redis_client
    
    def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int = 60,
        burst_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Check if request is allowed based on token bucket algorithm
        
        Args:
            key: Unique key for the rate limit (e.g., "org_123", "user_456")
            limit: Number of requests allowed per window
            window_seconds: Time window in seconds
            burst_limit: Maximum burst capacity (defaults to limit * 2)
            
        Returns:
            Dictionary with rate limit status and headers
        """
        if burst_limit is None:
            burst_limit = limit * 2
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Use Lua script for atomic operations
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window_seconds = tonumber(ARGV[2])
        local burst_limit = tonumber(ARGV[3])
        local current_time = tonumber(ARGV[4])
        
        -- Get current bucket state
        local bucket_data = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket_data[1]) or burst_limit
        local last_refill = tonumber(bucket_data[2]) or current_time
        
        -- Calculate tokens to add based on time passed
        local time_passed = current_time - last_refill
        local tokens_to_add = math.floor(time_passed * limit / window_seconds)
        
        -- Refill bucket (up to burst limit)
        tokens = math.min(tokens + tokens_to_add, burst_limit)
        last_refill = current_time
        
        -- Check if request is allowed
        local allowed = false
        if tokens >= 1 then
            tokens = tokens - 1
            allowed = true
        end
        
        -- Update bucket state
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', last_refill)
        redis.call('EXPIRE', key, window_seconds * 2)  -- Keep data for 2x window
        
        -- Calculate retry after
        local retry_after = 0
        if not allowed then
            retry_after = math.ceil((1 - tokens) * window_seconds / limit)
        end
        
        return {allowed, tokens, retry_after}
        """
        
        try:
            if not self.redis:
                # If Redis is unavailable, allow all requests
                return {
                    "allowed": True,
                    "remaining": limit,
                    "retry_after": 0,
                    "limit": limit,
                    "window_seconds": window_seconds,
                    "error": "Rate limiter unavailable"
                }
                
            result = self.redis.eval(
                lua_script,
                1,  # Number of keys
                key,
                limit,
                window_seconds,
                burst_limit,
                current_time
            )
            
            allowed, remaining_tokens, retry_after = result
            
            return {
                "allowed": bool(allowed),
                "remaining": int(remaining_tokens),
                "retry_after": int(retry_after),
                "limit": limit,
                "window_seconds": window_seconds
            }
            
        except redis.RedisError as e:
            # If Redis is down, allow the request but log the error
            print(f"Redis error in rate limiter: {e}")
            return {
                "allowed": True,
                "remaining": limit,
                "retry_after": 0,
                "limit": limit,
                "window_seconds": window_seconds,
                "error": "Rate limiter unavailable"
            }


# Global rate limiter instance
rate_limiter = RateLimiter(redis_client)


def get_rate_limit_key(request: Request, user_id: Optional[str] = None, org_id: Optional[str] = None) -> str:
    """
    Generate rate limit key based on request context
    
    Args:
        request: FastAPI request object
        user_id: User ID (if available)
        org_id: Organization ID (if available)
        
    Returns:
        Rate limit key string
    """
    # Priority: org_id > user_id > IP address
    if org_id:
        return f"rate_limit:org:{org_id}"
    elif user_id:
        return f"rate_limit:user:{user_id}"
    else:
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"rate_limit:ip:{client_ip}"


def get_rate_limit_config(request: Request) -> Dict[str, Any]:
    """
    Get rate limit configuration based on request path and method
    
    Args:
        request: FastAPI request object
        
    Returns:
        Rate limit configuration
    """
    path = request.url.path
    method = request.method
    
    # Default rate limits
    default_limits = {
        "limit": 100,
        "window_seconds": 60,
        "burst_limit": 200
    }
    
    # API-specific rate limits
    if path.startswith("/api/v1/"):
        if path.startswith("/api/v1/ai/"):
            # AI endpoints - more restrictive
            return {
                "limit": 50,
                "window_seconds": 60,
                "burst_limit": 100
            }
        elif path.startswith("/api/v1/billing/"):
            # Billing endpoints - very restrictive
            return {
                "limit": 20,
                "window_seconds": 60,
                "burst_limit": 40
            }
        elif path.startswith("/api/v1/privacy/"):
            # Privacy endpoints - very restrictive
            return {
                "limit": 10,
                "window_seconds": 60,
                "burst_limit": 20
            }
        elif path.startswith("/api/v1/analytics/"):
            # Analytics endpoints - moderate
            return {
                "limit": 200,
                "window_seconds": 60,
                "burst_limit": 400
            }
        else:
            # General API endpoints
            return {
                "limit": 100,
                "window_seconds": 60,
                "burst_limit": 200
            }
    
    # Webhook endpoints - more permissive
    elif path.startswith("/webhooks/"):
        return {
            "limit": 1000,
            "window_seconds": 60,
            "burst_limit": 2000
        }
    
    # Default for other endpoints
    return default_limits


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler
        
    Returns:
        Response with rate limit headers
    """
    # Skip rate limiting for health checks and static files
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Get rate limit configuration
    config = get_rate_limit_config(request)
    
    # Get user context from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    org_id = getattr(request.state, "org_id", None)
    
    # Generate rate limit key
    key = get_rate_limit_key(request, user_id, org_id)
    
    # Check rate limit
    rate_limit_result = rate_limiter.is_allowed(
        key=key,
        limit=config["limit"],
        window_seconds=config["window_seconds"],
        burst_limit=config["burst_limit"]
    )
    
    # Add rate limit headers to response
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_limit_result["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_limit_result["remaining"])
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + rate_limit_result["window_seconds"]))
    
    if not rate_limit_result["allowed"]:
        response.headers["Retry-After"] = str(rate_limit_result["retry_after"])
        
        # Return 429 Too Many Requests
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again in {rate_limit_result['retry_after']} seconds.",
                "retry_after": rate_limit_result["retry_after"],
                "limit": rate_limit_result["limit"],
                "window_seconds": rate_limit_result["window_seconds"]
            },
            headers={
                "X-RateLimit-Limit": str(rate_limit_result["limit"]),
                "X-RateLimit-Remaining": str(rate_limit_result["remaining"]),
                "X-RateLimit-Reset": str(int(time.time() + rate_limit_result["window_seconds"])),
                "Retry-After": str(rate_limit_result["retry_after"])
            }
        )
    
    return response


class RateLimitError(HTTPException):
    """Custom exception for rate limit exceeded"""
    
    def __init__(self, retry_after: int, limit: int, window_seconds: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again in {retry_after} seconds.",
                "retry_after": retry_after,
                "limit": limit,
                "window_seconds": window_seconds
            }
        )


def check_rate_limit(
    request: Request,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    custom_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Check rate limit for a specific request (for use in endpoints)
    
    Args:
        request: FastAPI request object
        user_id: User ID (if available)
        org_id: Organization ID (if available)
        custom_config: Custom rate limit configuration
        
    Returns:
        Rate limit result
        
    Raises:
        RateLimitError: If rate limit is exceeded
    """
    # Get rate limit configuration
    config = custom_config or get_rate_limit_config(request)
    
    # Generate rate limit key
    key = get_rate_limit_key(request, user_id, org_id)
    
    # Check rate limit
    result = rate_limiter.is_allowed(
        key=key,
        limit=config["limit"],
        window_seconds=config["window_seconds"],
        burst_limit=config["burst_limit"]
    )
    
    if not result["allowed"]:
        raise RateLimitError(
            retry_after=result["retry_after"],
            limit=result["limit"],
            window_seconds=result["window_seconds"]
        )
    
    return result


def get_rate_limit_status(
    request: Request,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get current rate limit status without consuming a token
    
    Args:
        request: FastAPI request object
        user_id: User ID (if available)
        org_id: Organization ID (if available)
        
    Returns:
        Rate limit status
    """
    config = get_rate_limit_config(request)
    key = get_rate_limit_key(request, user_id, org_id)
    
    # Get current bucket state without consuming a token
    bucket_data = redis_client.hmget(key, "tokens", "last_refill")
    tokens = int(bucket_data[0]) if bucket_data[0] else config["burst_limit"]
    last_refill = float(bucket_data[1]) if bucket_data[1] else time.time()
    
    current_time = time.time()
    time_passed = current_time - last_refill
    tokens_to_add = int(time_passed * config["limit"] / config["window_seconds"])
    
    # Calculate current tokens (without consuming)
    current_tokens = min(tokens + tokens_to_add, config["burst_limit"])
    
    return {
        "remaining": current_tokens,
        "limit": config["limit"],
        "window_seconds": config["window_seconds"],
        "reset_time": int(last_refill + config["window_seconds"])
    }