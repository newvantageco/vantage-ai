from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WebPushSubscription(Base):
    """WebPush subscription for PWA notifications."""
    __tablename__ = "webpush_subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)  # Clerk user ID
    
    # WebPush subscription data
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    p256dh: Mapped[str] = mapped_column(Text, nullable=False)  # P-256 ECDH public key
    auth: Mapped[str] = mapped_column(Text, nullable=False)    # Authentication secret
    
    # Metadata
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    __table_args__ = (
        # One subscription per user per endpoint
        UniqueConstraint("user_id", "endpoint", name="uq_webpush_user_endpoint"),
        Index("ix_webpush_org_id", "org_id"),
        Index("ix_webpush_user_id", "user_id"),
        Index("ix_webpush_endpoint", "endpoint"),
        Index("ix_webpush_is_active", "is_active"),
    )


class WebPushNotification(Base):
    """Log of sent WebPush notifications."""
    __tablename__ = "webpush_notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    subscription_id: Mapped[str] = mapped_column(ForeignKey("webpush_subscriptions.id", ondelete="CASCADE"), index=True)
    
    # Notification content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    badge: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    data_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON data
    
    # Delivery status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, sent, failed, expired
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_webpush_notifications_subscription_id", "subscription_id"),
        Index("ix_webpush_notifications_status", "status"),
        Index("ix_webpush_notifications_created_at", "created_at"),
    )


class WebPushEvent(Base):
    """Event types that can trigger WebPush notifications."""
    __tablename__ = "webpush_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # POST_FAILED, APPROVAL_NEEDED, etc.
    title_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    icon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    badge_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Configuration
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    throttle_minutes: Mapped[int] = mapped_column(default=60, nullable=False)  # Throttle per user
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("org_id", "event_type", name="uq_webpush_events_org_type"),
        Index("ix_webpush_events_org_id", "org_id"),
        Index("ix_webpush_events_event_type", "event_type"),
        Index("ix_webpush_events_is_enabled", "is_enabled"),
    )
