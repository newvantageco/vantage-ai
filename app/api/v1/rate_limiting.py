from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets

from app.db.session import get_db
from app.models.rate_limiting import (
    IPAllowlist, RateLimit, RateLimitUsage, RateLimitViolation,
    RateLimitScopes, DEFAULT_RATE_LIMITS
)
from app.models.entities import Organization
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()


class IPAllowlistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cidrs: List[str]


class IPAllowlistResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    cidrs: List[str]
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RateLimitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    scope: str
    scope_value: Optional[str] = None


class RateLimitResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    scope: str
    scope_value: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RateLimitViolationResponse(BaseModel):
    id: str
    scope_key: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    requests_count: int
    limit_exceeded: int
    window_start: str
    window_end: str
    response_status: int
    response_message: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/ip-allowlists", response_model=IPAllowlistResponse)
async def create_ip_allowlist(
    allowlist_data: IPAllowlistCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create an IP allowlist."""
    
    # Validate CIDR blocks
    for cidr in allowlist_data.cidrs:
        try:
            import ipaddress
            ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CIDR block: {cidr}"
            )
    
    # Create allowlist
    allowlist = IPAllowlist(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        name=allowlist_data.name,
        description=allowlist_data.description,
        cidrs=json.dumps(allowlist_data.cidrs)
    )
    
    db.add(allowlist)
    db.commit()
    db.refresh(allowlist)
    
    return IPAllowlistResponse(
        id=allowlist.id,
        name=allowlist.name,
        description=allowlist.description,
        cidrs=allowlist.get_cidrs(),
        is_active=allowlist.is_active,
        created_at=allowlist.created_at.isoformat(),
        updated_at=allowlist.updated_at.isoformat()
    )


@router.get("/ip-allowlists", response_model=List[IPAllowlistResponse])
async def list_ip_allowlists(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List IP allowlists for the organization."""
    allowlists = db.query(IPAllowlist).filter(IPAllowlist.org_id == current_user["org_id"]).all()
    
    return [
        IPAllowlistResponse(
            id=allowlist.id,
            name=allowlist.name,
            description=allowlist.description,
            cidrs=allowlist.get_cidrs(),
            is_active=allowlist.is_active,
            created_at=allowlist.created_at.isoformat(),
            updated_at=allowlist.updated_at.isoformat()
        )
        for allowlist in allowlists
    ]


@router.get("/ip-allowlists/{allowlist_id}", response_model=IPAllowlistResponse)
async def get_ip_allowlist(
    allowlist_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific IP allowlist."""
    allowlist = db.query(IPAllowlist).filter(
        IPAllowlist.id == allowlist_id,
        IPAllowlist.org_id == current_user["org_id"]
    ).first()
    
    if not allowlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP allowlist not found"
        )
    
    return IPAllowlistResponse(
        id=allowlist.id,
        name=allowlist.name,
        description=allowlist.description,
        cidrs=allowlist.get_cidrs(),
        is_active=allowlist.is_active,
        created_at=allowlist.created_at.isoformat(),
        updated_at=allowlist.updated_at.isoformat()
    )


@router.put("/ip-allowlists/{allowlist_id}", response_model=IPAllowlistResponse)
async def update_ip_allowlist(
    allowlist_id: str,
    allowlist_data: IPAllowlistCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an IP allowlist."""
    allowlist = db.query(IPAllowlist).filter(
        IPAllowlist.id == allowlist_id,
        IPAllowlist.org_id == current_user["org_id"]
    ).first()
    
    if not allowlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP allowlist not found"
        )
    
    # Validate CIDR blocks
    for cidr in allowlist_data.cidrs:
        try:
            import ipaddress
            ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CIDR block: {cidr}"
            )
    
    # Update fields
    allowlist.name = allowlist_data.name
    allowlist.description = allowlist_data.description
    allowlist.set_cidrs(allowlist_data.cidrs)
    
    db.commit()
    db.refresh(allowlist)
    
    return IPAllowlistResponse(
        id=allowlist.id,
        name=allowlist.name,
        description=allowlist.description,
        cidrs=allowlist.get_cidrs(),
        is_active=allowlist.is_active,
        created_at=allowlist.created_at.isoformat(),
        updated_at=allowlist.updated_at.isoformat()
    )


