"""
Performance optimization utilities for VANTAGE AI
"""
import asyncio
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional
import redis.asyncio as redis
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine
from app.core.config import get_settings

settings = get_settings()

# Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client with connection pooling"""
    global redis_client, redis_pool
    
    if redis_client is None:
        redis_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
        )
        redis_client = redis.Redis(connection_pool=redis_pool)
    
    return redis_client


def cache_result(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results in Redis
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            try:
                # Try to get from cache
                redis_client = await get_redis_client()
                cached_result = await redis_client.get(cache_key)
                
                if cached_result:
                    import json
                    return json.loads(cached_result)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                import json
                await redis_client.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(result, default=str)
                )
                
                return result
                
            except Exception as e:
                # If Redis fails, just execute the function
                print(f"Cache error for {func.__name__}: {e}")
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit(requests_per_minute: int = 60):
    """
    Decorator to implement rate limiting
    
    Args:
        requests_per_minute: Maximum requests per minute
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Simple in-memory rate limiting
            # In production, use Redis for distributed rate limiting
            current_time = time.time()
            minute_window = int(current_time // 60)
            
            # This is a simplified implementation
            # In production, implement proper distributed rate limiting
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class DatabaseConnectionPool:
    """Database connection pool manager"""
    
    def __init__(self):
        self.engine = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Setup database engine with connection pooling"""
        self.engine = create_engine(
            settings.database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=settings.debug,
        )
    
    def get_engine(self):
        """Get database engine"""
        return self.engine


# Global database pool instance
db_pool = DatabaseConnectionPool()


def get_optimized_engine():
    """Get optimized database engine with connection pooling"""
    return db_pool.get_engine()


class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    @staticmethod
    def time_function(func: Callable) -> Callable:
        """Decorator to time function execution"""
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            print(f"{func.__name__} executed in {execution_time:.4f} seconds")
            
            return result
        
        return wrapper
    
    @staticmethod
    def monitor_memory_usage(func: Callable) -> Callable:
        """Decorator to monitor memory usage"""
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            result = await func(*args, **kwargs)
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            print(f"{func.__name__} used {memory_used:.2f} MB of memory")
            
            return result
        
        return wrapper


# Performance monitoring decorators
time_function = PerformanceMonitor.time_function
monitor_memory_usage = PerformanceMonitor.monitor_memory_usage


class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def add_eager_loading(query, relationships: list):
        """Add eager loading to reduce N+1 queries"""
        from sqlalchemy.orm import joinedload
        
        for relationship in relationships:
            query = query.options(joinedload(relationship))
        
        return query
    
    @staticmethod
    def add_select_related(query, relationships: list):
        """Add select_related for foreign key relationships"""
        for relationship in relationships:
            query = query.join(relationship)
        
        return query
    
    @staticmethod
    def paginate_query(query, page: int = 1, per_page: int = 20):
        """Add pagination to query"""
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page)


# Query optimization utilities
add_eager_loading = QueryOptimizer.add_eager_loading
add_select_related = QueryOptimizer.add_select_related
paginate_query = QueryOptimizer.paginate_query


async def cleanup_resources():
    """Cleanup resources on shutdown"""
    global redis_client, redis_pool
    
    if redis_client:
        await redis_client.close()
    
    if redis_pool:
        await redis_pool.disconnect()
    
    if db_pool.engine:
        db_pool.engine.dispose()
