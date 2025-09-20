"""
Authentication API endpoints
Handles Clerk JWT token validation and user management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
import logging

from app.db.session import get_db
from app.models.cms import UserAccount, Organization
from app.core.security import verify_clerk_jwt, AuthClaims
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class LoginRequest(BaseModel):
    token: str


class RegisterRequest(BaseModel):
    token: str


@router.post("/auth/login")
def login_with_clerk(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate Clerk JWT token and return user information.
    This endpoint is called by the frontend after Clerk authentication.
    """
    try:
        # Verify the Clerk JWT token
        claims = verify_clerk_jwt(request.token)
        
        # Get or create user in database
        user = db.query(UserAccount).filter(
            UserAccount.clerk_user_id == claims.user_id
        ).first()
        
        if not user:
            # Create new user if they don't exist
            user = UserAccount(
                clerk_user_id=claims.user_id,
                email=claims.email or "",
                name="",  # Will be updated from Clerk profile
                is_active=True,
                organization_id=None  # Will be set when organization is created
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {claims.user_id}")
        
        # Update user info from token
        if claims.email and user.email != claims.email:
            user.email = claims.email
        
        if claims.org_id:
            # Get or create organization
            org = db.query(Organization).filter(
                Organization.clerk_org_id == claims.org_id
            ).first()
            
            if not org:
                org = Organization(
                    clerk_org_id=claims.org_id,
                    name=f"Organization {claims.org_id}",
                    is_active=True
                )
                db.add(org)
                db.commit()
                db.refresh(org)
                logger.info(f"Created new organization: {claims.org_id}")
            
            user.organization_id = org.id
        
        db.commit()
        
        return {
            "access_token": request.token,  # Return the same token for consistency
            "token_type": "bearer",
            "expires_in": 3600,  # Clerk tokens typically last 1 hour
            "user": {
                "id": str(user.id),
                "clerk_user_id": user.clerk_user_id,
                "email": user.email,
                "name": user.name,
                "org_id": str(user.organization_id) if user.organization_id else None,
                "is_active": user.is_active
            }
        }
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/auth/me")
def get_current_user_info(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current user information from Clerk JWT token.
    """
    try:
        # Verify the Clerk JWT token
        claims = verify_clerk_jwt(request.token)
        
        # Get user from database
        user = db.query(UserAccount).filter(
            UserAccount.clerk_user_id == claims.user_id
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
        
        return {
            "id": str(user.id),
            "clerk_user_id": user.clerk_user_id,
            "email": user.email,
            "name": user.name,
            "org_id": str(user.organization_id) if user.organization_id else None,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/auth/register")
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Register a new user with Clerk JWT token.
    This is essentially the same as login but with explicit registration semantics.
    """
    login_request = LoginRequest(token=request.token)
    return login_with_clerk(login_request, db)


@router.post("/auth/logout")
def logout() -> Dict[str, str]:
    """
    Logout endpoint (client-side token removal).
    Clerk handles token invalidation on their end.
    """
    return {"message": "Logged out successfully"}


@router.get("/auth/health")
def auth_health() -> Dict[str, Any]:
    """
    Check authentication service health.
    """
    return {
        "status": "ok",
        "service": "authentication",
        "provider": "clerk",
        "configured": bool(settings.clerk_jwks_url and settings.clerk_issuer)
    }