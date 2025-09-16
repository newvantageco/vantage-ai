from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Schedule
from app.models.entities import Channel
from app.models.optimiser import OptimiserState


TimeslotKey = str  # "{channel}:{format}:{timeslot_bucket}"


def timeslot_bucket(dt: datetime) -> str:
	weekday = dt.strftime("%a")
	hour = dt.hour
	return f"{weekday}:{hour:02d}"


def derive_key(channel: Channel, fmt: str, dt: datetime) -> TimeslotKey:
	return f"{channel.provider}:{fmt}:{timeslot_bucket(dt)}"


def get_candidates(db: Session, org_id: str, window_days: int = 28) -> List[TimeslotKey]:
	cutoff = datetime.utcnow() - timedelta(days=window_days)
	stmt = (
		select(Schedule, Channel)
		.join(Channel, Channel.id == Schedule.channel_id)
		.where(Schedule.org_id == org_id)
		.where(Schedule.scheduled_at >= cutoff)
	)
	rows = db.execute(stmt).all()
	keys: set[str] = set()
	for sch, ch in rows:
		fmt = "post"
		keys.add(derive_key(ch, fmt, sch.scheduled_at))
	return sorted(keys)


def thompson_sample(states: Iterable[OptimiserState]) -> Optional[TimeslotKey]:
	best_key: Optional[str] = None
	best_score = -1.0
	for st in states:
		scale = max(1, st.pulls) * 10
		successes = max(0.0, min(scale, st.rewards * 10))
		failures = max(1.0, scale - successes)
		sample = random.betavariate(1.0 + successes, 1.0 + failures)
		if st.pulls == 0:
			sample = random.random()
		if sample > best_score:
			best_score = sample
			best_key = st.key
	return best_key


def update_state(db: Session, org_id: str, key: str, reward: float) -> OptimiserState:
	from uuid import uuid4
	reward = max(0.0, min(1.0, reward))
	row = db.execute(
		select(OptimiserState).where(OptimiserState.org_id == org_id, OptimiserState.key == key)
	).scalar_one_or_none()
	if row is None:
		row = OptimiserState(
			id=str(uuid4()), org_id=org_id, key=key, pulls=1, rewards=reward, last_action_at=datetime.utcnow()
		)
		db.add(row)
	else:
		row.pulls += 1
		row.rewards += reward
		row.last_action_at = datetime.utcnow()
		db.add(row)
	db.commit()
	return row


def suggest_timeslots(db: Session, org_id: str, channel: str, n: int = 5) -> List[Dict[str, str]]:
	prefix = f"{channel}:"
	states = db.execute(
		select(OptimiserState).where(OptimiserState.org_id == org_id, OptimiserState.key.like(prefix + "%"))
	).scalars().all()
	if not states:
		cands = [k for k in get_candidates(db, org_id) if k.startswith(prefix)]
		if not cands:
			now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
			return [
				{"key": f"{channel}:post:{timeslot_bucket(now + timedelta(hours=i))}", "when": (now + timedelta(hours=i)).isoformat()}
				for i in range(1, n + 1)
			]
		return [{"key": k, "when": ""} for k in cands[:n]]
	picked: List[str] = []
	for _ in range(n * 2):
		k = thompson_sample(states)
		if not k:
			break
		if k not in picked:
			picked.append(k)
		if len(picked) >= n:
			break
	results: List[Dict[str, str]] = []
	now = datetime.utcnow()
	for k in picked:
		parts = k.split(":")
		bucket = parts[-1]
		weekday_abbr, hour_str = bucket.split(":")
		for i in range(1, 8 * 24):
			cand = now + timedelta(hours=i)
			if cand.strftime("%a") == weekday_abbr and cand.hour == int(hour_str):
				results.append({"key": k, "when": cand.isoformat()})
				break
	return results[:n]


