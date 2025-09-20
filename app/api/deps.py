"""
API Dependencies
Handles authentication, database sessions, and common dependencies
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from jose import jwt, JWTError
import os

from app.db.session import get_db
from app.models.cms import UserAccount, Organization
from app.core.config import get_settings

settings = get_settings()
security = HTTPBearer()


def get_bearer_token(authorization: str = Header(None)) -> str:
    """Extract bearer token from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.split(" ")[1]


def get_current_user_mock() -> dict:
    """
    Mock current user for testing without authentication.
    """
    return {
        "org_id": 1,
        "user_id": 1,
        "email": "test@example.com"
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserAccount:
    """
    Get current authenticated user from JWT token.
    """
    # Development bypass for simple tokens
    if credentials.credentials.startswith("simple_token_"):
        # Create a mock user for development
        mock_user = UserAccount(
            id=1,
            email="admin@vantage.ai",
            name="Demo Admin",
            organization_id=1,
            is_active=True
        )
        return mock_user
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.clerk_jwks_url,  # FIXME: Use proper JWT secret
            algorithms=["RS256"]
        )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        user = db.query(UserAccount).filter(
            UserAccount.clerk_user_id == user_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


def get_current_active_user(
    current_user: UserAccount = Depends(get_current_user)
) -> UserAccount:
    """
    Get current active user (alias for get_current_user).
    """
    return current_user


def get_current_organization(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Get current user's organization.
    """
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization


def require_role(required_roles: list):
    """
    Dependency factory for role-based access control.
    """
    def role_checker(current_user: UserAccount = Depends(get_current_user)) -> UserAccount:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_owner_or_admin(
    current_user: UserAccount = Depends(get_current_user)
) -> UserAccount:
    """
    Require user to be owner or admin.
    """
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner or admin access required"
        )
    return current_user


def require_editor_or_above(
    current_user: UserAccount = Depends(get_current_user)
) -> UserAccount:
    """
    Require user to be editor or above.
    """
    if current_user.role not in ["owner", "admin", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor access or above required"
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserAccount]:
    """
    Get current user if authenticated, otherwise return None.
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def get_pagination_params(
    skip: int = 0,
    limit: int = 20
) -> dict:
    """
    Get pagination parameters.
    """
    if skip < 0:
        skip = 0
    if limit < 1 or limit > 100:
        limit = 20
    
    return {"skip": skip, "limit": limit}


def get_admin_user(
    current_user: UserAccount = Depends(get_current_user)
) -> UserAccount:
    """
    Get current user and verify they have admin privileges.
    For now, any authenticated user is considered an admin.
    """
    # TODO: Implement proper admin role checking
    return current_user