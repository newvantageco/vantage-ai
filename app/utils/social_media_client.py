"""
Social Media API Client
Robust HTTP client for making API calls to social media platforms with rate limiting and error handling
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RateLimitType(str, Enum):
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"


@dataclass
class RateLimit:
    """Rate limit configuration for a platform"""
    requests: int
    window_seconds: int
    limit_type: RateLimitType


class SocialMediaClient:
    """HTTP client for social media APIs with rate limiting and error handling"""
    
    # Platform-specific rate limits
    RATE_LIMITS = {
        "meta": RateLimit(requests=200, window_seconds=3600, limit_type=RateLimitType.PER_HOUR),
        "linkedin": RateLimit(requests=100, window_seconds=3600, limit_type=RateLimitType.PER_HOUR),
        "google": RateLimit(requests=1000, window_seconds=3600, limit_type=RateLimitType.PER_HOUR),
        "tiktok": RateLimit(requests=100, window_seconds=3600, limit_type=RateLimitType.PER_HOUR),
    }
    
    def __init__(self, platform: str, base_url: str, timeout: int = 30):
        self.platform = platform
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.rate_limit = self.RATE_LIMITS.get(platform)
        self.request_times: List[float] = []
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "User-Agent": "VantageAI/1.0",
                "Accept": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
    
    async def _check_rate_limit(self):
        """Check and enforce rate limits"""
        if not self.rate_limit:
            return
        
        now = time.time()
        window_start = now - self.rate_limit.window_seconds
        
        # Remove old requests outside the window
        self.request_times = [t for t in self.request_times if t > window_start]
        
        # Check if we're at the limit
        if len(self.request_times) >= self.rate_limit.requests:
            sleep_time = self.rate_limit.window_seconds - (now - self.request_times[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached for {self.platform}, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                # Clean up old requests after sleep
                self.request_times = [t for t in self.request_times if t > now - self.rate_limit.window_seconds]
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to the platform API"""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Check rate limits
        await self._check_rate_limit()
        
        # Prepare request
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {"Content-Type": "application/json"}
        
        if headers:
            request_headers.update(headers)
        
        if access_token:
            if self.platform == "meta":
                request_headers["Authorization"] = f"Bearer {access_token}"
            elif self.platform == "linkedin":
                request_headers["Authorization"] = f"Bearer {access_token}"
            elif self.platform == "google":
                request_headers["Authorization"] = f"Bearer {access_token}"
        
        # Record request time for rate limiting
        self.request_times.append(time.time())
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=data if data else None,
                headers=request_headers
            )
            
            # Handle rate limit responses
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limited by {self.platform}, retrying after {retry_after}s")
                await asyncio.sleep(retry_after)
                return await self._make_request(method, endpoint, params, data, headers, access_token)
            
            # Handle other HTTP errors
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text}
                
                logger.error(f"API error from {self.platform}: {response.status_code} - {error_data}")
                raise HTTPError(
                    status_code=response.status_code,
                    message=error_data.get("error", {}).get("message", "Unknown error"),
                    platform=self.platform,
                    endpoint=endpoint
                )
            
            return response.json()
            
        except httpx.TimeoutException:
            logger.error(f"Timeout error from {self.platform} API")
            raise APIError(f"Timeout error from {self.platform} API")
        except httpx.RequestError as e:
            logger.error(f"Request error from {self.platform} API: {str(e)}")
            raise APIError(f"Request error from {self.platform} API: {str(e)}")
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a GET request"""
        return await self._make_request("GET", endpoint, params=params, headers=headers, access_token=access_token)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a POST request"""
        return await self._make_request("POST", endpoint, data=data, headers=headers, access_token=access_token)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a PUT request"""
        return await self._make_request("PUT", endpoint, data=data, headers=headers, access_token=access_token)
    
    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a DELETE request"""
        return await self._make_request("DELETE", endpoint, headers=headers, access_token=access_token)


class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, platform: str = None):
        self.message = message
        self.platform = platform
        super().__init__(self.message)


class HTTPError(APIError):
    """HTTP-specific API error"""
    def __init__(self, status_code: int, message: str, platform: str, endpoint: str):
        self.status_code = status_code
        self.endpoint = endpoint
        super().__init__(f"HTTP {status_code}: {message}", platform)


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, platform: str, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for {platform}", platform)


class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message: str, platform: str = None):
        super().__init__(f"Authentication failed: {message}", platform)
