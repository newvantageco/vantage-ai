from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class RuleStatus(str, Enum):
    """Status of a rule run."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class Rule(Base):
    """Automation rules for triggering actions based on conditions."""
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Rule definition
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger: Mapped[str] = mapped_column(String(100), nullable=False)  # "post_performance", "weekly_brief_generated", etc.
    
    # JSON logic for conditions and actions
    condition_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    action_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # Rule state
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    runs: Mapped[list["RuleRun"]] = relationship(back_populates="rule", cascade="all, delete-orphan")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_rules_org_id", "org_id"),
        Index("ix_rules_trigger", "trigger"),
        Index("ix_rules_enabled", "enabled"),
    )


class RuleRun(Base):
    """Execution history of rule runs."""
    __tablename__ = "rule_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    rule_id: Mapped[str] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"), index=True)
    
    # Execution details
    status: Mapped[RuleStatus] = mapped_column(String(20), nullable=False, default=RuleStatus.PENDING)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Execution metadata
    meta_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)  # Error messages, execution context, etc.
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    rule: Mapped["Rule"] = relationship(back_populates="runs")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_rule_runs_rule_id", "rule_id"),
        Index("ix_rule_runs_status", "status"),
        Index("ix_rule_runs_last_run_at", "last_run_at"),
    )
