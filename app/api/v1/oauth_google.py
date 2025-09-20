from __future__ import annotations

import urllib.parse
from typing import Optional
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_bearer_token, get_db
from app.core.config import get_settings
from app.core.security import verify_clerk_jwt
from app.integrations.oauth.google import GoogleOAuth
from app.models.publishing import PlatformIntegration
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/oauth/google", tags=["oauth-google"])


async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return await verify_clerk_jwt(token)


@router.get("/authorize")
async def get_google_auth_url(state: str, claims=Depends(get_auth_claims)) -> dict:
    _ = claims
    settings = get_settings()
    if not settings.google_client_id or not settings.google_redirect_url:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    oauth = GoogleOAuth()
    authorization_url = oauth.get_authorization_url(state)
    
    return {"authorization_url": authorization_url}


@router.get("/callback")
async def google_callback(
    code: str, 
    state: str, 
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Handle Google OAuth callback and exchange code for token."""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        oauth = GoogleOAuth()
        token_data = await oauth.get_access_token(code)
        
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        # Store or update integration
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "google_gbp"
        ).first()
        
        if not integration:
            integration = PlatformIntegration(
                user_id=user_id,
                platform="google_gbp",
                status="active",
                settings={
                    "access_token": oauth._encrypt_token(access_token),
                    "refresh_token": oauth._encrypt_token(refresh_token) if refresh_token else None,
                    "expires_at": datetime.utcnow().timestamp() + expires_in,
                    "connected_at": datetime.utcnow().isoformat()
                }
            )
            db.add(integration)
        else:
            integration.settings.update({
                "access_token": oauth._encrypt_token(access_token),
                "refresh_token": oauth._encrypt_token(refresh_token) if refresh_token else None,
                "expires_at": datetime.utcnow().timestamp() + expires_in,
                "connected_at": datetime.utcnow().isoformat()
            })
            integration.status = "active"
        
        db.commit()
        
        logger.info(f"Google OAuth successful for user {user_id}")
        
        return {
            "success": True,
            "message": "Google My Business account connected successfully",
            "platform": "google_gbp",
            "expires_in": expires_in
        }
        
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Google OAuth callback failed: {str(e)}"
        )


@router.get("/accounts")
async def get_google_accounts(
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Get Google Business accounts for the authenticated user."""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "google_gbp",
            PlatformIntegration.status == "active"
        ).first()
        
        if not integration:
            return {"accounts": []}
        
        # Decrypt and get account info
        oauth = GoogleOAuth()
        settings = integration.settings or {}
        
        access_token = None
        if settings.get("access_token"):
            try:
                access_token = oauth._decrypt_token(settings["access_token"])
            except Exception as e:
                logger.error(f"Failed to decrypt Google token: {str(e)}")
                return {"accounts": []}
        
        if not access_token:
            return {"accounts": []}
        
        # Get actual business accounts
        accounts = await oauth.get_business_accounts(access_token)
        
        return {
            "success": True,
            "accounts": accounts
        }
        
    except Exception as e:
        logger.error(f"Failed to get Google Business accounts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Google Business accounts: {str(e)}"
        )


@router.get("/locations")
async def get_google_locations(
    account_name: str,
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Get business locations for the authenticated user."""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "google_gbp",
            PlatformIntegration.status == "active"
        ).first()
        
        if not integration:
            return {"locations": []}
        
        # Decrypt and get account info
        oauth = GoogleOAuth()
        settings = integration.settings or {}
        
        access_token = None
        if settings.get("access_token"):
            try:
                access_token = oauth._decrypt_token(settings["access_token"])
            except Exception as e:
                logger.error(f"Failed to decrypt Google token: {str(e)}")
                return {"locations": []}
        
        if not access_token:
            return {"locations": []}
        
        # Get actual business locations
        locations = await oauth.get_business_locations(access_token, account_name)
        
        return {
            "success": True,
            "locations": locations
        }
        
    except Exception as e:
        logger.error(f"Failed to get Google Business locations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Google Business locations: {str(e)}"
        )
