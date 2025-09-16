from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.reports.weekly_brief import generate_weekly_brief


async def generate_and_store(org_id: str, now: Optional[datetime] = None) -> None:
    db: Session = SessionLocal()
    try:
        _ = generate_weekly_brief(db=db, org_id=org_id, now=now)
        # TODO: persist to a reports table or blob store
    finally:
        db.close()


async def main() -> None:
    # This would be triggered by cron Mondays 08:00 in each org's local tz.
    # For now, just run for demo org.
    await generate_and_store(org_id="demo-org")


if __name__ == "__main__":
    asyncio.run(main())


