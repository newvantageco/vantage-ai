from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import os
import logging

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.analytics.reward import compute_reward
from app.models.content import Schedule, ContentStatus
from app.models.entities import Channel
from app.models.optimiser import ScheduleMetrics
from app.optimiser.bandit import derive_key

logger = logging.getLogger(__name__)


async def tick_once(db: Session) -> int:
	cutoff = datetime.utcnow() - timedelta(hours=72)
	# Find posted schedules with metrics present but not applied
	rows = db.execute(
		select(Schedule).where(Schedule.status == ContentStatus.posted, Schedule.created_at >= cutoff)
	).scalars().all()
	updated = 0
	for sch in rows:
		met = db.get(ScheduleMetrics, sch.id)
		if not met or met.applied:
			continue
		rew = compute_reward(sch.id, db)
		if rew is None:
			continue
		ch = db.get(Channel, sch.channel_id)
		if not ch:
			continue
		key = derive_key(ch, "post", sch.scheduled_at)
		from app.optimiser.bandit import update_state
		update_state(db, sch.org_id, key, rew)
		met.applied = True
		db.add(met)
		updated += 1
	db.commit()
	return updated


async def main() -> None:
	from app.db.session import SessionLocal
	while True:
		with SessionLocal() as db:
			try:
				count = await tick_once(db)
				logger.info(f"optimiser tick updated={count}")
			except Exception as e:
				logger.error(f"optimiser error: {e}")
		await asyncio.sleep(3600)


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		pass


