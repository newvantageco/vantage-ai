from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import redis.asyncio as redis
from app.core.config import get_settings

from app.db.session import get_db
from app.models.content import Schedule, ContentStatus
from app.scheduler.engine import fetch_due_schedules, run_tick


async def get_redis_client() -> redis.Redis:
    """Get Redis client for distributed operations."""
    settings = get_settings()
    return redis.from_url(settings.redis_url)


router = APIRouter(prefix="/schedule", tags=["schedule"])


class ScheduleIn(BaseModel):
    content_id: str
    channel_id: str
    scheduled_for: datetime


@router.post("/bulk")
def bulk_create(payload: List[ScheduleIn], db: Session = Depends(get_db)):
    from uuid import uuid4
    rows: list[Schedule] = []
    for item in payload:
        sch = Schedule(
            id=str(uuid4()),
            org_id="demo-org",  # Use consistent org_id for demo
            content_item_id=item.content_id,
            channel_id=item.channel_id,
            scheduled_at=item.scheduled_for,
            status=ContentStatus.scheduled,
        )
        rows.append(sch)
        db.add(sch)
    db.commit()
    return {"created": len(rows)}


@router.get("/due")
def list_due(db: Session = Depends(get_db)):
    rows = list(fetch_due_schedules(db, limit=100))
    return [
        {
            "id": r.id,
            "content_item_id": r.content_item_id,
            "channel_id": r.channel_id,
            "scheduled_at": r.scheduled_at.isoformat(),
            "status": r.status.value,
        }
        for r in rows
    ]


@router.post("/run")
async def run_once(db: Session = Depends(get_db)):
    """Run scheduler once with Redis support."""
    try:
        redis_client = await get_redis_client()
        n = await run_tick(db, redis_client)
        return {"processed": n, "status": "success"}
    except Exception as e:
        # Fallback to direct processing if Redis fails
        n = await run_tick(db, None)
        return {"processed": n, "status": "fallback", "error": str(e)}


@router.get("/health")
async def health_check():
    """Health check for scheduler service."""
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "degraded", "redis": "disconnected", "error": str(e)}


