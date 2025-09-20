"""
Simple AI Content Generation API
A minimal AI endpoint without complex dependencies
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging

from app.api.deps import get_current_user
from app.models.cms import UserAccount

logger = logging.getLogger(__name__)
router = APIRouter()


class SimpleAIRequest(BaseModel):
    prompt: str
    content_type: str = "social_post"
    platform: str = "facebook"
    brand_voice: str = "professional"
    max_tokens: int = 150
    temperature: float = 0.7


class SimpleAIResponse(BaseModel):
    content: str
    content_type: str
    platform: str
    tokens_used: int
    cost_usd: float
    provider: str


@router.post("/ai/simple/generate", response_model=SimpleAIResponse)
async def generate_simple_ai_content(
    request: SimpleAIRequest,
    current_user: UserAccount = Depends(get_current_user)
) -> SimpleAIResponse:
    """
    Simple AI content generation without complex dependencies.
    For now, returns mock content until we set up real AI providers.
    """
    try:
        logger.info(f"AI generation request from user {current_user.email}: {request.prompt[:50]}...")
        
        # Use real AI service - this should integrate with your AI provider
        from app.services.ai_service import AIService
        
        ai_service = AIService()
        result = await ai_service.generate_content(
            prompt=request.prompt,
            platform=request.platform,
            content_type=request.content_type,
            brand_voice=request.brand_voice
        )
        
        return SimpleAIResponse(
            content=result.content,
            content_type=request.content_type,
            platform=request.platform,
            tokens_used=result.tokens_used,
            cost_usd=result.cost_usd,
            provider=result.provider
        )
        
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}"
        )


@router.get("/ai/simple/status")
async def get_ai_status():
    """Get AI service status"""
    return {
        "status": "operational",
        "providers": ["mock"],
        "features": ["content_generation", "platform_optimization"],
        "version": "1.0.0"
    }
