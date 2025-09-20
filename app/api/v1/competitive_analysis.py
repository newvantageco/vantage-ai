"""
Competitive Analysis API Router
Handles competitor tracking, benchmarking, and competitive intelligence
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.cms import UserAccount
from app.services.competitive_analysis import CompetitiveAnalysisService

router = APIRouter()


class CompetitorCreate(BaseModel):
    """Schema for creating a competitor"""
    name: str
    handle: str
    platforms: List[str]
    industry: Optional[str] = None


class CompetitorResponse(BaseModel):
    """Schema for competitor response"""
    name: str
    handle: str
    platforms: List[str]
    industry: Optional[str] = None
    added_at: str


class BenchmarkRequest(BaseModel):
    """Schema for benchmarking request"""
    competitors: List[str]
    platforms: List[str]
    days: int = 30


@router.post("/competitive/competitors", response_model=CompetitorResponse)
async def add_competitor(
    competitor: CompetitorCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> CompetitorResponse:
    """
    Add a new competitor to track.
    """
    try:
        competitive_service = CompetitiveAnalysisService(db)
        
        result = competitive_service.add_competitor(
            org_id=current_user.organization_id,
            name=competitor.name,
            handle=competitor.handle,
            platforms=competitor.platforms,
            industry=competitor.industry
        )
        
        return CompetitorResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add competitor: {str(e)}"
        )


@router.get("/competitive/competitors/{competitor_handle}/metrics")
async def get_competitor_metrics(
    competitor_handle: str,
    platform: str = Query(..., description="Platform to analyze"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get metrics for a specific competitor.
    """
    try:
        competitive_service = CompetitiveAnalysisService(db)
        
        metrics = competitive_service.get_competitor_metrics(
            competitor_handle=competitor_handle,
            platform=platform,
            days=days
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get competitor metrics: {str(e)}"
        )


@router.post("/competitive/benchmark")
async def benchmark_against_competitors(
    request: BenchmarkRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Benchmark organization performance against competitors.
    """
    try:
        competitive_service = CompetitiveAnalysisService(db)
        
        benchmark_data = competitive_service.benchmark_against_competitors(
            org_id=current_user.organization_id,
            competitors=request.competitors,
            platforms=request.platforms,
            days=request.days
        )
        
        return benchmark_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to benchmark against competitors: {str(e)}"
        )


@router.get("/competitive/industry-benchmarks")
async def get_industry_benchmarks(
    industry: str = Query(..., description="Industry to analyze"),
    platforms: List[str] = Query(..., description="Platforms to analyze"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get industry benchmark data.
    """
    try:
        competitive_service = CompetitiveAnalysisService(db)
        
        benchmarks = competitive_service.get_industry_benchmarks(
            industry=industry,
            platforms=platforms,
            days=days
        )
        
        return benchmarks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get industry benchmarks: {str(e)}"
        )


