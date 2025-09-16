from __future__ import annotations

import asyncio
import os
import time
import logging
import signal
import sys

import httpx

logger = logging.getLogger(__name__)

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1")


async def tick_once(client: httpx.AsyncClient) -> None:
    try:
        resp = await client.post(f"{API_BASE}/schedule/run")
        resp.raise_for_status()
        result = resp.json()
        logger.info(f"Scheduler processed: {result.get('processed', 0)} items, status: {result.get('status', 'unknown')}")
        
        # If the scheduler returns post results, we could save them here
        # This would typically involve updating the database with post IDs and permalinks
        if "post_results" in result:
            await save_post_results(result["post_results"])
            
    except Exception as e:
        logger.error(f"Scheduler error: {e}")


async def save_post_results(post_results: list[dict]) -> None:
    """Save post results to database."""
    for result in post_results:
        try:
            # This would typically save to your database
            # For now, we'll just log the results
            logger.info(f"Saving post result: {result}")
            
            # Example of what you might save:
            # - schedule_id: The ID of the scheduled post
            # - platform: The platform (linkedin, meta, etc.)
            # - external_post_id: The ID returned by the platform
            # - permalink: The URL to the published post
            # - published_at: Timestamp when it was published
            # - status: success, failed, etc.
            
        except Exception as e:
            logger.error(f"Failed to save post result {result}: {e}")


async def main() -> None:
    """Main scheduler worker loop with improved error handling."""
    backoff = 1.0
    max_backoff = 60.0
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    async with httpx.AsyncClient(timeout=30) as client:
        logger.info("Scheduler worker started")
        while True:
            try:
                await tick_once(client)
                backoff = 1.0  # Reset backoff on success
            except Exception as e:
                logger.error(f"Tick failed: {e}, backing off for {backoff}s")
                backoff = min(backoff * 2, max_backoff)  # Exponential backoff with cap
            
            await asyncio.sleep(backoff)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Scheduler worker stopped by user")
        pass
    except Exception as e:
        logger.error(f"Scheduler worker failed: {e}")
        sys.exit(1)


