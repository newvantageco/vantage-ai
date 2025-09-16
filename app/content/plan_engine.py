from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session

from app.optimiser.bandit import suggest_timeslots as _suggest_timeslots


def suggest_timeslots(db: Session, org_id: str, channel: str, n: int = 5) -> List[dict]:
	return _suggest_timeslots(db, org_id, channel, n)


