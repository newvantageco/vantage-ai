from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
import json

from app.db.session import get_db
from app.models.api_keys import APIKey, APIKeyUsage, APIRateLimit, APIScopes
from app.models.entities import Organization
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()


class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    scopes: List[str]
    rate_limit_per_hour: Optional[int] = 1000
    expires_at: Optional[str] = None


class APIKeyResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    scopes: List[str]
    is_active: bool
    rate_limit_per_hour: int
    created_at: str
    last_used_at: Optional[str]
    usage_count: int
    expires_at: Optional[str]

    class Config:
        from_attributes = True


class APIKeyWithSecret(APIKeyResponse):
    key: str  # Only returned on creation


@router.post("/api-keys", response_model=APIKeyWithSecret)
async def create_api_key(
    api_key_data: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new API key."""
    # Validate scopes
    if not APIScopes.validate_scopes(api_key_data.scopes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scopes provided"
        )
    
    # Generate API key
    key = APIKey.generate_key()
    key_hash = APIKey.hash_key(key)
    
    # Create API key record
    api_key = APIKey(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        user_id=current_user["user_id"],
        key_hash=key_hash,
        name=api_key_data.name,
        description=api_key_data.description,
        scopes=json.dumps(api_key_data.scopes),
        rate_limit_per_hour=api_key_data.rate_limit_per_hour or 1000,
        expires_at=api_key_data.expires_at
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    # Return with the actual key (only time it's shown)
    response = APIKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        description=api_key.description,
        scopes=api_key.get_scopes(),
        is_active=api_key.is_active,
        rate_limit_per_hour=api_key.rate_limit_per_hour,
        created_at=api_key.created_at.isoformat(),
        last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        usage_count=api_key.usage_count,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
        key=key
    )
    
    return response


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all API keys for the organization."""
    api_keys = db.query(APIKey).filter(
        APIKey.org_id == current_user["org_id"]
    ).all()
    
    return [
        APIKeyResponse(
            id=key.id,
            name=key.name,
            description=key.description,
            scopes=key.get_scopes(),
            is_active=key.is_active,
            rate_limit_per_hour=key.rate_limit_per_hour,
            created_at=key.created_at.isoformat(),
            last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
            usage_count=key.usage_count,
            expires_at=key.expires_at.isoformat() if key.expires_at else None
        )
        for key in api_keys
    ]


@router.get("/api-keys/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific API key."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.org_id == current_user["org_id"]
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        description=api_key.description,
        scopes=api_key.get_scopes(),
        is_active=api_key.is_active,
        rate_limit_per_hour=api_key.rate_limit_per_hour,
        created_at=api_key.created_at.isoformat(),
        last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        usage_count=api_key.usage_count,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None
    )


@router.put("/api-keys/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str,
    api_key_data: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an API key."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.org_id == current_user["org_id"]
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Validate scopes
    if not APIScopes.validate_scopes(api_key_data.scopes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scopes provided"
        )
    
    # Update fields
    api_key.name = api_key_data.name
    api_key.description = api_key_data.description
    api_key.scopes = json.dumps(api_key_data.scopes)
    api_key.rate_limit_per_hour = api_key_data.rate_limit_per_hour or 1000
    api_key.expires_at = api_key_data.expires_at
    
    db.commit()
    db.refresh(api_key)
    
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        description=api_key.description,
        scopes=api_key.get_scopes(),
        is_active=api_key.is_active,
        rate_limit_per_hour=api_key.rate_limit_per_hour,
        created_at=api_key.created_at.isoformat(),
        last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        usage_count=api_key.usage_count,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None
    )


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an API key."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.org_id == current_user["org_id"]
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API key deleted successfully"}


@router.post("/api-keys/{key_id}/regenerate", response_model=APIKeyWithSecret)
async def regenerate_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Regenerate an API key (creates new key, invalidates old one)."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.org_id == current_user["org_id"]
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Generate new key
    new_key = APIKey.generate_key()
    new_key_hash = APIKey.hash_key(new_key)
    
    # Update the key hash
    api_key.key_hash = new_key_hash
    api_key.usage_count = 0  # Reset usage count
    
    db.commit()
    db.refresh(api_key)
    
    # Return with the new key
    response = APIKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        description=api_key.description,
        scopes=api_key.get_scopes(),
        is_active=api_key.is_active,
        rate_limit_per_hour=api_key.rate_limit_per_hour,
        created_at=api_key.created_at.isoformat(),
        last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        usage_count=api_key.usage_count,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
        key=new_key
    )
    
    return response


@router.get("/api-keys/{key_id}/usage")
async def get_api_key_usage(
    key_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get usage statistics for an API key."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.org_id == current_user["org_id"]
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Get usage data for the specified period
    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=days)
    
    usage_data = db.query(APIKeyUsage).filter(
        APIKeyUsage.api_key_id == key_id,
        APIKeyUsage.created_at >= start_date
    ).all()
    
    # Calculate statistics
    total_requests = len(usage_data)
    successful_requests = len([u for u in usage_data if 200 <= u.status_code < 300])
    error_requests = len([u for u in usage_data if u.status_code >= 400])
    avg_response_time = sum(u.response_time_ms for u in usage_data) / total_requests if total_requests > 0 else 0
    
    # Group by endpoint
    endpoint_stats = {}
    for usage in usage_data:
        endpoint = usage.endpoint
        if endpoint not in endpoint_stats:
            endpoint_stats[endpoint] = {
                'total_requests': 0,
                'successful_requests': 0,
                'error_requests': 0,
                'avg_response_time': 0
            }
        
        endpoint_stats[endpoint]['total_requests'] += 1
        if 200 <= usage.status_code < 300:
            endpoint_stats[endpoint]['successful_requests'] += 1
        elif usage.status_code >= 400:
            endpoint_stats[endpoint]['error_requests'] += 1
    
    # Calculate averages for each endpoint
    for endpoint, stats in endpoint_stats.items():
        endpoint_usages = [u for u in usage_data if u.endpoint == endpoint]
        stats['avg_response_time'] = sum(u.response_time_ms for u in endpoint_usages) / len(endpoint_usages)
    
    return {
        'api_key_id': key_id,
        'period_days': days,
        'total_requests': total_requests,
        'successful_requests': successful_requests,
        'error_requests': error_requests,
        'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
        'avg_response_time_ms': round(avg_response_time, 2),
        'endpoint_stats': endpoint_stats
    }


@router.get("/api-keys/scopes")
async def get_available_scopes():
    """Get all available API scopes."""
    return {
        'scopes': APIScopes.ALL_SCOPES,
        'scope_groups': APIScopes.get_scope_groups()
    }
