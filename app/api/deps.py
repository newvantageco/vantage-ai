from __future__ import annotations

from typing import Optional
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.mocks import get_mock_response

security = HTTPBearer()


async def get_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract bearer token from Authorization header.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization token"
        )
    return credentials.credentials


async def get_current_user(token: str = Depends(get_bearer_token)) -> dict:
    """
    Get current user from JWT token.
    For demo purposes, returns a mock user.
    """
    # In a real implementation, this would verify the JWT token
    # and return the actual user data from the database
    return {
        "id": "demo-user",
        "org_id": "demo-org",
        "email": "demo@vantage.ai"
    }


async def get_mock_or_real_response(
    request: Request,
    endpoint: str,
    method: str = "GET",
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Dependency that returns mock response if E2E_MOCKS is enabled,
    otherwise returns None to let the real endpoint handle the request.
    """
    # Try to get mock response first
    mock_response = get_mock_response(endpoint, method)
    if mock_response:
        return mock_response.body.decode() if hasattr(mock_response, 'body') else None
    
    return None