@router.delete("/ip-allowlists/{allowlist_id}")
async def delete_ip_allowlist(
    allowlist_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an IP allowlist."""
    allowlist = db.query(IPAllowlist).filter(
        IPAllowlist.id == allowlist_id,
        IPAllowlist.org_id == current_user["org_id"]
    ).first()
    
    if not allowlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP allowlist not found"
        )
    
    db.delete(allowlist)
    db.commit()
    
    return {"message": "IP allowlist deleted successfully"}


@router.post("/ip-allowlists/{allowlist_id}/test")
async def test_ip_allowlist(
    allowlist_id: str,
    ip_address: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Test if an IP address is allowed by the allowlist."""
    allowlist = db.query(IPAllowlist).filter(
        IPAllowlist.id == allowlist_id,
        IPAllowlist.org_id == current_user["org_id"]
    ).first()
    
    if not allowlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP allowlist not found"
        )
    
    is_allowed = allowlist.is_ip_allowed(ip_address)
    
    return {
        "ip_address": ip_address,
        "is_allowed": is_allowed,
        "allowlist_name": allowlist.name
    }


@router.post("/rate-limits", response_model=RateLimitResponse)
async def create_rate_limit(
    rate_limit_data: RateLimitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a rate limit."""
    
    # Validate scope
    if not RateLimitScopes.validate_scope(rate_limit_data.scope):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scope. Must be one of: {RateLimitScopes.ALL_SCOPES}"
        )
    
    # Create rate limit
    rate_limit = RateLimit(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        name=rate_limit_data.name,
        description=rate_limit_data.description,
        requests_per_minute=rate_limit_data.requests_per_minute,
        requests_per_hour=rate_limit_data.requests_per_hour,
        requests_per_day=rate_limit_data.requests_per_day,
        scope=rate_limit_data.scope,
        scope_value=rate_limit_data.scope_value
    )
    
    db.add(rate_limit)
    db.commit()
    db.refresh(rate_limit)
    
    return RateLimitResponse(
        id=rate_limit.id,
        name=rate_limit.name,
        description=rate_limit.description,
        requests_per_minute=rate_limit.requests_per_minute,
        requests_per_hour=rate_limit.requests_per_hour,
        requests_per_day=rate_limit.requests_per_day,
        scope=rate_limit.scope,
        scope_value=rate_limit.scope_value,
        is_active=rate_limit.is_active,
        created_at=rate_limit.created_at.isoformat(),
        updated_at=rate_limit.updated_at.isoformat()
    )


@router.get("/rate-limits", response_model=List[RateLimitResponse])
async def list_rate_limits(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List rate limits for the organization."""
    rate_limits = db.query(RateLimit).filter(RateLimit.org_id == current_user["org_id"]).all()
    
    return [
        RateLimitResponse(
            id=limit.id,
            name=limit.name,
            description=limit.description,
            requests_per_minute=limit.requests_per_minute,
            requests_per_hour=limit.requests_per_hour,
            requests_per_day=limit.requests_per_day,
            scope=limit.scope,
            scope_value=limit.scope_value,
            is_active=limit.is_active,
            created_at=limit.created_at.isoformat(),
            updated_at=limit.updated_at.isoformat()
        )
        for limit in rate_limits
    ]


@router.get("/rate-limits/{limit_id}", response_model=RateLimitResponse)
async def get_rate_limit(
    limit_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific rate limit."""
    rate_limit = db.query(RateLimit).filter(
        RateLimit.id == limit_id,
        RateLimit.org_id == current_user["org_id"]
    ).first()
    
    if not rate_limit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate limit not found"
        )
    
    return RateLimitResponse(
        id=rate_limit.id,
        name=rate_limit.name,
        description=rate_limit.description,
        requests_per_minute=rate_limit.requests_per_minute,
        requests_per_hour=rate_limit.requests_per_hour,
        requests_per_day=rate_limit.requests_per_day,
        scope=rate_limit.scope,
        scope_value=rate_limit.scope_value,
        is_active=rate_limit.is_active,
        created_at=rate_limit.created_at.isoformat(),
        updated_at=rate_limit.updated_at.isoformat()
    )


@router.put("/rate-limits/{limit_id}", response_model=RateLimitResponse)
async def update_rate_limit(
    limit_id: str,
    rate_limit_data: RateLimitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a rate limit."""
    rate_limit = db.query(RateLimit).filter(
        RateLimit.id == limit_id,
        RateLimit.org_id == current_user["org_id"]
    ).first()
    
    if not rate_limit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate limit not found"
        )
    
    # Validate scope
    if not RateLimitScopes.validate_scope(rate_limit_data.scope):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scope. Must be one of: {RateLimitScopes.ALL_SCOPES}"
        )
    
    # Update fields
    rate_limit.name = rate_limit_data.name
    rate_limit.description = rate_limit_data.description
    rate_limit.requests_per_minute = rate_limit_data.requests_per_minute
    rate_limit.requests_per_hour = rate_limit_data.requests_per_hour
    rate_limit.requests_per_day = rate_limit_data.requests_per_day
    rate_limit.scope = rate_limit_data.scope
    rate_limit.scope_value = rate_limit_data.scope_value
    
    db.commit()
    db.refresh(rate_limit)
    
    return RateLimitResponse(
        id=rate_limit.id,
        name=rate_limit.name,
        description=rate_limit.description,
        requests_per_minute=rate_limit.requests_per_minute,
        requests_per_hour=rate_limit.requests_per_hour,
        requests_per_day=rate_limit.requests_per_day,
        scope=rate_limit.scope,
        scope_value=rate_limit.scope_value,
        is_active=rate_limit.is_active,
        created_at=rate_limit.created_at.isoformat(),
        updated_at=rate_limit.updated_at.isoformat()
    )


