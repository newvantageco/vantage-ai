from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import httpx
import redis.asyncio as redis
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.automation.rules_engine import rules_engine, TriggerType
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Redis connection
redis_client: Optional[redis.Redis] = None

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1")


async def get_redis_client() -> redis.Redis:
    """Get Redis client connection."""
    global redis_client
    if redis_client is None:
        settings = get_settings()
        redis_client = redis.from_url(settings.redis_url)
    return redis_client


class RulesWorker:
    """Background worker for processing automation rules."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis = None
    
    async def initialize(self):
        """Initialize the worker."""
        self.redis = await get_redis_client()
        logger.info("Rules worker initialized")
    
    async def process_trigger_event(self, trigger_type: str, payload: Dict[str, Any]) -> int:
        """Process a trigger event."""
        try:
            db = SessionLocal()
            try:
                # Convert string to enum
                trigger_enum = TriggerType(trigger_type)
                
                # Process the trigger
                executed_count = await rules_engine.process_trigger(trigger_enum, payload, db)
                
                logger.info(f"Processed trigger {trigger_type}, executed {executed_count} rules")
                return executed_count
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing trigger {trigger_type}: {e}")
            return 0
    
    async def poll_redis_events(self) -> int:
        """Poll Redis for trigger events."""
        if not self.redis:
            await self.initialize()
        
        processed_count = 0
        
        try:
            # Check for events in Redis streams or pub/sub
            # For now, we'll use a simple list-based approach
            while True:
                # Pop event from Redis list
                event_data = await self.redis.lpop("rules:events")
                if not event_data:
                    break
                
                try:
                    event = json.loads(event_data)
                    trigger_type = event.get("trigger_type")
                    payload = event.get("payload", {})
                    
                    if trigger_type:
                        count = await self.process_trigger_event(trigger_type, payload)
                        processed_count += count
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse event data: {e}")
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
            
        except Exception as e:
            logger.error(f"Error polling Redis events: {e}")
        
        return processed_count
    
    async def check_scheduled_rules(self) -> int:
        """Check for rules that should be triggered based on time or data conditions."""
        db = SessionLocal()
        try:
            # This would check for time-based triggers, performance thresholds, etc.
            # For now, we'll implement a simple example
            
            # Check for post performance rules
            await self._check_post_performance_rules(db)
            
            return 0
            
        finally:
            db.close()
    
    async def _check_post_performance_rules(self, db: Session):
        """Check for post performance rules that need to be triggered."""
        # This would query for posts that have been up for 24+ hours
        # and check if they meet performance criteria
        # For now, this is a placeholder
        logger.debug("Checking post performance rules")
    
    async def run_once(self) -> int:
        """Run the worker once."""
        if not self.settings.automations_enabled:
            logger.debug("Automations disabled, skipping rules worker")
            return 0
        
        processed_count = 0
        
        # Process Redis events
        redis_count = await self.poll_redis_events()
        processed_count += redis_count
        
        # Check scheduled rules
        scheduled_count = await self.check_scheduled_rules()
        processed_count += scheduled_count
        
        return processed_count


async def publish_trigger_event(trigger_type: str, payload: Dict[str, Any]):
    """Publish a trigger event to Redis."""
    try:
        redis_client = await get_redis_client()
        
        event = {
            "trigger_type": trigger_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await redis_client.lpush("rules:events", json.dumps(event))
        logger.info(f"Published trigger event: {trigger_type}")
        
    except Exception as e:
        logger.error(f"Failed to publish trigger event: {e}")


async def main() -> None:
    """Main function for running the rules worker."""
    settings = get_settings()
    
    logger.info("Starting rules worker")
    
    worker = RulesWorker()
    await worker.initialize()
    
    backoff = 1.0
    
    while True:
        try:
            processed = await worker.run_once()
            if processed > 0:
                logger.info(f"Rules worker processed {processed} events")
                backoff = 1.0  # Reset backoff on success
            else:
                logger.debug("Rules worker found no events to process")
            
            # Wait for next poll interval
            await asyncio.sleep(settings.rules_worker_interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("Rules worker shutting down")
            break
        except Exception as e:
            logger.error(f"Rules worker error: {e}")
            await asyncio.sleep(min(backoff, 60))  # Exponential backoff, max 60s
            backoff *= 2


if __name__ == "__main__":
    asyncio.run(main())
