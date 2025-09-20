from __future__ import annotations

import urllib.parse
from typing import Optional
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_bearer_token, get_db
from app.core.config import get_settings
from app.core.security import verify_clerk_jwt
from app.integrations.oauth.meta import MetaOAuth
from app.models.publishing import PlatformIntegration
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/oauth/meta", tags=["oauth-meta"])


async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
	return await verify_clerk_jwt(token)


@router.get("/authorize")
async def get_meta_auth_url(state: str, claims=Depends(get_auth_claims)) -> dict:
	_ = claims
	settings = get_settings()
	if not settings.meta_app_id or not settings.meta_redirect_uri:
		raise HTTPException(status_code=500, detail="Meta OAuth not configured")
	params = {
		"client_id": settings.meta_app_id,
		"redirect_uri": settings.meta_redirect_uri,
		"response_type": "code",
		"scope": "pages_manage_metadata,pages_read_engagement,instagram_basic,instagram_manage_comments,pages_manage_posts",
		"state": state,
	}
	url = "https://www.facebook.com/v20.0/dialog/oauth?" + urllib.parse.urlencode(params)
	return {"authorization_url": url}


@router.get("/callback")
async def meta_callback(
    code: str, 
    state: str, 
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Handle Meta OAuth callback and exchange code for tokens"""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        # Exchange code for access token
        oauth_client = MetaOAuth()
        token_data = await oauth_client.get_access_token(code)
        
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 3600)
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        # Get long-lived token
        long_lived_data = await oauth_client.get_long_lived_token(access_token)
        long_lived_token = long_lived_data.get("access_token")
        long_lived_expires_in = long_lived_data.get("expires_in", 5184000)  # 60 days
        
        # Store or update integration
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "facebook"
        ).first()
        
        if not integration:
            integration = PlatformIntegration(
                user_id=user_id,
                platform="facebook",
                status="active",
                settings={
                    "access_token": oauth_client._encrypt_token(long_lived_token),
                    "expires_at": datetime.utcnow().timestamp() + long_lived_expires_in,
                    "connected_at": datetime.utcnow().isoformat(),
                    "token_type": "long_lived"
                }
            )
            db.add(integration)
        else:
            integration.settings.update({
                "access_token": oauth_client._encrypt_token(long_lived_token),
                "expires_at": datetime.utcnow().timestamp() + long_lived_expires_in,
                "connected_at": datetime.utcnow().isoformat(),
                "token_type": "long_lived"
            })
            integration.status = "active"
        
        db.commit()
        
        logger.info(f"Meta OAuth successful for user {user_id}")
        
        return {
            "success": True,
            "message": "Facebook account connected successfully",
            "platform": "facebook",
            "expires_in": long_lived_expires_in
        }
        
    except Exception as e:
        logger.error(f"Meta OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Meta OAuth failed: {str(e)}"
        )


@router.get("/pages")
async def get_facebook_pages(
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Get Facebook pages for the authenticated user."""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "facebook",
            PlatformIntegration.status == "active"
        ).first()
        
        if not integration:
            return {"pages": []}
        
        # Decrypt and get account info
        oauth_client = MetaOAuth()
        settings = integration.settings or {}
        
        access_token = None
        if settings.get("access_token"):
            try:
                access_token = oauth_client._decrypt_token(settings["access_token"])
            except Exception as e:
                logger.error(f"Failed to decrypt Meta token: {str(e)}")
                return {"pages": []}
        
        if not access_token:
            return {"pages": []}
        
        # Get Facebook pages
        from app.utils.http import HTTPClient
        async with HTTPClient() as client:
            response = await client.request(
                "GET",
                f"https://graph.facebook.com/v{oauth_client.settings.meta_graph_version}/me/accounts",
                params={"access_token": access_token}
            )
            
            pages_data = response.json()
            pages = pages_data.get("data", [])
            
            # Get Instagram Business accounts for each page
            for page in pages:
                try:
                    page_token = await oauth_client.get_page_access_token(access_token, page["id"])
                    ig_business_id = await oauth_client.get_instagram_business_id(page_token, page["id"])
                    page["instagram_business_id"] = ig_business_id
                    page["page_access_token"] = page_token
                except Exception as e:
                    logger.warning(f"Could not get Instagram Business ID for page {page['id']}: {e}")
                    page["instagram_business_id"] = None
                    page["page_access_token"] = None
        
        return {
            "success": True,
            "pages": pages
        }
        
    except Exception as e:
        logger.error(f"Failed to get Facebook pages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Facebook pages: {str(e)}"
        )


@router.post("/disconnect")
async def disconnect_facebook(
    db: Session = Depends(get_db),
    claims=Depends(get_auth_claims)
) -> dict:
    """Disconnect Facebook account"""
    try:
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user claims")
        
        integration = db.query(PlatformIntegration).filter(
            PlatformIntegration.user_id == user_id,
            PlatformIntegration.platform == "facebook"
        ).first()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Facebook account not found")
        
        integration.status = "disconnected"
        integration.settings = {}  # Clear sensitive data
        db.commit()
        
        logger.info(f"Facebook account disconnected for user {user_id}")
        
        return {
            "success": True,
            "message": "Facebook account disconnected successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to disconnect Facebook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect Facebook: {str(e)}"
        )

