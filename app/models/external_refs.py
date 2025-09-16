from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScheduleExternal(Base):
    """Links schedules to platform-specific post IDs and URLs."""
    __tablename__ = "schedule_external"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    schedule_id: Mapped[str] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"), index=True)
    
    # Platform-specific identifiers
    ref_id: Mapped[str] = mapped_column(String(255), nullable=False)  # Platform post ID
    ref_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Platform post URL
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'linkedin', 'facebook', 'instagram'
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        # One external ref per schedule per provider
        UniqueConstraint("schedule_id", "provider", name="uq_schedule_external_schedule_provider"),
        Index("ix_schedule_external_schedule_id", "schedule_id"),
        Index("ix_schedule_external_provider", "provider"),
        Index("ix_schedule_external_ref_id", "ref_id"),
    )
