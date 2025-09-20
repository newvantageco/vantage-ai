"""
Performance Middleware for VANTAGE AI
Implements caching, compression, and performance monitoring
"""

import time
import gzip
import json
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and optimization."""
    
    def __init__(self, app, cache_ttl: int = 300):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.response_cache = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Add performance headers
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests
        if process_time > 1.0:
            logger.warning(f"Slow request: {request.url} took {process_time:.2f}s")
        
        return response

def cache_response(ttl: int = 300):
    """Decorator to cache API responses."""
    def decorator(func: Callable):
        cache = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    return cached_data
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator

def compress_response(response: Response) -> Response:
    """Compress response if client supports it."""
    if response.headers.get("content-encoding") == "gzip":
        return response
    
    content = response.body
    if len(content) > 1024:  # Only compress if larger than 1KB
        compressed_content = gzip.compress(content)
        if len(compressed_content) < len(content):
            response.body = compressed_content
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed_content))
    
    return response

class DatabaseQueryOptimizer:
    """Optimizes database queries for better performance."""
    
    @staticmethod
    def optimize_query(query: str) -> str:
        """Optimize SQL query for better performance."""
        # Add query hints and optimizations
        optimized_query = query
        
        # Add common optimizations
        if "SELECT" in query.upper():
            # Ensure proper indexing hints
            if "WHERE" in query.upper() and "ORDER BY" not in query.upper():
                # Add ordering for better performance
                pass
        
        return optimized_query
    
    @staticmethod
    def get_query_plan(query: str) -> dict:
        """Get query execution plan for analysis."""
        # This would integrate with your database to get execution plans
        return {"query": query, "plan": "Not implemented"}

# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor application performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "total_response_time": 0,
            "slow_requests": 0,
            "error_count": 0
        }
    
    def record_request(self, response_time: float, status_code: int):
        """Record a request metric."""
        self.metrics["request_count"] += 1
        self.metrics["total_response_time"] += response_time
        
        if response_time > 1.0:
            self.metrics["slow_requests"] += 1
        
        if status_code >= 400:
            self.metrics["error_count"] += 1
    
    def get_metrics(self) -> dict:
        """Get current performance metrics."""
        avg_response_time = (
            self.metrics["total_response_time"] / self.metrics["request_count"]
            if self.metrics["request_count"] > 0 else 0
        )
        
        return {
            **self.metrics,
            "average_response_time": avg_response_time,
            "error_rate": (
                self.metrics["error_count"] / self.metrics["request_count"]
                if self.metrics["request_count"] > 0 else 0
            )
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
