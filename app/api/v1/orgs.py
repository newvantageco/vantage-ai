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
from app.models.entities import Organization, UserAccount


router = APIRouter(prefix="/orgs", tags=["orgs"])


class OrgCreate(BaseModel):
	name: str


class OrgOut(BaseModel):
	id: str
	name: str

	class Config:
		from_attributes = True


async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
	return await verify_clerk_jwt(token)


@router.post("", response_model=OrgOut)
async def create_org(payload: OrgCreate, db: Session = Depends(get_db), claims=Depends(get_auth_claims)):
	org = Organization(id=str(uuid.uuid4()), name=payload.name)
	db.add(org)
	db.flush()

	user = UserAccount(id=claims.user_id, org_id=org.id, email=claims.email, role="owner")
	db.merge(user)
	db.commit()
	db.refresh(org)
	return org


@router.get("", response_model=list[OrgOut])
async def list_orgs(db: Session = Depends(get_db), claims=Depends(get_auth_claims)):
	stmt = select(Organization).join(UserAccount, UserAccount.org_id == Organization.id).where(UserAccount.id == claims.user_id)
	orgs = db.scalars(stmt).all()
	return orgs



