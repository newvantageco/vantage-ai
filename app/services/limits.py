from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models.billing import OrganizationBilling, PlanTier
from app.models.entities import Organization, Channel, UserAccount
from app.models.content import ContentItem, Campaign, Schedule
from app.models.ai_budget import AIUsage

logger = logging.getLogger(__name__)


class LimitType(str, Enum):
    POSTS_PER_MONTH = "posts_per_month"
    CHANNELS = "channels"
    USERS = "users"
    CAMPAIGNS = "campaigns"
    CONTENT_ITEMS = "content_items"
    AI_GENERATIONS = "ai_generations"


class LimitCheckResult:
    """Result of a limit check."""
    
    def __init__(self, allowed: bool, current: int, limit: int, limit_type: LimitType):
        self.allowed = allowed
        self.current = current
        self.limit = limit
        self.limit_type = limit_type
        self.remaining = max(0, limit - current)
        self.usage_percentage = (current / limit * 100) if limit > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "current": self.current,
            "limit": self.limit,
            "remaining": self.remaining,
            "usage_percentage": round(self.usage_percentage, 2),
            "limit_type": self.limit_type.value
        }


class LimitsService:
    """Service for checking organization limits against their billing plan."""
    
    # Plan limits mapping
    PLAN_LIMITS = {
        PlanTier.STARTER: {
            LimitType.POSTS_PER_MONTH: 50,
            LimitType.CHANNELS: 3,
            LimitType.USERS: 2,
            LimitType.CAMPAIGNS: 5,
            LimitType.CONTENT_ITEMS: 100,
            LimitType.AI_GENERATIONS: 200,
        },
        PlanTier.GROWTH: {
            LimitType.POSTS_PER_MONTH: 200,
            LimitType.CHANNELS: 10,
            LimitType.USERS: 5,
            LimitType.CAMPAIGNS: 20,
            LimitType.CONTENT_ITEMS: 500,
            LimitType.AI_GENERATIONS: 1000,
        },
        PlanTier.PRO: {
            LimitType.POSTS_PER_MONTH: 1000,
            LimitType.CHANNELS: 50,
            LimitType.USERS: 25,
            LimitType.CAMPAIGNS: 100,
            LimitType.CONTENT_ITEMS: 2500,
            LimitType.AI_GENERATIONS: 5000,
        },
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_plan_limits(self, plan: PlanTier) -> Dict[LimitType, int]:
        """Get limits for a specific plan."""
        return self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS[PlanTier.STARTER])
    
    def get_organization_plan(self, org_id: str) -> PlanTier:
        """Get the current plan for an organization."""
        billing = self.db.query(OrganizationBilling).filter(
            OrganizationBilling.org_id == org_id
        ).first()
        
        if not billing:
            # Default to starter plan if no billing record
            return PlanTier.STARTER
        
        return billing.plan
    
    def check_posts_per_month_limit(self, org_id: str) -> LimitCheckResult:
        """Check if organization is within posts per month limit."""
        plan = self.get_organization_plan(org_id)
        limits = self.get_plan_limits(plan)
        limit = limits[LimitType.POSTS_PER_MONTH]
        
        # Count posts scheduled in the current month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current = self.db.query(Schedule).join(Channel).filter(
            and_(
                Channel.org_id == org_id,
                Schedule.scheduled_at >= month_start,
                Schedule.scheduled_at < now
            )
        ).count()
        
        return LimitCheckResult(
            allowed=current < limit,
            current=current,
            limit=limit,
            limit_type=LimitType.POSTS_PER_MONTH
        )
    
    def check_channels_limit(self, org_id: str) -> LimitCheckResult:
        """Check if organization is within channels limit."""
        plan = self.get_organization_plan(org_id)
        limits = self.get_plan_limits(plan)
        limit = limits[LimitType.CHANNELS]
        
        current = self.db.query(Channel).filter(Channel.org_id == org_id).count()
        
        return LimitCheckResult(
            allowed=current < limit,
            current=current,
            limit=limit,
            limit_type=LimitType.CHANNELS
        )
    
    def check_users_limit(self, org_id: str) -> LimitCheckResult:
        """Check if organization is within users limit."""
        plan = self.get_organization_plan(org_id)
        limits = self.get_plan_limits(plan)
        limit = limits[LimitType.USERS]
        
        current = self.db.query(UserAccount).filter(UserAccount.org_id == org_id).count()
        
        return LimitCheckResult(
            allowed=current < limit,
            current=current,
            limit=limit,
            limit_type=LimitType.USERS
        )
    
    def check_campaigns_limit(self, org_id: str) -> LimitCheckResult:
        """Check if organization is within campaigns limit."""
        plan = self.get_organization_plan(org_id)
        limits = self.get_plan_limits(plan)
        limit = limits[LimitType.CAMPAIGNS]
        
        current = self.db.query(Campaign).filter(Campaign.org_id == org_id).count()
        
        return LimitCheckResult(
            allowed=current < limit,
            current=current,
            limit=limit,
            limit_type=LimitType.CAMPAIGNS
        )
    
    def check_content_items_limit(self, org_id: str) -> LimitCheckResult:
        """Check if organization is within content items limit."""
        plan = self.get_organization_plan(org_id)
        limits = self.get_plan_limits(plan)
        limit = limits[LimitType.CONTENT_ITEMS]
        
        current = self.db.query(ContentItem).filter(ContentItem.org_id == org_id).count()
        
        return LimitCheckResult(
            allowed=current < limit,
            current=current,
            limit=limit,
            limit_type=LimitType.CONTENT_ITEMS
        )
    
    def check_ai_generations_limit(self, org_id: str) -> LimitCheckResult:
        """Check if organization is within AI generations limit."""
        plan = self.get_organization_plan(org_id)
        limits = self.get_plan_limits(plan)
        limit = limits[LimitType.AI_GENERATIONS]
        
        # Count AI usage in the current month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current = self.db.query(func.sum(AIUsage.tokens_used)).filter(
            and_(
                AIUsage.org_id == org_id,
                AIUsage.created_at >= month_start,
                AIUsage.created_at < now
            )
        ).scalar() or 0
        
        return LimitCheckResult(
            allowed=current < limit,
            current=current,
            limit=limit,
            limit_type=LimitType.AI_GENERATIONS
        )
    
    def check_limit(self, org_id: str, limit_type: LimitType) -> LimitCheckResult:
        """Check a specific limit type for an organization."""
        if limit_type == LimitType.POSTS_PER_MONTH:
            return self.check_posts_per_month_limit(org_id)
        elif limit_type == LimitType.CHANNELS:
            return self.check_channels_limit(org_id)
        elif limit_type == LimitType.USERS:
            return self.check_users_limit(org_id)
        elif limit_type == LimitType.CAMPAIGNS:
            return self.check_campaigns_limit(org_id)
        elif limit_type == LimitType.CONTENT_ITEMS:
            return self.check_content_items_limit(org_id)
        elif limit_type == LimitType.AI_GENERATIONS:
            return self.check_ai_generations_limit(org_id)
        else:
            raise ValueError(f"Unknown limit type: {limit_type}")
    
    def check_all_limits(self, org_id: str) -> Dict[LimitType, LimitCheckResult]:
        """Check all limits for an organization."""
        results = {}
        for limit_type in LimitType:
            results[limit_type] = self.check_limit(org_id, limit_type)
        return results
    
    def can_perform_action(self, org_id: str, limit_type: LimitType) -> bool:
        """Check if an action can be performed without exceeding limits."""
        result = self.check_limit(org_id, limit_type)
        return result.allowed
    
    def get_usage_summary(self, org_id: str) -> Dict[str, Any]:
        """Get a summary of current usage vs limits."""
        plan = self.get_organization_plan(org_id)
        limits = self.get_plan_limits(plan)
        results = self.check_all_limits(org_id)
        
        return {
            "org_id": org_id,
            "plan": plan.value,
            "limits": {lt.value: limits[lt] for lt in LimitType},
            "usage": {lt.value: results[lt].to_dict() for lt in LimitType},
            "overall_status": "within_limits" if all(r.allowed for r in results.values()) else "over_limits"
        }
    
    def enforce_limit(self, org_id: str, limit_type: LimitType) -> None:
        """Enforce a limit by raising an exception if exceeded."""
        result = self.check_limit(org_id, limit_type)
        if not result.allowed:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Limit exceeded",
                    "limit_type": limit_type.value,
                    "current": result.current,
                    "limit": result.limit,
                    "message": f"You have reached your {limit_type.value} limit of {result.limit}. Please upgrade your plan to continue."
                }
            )
    
    def get_remaining_usage(self, org_id: str, limit_type: LimitType) -> int:
        """Get remaining usage for a specific limit type."""
        result = self.check_limit(org_id, limit_type)
        return result.remaining
    
    def is_near_limit(self, org_id: str, limit_type: LimitType, threshold: float = 0.8) -> bool:
        """Check if usage is near the limit (above threshold percentage)."""
        result = self.check_limit(org_id, limit_type)
        return result.usage_percentage >= (threshold * 100)
    
    def get_limit_warnings(self, org_id: str, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Get warnings for limits that are near or exceeded."""
        warnings = []
        results = self.check_all_limits(org_id)
        
        for limit_type, result in results.items():
            if not result.allowed:
                warnings.append({
                    "type": "exceeded",
                    "limit_type": limit_type.value,
                    "current": result.current,
                    "limit": result.limit,
                    "message": f"You have exceeded your {limit_type.value} limit of {result.limit}."
                })
            elif result.usage_percentage >= (threshold * 100):
                warnings.append({
                    "type": "warning",
                    "limit_type": limit_type.value,
                    "current": result.current,
                    "limit": result.limit,
                    "usage_percentage": result.usage_percentage,
                    "message": f"You are using {result.usage_percentage:.1f}% of your {limit_type.value} limit."
                })
        
        return warnings


# Convenience function for dependency injection
def get_limits_service(db: Session) -> LimitsService:
    """Get a limits service instance."""
    return LimitsService(db)
