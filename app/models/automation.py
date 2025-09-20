from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Index, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class WorkflowStatus(str, Enum):
    """Status of a workflow."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowTriggerType(str, Enum):
    """Types of workflow triggers."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    WEBHOOK = "webhook"


class WorkflowStepType(str, Enum):
    """Types of workflow steps."""
    CONDITION = "condition"
    ACTION = "action"
    DELAY = "delay"
    WEBHOOK = "webhook"
    AI_TASK = "ai_task"
    NOTIFICATION = "notification"


class RecommendationType(str, Enum):
    """Types of smart recommendations."""
    CONTENT_OPTIMIZATION = "content_optimization"
    POSTING_TIME = "posting_time"
    HASHTAG_SUGGESTION = "hashtag_suggestion"
    AUDIENCE_TARGETING = "audience_targeting"
    BUDGET_ALLOCATION = "budget_allocation"
    CONTENT_VARIATION = "content_variation"


class RecommendationStatus(str, Enum):
    """Status of recommendations."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    EXPIRED = "expired"


class ABTestStatus(str, Enum):
    """Status of A/B tests."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ABTestVariantStatus(str, Enum):
    """Status of A/B test variants."""
    ACTIVE = "active"
    WINNER = "winner"
    LOSER = "loser"
    PAUSED = "paused"


class Workflow(Base):
    """Workflow automation definitions."""
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Workflow definition
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[WorkflowTriggerType] = mapped_column(String(20), nullable=False)
    trigger_config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    
    # Workflow steps (JSON array of step definitions)
    steps: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    
    # Workflow state
    status: Mapped[WorkflowStatus] = mapped_column(String(20), nullable=False, default=WorkflowStatus.DRAFT)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Execution tracking
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    run_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions: Mapped[List["WorkflowExecution"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_workflows_org_id", "org_id"),
        Index("ix_workflows_status", "status"),
        Index("ix_workflows_trigger_type", "trigger_type"),
    )


class WorkflowExecution(Base):
    """Workflow execution history."""
    __tablename__ = "workflow_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), index=True)
    
    # Execution details
    status: Mapped[WorkflowStatus] = mapped_column(String(20), nullable=False, default=WorkflowStatus.DRAFT)
    trigger_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    execution_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="executions")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_workflow_executions_workflow_id", "workflow_id"),
        Index("ix_workflow_executions_status", "status"),
        Index("ix_workflow_executions_started_at", "started_at"),
    )


class Recommendation(Base):
    """Smart recommendations for content optimization."""
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Recommendation details
    type: Mapped[RecommendationType] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    
    # Recommendation data
    data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    implementation_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Status and tracking
    status: Mapped[RecommendationStatus] = mapped_column(String(20), nullable=False, default=RecommendationStatus.PENDING)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # 1-5 scale
    
    # Context
    content_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_recommendations_org_id", "org_id"),
        Index("ix_recommendations_type", "type"),
        Index("ix_recommendations_status", "status"),
        Index("ix_recommendations_priority", "priority"),
        Index("ix_recommendations_created_at", "created_at"),
    )


class ABTest(Base):
    """A/B test definitions."""
    __tablename__ = "ab_tests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Test definition
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Test configuration
    test_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "content", "timing", "audience", etc.
    traffic_allocation: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    minimum_sample_size: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    significance_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.05)
    
    # Test state
    status: Mapped[ABTestStatus] = mapped_column(String(20), nullable=False, default=ABTestStatus.DRAFT)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timing
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    planned_duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    
    # Results
    winner_variant_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    confidence_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    p_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variants: Mapped[List["ABTestVariant"]] = relationship(back_populates="ab_test", cascade="all, delete-orphan")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_ab_tests_org_id", "org_id"),
        Index("ix_ab_tests_status", "status"),
        Index("ix_ab_tests_test_type", "test_type"),
        Index("ix_ab_tests_start_date", "start_date"),
    )


class ABTestVariant(Base):
    """A/B test variants."""
    __tablename__ = "ab_test_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ab_test_id: Mapped[str] = mapped_column(ForeignKey("ab_tests.id", ondelete="CASCADE"), index=True)
    
    # Variant details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    variant_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    
    # Traffic allocation
    traffic_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    
    # Status
    status: Mapped[ABTestVariantStatus] = mapped_column(String(20), nullable=False, default=ABTestVariantStatus.ACTIVE)
    
    # Performance metrics
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conversions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    conversion_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ab_test: Mapped["ABTest"] = relationship(back_populates="variants")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_ab_test_variants_ab_test_id", "ab_test_id"),
        Index("ix_ab_test_variants_status", "status"),
    )


class ABTestResult(Base):
    """A/B test results and metrics."""
    __tablename__ = "ab_test_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ab_test_id: Mapped[str] = mapped_column(ForeignKey("ab_tests.id", ondelete="CASCADE"), index=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("ab_test_variants.id", ondelete="CASCADE"), index=True)
    
    # Result data
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Statistical data
    confidence_interval_lower: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_interval_upper: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    p_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timing
    measured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ab_test_results_ab_test_id", "ab_test_id"),
        Index("ix_ab_test_results_variant_id", "variant_id"),
        Index("ix_ab_test_results_metric_name", "metric_name"),
        Index("ix_ab_test_results_measured_at", "measured_at"),
    )
