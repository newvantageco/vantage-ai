"""
Budget Guard Service

Enforces per-organization and per-user soft caps for AI usage with friendly
error messages and upgrade suggestions when limits are exceeded.
"""

from __future__ import annotations

import os
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.core.config import get_settings
from app.models.ai_budget import AIBudget, AIUsage
from app.models.cms import Organization, UserAccount


class LimitType(Enum):
    DAILY = "daily"
    MONTHLY = "monthly"


@dataclass
class BudgetLimits:
    """Budget limits for an entity (org or user)"""
    daily_tokens: int
    daily_cost_usd: float
    monthly_tokens: int
    monthly_cost_usd: float


@dataclass
class BudgetUsage:
    """Current usage for an entity"""
    daily_tokens_used: int
    daily_cost_used: float
    monthly_tokens_used: int
    monthly_cost_used: float
    daily_percentage: float
    monthly_percentage: float


@dataclass
class BudgetViolation:
    """Details about a budget violation"""
    is_violated: bool
    limit_type: Optional[LimitType]
    current_usage: float
    limit: float
    percentage: float
    friendly_message: str
    upgrade_suggestion: str


class BudgetGuard:
    """Service for enforcing AI usage budget limits"""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        
        # Default limits from environment or sensible defaults
        self.default_org_limits = BudgetLimits(
            daily_tokens=int(os.getenv("AI_ORG_DAILY_TOKEN_LIMIT", "100000")),
            daily_cost_usd=float(os.getenv("AI_ORG_DAILY_COST_LIMIT_USD", "50.0")),
            monthly_tokens=int(os.getenv("AI_ORG_MONTHLY_TOKEN_LIMIT", "2000000")),
            monthly_cost_usd=float(os.getenv("AI_ORG_MONTHLY_COST_LIMIT_USD", "1000.0"))
        )
        
        self.default_user_limits = BudgetLimits(
            daily_tokens=int(os.getenv("AI_USER_DAILY_TOKEN_LIMIT", "10000")),
            daily_cost_usd=float(os.getenv("AI_USER_DAILY_COST_LIMIT_USD", "5.0")),
            monthly_tokens=int(os.getenv("AI_USER_MONTHLY_TOKEN_LIMIT", "200000")),
            monthly_cost_usd=float(os.getenv("AI_USER_MONTHLY_COST_LIMIT_USD", "100.0"))
        )
    
    def _get_org_limits(self, org_id: str) -> BudgetLimits:
        """Get budget limits for an organization"""
        # Check if org has custom limits in database
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if org and hasattr(org, 'ai_limits') and org.ai_limits:
            # Custom limits stored in org.ai_limits JSON field
            limits_data = org.ai_limits
            return BudgetLimits(
                daily_tokens=limits_data.get("daily_tokens", self.default_org_limits.daily_tokens),
                daily_cost_usd=limits_data.get("daily_cost_usd", self.default_org_limits.daily_cost_usd),
                monthly_tokens=limits_data.get("monthly_tokens", self.default_org_limits.monthly_tokens),
                monthly_cost_usd=limits_data.get("monthly_cost_usd", self.default_org_limits.monthly_cost_usd)
            )
        
        return self.default_org_limits
    
    def _get_user_limits(self, user_id: str) -> BudgetLimits:
        """Get budget limits for a user"""
        # Check if user has custom limits in database
        user = self.db.query(UserAccount).filter(UserAccount.id == user_id).first()
        if user and hasattr(user, 'ai_limits') and user.ai_limits:
            # Custom limits stored in user.ai_limits JSON field
            limits_data = user.ai_limits
            return BudgetLimits(
                daily_tokens=limits_data.get("daily_tokens", self.default_user_limits.daily_tokens),
                daily_cost_usd=limits_data.get("daily_cost_usd", self.default_user_limits.daily_cost_usd),
                monthly_tokens=limits_data.get("monthly_tokens", self.default_user_limits.monthly_tokens),
                monthly_cost_usd=limits_data.get("monthly_cost_usd", self.default_user_limits.monthly_cost_usd)
            )
        
        return self.default_user_limits
    
    def _get_org_usage(self, org_id: str) -> BudgetUsage:
        """Get current usage for an organization"""
        today = date.today()
        month_start = today.replace(day=1)
        
        # Daily usage
        daily_usage = self.db.query(
            func.sum(AIUsage.tokens_used).label('tokens'),
            func.sum(AIUsage.cost_gbp).label('cost')
        ).filter(
            and_(
                AIUsage.org_id == org_id,
                func.date(AIUsage.created_at) == today
            )
        ).first()
        
        # Monthly usage
        monthly_usage = self.db.query(
            func.sum(AIUsage.tokens_used).label('tokens'),
            func.sum(AIUsage.cost_gbp).label('cost')
        ).filter(
            and_(
                AIUsage.org_id == org_id,
                AIUsage.created_at >= month_start
            )
        ).first()
        
        daily_tokens = daily_usage.tokens or 0
        daily_cost = daily_usage.cost or 0.0
        monthly_tokens = monthly_usage.tokens or 0
        monthly_cost = monthly_usage.cost or 0.0
        
        # Convert GBP to USD (rough conversion)
        daily_cost_usd = daily_cost * 1.25
        monthly_cost_usd = monthly_cost * 1.25
        
        limits = self._get_org_limits(org_id)
        
        return BudgetUsage(
            daily_tokens_used=daily_tokens,
            daily_cost_used=daily_cost_usd,
            monthly_tokens_used=monthly_tokens,
            monthly_cost_used=monthly_cost_usd,
            daily_percentage=(daily_tokens / limits.daily_tokens) * 100 if limits.daily_tokens > 0 else 0,
            monthly_percentage=(monthly_tokens / limits.monthly_tokens) * 100 if limits.monthly_tokens > 0 else 0
        )
    
    def _get_user_usage(self, user_id: str) -> BudgetUsage:
        """Get current usage for a user"""
        today = date.today()
        month_start = today.replace(day=1)
        
        # Daily usage
        daily_usage = self.db.query(
            func.sum(AIUsage.tokens_used).label('tokens'),
            func.sum(AIUsage.cost_gbp).label('cost')
        ).filter(
            and_(
                AIUsage.user_id == user_id,
                func.date(AIUsage.created_at) == today
            )
        ).first()
        
        # Monthly usage
        monthly_usage = self.db.query(
            func.sum(AIUsage.tokens_used).label('tokens'),
            func.sum(AIUsage.cost_gbp).label('cost')
        ).filter(
            and_(
                AIUsage.user_id == user_id,
                AIUsage.created_at >= month_start
            )
        ).first()
        
        daily_tokens = daily_usage.tokens or 0
        daily_cost = daily_usage.cost or 0.0
        monthly_tokens = monthly_usage.tokens or 0
        monthly_cost = monthly_usage.cost or 0.0
        
        # Convert GBP to USD (rough conversion)
        daily_cost_usd = daily_cost * 1.25
        monthly_cost_usd = monthly_cost * 1.25
        
        limits = self._get_user_limits(user_id)
        
        return BudgetUsage(
            daily_tokens_used=daily_tokens,
            daily_cost_used=daily_cost_usd,
            monthly_tokens_used=monthly_tokens,
            monthly_cost_used=monthly_cost_usd,
            daily_percentage=(daily_tokens / limits.daily_tokens) * 100 if limits.daily_tokens > 0 else 0,
            monthly_percentage=(monthly_tokens / limits.monthly_tokens) * 100 if limits.monthly_tokens > 0 else 0
        )
    
    def check_org_budget(self, org_id: str, estimated_tokens: int, estimated_cost_usd: float) -> BudgetViolation:
        """Check if organization can make an AI request"""
        limits = self._get_org_limits(org_id)
        usage = self._get_org_usage(org_id)
        
        # Check daily limits
        if (usage.daily_tokens_used + estimated_tokens > limits.daily_tokens or
            usage.daily_cost_used + estimated_cost_usd > limits.daily_cost_usd):
            
            daily_percentage = ((usage.daily_tokens_used + estimated_tokens) / limits.daily_tokens) * 100
            return BudgetViolation(
                is_violated=True,
                limit_type=LimitType.DAILY,
                current_usage=usage.daily_tokens_used + estimated_tokens,
                limit=limits.daily_tokens,
                percentage=daily_percentage,
                friendly_message=f"Daily AI usage limit reached ({daily_percentage:.1f}% of {limits.daily_tokens:,} tokens). Please try again tomorrow or upgrade your plan.",
                upgrade_suggestion="Upgrade to Pro plan for 5x higher daily limits and priority support."
            )
        
        # Check monthly limits
        if (usage.monthly_tokens_used + estimated_tokens > limits.monthly_tokens or
            usage.monthly_cost_used + estimated_cost_usd > limits.monthly_cost_usd):
            
            monthly_percentage = ((usage.monthly_tokens_used + estimated_tokens) / limits.monthly_tokens) * 100
            return BudgetViolation(
                is_violated=True,
                limit_type=LimitType.MONTHLY,
                current_usage=usage.monthly_tokens_used + estimated_tokens,
                limit=limits.monthly_tokens,
                percentage=monthly_percentage,
                friendly_message=f"Monthly AI usage limit reached ({monthly_percentage:.1f}% of {limits.monthly_tokens:,} tokens). Please upgrade your plan or wait until next month.",
                upgrade_suggestion="Upgrade to Enterprise plan for unlimited AI usage and dedicated support."
            )
        
        return BudgetViolation(
            is_violated=False,
            limit_type=None,
            current_usage=0,
            limit=0,
            percentage=0,
            friendly_message="",
            upgrade_suggestion=""
        )
    
    def check_user_budget(self, user_id: str, estimated_tokens: int, estimated_cost_usd: float) -> BudgetViolation:
        """Check if user can make an AI request"""
        limits = self._get_user_limits(user_id)
        usage = self._get_user_usage(user_id)
        
        # Check daily limits
        if (usage.daily_tokens_used + estimated_tokens > limits.daily_tokens or
            usage.daily_cost_used + estimated_cost_usd > limits.daily_cost_usd):
            
            daily_percentage = ((usage.daily_tokens_used + estimated_tokens) / limits.daily_tokens) * 100
            return BudgetViolation(
                is_violated=True,
                limit_type=LimitType.DAILY,
                current_usage=usage.daily_tokens_used + estimated_tokens,
                limit=limits.daily_tokens,
                percentage=daily_percentage,
                friendly_message=f"Your daily AI usage limit reached ({daily_percentage:.1f}% of {limits.daily_tokens:,} tokens). Please try again tomorrow.",
                upgrade_suggestion="Ask your admin to upgrade the organization plan for higher limits."
            )
        
        # Check monthly limits
        if (usage.monthly_tokens_used + estimated_tokens > limits.monthly_tokens or
            usage.monthly_cost_used + estimated_cost_usd > limits.monthly_cost_usd):
            
            monthly_percentage = ((usage.monthly_tokens_used + estimated_tokens) / limits.monthly_tokens) * 100
            return BudgetViolation(
                is_violated=True,
                limit_type=LimitType.MONTHLY,
                current_usage=usage.monthly_tokens_used + estimated_tokens,
                limit=limits.monthly_tokens,
                percentage=monthly_percentage,
                friendly_message=f"Your monthly AI usage limit reached ({monthly_percentage:.1f}% of {limits.monthly_tokens:,} tokens). Please ask your admin to upgrade the plan.",
                upgrade_suggestion="Contact your admin to upgrade to a higher plan with increased limits."
            )
        
        return BudgetViolation(
            is_violated=False,
            limit_type=None,
            current_usage=0,
            limit=0,
            percentage=0,
            friendly_message="",
            upgrade_suggestion=""
        )
    
    def record_usage(
        self, 
        org_id: str, 
        user_id: str, 
        tokens_used: int, 
        cost_gbp: float,
        model_name: Optional[str] = None,
        operation_type: Optional[str] = None
    ) -> None:
        """Record AI usage for billing and tracking"""
        usage_record = AIUsage(
            id=f"usage_{org_id}_{user_id}_{int(datetime.utcnow().timestamp())}",
            org_id=org_id,
            user_id=user_id,
            tokens_used=tokens_used,
            cost_gbp=cost_gbp,
            model_name=model_name,
            operation_type=operation_type
        )
        
        self.db.add(usage_record)
        self.db.commit()
    
    def get_org_budget_status(self, org_id: str) -> Dict[str, Any]:
        """Get comprehensive budget status for an organization"""
        limits = self._get_org_limits(org_id)
        usage = self._get_org_usage(org_id)
        
        return {
            "limits": {
                "daily_tokens": limits.daily_tokens,
                "daily_cost_usd": limits.daily_cost_usd,
                "monthly_tokens": limits.monthly_tokens,
                "monthly_cost_usd": limits.monthly_cost_usd
            },
            "usage": {
                "daily_tokens_used": usage.daily_tokens_used,
                "daily_cost_used": usage.daily_cost_used,
                "monthly_tokens_used": usage.monthly_tokens_used,
                "monthly_cost_used": usage.monthly_cost_used,
                "daily_percentage": usage.daily_percentage,
                "monthly_percentage": usage.monthly_percentage
            },
            "status": {
                "daily_remaining": max(0, limits.daily_tokens - usage.daily_tokens_used),
                "monthly_remaining": max(0, limits.monthly_tokens - usage.monthly_tokens_used),
                "daily_cost_remaining": max(0, limits.daily_cost_usd - usage.daily_cost_used),
                "monthly_cost_remaining": max(0, limits.monthly_cost_usd - usage.monthly_cost_used)
            }
        }
    
    def get_user_budget_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive budget status for a user"""
        limits = self._get_user_limits(user_id)
        usage = self._get_user_usage(user_id)
        
        return {
            "limits": {
                "daily_tokens": limits.daily_tokens,
                "daily_cost_usd": limits.daily_cost_usd,
                "monthly_tokens": limits.monthly_tokens,
                "monthly_cost_usd": limits.monthly_cost_usd
            },
            "usage": {
                "daily_tokens_used": usage.daily_tokens_used,
                "daily_cost_used": usage.daily_cost_used,
                "monthly_tokens_used": usage.monthly_tokens_used,
                "monthly_cost_used": usage.monthly_cost_used,
                "daily_percentage": usage.daily_percentage,
                "monthly_percentage": usage.monthly_percentage
            },
            "status": {
                "daily_remaining": max(0, limits.daily_tokens - usage.daily_tokens_used),
                "monthly_remaining": max(0, limits.monthly_tokens - usage.monthly_tokens_used),
                "daily_cost_remaining": max(0, limits.daily_cost_usd - usage.daily_cost_used),
                "monthly_cost_remaining": max(0, limits.monthly_cost_usd - usage.monthly_cost_used)
            }
        }
    
    def can_make_request(
        self, 
        org_id: str, 
        user_id: str, 
        estimated_tokens: int, 
        estimated_cost_usd: float
    ) -> Tuple[bool, Optional[BudgetViolation]]:
        """
        Check if a request can be made, considering both org and user limits.
        Returns (can_make_request, violation_details)
        """
        # Check organization limits first
        org_violation = self.check_org_budget(org_id, estimated_tokens, estimated_cost_usd)
        if org_violation.is_violated:
            return False, org_violation
        
        # Check user limits
        user_violation = self.check_user_budget(user_id, estimated_tokens, estimated_cost_usd)
        if user_violation.is_violated:
            return False, user_violation
        
        return True, None
