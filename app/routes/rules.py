from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from app.api.deps import get_db, get_bearer_token
from app.core.security import verify_clerk_jwt
from app.models.rules import Rule, RuleRun, RuleStatus
from app.automation.rules_engine import rules_engine, TriggerType, ActionType
from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rules", tags=["rules"])


# Request/Response Models
class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    trigger: str = Field(..., description="Trigger type")
    condition_json: Dict[str, Any] = Field(..., description="JSON logic condition")
    action_json: Dict[str, Any] = Field(..., description="Action configuration")
    enabled: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    condition_json: Optional[Dict[str, Any]] = None
    action_json: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class RuleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    trigger: str
    condition_json: Dict[str, Any]
    action_json: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime


class RuleRunResponse(BaseModel):
    id: str
    rule_id: str
    status: str
    last_run_at: Optional[datetime]
    meta_json: Optional[Dict[str, Any]]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class RuleTestRequest(BaseModel):
    trigger: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class RuleTestResponse(BaseModel):
    condition_met: bool
    action_preview: Dict[str, Any]
    dry_run_result: Dict[str, Any]


# Helper functions
async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    return await verify_clerk_jwt(token)


def get_org_id_from_claims(claims: dict) -> str:
    """Extract organization ID from JWT claims."""
    # This would depend on your JWT structure
    # For now, we'll assume it's in the claims
    return claims.get("org_id", "default_org")


# Routes
@router.post("/", response_model=RuleResponse)
async def create_rule(
    rule_data: RuleCreate,
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Create a new automation rule."""
    org_id = get_org_id_from_claims(claims)
    
    # Validate trigger type
    try:
        TriggerType(rule_data.trigger)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trigger type: {rule_data.trigger}"
        )
    
    # Validate action type
    action_type = rule_data.action_json.get("type")
    if action_type:
        try:
            ActionType(action_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action type: {action_type}"
            )
    
    # Create rule
    rule = Rule(
        id=str(uuid4()),
        org_id=org_id,
        name=rule_data.name,
        description=rule_data.description,
        trigger=rule_data.trigger,
        condition_json=rule_data.condition_json,
        action_json=rule_data.action_json,
        enabled=rule_data.enabled
    )
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    logger.info(f"Created rule {rule.id} for org {org_id}")
    
    return RuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger=rule.trigger,
        condition_json=rule.condition_json,
        action_json=rule.action_json,
        enabled=rule.enabled,
        created_at=rule.created_at,
        updated_at=rule.updated_at
    )


@router.get("/", response_model=List[RuleResponse])
async def list_rules(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    enabled_only: bool = Query(False),
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """List automation rules for the organization."""
    org_id = get_org_id_from_claims(claims)
    
    query = select(Rule).where(Rule.org_id == org_id)
    
    if enabled_only:
        query = query.where(Rule.enabled == True)
    
    query = query.order_by(desc(Rule.created_at)).offset(offset).limit(limit)
    
    rules = db.execute(query).scalars().all()
    
    return [
        RuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            trigger=rule.trigger,
            condition_json=rule.condition_json,
            action_json=rule.action_json,
            enabled=rule.enabled,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
        for rule in rules
    ]


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Get a specific rule."""
    org_id = get_org_id_from_claims(claims)
    
    rule = db.execute(
        select(Rule).where(
            and_(Rule.id == rule_id, Rule.org_id == org_id)
        )
    ).scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return RuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger=rule.trigger,
        condition_json=rule.condition_json,
        action_json=rule.action_json,
        enabled=rule.enabled,
        created_at=rule.created_at,
        updated_at=rule.updated_at
    )


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: str,
    rule_data: RuleUpdate,
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Update a rule."""
    org_id = get_org_id_from_claims(claims)
    
    rule = db.execute(
        select(Rule).where(
            and_(Rule.id == rule_id, Rule.org_id == org_id)
        )
    ).scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update fields
    if rule_data.name is not None:
        rule.name = rule_data.name
    if rule_data.description is not None:
        rule.description = rule_data.description
    if rule_data.condition_json is not None:
        rule.condition_json = rule_data.condition_json
    if rule_data.action_json is not None:
        rule.action_json = rule_data.action_json
    if rule_data.enabled is not None:
        rule.enabled = rule_data.enabled
    
    rule.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rule)
    
    logger.info(f"Updated rule {rule_id}")
    
    return RuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger=rule.trigger,
        condition_json=rule.condition_json,
        action_json=rule.action_json,
        enabled=rule.enabled,
        created_at=rule.created_at,
        updated_at=rule.updated_at
    )


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Delete a rule."""
    org_id = get_org_id_from_claims(claims)
    
    rule = db.execute(
        select(Rule).where(
            and_(Rule.id == rule_id, Rule.org_id == org_id)
        )
    ).scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    
    logger.info(f"Deleted rule {rule_id}")
    
    return {"message": "Rule deleted successfully"}


