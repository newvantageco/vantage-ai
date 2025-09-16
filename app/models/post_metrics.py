from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PostMetrics(Base):
    """Raw platform metrics for individual posts."""
    __tablename__ = "post_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    schedule_id: Mapped[str] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"), index=True)
    
    # Core metrics
    impressions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reach: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    likes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shares: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    clicks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    video_views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    saves: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Instagram saves
    
    # Cost metrics (for paid posts)
    cost_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Metadata
    fetched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        # Ensure one metrics record per schedule per day
        UniqueConstraint("schedule_id", "fetched_at", name="uq_post_metrics_schedule_fetched"),
        Index("ix_post_metrics_schedule_id", "schedule_id"),
        Index("ix_post_metrics_fetched_at", "fetched_at"),
    )
