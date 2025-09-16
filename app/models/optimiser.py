from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OptimiserState(Base):
	__tablename__ = "optimiser_state"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
	key: Mapped[str] = mapped_column(String(128), index=True)
	pulls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	rewards: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
	last_action_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

	__table_args__ = (
		UniqueConstraint("org_id", "key", name="uq_optimiser_org_key"),
	)


class ScheduleMetrics(Base):
	__tablename__ = "schedule_metrics"

	schedule_id: Mapped[str] = mapped_column(String(36), primary_key=True)
	ctr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	engagement_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	reach_norm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	conv_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	applied: Mapped[bool] = mapped_column(default=False, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


