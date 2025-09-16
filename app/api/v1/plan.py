from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.content.plan_engine import suggest_timeslots

router = APIRouter(prefix="/content/plan", tags=["content-plan"])


@router.get("/timeslots")
def get_timeslots(
	org_id: str = Query(...),
	channel: str = Query(..., description="provider key, e.g., meta, linkedin"),
	n: int = Query(5, ge=1, le=20),
	db: Session = Depends(get_db),
):
	return {"org_id": org_id, "channel": channel, "suggestions": suggest_timeslots(db, org_id, channel, n)}


