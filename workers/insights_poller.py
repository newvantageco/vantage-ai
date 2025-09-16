from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.db.session import get_db
from app.models.content import Schedule, ContentStatus
from app.models.entities import Channel
from app.models.external_refs import ScheduleExternal
from app.models.post_metrics import PostMetrics
from app.services.insights_mapper import InsightsMapper
from app.integrations.meta_insights import MetaInsightsFetcher
from app.integrations.linkedin_insights import LinkedInInsightsFetcher
from app.core.config import get_settings
from app.automation.rules_engine import rules_engine, TriggerType

logger = logging.getLogger(__name__)


class InsightsPoller:
    """Background worker for polling post insights from platforms."""
    
    def __init__(self):
        self.settings = get_settings()
        self.insights_mapper = InsightsMapper()
        self.meta_fetcher = MetaInsightsFetcher()
        self.linkedin_fetcher = LinkedInInsightsFetcher()
    
    async def poll_insights_once(self, db: Session) -> int:
        """
        Poll insights for all eligible schedules once.
        
        Args:
            db: Database session
            
        Returns:
            Number of schedules processed
        """
        logger.info("[Insights Poller] Starting insights polling cycle")
        
        # Find posted schedules with external references that need insights
        cutoff_time = datetime.utcnow() - timedelta(hours=self.settings.insights_poll_interval_hours)
        
        # Query for schedules that:
        # 1. Are posted
        # 2. Have external references
        # 3. Either have no recent metrics or metrics are older than poll interval
        stmt = select(Schedule).join(ScheduleExternal).where(
            and_(
                Schedule.status == ContentStatus.posted,
                Schedule.created_at >= datetime.utcnow() - timedelta(days=30)  # Only recent posts
            )
        )
        
        schedules = db.execute(stmt).scalars().all()
        processed = 0
        
        for schedule in schedules:
            try:
                await self._process_schedule_insights(schedule, db)
                processed += 1
            except Exception as e:
                logger.error(f"[Insights Poller] Failed to process schedule {schedule.id}: {e}")
                continue
        
        db.commit()
        logger.info(f"[Insights Poller] Processed {processed} schedules")
        return processed
    
    async def _process_schedule_insights(self, schedule: Schedule, db: Session) -> None:
        """Process insights for a single schedule."""
        logger.info(f"[Insights Poller] Processing insights for schedule {schedule.id}")
        
        # Get external references for this schedule
        external_refs = db.query(ScheduleExternal).filter(
            ScheduleExternal.schedule_id == schedule.id
        ).all()
        
        if not external_refs:
            logger.warning(f"[Insights Poller] No external references found for schedule {schedule.id}")
            return
        
        # Get channel to determine provider
        channel = db.get(Channel, schedule.channel_id)
        if not channel:
            logger.warning(f"[Insights Poller] Channel not found for schedule {schedule.id}")
            return
        
        provider = channel.provider.lower()
        
        # Check if we should use fake insights
        if not self.insights_mapper.should_fetch_real_insights():
            logger.info(f"[Insights Poller] Using fake insights for {provider} schedule {schedule.id}")
            await self._generate_fake_insights(schedule, provider, db)
            return
        
        # Check if we already have recent metrics for today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_metrics = db.query(PostMetrics).filter(
            and_(
                PostMetrics.schedule_id == schedule.id,
                func.date(PostMetrics.fetched_at) == today.date()
            )
        ).first()
        
        if recent_metrics:
            logger.info(f"[Insights Poller] Recent metrics already exist for schedule {schedule.id} on {today.date()}")
            return
        
        # Fetch real insights
        try:
            await self._fetch_and_store_insights(schedule, external_refs, provider, db)
        except Exception as e:
            logger.error(f"[Insights Poller] Failed to fetch insights for schedule {schedule.id}: {e}")
            # Fall back to fake insights if real fetching fails
            await self._generate_fake_insights(schedule, provider, db)
    
    async def _fetch_and_store_insights(
        self, 
        schedule: Schedule, 
        external_refs: List[ScheduleExternal], 
        provider: str,
        db: Session
    ) -> None:
        """Fetch and store real insights from platform APIs."""
        logger.info(f"[Insights Poller] Fetching real insights for schedule {schedule.id}")
        
        # For now, this is a placeholder - would need access tokens
        # In practice, you'd get access tokens from your token storage system
        
        if provider in ["facebook", "instagram"]:
            logger.warning(f"[Insights Poller] Meta insights fetching not fully implemented for {schedule.id}")
            # Would implement: await self.meta_fetcher.get_post_insights(...)
        elif provider == "linkedin":
            logger.warning(f"[Insights Poller] LinkedIn insights fetching not fully implemented for {schedule.id}")
            # Would implement: await self.linkedin_fetcher.get_post_insights(...)
        
        # For now, generate fake insights as fallback
        await self._generate_fake_insights(schedule, provider, db)
    
    async def _generate_fake_insights(
        self, 
        schedule: Schedule, 
        provider: str, 
        db: Session
    ) -> None:
        """Generate fake insights for testing/development."""
        logger.info(f"[Insights Poller] Generating fake insights for {provider} schedule {schedule.id}")
        
        post_metrics = self.insights_mapper.generate_fake_metrics(schedule.id, provider)
        await self._upsert_post_metrics(post_metrics, db)
        
        # Trigger rules for post performance
        await self._trigger_post_performance_rules(schedule.id, post_metrics, db)
    
    async def _upsert_post_metrics(self, post_metrics: PostMetrics, db: Session) -> None:
        """
        Upsert PostMetrics to prevent duplicates by schedule_id + fetched_at::date.
        Uses PostgreSQL's ON CONFLICT for atomic upsert.
        """
        try:
            # Create upsert statement using PostgreSQL's ON CONFLICT
            stmt = insert(PostMetrics).values(
                id=post_metrics.id,
                schedule_id=post_metrics.schedule_id,
                impressions=post_metrics.impressions,
                reach=post_metrics.reach,
                likes=post_metrics.likes,
                comments=post_metrics.comments,
                shares=post_metrics.shares,
                clicks=post_metrics.clicks,
                video_views=post_metrics.video_views,
                saves=post_metrics.saves,
                cost_cents=post_metrics.cost_cents,
                fetched_at=post_metrics.fetched_at,
                created_at=post_metrics.created_at
            )
            
            # On conflict with unique constraint (schedule_id, fetched_at), update the metrics
            stmt = stmt.on_conflict_do_update(
                constraint="uq_post_metrics_schedule_fetched",
                set_={
                    "impressions": stmt.excluded.impressions,
                    "reach": stmt.excluded.reach,
                    "likes": stmt.excluded.likes,
                    "comments": stmt.excluded.comments,
                    "shares": stmt.excluded.shares,
                    "clicks": stmt.excluded.clicks,
                    "video_views": stmt.excluded.video_views,
                    "saves": stmt.excluded.saves,
                    "cost_cents": stmt.excluded.cost_cents,
                    "created_at": stmt.excluded.created_at
                }
            )
            
            db.execute(stmt)
            logger.info(f"[Insights Poller] Upserted PostMetrics for schedule {post_metrics.schedule_id}")
            
        except Exception as e:
            logger.error(f"[Insights Poller] Failed to upsert PostMetrics: {e}")
            # Fallback to regular insert
            db.add(post_metrics)
    
    async def poll_insights_for_schedule(self, schedule_id: str, db: Session) -> bool:
        """
        Poll insights for a specific schedule.
        
        Args:
            schedule_id: Schedule ID
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            schedule = db.get(Schedule, schedule_id)
            if not schedule:
                logger.error(f"[Insights Poller] Schedule {schedule_id} not found")
                return False
            
            await self._process_schedule_insights(schedule, db)
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"[Insights Poller] Failed to poll insights for schedule {schedule_id}: {e}")
            return False
    
    async def get_insights_summary(self, db: Session) -> Dict[str, Any]:
        """
        Get summary of insights polling status.
        
        Args:
            db: Database session
            
        Returns:
            Dict containing polling summary
        """
        # Count schedules with external references
        total_schedules = db.query(Schedule).filter(
            Schedule.status == ContentStatus.posted
        ).count()
        
        schedules_with_refs = db.query(Schedule).join(ScheduleExternal).filter(
            Schedule.status == ContentStatus.posted
        ).count()
        
        # Count schedules with recent metrics
        cutoff_time = datetime.utcnow() - timedelta(hours=self.settings.insights_poll_interval_hours)
        schedules_with_metrics = db.query(PostMetrics).filter(
            PostMetrics.fetched_at >= cutoff_time
        ).count()
        
        return {
            "total_posted_schedules": total_schedules,
            "schedules_with_external_refs": schedules_with_refs,
            "schedules_with_recent_metrics": schedules_with_metrics,
            "poll_interval_hours": self.settings.insights_poll_interval_hours,
            "using_fake_insights": self.settings.feature_fake_insights
        }
    
    async def _trigger_post_performance_rules(
        self, 
        schedule_id: str, 
        post_metrics: PostMetrics, 
        db: Session
    ) -> None:
        """Trigger post performance rules based on metrics."""
        try:
            # Calculate engagement rate
            impressions = post_metrics.impressions or 0
            likes = post_metrics.likes or 0
            comments = post_metrics.comments or 0
            shares = post_metrics.shares or 0
            
            total_engagement = likes + comments + shares
            engagement_rate = total_engagement / impressions if impressions > 0 else 0
            
            # Create payload for rules engine
            payload = {
                "schedule_id": schedule_id,
                "impressions": impressions,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "engagement_rate": engagement_rate,
                "video_views": post_metrics.video_views or 0,
                "clicks": post_metrics.clicks or 0,
                "fetched_at": post_metrics.fetched_at.isoformat()
            }
            
            # Trigger post performance rules
            await rules_engine.process_trigger(TriggerType.POST_PERFORMANCE, payload, db)
            logger.info(f"[Insights Poller] Triggered post performance rules for schedule {schedule_id}")
            
        except Exception as e:
            logger.error(f"[Insights Poller] Failed to trigger post performance rules: {e}")


async def main() -> None:
    """Main function for running the insights poller."""
    from app.db.session import SessionLocal
    
    logger.info("[Insights Poller] Starting insights poller worker")
    
    poller = InsightsPoller()
    
    while True:
        try:
            db = SessionLocal()
            try:
                processed = await poller.poll_insights_once(db)
                logger.info(f"[Insights Poller] Processed {processed} schedules")
            finally:
                db.close()
            
            # Wait for next poll interval
            poll_interval = poller.settings.insights_poll_interval_hours * 3600  # Convert to seconds
            logger.info(f"[Insights Poller] Waiting {poller.settings.insights_poll_interval_hours} hours before next poll")
            await asyncio.sleep(poll_interval)
            
        except KeyboardInterrupt:
            logger.info("[Insights Poller] Shutting down insights poller")
            break
        except Exception as e:
            logger.error(f"[Insights Poller] Unexpected error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    asyncio.run(main())
