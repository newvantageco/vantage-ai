from __future__ import annotations

import urllib.parse
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_bearer_token
from app.core.config import get_settings
from app.core.security import verify_clerk_jwt
from app.integrations.oauth.linkedin import LinkedInOAuth
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.entities import UserAccount
from app.models.publishing import PlatformIntegration
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth/linkedin", tags=["oauth-linkedin"])


async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return await verify_clerk_jwt(token)


@router.get("/authorize")
async def get_linkedin_auth_url(state: str, claims=Depends(get_auth_claims)) -> dict:
    """Get LinkedIn OAuth authorization URL"""
    _ = claims
    settings = get_settings()
    
    if not settings.linkedin_client_id or not settings.linkedin_redirect_url:
        raise HTTPException(
            status_code=500, 
            detail="LinkedIn OAuth not configured. Please set LINKEDIN_CLIENT_ID and LINKEDIN_REDIRECT_URL"
        )
    
    params = {
        "response_type": "code",
        "client_id": settings.linkedin_client_id,
        "redirect_uri": settings.linkedin_redirect_url,
        "state": state,
        "scope": "r_liteprofile r_emailaddress w_member_social"
    }
    
    url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(params)
    return {"authorization_url": url}


@router.get("/callback")
async def linkedin_callback(
    code: str, 
    state: str, 
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Handle LinkedIn OAuth callback and exchange code for tokens"""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        # Exchange code for access token
        oauth_client = LinkedInOAuth()
        token_data = await oauth_client.get_access_token(code)
        
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 3600)
        refresh_token = token_data.get("refresh_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        # Store or update integration
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "linkedin"
        ).first()
        
        if not integration:
            integration = PlatformIntegration(
                user_id=user_id,
                platform="linkedin",
                status="active",
                settings={
                    "access_token": oauth_client._encrypt_token(access_token),
                    "refresh_token": oauth_client._encrypt_token(refresh_token) if refresh_token else None,
                    "expires_at": datetime.utcnow().timestamp() + expires_in,
                    "connected_at": datetime.utcnow().isoformat()
                }
            )
            db.add(integration)
        else:
            integration.settings.update({
                "access_token": oauth_client._encrypt_token(access_token),
                "refresh_token": oauth_client._encrypt_token(refresh_token) if refresh_token else None,
                "expires_at": datetime.utcnow().timestamp() + expires_in,
                "connected_at": datetime.utcnow().isoformat()
            })
            integration.status = "active"
        
        db.commit()
        
        logger.info(f"LinkedIn OAuth successful for user {user_id}")
        
        return {
            "success": True,
            "message": "LinkedIn account connected successfully",
            "platform": "linkedin",
            "expires_in": expires_in
        }
        
    except Exception as e:
        logger.error(f"LinkedIn OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LinkedIn OAuth failed: {str(e)}"
        )


@router.get("/accounts")
async def get_linkedin_accounts(
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Get connected LinkedIn accounts for the user"""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "linkedin",
            PlatformIntegration.status == "active"
        ).first()
        
        if not integration:
            return {"accounts": []}
        
        # Decrypt and return account info
        oauth_client = LinkedInOAuth()
        settings = integration.settings or {}
        
        access_token = None
        if settings.get("access_token"):
            try:
                access_token = oauth_client._decrypt_token(settings["access_token"])
            except Exception as e:
                logger.error(f"Failed to decrypt LinkedIn token: {str(e)}")
                return {"accounts": []}
        
        if not access_token:
            return {"accounts": []}
        
        # TODO: Make API call to get LinkedIn profile info
        # For now, return basic account info
        return {
            "accounts": [{
                "id": integration.id,
                "platform": "linkedin",
                "status": integration.status,
                "connected_at": settings.get("connected_at"),
                "expires_at": settings.get("expires_at")
            }]
        }
        
    except Exception as e:
        logger.error(f"Failed to get LinkedIn accounts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get LinkedIn accounts: {str(e)}"
        )


@router.post("/disconnect")
async def disconnect_linkedin(
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Disconnect LinkedIn account"""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "linkedin"
        ).first()
        
        if not integration:
            raise HTTPException(status_code=404, detail="LinkedIn account not found")
        
        integration.status = "disconnected"
        integration.settings = {}  # Clear sensitive data
        db.commit()
        
        logger.info(f"LinkedIn account disconnected for user {user_id}")
        
        return {
            "success": True,
            "message": "LinkedIn account disconnected successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to disconnect LinkedIn: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect LinkedIn: {str(e)}"
        )
