from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime

from app.workers.privacy_worker import cleanup_expired_data

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main loop for privacy cleanup worker."""
    logger.info("Starting privacy cleanup worker")
    
    while True:
        try:
            await cleanup_expired_data()
            logger.info("Privacy cleanup cycle completed")
        except Exception as e:
            logger.error(f"Privacy cleanup error: {e}")
        
        # Run once per day
        await asyncio.sleep(24 * 3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Privacy cleanup worker stopped")
