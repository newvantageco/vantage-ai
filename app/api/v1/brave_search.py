"""
Brave Search API endpoints for VANTAGE AI
Provides REST API access to Brave Search functionality
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from pydantic import BaseModel, Field
import logging

from app.integrations.brave_search import (
    BraveSearchClient,
    SearchType,
    SafeSearchLevel,
    search_web,
    search_local,
    search_images,
    search_videos,
    search_news,
    get_ai_summary
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/brave-search", tags=["brave-search"])


# Request/Response Models
class SearchRequest(BaseModel):
    """Base search request model"""
    query: str = Field(..., description="Search query", max_length=400)
    count: int = Field(10, ge=1, le=50, description="Number of results to return")
    offset: int = Field(0, ge=0, le=9, description="Pagination offset")
    country: str = Field("US", description="Country code")
    search_lang: str = Field("en", description="Search language")
    ui_lang: str = Field("en-US", description="UI language")
    safesearch: str = Field("strict", description="Content filtering level")


class WebSearchRequest(SearchRequest):
    """Web search request model"""
    summary: bool = Field(False, description="Include AI summary")
    extra_snippets: bool = Field(False, description="Include extra snippets")
    freshness: Optional[str] = Field(None, description="Time filter (e.g., 'pd' for past day)")
    spellcheck: bool = Field(True, description="Enable spell checking")


class LocalSearchRequest(SearchRequest):
    """Local search request model"""
    location: str = Field(..., description="Location for local search")


class ImageSearchRequest(SearchRequest):
    """Image search request model"""
    size: Optional[str] = Field(None, description="Image size filter")
    color: Optional[str] = Field(None, description="Color filter")
    type: Optional[str] = Field(None, description="Image type filter")
    layout: Optional[str] = Field(None, description="Layout filter")


class VideoSearchRequest(SearchRequest):
    """Video search request model"""
    duration: Optional[str] = Field(None, description="Video duration filter")


class NewsSearchRequest(SearchRequest):
    """News search request model"""
    freshness: str = Field("pd", description="Time filter (default: past day)")
    spellcheck: bool = Field(True, description="Enable spell checking")
    extra_snippets: bool = Field(False, description="Include extra snippets")


class SummaryRequest(BaseModel):
    """AI summary request model"""
    summary_key: str = Field(..., description="Summary key from web search")
    entity_info: bool = Field(False, description="Include entity information")
    inline_references: bool = Field(False, description="Add source URL references")


class SearchResultResponse(BaseModel):
    """Search result response model"""
    title: str
    url: str
    description: str
    published_date: Optional[str] = None
    thumbnail: Optional[str] = None
    source: Optional[str] = None
    location: Optional[dict] = None
    price: Optional[str] = None
    rating: Optional[float] = None


class SearchResponse(BaseModel):
    """Search response model"""
    results: List[SearchResultResponse]
    total_results: int
    search_time: float
    query: str
    search_type: str
    summary: Optional[str] = None
    summary_key: Optional[str] = None


# Helper function to convert SafeSearchLevel
def get_safesearch_level(level: str) -> SafeSearchLevel:
    """Convert string to SafeSearchLevel enum"""
    try:
        return SafeSearchLevel(level.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid safesearch level: {level}. Must be one of: off, moderate, strict"
        )


@router.post("/web", response_model=SearchResponse)
async def web_search(request: WebSearchRequest):
    """Perform web search with optional AI summary"""
    try:
        safesearch = get_safesearch_level(request.safesearch)
        
        response = await search_web(
            query=request.query,
            count=request.count,
            offset=request.offset,
            country=request.country,
            search_lang=request.search_lang,
            ui_lang=request.ui_lang,
            safesearch=safesearch,
            summary=request.summary,
            extra_snippets=request.extra_snippets,
            freshness=request.freshness,
            spellcheck=request.spellcheck
        )
        
        return SearchResponse(
            results=[SearchResultResponse(**result.__dict__) for result in response.results],
            total_results=response.total_results,
            search_time=response.search_time,
            query=response.query,
            search_type=response.search_type.value,
            summary=response.summary,
            summary_key=response.summary_key
        )
    
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")


@router.post("/local", response_model=SearchResponse)
async def local_search(request: LocalSearchRequest):
    """Search for local businesses and services"""
    try:
        safesearch = get_safesearch_level(request.safesearch)
        
        response = await search_local(
            query=request.query,
            location=request.location,
            count=request.count,
            offset=request.offset,
            country=request.country,
            search_lang=request.search_lang,
            ui_lang=request.ui_lang,
            safesearch=safesearch
        )
        
        return SearchResponse(
            results=[SearchResultResponse(**result.__dict__) for result in response.results],
            total_results=response.total_results,
            search_time=response.search_time,
            query=response.query,
            search_type=response.search_type.value
        )
    
    except Exception as e:
        logger.error(f"Local search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Local search failed: {str(e)}")


@router.post("/images", response_model=SearchResponse)
async def image_search(request: ImageSearchRequest):
    """Search for images"""
    try:
        safesearch = get_safesearch_level(request.safesearch)
        
        response = await search_images(
            query=request.query,
            count=request.count,
            offset=request.offset,
            country=request.country,
            search_lang=request.search_lang,
            ui_lang=request.ui_lang,
            safesearch=safesearch,
            size=request.size,
            color=request.color,
            type=request.type,
            layout=request.layout
        )
        
        return SearchResponse(
            results=[SearchResultResponse(**result.__dict__) for result in response.results],
            total_results=response.total_results,
            search_time=response.search_time,
            query=response.query,
            search_type=response.search_type.value
        )
    
    except Exception as e:
        logger.error(f"Image search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image search failed: {str(e)}")


@router.post("/videos", response_model=SearchResponse)
async def video_search(request: VideoSearchRequest):
    """Search for videos"""
    try:
        safesearch = get_safesearch_level(request.safesearch)
        
        response = await search_videos(
            query=request.query,
            count=request.count,
            offset=request.offset,
            country=request.country,
            search_lang=request.search_lang,
            ui_lang=request.ui_lang,
            safesearch=safesearch,
            duration=request.duration
        )
        
        return SearchResponse(
            results=[SearchResultResponse(**result.__dict__) for result in response.results],
            total_results=response.total_results,
            search_time=response.search_time,
            query=response.query,
            search_type=response.search_type.value
        )
    
    except Exception as e:
        logger.error(f"Video search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Video search failed: {str(e)}")


@router.post("/news", response_model=SearchResponse)
async def news_search(request: NewsSearchRequest):
    """Search for news articles"""
    try:
        safesearch = get_safesearch_level(request.safesearch)
        
        response = await search_news(
            query=request.query,
            count=request.count,
            offset=request.offset,
            country=request.country,
            search_lang=request.search_lang,
            ui_lang=request.ui_lang,
            safesearch=safesearch,
            freshness=request.freshness,
            spellcheck=request.spellcheck,
            extra_snippets=request.extra_snippets
        )
        
        return SearchResponse(
            results=[SearchResultResponse(**result.__dict__) for result in response.results],
            total_results=response.total_results,
            search_time=response.search_time,
            query=response.query,
            search_type=response.search_type.value
        )
    
    except Exception as e:
        logger.error(f"News search failed: {e}")
        raise HTTPException(status_code=500, detail=f"News search failed: {str(e)}")


@router.post("/summary")
async def get_summary(request: SummaryRequest):
    """Get AI-powered summary using summary key from web search"""
    try:
        summary = await get_ai_summary(
            summary_key=request.summary_key,
            entity_info=request.entity_info,
            inline_references=request.inline_references
        )
        
        return {"summary": summary}
    
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


# Quick search endpoints for common use cases
@router.get("/quick/web")
async def quick_web_search(
    q: str = Query(..., description="Search query"),
    count: int = Query(10, ge=1, le=50),
    summary: bool = Query(False, description="Include AI summary")
):
    """Quick web search endpoint"""
    try:
        response = await search_web(
            query=q,
            count=count,
            summary=summary
        )
        
        return SearchResponse(
            results=[SearchResultResponse(**result.__dict__) for result in response.results],
            total_results=response.total_results,
            search_time=response.search_time,
            query=response.query,
            search_type=response.search_type.value,
            summary=response.summary,
            summary_key=response.summary_key
        )
    
    except Exception as e:
        logger.error(f"Quick web search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quick web search failed: {str(e)}")


@router.get("/quick/news")
async def quick_news_search(
    q: str = Query(..., description="Search query"),
    count: int = Query(20, ge=1, le=50),
    freshness: str = Query("pd", description="Time filter")
):
    """Quick news search endpoint"""
    try:
        response = await search_news(
            query=q,
            count=count,
            freshness=freshness
        )
        
        return SearchResponse(
            results=[SearchResultResponse(**result.__dict__) for result in response.results],
            total_results=response.total_results,
            search_time=response.search_time,
            query=response.query,
            search_type=response.search_type.value
        )
    
    except Exception as e:
        logger.error(f"Quick news search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quick news search failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for Brave Search integration"""
    try:
        # Test API key by making a simple request
        async with BraveSearchClient() as client:
            # This will raise an exception if the API key is invalid
            await client.web_search("test", count=1)
        
        return {"status": "healthy", "service": "brave-search"}
    
    except Exception as e:
        logger.error(f"Brave Search health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Brave Search service unavailable: {str(e)}")
