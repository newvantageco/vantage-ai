"""
Brave Search API Integration for VANTAGE AI
Provides comprehensive search capabilities including web, local, image, video, and news search
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class SearchType(Enum):
    """Available search types"""
    WEB = "web"
    LOCAL = "local"
    IMAGE = "image"
    VIDEO = "video"
    NEWS = "news"


class SafeSearchLevel(Enum):
    """Content filtering levels"""
    OFF = "off"
    MODERATE = "moderate"
    STRICT = "strict"


@dataclass
class SearchResult:
    """Search result data structure"""
    title: str
    url: str
    description: str
    published_date: Optional[str] = None
    thumbnail: Optional[str] = None
    source: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    price: Optional[str] = None
    rating: Optional[float] = None


@dataclass
class SearchResponse:
    """Search response data structure"""
    results: List[SearchResult]
    total_results: int
    search_time: float
    query: str
    search_type: SearchType
    summary: Optional[str] = None
    summary_key: Optional[str] = None


class BraveSearchClient:
    """Brave Search API client for VANTAGE AI"""
    
    BASE_URL = "https://api.search.brave.com/res/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY environment variable is required")
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "X-Subscription-Token": self.api_key,
                "Accept": "application/json",
                "User-Agent": "VANTAGE-AI/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to Brave Search API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Convert boolean values to strings for aiohttp compatibility
        processed_params = {}
        for key, value in params.items():
            if isinstance(value, bool):
                processed_params[key] = str(value).lower()
            else:
                processed_params[key] = value
        
        try:
            async with self.session.get(url, params=processed_params) as response:
                if response.status == 429:
                    logger.warning("Rate limit exceeded. Please wait before making more requests.")
                    raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait before making more requests.")
                elif response.status == 400:
                    logger.error(f"Bad request: {response.status}")
                    raise HTTPException(status_code=400, detail="Bad request. Check your search parameters.")
                elif response.status == 401:
                    logger.error("Unauthorized. Check your API key.")
                    raise HTTPException(status_code=401, detail="Unauthorized. Check your API key.")
                
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Brave Search API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Brave Search API request: {e}")
            raise
    
    async def web_search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        country: str = "US",
        search_lang: str = "en",
        ui_lang: str = "en-US",
        safesearch: SafeSearchLevel = SafeSearchLevel.STRICT,
        spellcheck: bool = True,
        summary: bool = False,
        extra_snippets: bool = False,
        freshness: Optional[str] = None
    ) -> SearchResponse:
        """Perform web search with optional AI summary"""
        
        params = {
            "q": query,
            "count": min(count, 50),  # API limit
            "offset": min(offset, 9),  # API limit
            "country": country,
            "search_lang": search_lang,
            "ui_lang": ui_lang,
            "safesearch": safesearch.value,
            "spellcheck": spellcheck,
            "summary": summary,
            "extra_snippets": extra_snippets
        }
        
        if freshness:
            params["freshness"] = freshness
        
        response_data = await self._make_request("web/search", params)
        
        # Parse results
        results = []
        for item in response_data.get("web", {}).get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                published_date=item.get("published_date"),
                thumbnail=item.get("thumbnail", {}).get("src") if item.get("thumbnail") else None
            ))
        
        # Extract summary if available
        summary_text = None
        summary_key = None
        if summary and "summary" in response_data:
            summary_text = response_data["summary"].get("text")
            summary_key = response_data["summary"].get("key")
        
        return SearchResponse(
            results=results,
            total_results=response_data.get("web", {}).get("total_results", 0),
            search_time=response_data.get("web", {}).get("search_time", 0),
            query=query,
            search_type=SearchType.WEB,
            summary=summary_text,
            summary_key=summary_key
        )
    
    async def local_search(
        self,
        query: str,
        location: str,
        count: int = 10,
        offset: int = 0,
        country: str = "US",
        search_lang: str = "en",
        ui_lang: str = "en-US",
        safesearch: SafeSearchLevel = SafeSearchLevel.STRICT
    ) -> SearchResponse:
        """Search for local businesses and services"""
        
        params = {
            "q": query,
            "location": location,
            "count": min(count, 50),
            "offset": min(offset, 9),
            "country": country,
            "search_lang": search_lang,
            "ui_lang": ui_lang,
            "safesearch": safesearch.value
        }
        
        response_data = await self._make_request("local/search", params)
        
        results = []
        for item in response_data.get("local", {}).get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                location=item.get("location"),
                price=item.get("price"),
                rating=item.get("rating")
            ))
        
        return SearchResponse(
            results=results,
            total_results=response_data.get("local", {}).get("total_results", 0),
            search_time=response_data.get("local", {}).get("search_time", 0),
            query=query,
            search_type=SearchType.LOCAL
        )
    
    async def image_search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        country: str = "US",
        search_lang: str = "en",
        ui_lang: str = "en-US",
        safesearch: SafeSearchLevel = SafeSearchLevel.STRICT,
        size: Optional[str] = None,
        color: Optional[str] = None,
        type: Optional[str] = None,
        layout: Optional[str] = None
    ) -> SearchResponse:
        """Search for images"""
        
        params = {
            "q": query,
            "count": min(count, 50),
            "offset": min(offset, 9),
            "country": country,
            "search_lang": search_lang,
            "ui_lang": ui_lang,
            "safesearch": safesearch.value
        }
        
        if size:
            params["size"] = size
        if color:
            params["color"] = color
        if type:
            params["type"] = type
        if layout:
            params["layout"] = layout
        
        response_data = await self._make_request("images/search", params)
        
        results = []
        for item in response_data.get("images", {}).get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                thumbnail=item.get("thumbnail", {}).get("src") if item.get("thumbnail") else None,
                source=item.get("source")
            ))
        
        return SearchResponse(
            results=results,
            total_results=response_data.get("images", {}).get("total_results", 0),
            search_time=response_data.get("images", {}).get("search_time", 0),
            query=query,
            search_type=SearchType.IMAGE
        )
    
    async def video_search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        country: str = "US",
        search_lang: str = "en",
        ui_lang: str = "en-US",
        safesearch: SafeSearchLevel = SafeSearchLevel.STRICT,
        duration: Optional[str] = None
    ) -> SearchResponse:
        """Search for videos"""
        
        params = {
            "q": query,
            "count": min(count, 50),
            "offset": min(offset, 9),
            "country": country,
            "search_lang": search_lang,
            "ui_lang": ui_lang,
            "safesearch": safesearch.value
        }
        
        if duration:
            params["duration"] = duration
        
        response_data = await self._make_request("videos/search", params)
        
        results = []
        for item in response_data.get("videos", {}).get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                thumbnail=item.get("thumbnail", {}).get("src") if item.get("thumbnail") else None,
                published_date=item.get("published_date"),
                source=item.get("source")
            ))
        
        return SearchResponse(
            results=results,
            total_results=response_data.get("videos", {}).get("total_results", 0),
            search_time=response_data.get("videos", {}).get("search_time", 0),
            query=query,
            search_type=SearchType.VIDEO
        )
    
    async def news_search(
        self,
        query: str,
        count: int = 20,
        offset: int = 0,
        country: str = "US",
        search_lang: str = "en",
        ui_lang: str = "en-US",
        safesearch: SafeSearchLevel = SafeSearchLevel.MODERATE,
        freshness: str = "pd",  # past day
        spellcheck: bool = True,
        extra_snippets: bool = False
    ) -> SearchResponse:
        """Search for news articles"""
        
        params = {
            "q": query,
            "count": min(count, 50),
            "offset": min(offset, 9),
            "country": country,
            "search_lang": search_lang,
            "ui_lang": ui_lang,
            "safesearch": safesearch.value,
            "freshness": freshness,
            "spellcheck": spellcheck,
            "extra_snippets": extra_snippets
        }
        
        response_data = await self._make_request("news/search", params)
        
        results = []
        for item in response_data.get("news", {}).get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                published_date=item.get("published_date"),
                thumbnail=item.get("thumbnail", {}).get("src") if item.get("thumbnail") else None,
                source=item.get("source")
            ))
        
        return SearchResponse(
            results=results,
            total_results=response_data.get("news", {}).get("total_results", 0),
            search_time=response_data.get("news", {}).get("search_time", 0),
            query=query,
            search_type=SearchType.NEWS
        )
    
    async def get_summary(self, summary_key: str, entity_info: bool = False, inline_references: bool = False) -> str:
        """Get AI-powered summary using summary key from web search"""
        
        params = {
            "key": summary_key,
            "entity_info": entity_info,
            "inline_references": inline_references
        }
        
        response_data = await self._make_request("summarizer", params)
        return response_data.get("summary", "")


# Convenience functions for easy integration
async def search_web(query: str, **kwargs) -> SearchResponse:
    """Convenience function for web search"""
    async with BraveSearchClient() as client:
        return await client.web_search(query, **kwargs)


async def search_local(query: str, location: str, **kwargs) -> SearchResponse:
    """Convenience function for local search"""
    async with BraveSearchClient() as client:
        return await client.local_search(query, location, **kwargs)


async def search_images(query: str, **kwargs) -> SearchResponse:
    """Convenience function for image search"""
    async with BraveSearchClient() as client:
        return await client.image_search(query, **kwargs)


async def search_videos(query: str, **kwargs) -> SearchResponse:
    """Convenience function for video search"""
    async with BraveSearchClient() as client:
        return await client.video_search(query, **kwargs)


async def search_news(query: str, **kwargs) -> SearchResponse:
    """Convenience function for news search"""
    async with BraveSearchClient() as client:
        return await client.news_search(query, **kwargs)


async def get_ai_summary(summary_key: str, **kwargs) -> str:
    """Convenience function for AI summary"""
    async with BraveSearchClient() as client:
        return await client.get_summary(summary_key, **kwargs)
