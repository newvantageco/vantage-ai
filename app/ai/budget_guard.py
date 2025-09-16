from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session
from app.models.ai_budget import AIBudget
from app.core.config import get_settings


class BudgetGuard:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    async def get_or_create_budget(self, org_id: str) -> AIBudget:
        """Get or create AI budget for organization."""
        budget = self.db.query(AIBudget).filter(
            AIBudget.org_id == org_id,
            AIBudget.is_active == True
        ).first()
        
        if not budget:
            budget = AIBudget(
                id=f"budget_{org_id}",
                org_id=org_id
            )
            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
        
        # Reset daily usage if it's a new day
        from datetime import date
        if budget.current_date < date.today():
            budget.reset_daily_usage()
            self.db.commit()
        
        return budget

    def can_use_hosted_model(self, org_id: str, task_type: str) -> tuple[bool, str]:
        """
        Check if organization can use hosted model for given task.
        Returns (can_use, reason).
        """
        budget = self.db.query(AIBudget).filter(
            AIBudget.org_id == org_id,
            AIBudget.is_active == True
        ).first()
        
        if not budget:
            return True, "No budget limits set"
        
        # Critical tasks always use hosted model unless severely over limit
        critical_tasks = ["ads_copy", "brand_voice", "safety_check"]
        if task_type in critical_tasks:
            if budget.is_over_limit(self.settings.ai_budget_soft_limit_multiplier):
                return False, f"Budget exceeded by {self.settings.ai_budget_soft_limit_multiplier}x for critical task"
            return True, "Critical task - using hosted model"
        
        # Non-critical tasks degrade to open model when over soft limit
        if budget.is_over_limit(1.0):
            return False, "Budget exceeded - using open model"
        
        return True, "Within budget - using hosted model"

    def record_usage(self, org_id: str, tokens: int, cost_gbp: float) -> None:
        """Record AI usage for organization."""
        budget = self.get_or_create_budget(org_id)
        budget.add_usage(tokens, cost_gbp)
        self.db.commit()

    def get_usage_stats(self, org_id: str) -> dict:
        """Get current usage statistics for organization."""
        budget = self.db.query(AIBudget).filter(
            AIBudget.org_id == org_id,
            AIBudget.is_active == True
        ).first()
        
        if not budget:
            return {
                "tokens_used": 0,
                "tokens_limit": 100000,
                "cost_gbp_used": 0.0,
                "cost_gbp_limit": 50.0,
                "percentage_used": 0.0
            }
        
        token_percentage = (budget.tokens_used_today / budget.daily_token_limit) * 100
        cost_percentage = (budget.cost_gbp_today / budget.daily_cost_limit_gbp) * 100
        
        return {
            "tokens_used": budget.tokens_used_today,
            "tokens_limit": budget.daily_token_limit,
            "cost_gbp_used": budget.cost_gbp_today,
            "cost_gbp_limit": budget.daily_cost_limit_gbp,
            "percentage_used": max(token_percentage, cost_percentage)
        }
