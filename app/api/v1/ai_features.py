"""
AI Features API Endpoints
Exposes the new AI features: Performance Prediction, Content Variations, and Trend Analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.ai_service import AIService
from app.models.cms import UserAccount
from app.models.entities import Organization


router = APIRouter()


# Request/Response Models
class PerformancePredictionRequest(BaseModel):
    content: str = Field(..., description="Content to predict performance for")
    platform: str = Field(..., description="Target platform (facebook, instagram, twitter, linkedin)")
    scheduled_at: Optional[datetime] = Field(None, description="When the content will be posted")
    brand_guide_id: Optional[int] = Field(None, description="Brand guide ID for voice matching")


class ContentVariationsRequest(BaseModel):
    original_content: str = Field(..., description="Original content to create variations from")
    platforms: List[str] = Field(..., description="List of platforms to optimize for")
    target_audiences: List[str] = Field(..., description="List of target audiences")
    optimization_goals: List[str] = Field(..., description="List of optimization goals")
    brand_guide_id: Optional[int] = Field(None, description="Brand guide ID")
    max_variations_per_platform: int = Field(3, description="Maximum variations per platform")


class TrendAnalysisRequest(BaseModel):
    platform: str = Field(..., description="Platform to analyze trends for")
    days_back: int = Field(30, description="Number of days to look back")
    min_volume: int = Field(5, description="Minimum volume threshold for trends")


class HashtagVariationsRequest(BaseModel):
    content: str = Field(..., description="Content to generate hashtags for")
    platforms: List[str] = Field(..., description="List of platforms to optimize for")
    brand_guide_id: Optional[int] = Field(None, description="Brand guide ID")


class ToneVariationsRequest(BaseModel):
    content: str = Field(..., description="Content to create tone variations for")
    tones: List[str] = Field(..., description="List of tones to generate")
    brand_guide_id: Optional[int] = Field(None, description="Brand guide ID")


class ContentOptimizationRequest(BaseModel):
    platform: str = Field(..., description="Platform to optimize for")
    draft_content: str = Field(..., description="Content to optimize")
    brand_guide_id: Optional[int] = Field(None, description="Brand guide ID")


# API Endpoints
@router.post("/predict-performance")
async def predict_performance(
    request: PerformancePredictionRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Predict content performance using AI and historical data.
    """
    try:
        # Get user's organization
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with an organization"
            )
        
        ai_service = AIService(db)
        result = await ai_service.predict_performance(
            content=request.content,
            platform=request.platform,
            org_id=current_user.organization_id,
            scheduled_at=request.scheduled_at,
            brand_guide_id=request.brand_guide_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Performance prediction failed: {str(e)}"
        )


@router.post("/generate-variations")
async def generate_content_variations(
    request: ContentVariationsRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Generate content variations for multiple platforms and audiences.
    """
    try:
        ai_service = AIService(db)
        result = await ai_service.generate_content_variations(
            original_content=request.original_content,
            platforms=request.platforms,
            target_audiences=request.target_audiences,
            optimization_goals=request.optimization_goals,
            brand_guide_id=request.brand_guide_id,
            max_variations_per_platform=request.max_variations_per_platform
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content variations generation failed: {str(e)}"
        )


@router.post("/analyze-trends")
async def analyze_trends(
    request: TrendAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Analyze social media trends for an organization.
    """
    try:
        # Get user's organization
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with an organization"
            )
        
        ai_service = AIService(db)
        result = await ai_service.analyze_trends(
            org_id=current_user.organization_id,
            platform=request.platform,
            days_back=request.days_back,
            min_volume=request.min_volume
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trend analysis failed: {str(e)}"
        )


@router.post("/optimize-content")
async def optimize_content(
    request: ContentOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Optimize content for a specific platform using AI.
    """
    try:
        # Get user's organization
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with an organization"
            )
        
        ai_service = AIService(db)
        result = await ai_service.optimize_content(
            platform=request.platform,
            draft_content=request.draft_content,
            brand_guide_id=request.brand_guide_id,
            org_id=current_user.organization_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content optimization failed: {str(e)}"
        )


@router.post("/generate-hashtag-variations")
async def generate_hashtag_variations(
    request: HashtagVariationsRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Generate hashtag variations for different platforms.
    """
    try:
        ai_service = AIService(db)
        result = await ai_service.generate_hashtag_variations(
            content=request.content,
            platforms=request.platforms,
            brand_guide_id=request.brand_guide_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hashtag variations generation failed: {str(e)}"
        )


@router.post("/generate-tone-variations")
async def generate_tone_variations(
    request: ToneVariationsRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Generate content variations with different tones.
    """
    try:
        ai_service = AIService(db)
        result = await ai_service.generate_tone_variations(
            content=request.content,
            tones=request.tones,
            brand_guide_id=request.brand_guide_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tone variations generation failed: {str(e)}"
        )


@router.get("/performance-insights/{platform}")
async def get_performance_insights(
    platform: str,
    days_back: int = 30,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Get performance insights and patterns for an organization.
    """
    try:
        # Get user's organization
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with an organization"
            )
        
        ai_service = AIService(db)
        result = await ai_service.get_performance_insights(
            org_id=current_user.organization_id,
            platform=platform,
            days_back=days_back
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Performance insights failed: {str(e)}"
        )


@router.get("/feature-status")
async def get_feature_status(
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Get the status of AI features for the current user's organization.
    """
    try:
        # This would typically check feature gating based on subscription tier
        # For now, return the status of implemented features
        
        features = {
            "content_optimization": {
                "status": "available",
                "description": "AI-powered content optimization for different platforms"
            },
            "performance_prediction": {
                "status": "available", 
                "description": "Predict content performance using historical data and AI"
            },
            "content_variations": {
                "status": "available",
                "description": "Generate multiple content variations for different platforms and audiences"
            },
            "trend_analysis": {
                "status": "available",
                "description": "Analyze social media trends and provide insights"
            }
        }
        
        return {
            "success": True,
            "features": features,
            "organization_id": current_user.organization_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature status check failed: {str(e)}"
        )
