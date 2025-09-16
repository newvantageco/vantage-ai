from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Integer, Float, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIBudget(Base):
    __tablename__ = "ai_budgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Daily limits
    daily_token_limit: Mapped[int] = mapped_column(Integer, default=100000, nullable=False)
    daily_cost_limit_gbp: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    
    # Current usage (reset daily)
    current_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    tokens_used_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_gbp_today: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Settings
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def is_over_limit(self, multiplier: float = 1.0) -> bool:
        """Check if current usage exceeds limits with optional multiplier."""
        token_limit = int(self.daily_token_limit * multiplier)
        cost_limit = self.daily_cost_limit_gbp * multiplier
        
        return (self.tokens_used_today > token_limit or 
                self.cost_gbp_today > cost_limit)

    def reset_daily_usage(self) -> None:
        """Reset daily usage counters (call at start of new day)."""
        self.current_date = date.today()
        self.tokens_used_today = 0
        self.cost_gbp_today = 0.0

    def add_usage(self, tokens: int, cost_gbp: float) -> None:
        """Add usage to current day counters."""
        self.tokens_used_today += tokens
        self.cost_gbp_today += cost_gbp
