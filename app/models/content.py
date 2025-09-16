from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ContentStatus(str, Enum):
    draft = "draft"
    approved = "approved"
    scheduled = "scheduled"
    posted = "posted"
    failed = "failed"


class BrandGuide(Base):
    __tablename__ = "brand_guides"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    voice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pillars: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    content_items: Mapped[list[ContentItem]] = relationship(back_populates="campaign", cascade="all, delete-orphan")  # type: ignore[name-defined]


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    alt_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hashtags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ContentStatus] = mapped_column(SAEnum(ContentStatus, name="content_status"), default=ContentStatus.draft, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    campaign: Mapped[Optional[Campaign]] = relationship(back_populates="content_items")  # type: ignore[name-defined]


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    content_item_id: Mapped[str] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), index=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True)
    scheduled_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[ContentStatus] = mapped_column(SAEnum(ContentStatus, name="content_status"), default=ContentStatus.scheduled, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)


