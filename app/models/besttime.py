from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimeslotStats(Base):
    """Statistics for optimal posting times per organization and channel.
    
    Tracks performance metrics for different time slots (weekday + hour bucket)
    to enable data-driven posting time recommendations.
    """
    __tablename__ = "timeslot_stats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    hour_bucket: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-23
    posts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Number of posts in this slot
    avg_reward: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # EMA of reward scores
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("org_id", "channel_id", "weekday", "hour_bucket", name="uq_timeslot_org_channel_weekday_hour"),
    )