@router.delete("/rate-limits/{limit_id}")
async def delete_rate_limit(
    limit_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a rate limit."""
    rate_limit = db.query(RateLimit).filter(
        RateLimit.id == limit_id,
        RateLimit.org_id == current_user["org_id"]
    ).first()
    
    if not rate_limit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate limit not found"
        )
    
    db.delete(rate_limit)
    db.commit()
    
    return {"message": "Rate limit deleted successfully"}


@router.get("/rate-limits/{limit_id}/usage")
async def get_rate_limit_usage(
    limit_id: str,
    scope_key: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get rate limit usage statistics."""
    rate_limit = db.query(RateLimit).filter(
        RateLimit.id == limit_id,
        RateLimit.org_id == current_user["org_id"]
    ).first()
    
    if not rate_limit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate limit not found"
        )
    
    # Get usage records
    query = db.query(RateLimitUsage).filter(RateLimitUsage.rate_limit_id == limit_id)
    
    if scope_key:
        query = query.filter(RateLimitUsage.scope_key == scope_key)
    
    usage_records = query.all()
    
    # Calculate statistics
    total_requests = sum(record.requests_count for record in usage_records)
    active_windows = len([r for r in usage_records if not r.is_expired()])
    
    return {
        "rate_limit_id": limit_id,
        "total_requests": total_requests,
        "active_windows": active_windows,
        "usage_records": [
            {
                "scope_key": record.scope_key,
                "requests_count": record.requests_count,
                "window_start": record.window_start.isoformat(),
                "window_end": record.window_end.isoformat(),
                "is_expired": record.is_expired()
            }
            for record in usage_records
        ]
    }


@router.get("/rate-limits/violations", response_model=List[RateLimitViolationResponse])
async def list_rate_limit_violations(
    limit_id: Optional[str] = None,
    scope_key: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List rate limit violations."""
    query = db.query(RateLimitViolation).filter(RateLimitViolation.org_id == current_user["org_id"])
    
    if limit_id:
        query = query.filter(RateLimitViolation.rate_limit_id == limit_id)
    
    if scope_key:
        query = query.filter(RateLimitViolation.scope_key == scope_key)
    
    violations = query.order_by(RateLimitViolation.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        RateLimitViolationResponse(
            id=violation.id,
            scope_key=violation.scope_key,
            ip_address=violation.ip_address,
            user_agent=violation.user_agent,
            endpoint=violation.endpoint,
            requests_count=violation.requests_count,
            limit_exceeded=violation.limit_exceeded,
            window_start=violation.window_start.isoformat(),
            window_end=violation.window_end.isoformat(),
            response_status=violation.response_status,
            response_message=violation.response_message,
            created_at=violation.created_at.isoformat()
        )
        for violation in violations
    ]


@router.get("/rate-limits/available-scopes")
async def get_available_scopes():
    """Get available rate limit scopes."""
    return {
        "scopes": RateLimitScopes.ALL_SCOPES,
        "default_limits": DEFAULT_RATE_LIMITS
    }
