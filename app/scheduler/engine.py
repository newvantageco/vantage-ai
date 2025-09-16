from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
import redis.asyncio as redis
import json
import asyncio
from contextlib import asynccontextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Schedule, ContentStatus, ContentItem
from app.models.entities import Channel
from app.models.external_refs import ScheduleExternal
from app.publishers.base import Publisher
from app.publishers.linkedin import LinkedInPublisher
from app.publishers.meta import MetaPublisher
from app.core.config import get_settings
from uuid import uuid4


class SchedulerLock:
    """Distributed lock for scheduler operations."""
    
    def __init__(self, redis_client: redis.Redis, lock_key: str = "scheduler:lock", timeout: int = 300):
        self.redis = redis_client
        self.lock_key = lock_key
        self.timeout = timeout
        self.lock = None
    
    async def __aenter__(self):
        self.lock = await self.redis.lock(
            self.lock_key, 
            timeout=self.timeout,
            blocking_timeout=1.0
        )
        return self.lock
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.lock:
            await self.lock.release()


def _publisher_for_provider(provider: str) -> Publisher:
    provider_lc = (provider or "").lower()
    if provider_lc == "linkedin":
        return LinkedInPublisher()
    if provider_lc == "meta":
        return MetaPublisher()
    return MetaPublisher()


