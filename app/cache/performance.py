"""
High-Performance Caching Utilities for VANTAGE AI
Implements advanced caching strategies for optimal performance
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Union, Callable
from functools import wraps
import redis
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HighPerformanceCache:
    """High-performance caching system with multiple strategies."""
    
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 300):
        """
        Initialize high-performance cache.
        
        Args:
            redis_client: Redis client instance
            default_ttl: Default time-to-live in seconds
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data for storage."""
        try:
            # Try JSON first for simple data types
            return json.dumps(data).encode('utf-8')
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(data)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data from storage."""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate a cache key with namespace."""
        return f"vantage:{namespace}:{key}"
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._generate_key(key, namespace)
        
        try:
            data = self.redis.get(cache_key)
            if data is not None:
                self.cache_stats["hits"] += 1
                return self._deserialize(data)
            else:
                self.cache_stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "default") -> bool:
        """Set value in cache."""
        cache_key = self._generate_key(key, namespace)
        ttl = ttl or self.default_ttl
        
        try:
            serialized_data = self._serialize(value)
            result = self.redis.setex(cache_key, ttl, serialized_data)
            if result:
                self.cache_stats["sets"] += 1
            return result
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache."""
        cache_key = self._generate_key(key, namespace)
        
        try:
            result = self.redis.delete(cache_key)
            if result:
                self.cache_stats["deletes"] += 1
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def get_or_set(self, key: str, factory: Callable, ttl: Optional[int] = None, namespace: str = "default") -> Any:
        """Get value from cache or set it using factory function."""
        value = self.get(key, namespace)
        if value is None:
            value = factory()
            self.set(key, value, ttl, namespace)
        return value
    
    def invalidate_pattern(self, pattern: str, namespace: str = "default") -> int:
        """Invalidate all keys matching a pattern."""
        cache_pattern = self._generate_key(pattern, namespace)
        
        try:
            keys = self.redis.keys(cache_pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache pattern invalidation error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / total_requests
            if total_requests > 0 else 0
        )
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }

def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(ttl: int = 300, namespace: str = "default"):
    """Decorator for caching function results."""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from app.cache.redis import get_redis_client
            redis_client = get_redis_client()
            cache = HighPerformanceCache(redis_client, ttl)
            
            key = cache_key(func.__name__, *args, **kwargs)
            
            def factory():
                if asyncio.iscoroutinefunction(func):
                    return asyncio.run(func(*args, **kwargs))
                return func(*args, **kwargs)
            
            return cache.get_or_set(key, factory, ttl, namespace)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            from app.cache.redis import get_redis_client
            redis_client = get_redis_client()
            cache = HighPerformanceCache(redis_client, ttl)
            
            key = cache_key(func.__name__, *args, **kwargs)
            
            def factory():
                return func(*args, **kwargs)
            
            return cache.get_or_set(key, factory, ttl, namespace)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Global cache instance
_cache_instance: Optional[HighPerformanceCache] = None

def get_cache() -> HighPerformanceCache:
    """Get the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        from app.cache.redis import get_redis_client
        redis_client = get_redis_client()
        _cache_instance = HighPerformanceCache(redis_client)
    return _cache_instance
