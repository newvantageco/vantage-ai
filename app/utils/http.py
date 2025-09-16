from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with retry logic and rate limiting for social media APIs."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError))
    )
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> httpx.Response:
        """Make HTTP request with retry logic and rate limiting."""
        if not self._client:
            raise RuntimeError("HTTPClient not initialized. Use async context manager.")
        
        # Add idempotency header if provided
        request_headers = headers or {}
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key
        
        # Add request ID for tracking
        request_id = f"req_{int(time.time() * 1000)}"
        request_headers["X-Request-ID"] = request_id
        
        logger.info(f"Making {method} request to {url} (ID: {request_id})")
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=request_headers,
                json=json,
                data=data,
                files=files,
            )
            
            # Log response details
            response_id = response.headers.get("X-Request-ID") or response.headers.get("Request-ID")
            if response_id:
                logger.info(f"Response received (ID: {response_id}) - Status: {response.status_code}")
            
            # Check for rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limited. Waiting {retry_after} seconds before retry.")
                await asyncio.sleep(retry_after)
                raise httpx.HTTPStatusError("Rate limited", request=None, response=response)
            
            # Raise for client/server errors
            response.raise_for_status()
            return response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise


def mask_token(token: str) -> str:
    """Mask sensitive tokens in logs."""
    if not token or len(token) < 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"