def fetch_due_schedules(db: Session, limit: int = 50, timezone_offset: int = 0) -> Iterable[Schedule]:
    """Fetch schedules that are due for processing with proper timezone handling."""
    # Use UTC timezone consistently
    now = datetime.now(timezone.utc)
    # Apply timezone offset if provided (for testing)
    if timezone_offset != 0:
        now = now.replace(hour=(now.hour + timezone_offset) % 24)
    
    # Use SELECT FOR UPDATE SKIP LOCKED
    stmt = (
        select(Schedule)
        .where(Schedule.status == ContentStatus.scheduled)
        .where(Schedule.scheduled_at <= now.replace(tzinfo=None))
        .with_for_update(skip_locked=True)
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    return rows


async def run_tick(db: Session, redis_client: redis.Redis = None) -> int:
    """Run a single scheduler tick with proper locking and error handling."""
    if not redis_client:
        # Fallback to direct processing if no Redis
        return await _process_schedules_direct(db)
    
    # Use distributed lock to prevent multiple workers from processing the same schedules
    async with SchedulerLock(redis_client) as lock:
        if not lock:
            return 0  # Could not acquire lock
        
        return await _process_schedules_with_redis(db, redis_client)


async def _process_schedules_direct(db: Session) -> int:
    """Process schedules directly without Redis (fallback mode)."""
    due = fetch_due_schedules(db)
    processed = 0
    for sch in due:
        channel = db.get(Channel, sch.channel_id)
        content = db.get(ContentItem, sch.content_item_id)
        if not channel or not content:
            sch.status = ContentStatus.failed
            sch.error_message = "Missing channel or content"
            db.add(sch)
            continue
        pub = _publisher_for_provider(channel.provider)
        try:
            result = await pub.publish(
                caption=content.caption or content.title or "",
                media_paths=[],
                first_comment=content.first_comment,
                idempotency_key=f"{sch.id}:{sch.scheduled_at.isoformat()}",
            )
            sch.status = ContentStatus.posted
            # store result JSON-like as simple string for now
            sch.error_message = f"id={result.id} url={result.url}"
            
            # Store external references if available
            if result.external_refs:
                for provider, ref_id in result.external_refs.items():
                    external_ref = ScheduleExternal(
                        id=str(uuid4()),
                        schedule_id=sch.id,
                        ref_id=ref_id,
                        ref_url=result.url if provider == channel.provider.lower() else None,
                        provider=provider
                    )
                    db.add(external_ref)
            
            # In E2E mock mode, always create a schedule_external entry
            settings = get_settings()
            if settings.e2e_mocks:
                # Check if we already have an external ref for this schedule and provider
                existing_ref = db.query(ScheduleExternal).filter(
                    ScheduleExternal.schedule_id == sch.id,
                    ScheduleExternal.provider == channel.provider.lower()
                ).first()
                
                if not existing_ref:
                    mock_external_ref = ScheduleExternal(
                        id=str(uuid4()),
                        schedule_id=sch.id,
                        ref_id=f"mock_{sch.id}_{channel.provider.lower()}",
                        ref_url=f"https://mock.{channel.provider.lower()}.com/posts/{sch.id}",
                        provider=channel.provider.lower()
                    )
                    db.add(mock_external_ref)
            
            processed += 1
        except Exception as e:
            sch.status = ContentStatus.failed
            sch.error_message = str(e)
        db.add(sch)
    db.commit()
    return processed


async def _process_schedules_with_redis(db: Session, redis_client: redis.Redis) -> int:
    """Process schedules with Redis-based idempotency and error handling."""
    due = fetch_due_schedules(db)
    processed = 0
    
    for sch in due:
        # Check if already processed (idempotency)
        idempotency_key = f"scheduler:processed:{sch.id}"
        if await redis_client.exists(idempotency_key):
            continue
        
        # Mark as being processed
        await redis_client.setex(idempotency_key, 3600, "processing")  # 1 hour TTL
        
        try:
            channel = db.get(Channel, sch.channel_id)
            content = db.get(ContentItem, sch.content_item_id)
            
            if not channel or not content:
                sch.status = ContentStatus.failed
                sch.error_message = "Missing channel or content"
                db.add(sch)
                continue
            
            pub = _publisher_for_provider(channel.provider)
            
            # Retry logic for transient failures
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = await pub.publish(
                        caption=content.caption or content.title or "",
                        media_paths=[],
                        first_comment=content.first_comment,
                        idempotency_key=f"{sch.id}:{sch.scheduled_at.isoformat()}:{attempt}",
                    )
                    
                    sch.status = ContentStatus.posted
                    sch.error_message = f"id={result.id} url={result.url}"
                    
                    # Store external references if available
                    if result.external_refs:
                        for provider, ref_id in result.external_refs.items():
                            external_ref = ScheduleExternal(
                                id=str(uuid4()),
                                schedule_id=sch.id,
                                ref_id=ref_id,
                                ref_url=result.url if provider == channel.provider.lower() else None,
                                provider=provider
                            )
                            db.add(external_ref)
                    
                    # In E2E mock mode, always create a schedule_external entry
                    settings = get_settings()
                    if settings.e2e_mocks:
                        # Check if we already have an external ref for this schedule and provider
                        existing_ref = db.query(ScheduleExternal).filter(
                            ScheduleExternal.schedule_id == sch.id,
                            ScheduleExternal.provider == channel.provider.lower()
                        ).first()
                        
                        if not existing_ref:
                            mock_external_ref = ScheduleExternal(
                                id=str(uuid4()),
                                schedule_id=sch.id,
                                ref_id=f"mock_{sch.id}_{channel.provider.lower()}",
                                ref_url=f"https://mock.{channel.provider.lower()}.com/posts/{sch.id}",
                                provider=channel.provider.lower()
                            )
                            db.add(mock_external_ref)
                    
                    # Mark as successfully processed
                    await redis_client.setex(idempotency_key, 86400, "completed")  # 24 hours TTL
                    processed += 1
                    break
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        # Final attempt failed
                        sch.status = ContentStatus.failed
                        sch.error_message = f"Failed after {max_retries} attempts: {str(e)}"
                        await redis_client.setex(idempotency_key, 3600, "failed")
                    else:
                        # Retry after delay
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
            
            db.add(sch)
            
        except Exception as e:
            sch.status = ContentStatus.failed
            sch.error_message = f"Processing error: {str(e)}"
            db.add(sch)
            await redis_client.setex(idempotency_key, 3600, "error")
    
    db.commit()
    return processed


