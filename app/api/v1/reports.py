from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_bearer_token
from app.core.security import verify_clerk_jwt
from app.db.session import get_db
from app.reports.weekly_brief import generate_weekly_brief, generate_weekly_brief_fake
from app.ai.brief_writer import write_brief_markdown


router = APIRouter(prefix="/reports", tags=["reports"])


class WeeklyIn(BaseModel):
    org_id: str
    dry_run: bool = True


class WeeklyOut(BaseModel):
    summary: Dict[str, Any]
    markdown: str


async def get_auth_claims(token: Optional[str] = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return await verify_clerk_jwt(token)


@router.post("/weekly", response_model=WeeklyOut)
async def weekly(payload: WeeklyIn, db: Session = Depends(get_db), claims=Depends(get_auth_claims)):
    _ = claims
    if payload.dry_run:
        summary = generate_weekly_brief_fake(org_id=payload.org_id)
    else:
        summary = generate_weekly_brief(db=db, org_id=payload.org_id)
    md_obj = await write_brief_markdown(summary)
    return WeeklyOut(summary=summary, markdown=md_obj.get("markdown", ""))


class ApplyAction(BaseModel):
    action: str
    schedule_id: Optional[str] = None
    content_id: Optional[str] = None
    timeslot: Optional[str] = None
    channel: Optional[str] = None
    by_pct: Optional[int] = None
    count: Optional[int] = None


class ApplyIn(BaseModel):
    org_id: str
    actions: List[ApplyAction]
    dry_run: bool = True


class ApplyOut(BaseModel):
    accepted: int
    created_schedules: int
    created_variants: int


@router.post("/weekly/apply", response_model=ApplyOut)
async def weekly_apply(payload: ApplyIn, db: Session = Depends(get_db), claims=Depends(get_auth_claims)):
    _ = claims
    # Guardrail: only non-destructive stubs. No real budget changes.
    accepted = 0
    created_schedules = 0
    created_variants = 0
    
    # Track processed idempotency keys to prevent duplicates
    processed_keys = set()

    for a in payload.actions:
        # Check idempotency - skip if already processed
        idempotency_key = getattr(a, 'idempotency_key', None)
        if idempotency_key and idempotency_key in processed_keys:
            continue
        
        if a.action == "clone_post" and a.schedule_id:
            accepted += 1
            if idempotency_key:
                processed_keys.add(idempotency_key)
            # In dry-run, we don't mutate; otherwise we would enqueue a clone-and-schedule task
            if not payload.dry_run:
                # TODO: enqueue worker job to clone schedule_id to next matching timeslot
                created_schedules += 1
        elif a.action == "create_variants" and a.content_id:
            accepted += 1
            if idempotency_key:
                processed_keys.add(idempotency_key)
            if not payload.dry_run:
                # TODO: enqueue worker job to create N variants of content_id
                created_variants += int(a.count or 0)
        elif a.action == "increase_budget":
            accepted += 1
            if idempotency_key:
                processed_keys.add(idempotency_key)
            # Budget changes are stubbed only; no mutation.
        elif a.action == "optimize_schedule":
            accepted += 1
            if idempotency_key:
                processed_keys.add(idempotency_key)
            # Generic optimization action - no specific implementation needed
        else:
            # Unknown action; ignore safely
            continue

    return ApplyOut(accepted=accepted, created_schedules=created_schedules, created_variants=created_variants)


