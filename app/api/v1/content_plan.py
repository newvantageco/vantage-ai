from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.content import BrandGuide
from app.services.model_router import ai_router

router = APIRouter(prefix="/content/plan", tags=["content-plan"])


class SuggestionOut(BaseModel):
    topic: str
    caption: str
    hashtags: List[str]


@router.get("/suggestions", response_model=List[SuggestionOut])
async def get_suggestions(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    channels: str = Query("", description="Comma-separated channel IDs"),
    brand_guide_id: Optional[str] = Query(None, description="Brand guide ID for context"),
    db: Session = Depends(get_db),
):
    """Generate 10 topic ideas based on brand pillars and date range."""
    
    # Get brand guide if provided
    guide = None
    if brand_guide_id:
        guide = db.get(BrandGuide, brand_guide_id)
    
    # Extract brand voice and pillars for context
    brand_context = ""
    if guide:
        if guide.voice:
            brand_context += f"Brand voice: {guide.voice}\n"
        if guide.audience:
            brand_context += f"Target audience: {guide.audience}\n"
        if guide.pillars:
            brand_context += f"Brand pillars: {guide.pillars}\n"
    
    # Generate suggestions using AI
    suggestions = []
    for i in range(10):
        prompt = f"""
        Generate a social media post idea for the date range {from_date} to {to_date}.
        {brand_context}
        
        Return JSON with:
        - topic: Brief topic title
        - caption: Engaging caption (UK English, max 200 words)
        - hashtags: Array of 5-8 relevant hashtags
        
        Make it relevant to the time period and brand context.
        """
        
        try:
            response = await ai_router.generate_caption(
                system="You are a creative social media content strategist. Always return valid JSON.",
                prompt=prompt
            )
            
            # Parse JSON response
            import json
            try:
                data = json.loads(response)
                suggestion = SuggestionOut(
                    topic=data.get("topic", f"Topic {i+1}"),
                    caption=data.get("caption", f"Caption for suggestion {i+1}"),
                    hashtags=data.get("hashtags", [])
                )
                suggestions.append(suggestion)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                suggestion = SuggestionOut(
                    topic=f"Topic {i+1}",
                    caption=response or f"Caption for suggestion {i+1}",
                    hashtags=[]
                )
                suggestions.append(suggestion)
        except Exception as e:
            # Fallback for AI errors
            suggestion = SuggestionOut(
                topic=f"Topic {i+1}",
                caption=f"Caption for suggestion {i+1}",
                hashtags=[]
            )
            suggestions.append(suggestion)
    
    return suggestions