@router.get("/competitive/content-gaps")
async def analyze_content_gaps(
    competitors: List[str] = Query(..., description="List of competitor handles"),
    platforms: List[str] = Query(..., description="Platforms to analyze"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze content gaps compared to competitors.
    """
    try:
        competitive_service = CompetitiveAnalysisService(db)
        
        content_gaps = competitive_service.analyze_content_gaps(
            org_id=current_user.organization_id,
            competitor_handles=competitors,
            platforms=platforms,
            days=days
        )
        
        return content_gaps
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze content gaps: {str(e)}"
        )


@router.get("/competitive/insights")
async def get_competitive_insights(
    competitors: List[str] = Query(..., description="List of competitor handles"),
    platforms: List[str] = Query(..., description="Platforms to analyze"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive competitive insights.
    """
    try:
        competitive_service = CompetitiveAnalysisService(db)
        
        insights = competitive_service.get_competitive_insights(
            org_id=current_user.organization_id,
            competitors=competitors,
            platforms=platforms,
            days=days
        )
        
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get competitive insights: {str(e)}"
        )


@router.get("/competitive/available-industries")
async def get_available_industries() -> List[Dict[str, str]]:
    """
    Get list of available industries for benchmarking.
    """
    industries = [
        {"key": "technology", "name": "Technology", "description": "Software, hardware, and tech services"},
        {"key": "retail", "name": "Retail", "description": "E-commerce and physical retail"},
        {"key": "healthcare", "name": "Healthcare", "description": "Medical and healthcare services"},
        {"key": "finance", "name": "Finance", "description": "Banking, fintech, and financial services"},
        {"key": "education", "name": "Education", "description": "Educational institutions and edtech"},
        {"key": "manufacturing", "name": "Manufacturing", "description": "Industrial and manufacturing"},
        {"key": "consulting", "name": "Consulting", "description": "Professional services and consulting"},
        {"key": "media", "name": "Media & Entertainment", "description": "Media, entertainment, and content"},
        {"key": "real_estate", "name": "Real Estate", "description": "Property and real estate services"},
        {"key": "travel", "name": "Travel & Hospitality", "description": "Travel, tourism, and hospitality"}
    ]
    
    return industries


@router.get("/competitive/competitor-suggestions")
async def get_competitor_suggestions(
    industry: Optional[str] = Query(None, description="Industry to get suggestions for"),
    platform: Optional[str] = Query(None, description="Platform to get suggestions for"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """
    Get suggested competitors based on industry and platform.
    """
    # Mock competitor suggestions - in reality you would use AI or data sources
    suggestions = [
        {"name": "TechCorp", "handle": "@techcorp", "platforms": ["linkedin", "twitter"], "industry": "technology"},
        {"name": "InnovateLabs", "handle": "@innovatelabs", "platforms": ["linkedin", "facebook"], "industry": "technology"},
        {"name": "RetailMax", "handle": "@retailmax", "platforms": ["instagram", "facebook"], "industry": "retail"},
        {"name": "HealthFirst", "handle": "@healthfirst", "platforms": ["linkedin", "twitter"], "industry": "healthcare"},
        {"name": "FinancePro", "handle": "@financepro", "platforms": ["linkedin", "twitter"], "industry": "finance"},
        {"name": "EduTech", "handle": "@edutech", "platforms": ["linkedin", "facebook"], "industry": "education"},
        {"name": "ManufacturingCo", "handle": "@manufacturingco", "platforms": ["linkedin"], "industry": "manufacturing"},
        {"name": "ConsultingGroup", "handle": "@consultinggroup", "platforms": ["linkedin", "twitter"], "industry": "consulting"},
        {"name": "MediaHouse", "handle": "@mediahouse", "platforms": ["instagram", "twitter", "facebook"], "industry": "media"},
        {"name": "RealEstatePro", "handle": "@realestatepro", "platforms": ["linkedin", "facebook"], "industry": "real_estate"},
        {"name": "TravelAgency", "handle": "@travelagency", "platforms": ["instagram", "facebook"], "industry": "travel"}
    ]
    
    # Filter by industry if specified
    if industry:
        suggestions = [s for s in suggestions if s["industry"] == industry]
    
    # Filter by platform if specified
    if platform:
        suggestions = [s for s in suggestions if platform in s["platforms"]]
    
    return suggestions[:10]  # Return top 10 suggestions


@router.get("/competitive/trending-topics")
async def get_trending_topics(
    industry: Optional[str] = Query(None, description="Industry to get topics for"),
    platforms: List[str] = Query(..., description="Platforms to analyze"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get trending topics in the industry and platforms.
    """
    # Mock trending topics - in reality you would use social media APIs
    trending_topics = {
        "technology": [
            "artificial intelligence", "machine learning", "cloud computing", "cybersecurity",
            "blockchain", "IoT", "5G", "quantum computing", "edge computing", "automation"
        ],
        "retail": [
            "e-commerce", "omnichannel", "personalization", "sustainability", "mobile commerce",
            "social commerce", "subscription models", "last-mile delivery", "inventory management"
        ],
        "healthcare": [
            "telemedicine", "digital health", "AI in healthcare", "patient engagement",
            "health data privacy", "mental health", "preventive care", "health equity"
        ]
    }
    
    topics = trending_topics.get(industry, trending_topics["technology"])
    
    return {
        "industry": industry,
        "platforms": platforms,
        "trending_topics": topics[:10],  # Top 10 topics
        "analysis_date": datetime.utcnow().isoformat(),
        "data_source": "social_media_analysis"
    }
