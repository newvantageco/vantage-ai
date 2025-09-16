from __future__ import annotations

import urllib.parse
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_bearer_token
from app.core.config import get_settings
from app.core.security import verify_clerk_jwt


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
async def meta_callback(code: str, state: str) -> dict:
	# Placeholder: exchange code for token and persist
	return {"received": True, "code": code, "state": state}



