from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.ai.enhanced_router import EnhancedAIRouter
from app.models.ai_budget import AIBudget
from pydantic import BaseModel


router = APIRouter()


class AIUsageResponse(BaseModel):
    tokens_used: int
    tokens_limit: int
    cost_gbp_used: float
    cost_gbp_limit: float
    percentage_used: float
    is_over_limit: bool


class BudgetUpdateRequest(BaseModel):
    daily_token_limit: int
    daily_cost_limit_gbp: float


@router.get("/usage", response_model=AIUsageResponse)
async def get_ai_usage(
    org_id: str,
    db: Session = Depends(get_db)
) -> AIUsageResponse:
    """Get current AI usage statistics for organization."""
    enhanced_router = EnhancedAIRouter(db)
    stats = await enhanced_router.get_usage_stats(org_id)
    
    if "error" in stats:
        raise HTTPException(status_code=500, detail=stats["error"])
    
    return AIUsageResponse(
        tokens_used=stats["tokens_used"],
        tokens_limit=stats["tokens_limit"],
        cost_gbp_used=stats["cost_gbp_used"],
        cost_gbp_limit=stats["cost_gbp_limit"],
        percentage_used=stats["percentage_used"],
        is_over_limit=stats["percentage_used"] > 100.0
    )


@router.post("/budget")
async def update_ai_budget(
    org_id: str,
    request: BudgetUpdateRequest,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Update AI budget limits for organization."""
    budget = db.query(AIBudget).filter(
        AIBudget.org_id == org_id,
        AIBudget.is_active == True
    ).first()
    
    if not budget:
        # Create new budget
        budget = AIBudget(
            id=f"budget_{org_id}",
            org_id=org_id,
            daily_token_limit=request.daily_token_limit,
            daily_cost_limit_gbp=request.daily_cost_limit_gbp
        )
        db.add(budget)
    else:
        # Update existing budget
        budget.daily_token_limit = request.daily_token_limit
        budget.daily_cost_limit_gbp = request.daily_cost_limit_gbp
    
    db.commit()
    return {"message": "Budget updated successfully"}


@router.get("/budget")
async def get_ai_budget(
    org_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current AI budget settings for organization."""
    budget = db.query(AIBudget).filter(
        AIBudget.org_id == org_id,
        AIBudget.is_active == True
    ).first()
    
    if not budget:
        return {
            "daily_token_limit": 100000,
            "daily_cost_limit_gbp": 50.0,
            "tokens_used_today": 0,
            "cost_gbp_today": 0.0
        }
    
    return {
        "daily_token_limit": budget.daily_token_limit,
        "daily_cost_limit_gbp": budget.daily_cost_limit_gbp,
        "tokens_used_today": budget.tokens_used_today,
        "cost_gbp_today": budget.cost_gbp_today,
        "current_date": budget.current_date.isoformat()
    }


@router.post("/reset-daily")
async def reset_daily_usage(
    org_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Reset daily usage counters (admin only)."""
    budget = db.query(AIBudget).filter(
        AIBudget.org_id == org_id,
        AIBudget.is_active == True
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget.reset_daily_usage()
    db.commit()
    
    return {"message": "Daily usage reset successfully"}
