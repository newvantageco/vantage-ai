from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.db.session import get_db
from app.services.limits import LimitsService, LimitType
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()


class UsageSummaryResponse(BaseModel):
    org_id: str
    plan: str
    limits: Dict[str, int]
    usage: Dict[str, Dict[str, Any]]
    overall_status: str


class LimitWarningResponse(BaseModel):
    type: str
    limit_type: str
    current: int
    limit: int
    usage_percentage: float
    message: str


@router.get("/limits/usage", response_model=UsageSummaryResponse)
async def get_usage_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get usage summary for the organization."""
    limits_service = LimitsService(db)
    summary = limits_service.get_usage_summary(current_user["org_id"])
    
    return UsageSummaryResponse(**summary)


@router.get("/limits/check/{limit_type}")
async def check_limit(
    limit_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check a specific limit type."""
    try:
        limit_enum = LimitType(limit_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid limit type. Must be one of: {[lt.value for lt in LimitType]}"
        )
    
    limits_service = LimitsService(db)
    result = limits_service.check_limit(current_user["org_id"], limit_enum)
    
    return result.to_dict()


@router.get("/limits/remaining/{limit_type}")
async def get_remaining_usage(
    limit_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get remaining usage for a specific limit type."""
    try:
        limit_enum = LimitType(limit_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid limit type. Must be one of: {[lt.value for lt in LimitType]}"
        )
    
    limits_service = LimitsService(db)
    remaining = limits_service.get_remaining_usage(current_user["org_id"], limit_enum)
    
    return {
        "limit_type": limit_type,
        "remaining": remaining
    }


@router.get("/limits/warnings", response_model=List[LimitWarningResponse])
async def get_limit_warnings(
    threshold: float = 0.8,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get warnings for limits that are near or exceeded."""
    limits_service = LimitsService(db)
    warnings = limits_service.get_limit_warnings(current_user["org_id"], threshold)
    
    return [LimitWarningResponse(**warning) for warning in warnings]


@router.get("/limits/can-perform/{limit_type}")
async def can_perform_action(
    limit_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check if an action can be performed without exceeding limits."""
    try:
        limit_enum = LimitType(limit_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid limit type. Must be one of: {[lt.value for lt in LimitType]}"
        )
    
    limits_service = LimitsService(db)
    can_perform = limits_service.can_perform_action(current_user["org_id"], limit_enum)
    
    return {
        "limit_type": limit_type,
        "can_perform": can_perform
    }


@router.get("/limits/near-limit/{limit_type}")
async def is_near_limit(
    limit_type: str,
    threshold: float = 0.8,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check if usage is near the limit."""
    try:
        limit_enum = LimitType(limit_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid limit type. Must be one of: {[lt.value for lt in LimitType]}"
        )
    
    limits_service = LimitsService(db)
    is_near = limits_service.is_near_limit(current_user["org_id"], limit_enum, threshold)
    
    return {
        "limit_type": limit_type,
        "is_near_limit": is_near,
        "threshold": threshold
    }


@router.get("/limits/available-types")
async def get_available_limit_types():
    """Get available limit types."""
    return {
        "limit_types": [
            {
                "value": lt.value,
                "name": lt.value.replace("_", " ").title(),
                "description": f"Limit for {lt.value.replace('_', ' ')}"
            }
            for lt in LimitType
        ]
    }
