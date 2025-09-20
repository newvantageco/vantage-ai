"""
Simple Authentication API endpoints
Mock authentication that works without database for testing
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class SimpleLoginRequest(BaseModel):
    email: str
    password: str


class SimpleTokenRequest(BaseModel):
    token: str


@router.post("/auth/simple/login")
def simple_login(request: SimpleLoginRequest) -> Dict[str, Any]:
    """
    Simple login endpoint that works without database.
    """
    try:
        # Simple mock authentication
        if request.email == "admin@vantage.ai" and request.password == "admin123":
            # Generate a simple mock token
            mock_token = f"simple_token_{request.email.replace('@', '_').replace('.', '_')}"
            
            return {
                "access_token": mock_token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": "1",
                    "clerk_user_id": "simple_user_123",
                    "email": request.email,
                    "name": "Demo Admin",
                    "org_id": None,
                    "is_active": True
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials. Use admin@vantage.ai / admin123 for demo"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Simple login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/auth/simple/validate")
def simple_validate_token(request: SimpleTokenRequest) -> Dict[str, Any]:
    """
    Validate simple token and return user information.
    """
    try:
        # Simple token validation
        if not request.token.startswith("simple_token_"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        
        # Extract email from token
        email_part = request.token.replace("simple_token_", "").replace("_", "@", 1).replace("_", ".")
        
        return {
            "id": "1",
            "clerk_user_id": "simple_user_123",
            "email": email_part,
            "name": "Demo Admin",
            "org_id": None,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )


@router.get("/auth/simple/health")
def simple_auth_health() -> Dict[str, Any]:
    """
    Check simple authentication service health.
    """
    return {
        "status": "ok",
        "service": "simple_authentication",
        "provider": "mock",
        "configured": True
    }
