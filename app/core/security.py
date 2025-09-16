from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings


@dataclass
class AuthClaims:
	user_id: str
	org_id: Optional[str]
	email: Optional[str]


async def verify_clerk_jwt(token: str) -> AuthClaims:
	settings = get_settings()
	if not settings.clerk_jwks_url or not settings.clerk_issuer:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Auth not configured")

	async with httpx.AsyncClient(timeout=5) as client:
		jwks_resp = await client.get(settings.clerk_jwks_url)
		jwks = jwks_resp.json()

	unverified_header = jwt.get_unverified_header(token)
	kid = unverified_header.get("kid")
	if not kid:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")

	public_key = None
	for key in jwks.get("keys", []):
		if key.get("kid") == kid:
			public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
			break
	if public_key is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown key id")

	claims: Dict[str, Any] = jwt.decode(
		token,
		public_key,
		algorithms=["RS256"],
		audience=None,
		issuer=settings.clerk_issuer,
	)

	return AuthClaims(
		user_id=str(claims.get("sub")),
		org_id=str(claims.get("org_id")) if claims.get("org_id") else None,
		email=str(claims.get("email")) if claims.get("email") else None,
	)


