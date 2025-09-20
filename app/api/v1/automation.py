"""
Automation API endpoints
Handles automation rules, workflows, recommendations, and A/B testing
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, desc

from app.api.deps import get_db, get_current_user, get_current_organization
from app.models.cms import UserAccount as User
from app.models.entities import Organization
from app.models.rules import Rule, RuleRun, RuleStatus
from app.models.automation import (
    Workflow, WorkflowExecution, WorkflowStatus, WorkflowTriggerType,
    Recommendation, RecommendationType, RecommendationStatus,
    ABTest, ABTestVariant, ABTestResult, ABTestStatus, ABTestVariantStatus
)
from app.schemas.automation import (
    RuleCreate, RuleUpdate, RuleResponse, RuleRunResponse,
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowExecutionResponse,
    RecommendationResponse, RecommendationUpdate,
    ABTestCreate, ABTestUpdate, ABTestResponse, ABTestVariantResponse,
    ABTestResultResponse
)
from app.services.automation import AutomationService
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


# Rules Management
@router.get("/rules", response_model=List[RuleResponse])
async def get_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    enabled_only: bool = Query(False),
    trigger: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get automation rules for the organization."""
    query = select(Rule).where(Rule.org_id == current_org.id)
    
    if enabled_only:
        query = query.where(Rule.enabled == True)
    
    if trigger:
        query = query.where(Rule.trigger == trigger)
    
    query = query.order_by(desc(Rule.created_at)).offset(skip).limit(limit)
    
    rules = db.execute(query).scalars().all()
    return rules


