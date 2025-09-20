"""
Automation schemas
Pydantic models for automation rules, workflows, recommendations, and A/B testing
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.models.rules import RuleStatus
from app.models.automation import (
    WorkflowStatus, WorkflowTriggerType, WorkflowStepType,
    RecommendationType, RecommendationStatus,
    ABTestStatus, ABTestVariantStatus
)


# Rule Schemas
class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    trigger: str = Field(..., min_length=1, max_length=100)
    condition_json: Dict[str, Any] = Field(..., description="JSON logic condition")
    action_json: Dict[str, Any] = Field(..., description="JSON action definition")
    enabled: bool = Field(True)


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    condition_json: Optional[Dict[str, Any]] = Field(None, description="JSON logic condition")
    action_json: Optional[Dict[str, Any]] = Field(None, description="JSON action definition")
    enabled: Optional[bool] = None


class RuleResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str]
    trigger: str
    condition_json: Dict[str, Any]
    action_json: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RuleRunResponse(BaseModel):
    id: str
    rule_id: str
    status: RuleStatus
    last_run_at: Optional[datetime]
    meta_json: Optional[Dict[str, Any]]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowStepCreate(BaseModel):
    step_type: WorkflowStepType
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    config: Dict[str, Any] = Field(default_factory=dict)
    position: int = Field(..., ge=0)
    next_steps: List[int] = Field(default_factory=list, description="IDs of next steps")


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    trigger_type: WorkflowTriggerType
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    steps: List[WorkflowStepCreate] = Field(..., min_items=1)
    enabled: bool = Field(True)


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    trigger_config: Optional[Dict[str, Any]] = None
    steps: Optional[List[WorkflowStepCreate]] = None
    enabled: Optional[bool] = None


class WorkflowStepResponse(BaseModel):
    step_type: WorkflowStepType
    name: str
    description: Optional[str]
    config: Dict[str, Any]
    position: int
    next_steps: List[int]

    class Config:
        from_attributes = True


class WorkflowResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str]
    trigger_type: WorkflowTriggerType
    trigger_config: Dict[str, Any]
    steps: List[WorkflowStepResponse]
    status: WorkflowStatus
    enabled: bool
    last_run_at: Optional[datetime]
    run_count: int
    success_count: int
    failure_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: WorkflowStatus
    trigger_data: Optional[Dict[str, Any]]
    execution_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationUpdate(BaseModel):
    status: Optional[RecommendationStatus] = None
    implementation_data: Optional[Dict[str, Any]] = None


class RecommendationResponse(BaseModel):
    id: str
    org_id: str
    type: RecommendationType
    title: str
    description: str
    confidence_score: float
    data: Dict[str, Any]
    implementation_data: Optional[Dict[str, Any]]
    status: RecommendationStatus
    priority: int
    content_id: Optional[str]
    campaign_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# A/B Test Schemas
class ABTestVariantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    variant_data: Dict[str, Any] = Field(..., description="Variant configuration data")
    traffic_percentage: float = Field(..., ge=0.0, le=1.0)


class ABTestCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    hypothesis: str = Field(..., min_length=1, max_length=1000)
    test_type: str = Field(..., min_length=1, max_length=50)
    traffic_allocation: float = Field(0.5, ge=0.0, le=1.0)
    minimum_sample_size: int = Field(100, ge=10)
    significance_level: float = Field(0.05, ge=0.01, le=0.5)
    planned_duration_days: int = Field(7, ge=1, le=365)
    variants: List[ABTestVariantCreate] = Field(..., min_items=2, max_items=10)


class ABTestUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    hypothesis: Optional[str] = Field(None, min_length=1, max_length=1000)
    traffic_allocation: Optional[float] = Field(None, ge=0.0, le=1.0)
    minimum_sample_size: Optional[int] = Field(None, ge=10)
    significance_level: Optional[float] = Field(None, ge=0.01, le=0.5)
    planned_duration_days: Optional[int] = Field(None, ge=1, le=365)
    enabled: Optional[bool] = None


class ABTestVariantResponse(BaseModel):
    id: str
    ab_test_id: str
    name: str
    description: Optional[str]
    variant_data: Dict[str, Any]
    traffic_percentage: float
    status: ABTestVariantStatus
    impressions: int
    clicks: int
    conversions: int
    engagement_rate: float
    conversion_rate: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ABTestResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str]
    hypothesis: str
    test_type: str
    traffic_allocation: float
    minimum_sample_size: int
    significance_level: float
    status: ABTestStatus
    enabled: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    planned_duration_days: int
    winner_variant_id: Optional[str]
    confidence_level: Optional[float]
    p_value: Optional[float]
    created_at: datetime
    updated_at: datetime
    variants: List[ABTestVariantResponse] = []

    class Config:
        from_attributes = True


class ABTestResultResponse(BaseModel):
    id: str
    ab_test_id: str
    variant_id: str
    metric_name: str
    metric_value: float
    sample_size: int
    confidence_interval_lower: Optional[float]
    confidence_interval_upper: Optional[float]
    p_value: Optional[float]
    measured_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics and Dashboard Schemas
class AutomationDashboardResponse(BaseModel):
    total_rules: int
    active_rules: int
    total_workflows: int
    active_workflows: int
    pending_recommendations: int
    active_ab_tests: int
    recent_rule_runs: List[RuleRunResponse]
    recent_workflow_executions: List[WorkflowExecutionResponse]
    top_recommendations: List[RecommendationResponse]


class AutomationStatsResponse(BaseModel):
    period: str
    rules_executed: int
    workflows_executed: int
    recommendations_generated: int
    ab_tests_completed: int
    success_rate: float
    average_execution_time: float
    top_performing_rules: List[Dict[str, Any]]
    top_performing_workflows: List[Dict[str, Any]]


# Validation helpers
class AutomationValidator:
    @staticmethod
    def validate_workflow_steps(steps: List[WorkflowStepCreate]) -> List[WorkflowStepCreate]:
        """Validate workflow steps for proper flow and configuration."""
        if not steps:
            raise ValueError("Workflow must have at least one step")
        
        # Check for unique positions
        positions = [step.position for step in steps]
        if len(positions) != len(set(positions)):
            raise ValueError("Step positions must be unique")
        
        # Check for valid next_steps references
        valid_positions = set(positions)
        for step in steps:
            for next_step in step.next_steps:
                if next_step not in valid_positions:
                    raise ValueError(f"Invalid next step reference: {next_step}")
        
        return steps
    
    @staticmethod
    def validate_ab_test_variants(variants: List[ABTestVariantCreate]) -> List[ABTestVariantCreate]:
        """Validate A/B test variants for proper configuration."""
        if len(variants) < 2:
            raise ValueError("A/B test must have at least 2 variants")
        
        if len(variants) > 10:
            raise ValueError("A/B test cannot have more than 10 variants")
        
        # Check traffic allocation sums to 1.0
        total_traffic = sum(variant.traffic_percentage for variant in variants)
        if abs(total_traffic - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError("Variant traffic percentages must sum to 1.0")
        
        return variants
