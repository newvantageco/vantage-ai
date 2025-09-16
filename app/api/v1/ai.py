from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_bearer_token
from app.core.security import verify_clerk_jwt
from app.services.model_router import model_router


router = APIRouter(prefix="/ai", tags=["ai"])


class CompletionIn(BaseModel):
	prompt: str
	system: Optional[str] = None


class CompletionOut(BaseModel):
	text: str


async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
	return await verify_clerk_jwt(token)


@router.post("/complete", response_model=CompletionOut)
async def complete(payload: CompletionIn, claims=Depends(get_auth_claims)):
	_ = claims
	text = await model_router.complete(prompt=payload.prompt, system=payload.system)
	return CompletionOut(text=text)


