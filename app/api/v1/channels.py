from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_bearer_token
from app.core.security import verify_clerk_jwt
from app.db.session import get_db
from app.models.entities import Channel, Organization, UserAccount


router = APIRouter(prefix="/channels", tags=["channels"])


class ChannelCreate(BaseModel):
	org_id: str
	provider: str
	account_ref: Optional[str] = None
	access_token: Optional[str] = None
	refresh_token: Optional[str] = None
	metadata_json: Optional[str] = None


class ChannelOut(BaseModel):
	id: str
	org_id: str
	provider: str
	account_ref: Optional[str]

	class Config:
		from_attributes = True


async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
	return await verify_clerk_jwt(token)


def assert_user_in_org(db: Session, user_id: str, org_id: str) -> None:
	member = db.get(UserAccount, user_id)
	if not member or member.org_id != org_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("", response_model=ChannelOut)
async def create_channel(payload: ChannelCreate, db: Session = Depends(get_db), claims=Depends(get_auth_claims)):
	assert_user_in_org(db, claims.user_id, payload.org_id)
	channel = Channel(
		id=str(uuid.uuid4()),
		org_id=payload.org_id,
		provider=payload.provider,
		account_ref=payload.account_ref,
		access_token=payload.access_token,
		refresh_token=payload.refresh_token,
		metadata_json=payload.metadata_json,
	)
	db.add(channel)
	db.commit()
	db.refresh(channel)
	return channel


@router.get("", response_model=list[ChannelOut])
async def list_channels(org_id: str, db: Session = Depends(get_db), claims=Depends(get_auth_claims)):
	assert_user_in_org(db, claims.user_id, org_id)
	stmt = select(Channel).where(Channel.org_id == org_id)
	channels = db.scalars(stmt).all()
	return channels



