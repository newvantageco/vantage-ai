from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NotificationType(str, Enum):
    slack = "slack"
    email = "email"


class NotificationEvent(str, Enum):
    POST_FAILED = "POST_FAILED"
    APPROVAL_NEEDED = "APPROVAL_NEEDED"
    WEEKLY_BRIEF_READY = "WEEKLY_BRIEF_READY"
    RULE_FIRED = "RULE_FIRED"


class NotificationSubscription(Base):
    __tablename__ = "notification_subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType, name="notification_type"), nullable=False)
    target: Mapped[str] = mapped_column(String(500), nullable=False)  # webhook URL or email address
    events: Mapped[list[str]] = mapped_column(JSON, nullable=False)  # List of NotificationEvent values
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Optional metadata for additional configuration
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string for additional config
