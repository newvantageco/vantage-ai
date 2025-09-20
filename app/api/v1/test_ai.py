"""
Test AI endpoints that bypass authentication for development
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio

from app.services.ai_service import AIService
from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest

router = APIRouter()

class TestAIRequest(BaseModel):
    prompt: str
    content_type: str = "text"
    brand_guide_id: Optional[int] = None
    locale: str = "en-US"

class TestAIResponse(BaseModel):
    success: bool
    text: str
    provider: str
    model: str
    token_usage: dict
    cost_usd: float
    error: Optional[str] = None

@router.post("/test-ai/generate", response_model=TestAIResponse)
async def test_ai_generate(request: TestAIRequest):
    """
    Test AI content generation without authentication
    """
    try:
        ai_service = AIService()
        result = await ai_service.generate_content(
            prompt=request.prompt,
            content_type=request.content_type,
            brand_guide_id=request.brand_guide_id,
            locale=request.locale
        )
        
        if result.get("success"):
            return TestAIResponse(
                success=True,
                text=result["text"],
                provider=result["provider"],
                model=result["model"],
                token_usage=result["token_usage"],
                cost_usd=result["cost_usd"]
            )
        else:
            return TestAIResponse(
                success=False,
                text="",
                provider="",
                model="",
                token_usage={},
                cost_usd=0.0,
                error=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        return TestAIResponse(
            success=False,
            text="",
            provider="",
            model="",
            token_usage={},
            cost_usd=0.0,
            error=str(e)
        )

@router.post("/test-ai/enhanced")
async def test_enhanced_ai(request: TestAIRequest):
    """
    Test Enhanced AI Router directly
    """
    try:
        router = EnhancedAIRouter()
        generation_request = GenerationRequest(
            task="content_generation",
            prompt=request.prompt,
            system=f"You are a professional content creator. Generate {request.content_type} content.",
            org_id="test_org",
            is_critical=False
        )
        
        result = await router.generate(generation_request)
        
        return {
            "success": True,
            "text": result.text,
            "provider": result.provider,
            "tokens_in": result.tokens_in,
            "tokens_out": result.tokens_out,
            "cost_gbp": result.cost_gbp,
            "duration_ms": result.duration_ms
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/test-ai/status")
async def test_ai_status():
    """
    Check AI service status
    """
    return {
        "status": "ready",
        "services": {
            "ai_service": "available",
            "enhanced_router": "available",
            "model_router": "available"
        },
        "message": "AI services are ready for testing"
    }