@router.post("/test", response_model=RuleTestResponse)
async def test_rule(
    test_data: RuleTestRequest,
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Test a rule condition and action without executing."""
    # Validate trigger type
    try:
        trigger_enum = TriggerType(test_data.trigger)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trigger type: {test_data.trigger}"
        )
    
    # Create a test rule for evaluation
    test_rule = Rule(
        id="test_rule",
        org_id="test_org",
        name="Test Rule",
        trigger=test_data.trigger,
        condition_json={"operator": "eq", "field": "test", "value": "test"},  # Placeholder
        action_json={"type": "send_notification", "message": "Test notification"},
        enabled=True
    )
    
    try:
        # Evaluate condition
        condition_met = await rules_engine._evaluate_condition(
            test_rule.condition_json, 
            test_data.payload
        )
        
        # Preview action (dry run)
        action_preview = {
            "type": test_rule.action_json.get("type"),
            "description": "Action would be executed in dry run mode"
        }
        
        dry_run_result = {
            "status": "dry_run",
            "message": "Action would be executed in dry run mode",
            "condition_met": condition_met
        }
        
        return RuleTestResponse(
            condition_met=condition_met,
            action_preview=action_preview,
            dry_run_result=dry_run_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error testing rule: {str(e)}"
        )


@router.get("/{rule_id}/runs", response_model=List[RuleRunResponse])
async def get_rule_runs(
    rule_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Get rule execution history."""
    org_id = get_org_id_from_claims(claims)
    
    # Verify rule belongs to org
    rule = db.execute(
        select(Rule).where(
            and_(Rule.id == rule_id, Rule.org_id == org_id)
        )
    ).scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Get rule runs
    runs = db.execute(
        select(RuleRun)
        .where(RuleRun.rule_id == rule_id)
        .order_by(desc(RuleRun.created_at))
        .offset(offset)
        .limit(limit)
    ).scalars().all()
    
    return [
        RuleRunResponse(
            id=run.id,
            rule_id=run.rule_id,
            status=run.status.value,
            last_run_at=run.last_run_at,
            meta_json=run.meta_json,
            started_at=run.started_at,
            completed_at=run.completed_at,
            created_at=run.created_at
        )
        for run in runs
    ]


@router.get("/runs/recent", response_model=List[RuleRunResponse])
async def get_recent_rule_runs(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
):
    """Get recent rule runs across all rules for the organization."""
    org_id = get_org_id_from_claims(claims)
    
    # Get recent runs for this org
    runs = db.execute(
        select(RuleRun)
        .join(Rule)
        .where(Rule.org_id == org_id)
        .order_by(desc(RuleRun.created_at))
        .limit(limit)
    ).scalars().all()
    
    return [
        RuleRunResponse(
            id=run.id,
            rule_id=run.rule_id,
            status=run.status.value,
            last_run_at=run.last_run_at,
            meta_json=run.meta_json,
            started_at=run.started_at,
            completed_at=run.completed_at,
            created_at=run.created_at
        )
        for run in runs
    ]