@router.post("/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: RuleCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Create a new automation rule."""
    automation_service = AutomationService(db)
    rule = await automation_service.create_rule(current_org.id, rule_data)
    return rule


@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get a specific automation rule."""
    rule = db.execute(
        select(Rule).where(
            and_(Rule.id == rule_id, Rule.org_id == current_org.id)
        )
    ).scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return rule


@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: str,
    rule_data: RuleUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Update an automation rule."""
    automation_service = AutomationService(db)
    rule = await automation_service.update_rule(rule_id, current_org.id, rule_data)
    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Delete an automation rule."""
    automation_service = AutomationService(db)
    await automation_service.delete_rule(rule_id, current_org.id)


@router.post("/rules/{rule_id}/toggle", response_model=RuleResponse)
async def toggle_rule(
    rule_id: str,
    enabled: bool,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Enable or disable an automation rule."""
    automation_service = AutomationService(db)
    rule = await automation_service.toggle_rule(rule_id, current_org.id, enabled)
    return rule


@router.get("/rules/{rule_id}/runs", response_model=List[RuleRunResponse])
async def get_rule_runs(
    rule_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[RuleStatus] = Query(None),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get execution history for a rule."""
    # Verify rule belongs to organization
    rule = db.execute(
        select(Rule).where(
            and_(Rule.id == rule_id, Rule.org_id == current_org.id)
        )
    ).scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    query = select(RuleRun).where(RuleRun.rule_id == rule_id)
    
    if status:
        query = query.where(RuleRun.status == status)
    
    query = query.order_by(desc(RuleRun.last_run_at)).offset(skip).limit(limit)
    
    runs = db.execute(query).scalars().all()
    return runs


# Workflow Management
@router.get("/workflows", response_model=List[WorkflowResponse])
async def get_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[WorkflowStatus] = Query(None),
    trigger_type: Optional[WorkflowTriggerType] = Query(None),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get workflows for the organization."""
    query = select(Workflow).where(Workflow.org_id == current_org.id)
    
    if status:
        query = query.where(Workflow.status == status)
    
    if trigger_type:
        query = query.where(Workflow.trigger_type == trigger_type)
    
    query = query.order_by(desc(Workflow.created_at)).offset(skip).limit(limit)
    
    workflows = db.execute(query).scalars().all()
    return workflows


@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Create a new workflow."""
    automation_service = AutomationService(db)
    workflow = await automation_service.create_workflow(current_org.id, workflow_data)
    return workflow


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get a specific workflow."""
    workflow = db.execute(
        select(Workflow).where(
            and_(Workflow.id == workflow_id, Workflow.org_id == current_org.id)
        )
    ).scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Update a workflow."""
    automation_service = AutomationService(db)
    workflow = await automation_service.update_workflow(workflow_id, current_org.id, workflow_data)
    return workflow


@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Delete a workflow."""
    automation_service = AutomationService(db)
    await automation_service.delete_workflow(workflow_id, current_org.id)


@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    trigger_data: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Manually execute a workflow."""
    automation_service = AutomationService(db)
    execution = await automation_service.execute_workflow(workflow_id, current_org.id, trigger_data)
    return execution


@router.get("/workflows/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def get_workflow_executions(
    workflow_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[WorkflowStatus] = Query(None),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get execution history for a workflow."""
    # Verify workflow belongs to organization
    workflow = db.execute(
        select(Workflow).where(
            and_(Workflow.id == workflow_id, Workflow.org_id == current_org.id)
        )
    ).scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    query = select(WorkflowExecution).where(WorkflowExecution.workflow_id == workflow_id)
    
    if status:
        query = query.where(WorkflowExecution.status == status)
    
    query = query.order_by(desc(WorkflowExecution.started_at)).offset(skip).limit(limit)
    
    executions = db.execute(query).scalars().all()
    return executions


# Recommendations
@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[RecommendationType] = Query(None),
    status: Optional[RecommendationStatus] = Query(None),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get smart recommendations for the organization."""
    query = select(Recommendation).where(Recommendation.org_id == current_org.id)
    
    if type:
        query = query.where(Recommendation.type == type)
    
    if status:
        query = query.where(Recommendation.status == status)
    
    if min_confidence is not None:
        query = query.where(Recommendation.confidence_score >= min_confidence)
    
    query = query.order_by(desc(Recommendation.priority), desc(Recommendation.confidence_score)).offset(skip).limit(limit)
    
    recommendations = db.execute(query).scalars().all()
    return recommendations


@router.put("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
async def update_recommendation(
    recommendation_id: str,
    recommendation_data: RecommendationUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Update a recommendation status or implementation data."""
    automation_service = AutomationService(db)
    recommendation = await automation_service.update_recommendation(recommendation_id, current_org.id, recommendation_data)
    return recommendation


@router.post("/recommendations/generate", response_model=List[RecommendationResponse])
async def generate_recommendations(
    content_id: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    types: Optional[List[RecommendationType]] = Query(None),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Generate new smart recommendations."""
    automation_service = AutomationService(db)
    recommendations = await automation_service.generate_recommendations(
        current_org.id, content_id, campaign_id, types
    )
    return recommendations


# A/B Testing
@router.get("/ab-tests", response_model=List[ABTestResponse])
async def get_ab_tests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ABTestStatus] = Query(None),
    test_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get A/B tests for the organization."""
    query = select(ABTest).where(ABTest.org_id == current_org.id)
    
    if status:
        query = query.where(ABTest.status == status)
    
    if test_type:
        query = query.where(ABTest.test_type == test_type)
    
    query = query.order_by(desc(ABTest.created_at)).offset(skip).limit(limit)
    
    ab_tests = db.execute(query).scalars().all()
    return ab_tests


@router.post("/ab-tests", response_model=ABTestResponse, status_code=status.HTTP_201_CREATED)
async def create_ab_test(
    ab_test_data: ABTestCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Create a new A/B test."""
    automation_service = AutomationService(db)
    ab_test = await automation_service.create_ab_test(current_org.id, ab_test_data)
    return ab_test


@router.get("/ab-tests/{ab_test_id}", response_model=ABTestResponse)
async def get_ab_test(
    ab_test_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get a specific A/B test."""
    ab_test = db.execute(
        select(ABTest).where(
            and_(ABTest.id == ab_test_id, ABTest.org_id == current_org.id)
        )
    ).scalar_one_or_none()
    
    if not ab_test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    return ab_test


@router.put("/ab-tests/{ab_test_id}", response_model=ABTestResponse)
async def update_ab_test(
    ab_test_id: str,
    ab_test_data: ABTestUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Update an A/B test."""
    automation_service = AutomationService(db)
    ab_test = await automation_service.update_ab_test(ab_test_id, current_org.id, ab_test_data)
    return ab_test


@router.delete("/ab-tests/{ab_test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ab_test(
    ab_test_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Delete an A/B test."""
    automation_service = AutomationService(db)
    await automation_service.delete_ab_test(ab_test_id, current_org.id)


@router.post("/ab-tests/{ab_test_id}/start", response_model=ABTestResponse)
async def start_ab_test(
    ab_test_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Start an A/B test."""
    automation_service = AutomationService(db)
    ab_test = await automation_service.start_ab_test(ab_test_id, current_org.id)
    return ab_test


@router.post("/ab-tests/{ab_test_id}/stop", response_model=ABTestResponse)
async def stop_ab_test(
    ab_test_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Stop an A/B test."""
    automation_service = AutomationService(db)
    ab_test = await automation_service.stop_ab_test(ab_test_id, current_org.id)
    return ab_test


@router.get("/ab-tests/{ab_test_id}/results", response_model=List[ABTestResultResponse])
async def get_ab_test_results(
    ab_test_id: str,
    variant_id: Optional[str] = Query(None),
    metric_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get results for an A/B test."""
    # Verify A/B test belongs to organization
    ab_test = db.execute(
        select(ABTest).where(
            and_(ABTest.id == ab_test_id, ABTest.org_id == current_org.id)
        )
    ).scalar_one_or_none()
    
    if not ab_test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    query = select(ABTestResult).where(ABTestResult.ab_test_id == ab_test_id)
    
    if variant_id:
        query = query.where(ABTestResult.variant_id == variant_id)
    
    if metric_name:
        query = query.where(ABTestResult.metric_name == metric_name)
    
    query = query.order_by(desc(ABTestResult.measured_at))
    
    results = db.execute(query).scalars().all()
    return results


@router.get("/ab-tests/{ab_test_id}/variants", response_model=List[ABTestVariantResponse])
async def get_ab_test_variants(
    ab_test_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get variants for an A/B test."""
    # Verify A/B test belongs to organization
    ab_test = db.execute(
        select(ABTest).where(
            and_(ABTest.id == ab_test_id, ABTest.org_id == current_org.id)
        )
    ).scalar_one_or_none()
    
    if not ab_test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    variants = db.execute(
        select(ABTestVariant).where(ABTestVariant.ab_test_id == ab_test_id)
    ).scalars().all()
    
    return variants
