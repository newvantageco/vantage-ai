from __future__ import annotations

import urllib.parse
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_bearer_token
from app.core.config import get_settings
from app.core.security import verify_clerk_jwt
from app.integrations.oauth.google import GoogleOAuth


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
async def google_callback(code: str, state: str) -> dict:
    """Handle Google OAuth callback and exchange code for token."""
    try:
        oauth = GoogleOAuth()
        token_data = await oauth.get_access_token(code)
        
        # TODO: Store token_data in database for the user
        # This would typically involve:
        # 1. Decrypting the state parameter to get user/org info
        # 2. Storing the encrypted tokens in the database
        # 3. Associating with the user's organization
        
        return {
            "status": "success",
            "message": "Google OAuth token received successfully",
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "note": "Implement token storage in database"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Google OAuth callback failed: {str(e)}"
        )


@router.get("/accounts")
async def get_google_accounts(claims=Depends(get_auth_claims)) -> dict:
    """Get Google Business accounts for the authenticated user."""
    try:
        # TODO: Get access token from database for this user
        # For now, return a placeholder response
        return {
            "status": "success",
            "message": "Google Business accounts endpoint ready",
            "note": "Implement token retrieval from database to get actual accounts"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Google Business accounts: {str(e)}"
        )


@router.get("/locations")
async def get_google_locations(claims=Depends(get_auth_claims)) -> dict:
    """Get business locations for the authenticated user."""
    try:
        # TODO: Get access token from database for this user
        # For now, return a placeholder response
        return {
            "status": "success",
            "message": "Google Business locations endpoint ready",
            "note": "Implement token retrieval from database to get actual locations"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Google Business locations: {str(e)}"
        )
