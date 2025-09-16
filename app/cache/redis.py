from __future__ import annotations

import json
import hashlib
from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import get_settings


class RedisCache:
    def __init__(self) -> None:
        settings = get_settings()
        self.redis_url = settings.redis_url
        self.ttl = settings.ai_cache_ttl_secs
        self._client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    def _make_key(self, namespace: str, key_data: str) -> str:
        """Create a namespaced cache key with hash for long keys."""
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"{namespace}:{key_hash}"

    async def get(self, namespace: str, key_data: str) -> Optional[Any]:
        """Get JSON data from cache."""
        try:
            client = await self._get_client()
            key = self._make_key(namespace, key_data)
            data = await client.get(key)
            return json.loads(data) if data else None
        except Exception:
            # Fail silently for cache misses
            return None

    async def set(self, namespace: str, key_data: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set JSON data in cache with TTL."""
        try:
            client = await self._get_client()
            key = self._make_key(namespace, key_data)
            data = json.dumps(value, default=str)
            ttl = ttl or self.ttl
            await client.setex(key, ttl, data)
            return True
        except Exception:
            return False

    async def delete(self, namespace: str, key_data: str) -> bool:
        """Delete a cache key."""
        try:
            client = await self._get_client()
            key = self._make_key(namespace, key_data)
            await client.delete(key)
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None


# Global cache instance
cache = RedisCache()
