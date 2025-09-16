from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any
import json
import secrets

from sqlalchemy import String, Text, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    """Comments on content items for collaboration."""
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # Clerk user ID
    
    # Comment content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)  # For replies
    
    # Mentions
    mentioned_user_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of user IDs
    
    # Status
    is_resolved: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_edited: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_comments_content_id", "content_id"),
        Index("ix_comments_org_id", "org_id"),
        Index("ix_comments_user_id", "user_id"),
        Index("ix_comments_parent_id", "parent_id"),
        Index("ix_comments_created_at", "created_at"),
    )

    def get_mentioned_user_ids(self) -> list[str]:
        """Get mentioned user IDs as a list."""
        if not self.mentioned_user_ids:
            return []
        try:
            return json.loads(self.mentioned_user_ids)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_mentioned_user_ids(self, user_ids: list[str]) -> None:
        """Set mentioned user IDs from a list."""
        self.mentioned_user_ids = json.dumps(user_ids)

    def add_mention(self, user_id: str) -> None:
        """Add a user mention."""
        mentioned = self.get_mentioned_user_ids()
        if user_id not in mentioned:
            mentioned.append(user_id)
            self.set_mentioned_user_ids(mentioned)

    def remove_mention(self, user_id: str) -> None:
        """Remove a user mention."""
        mentioned = self.get_mentioned_user_ids()
        if user_id in mentioned:
            mentioned.remove(user_id)
            self.set_mentioned_user_ids(mentioned)


class VersionHistory(Base):
    """Version history for content items."""
    __tablename__ = "version_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # Clerk user ID
    
    # Version details
    version_number: Mapped[int] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # created, updated, published, etc.
    diff_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON diff of changes
    
    # Metadata
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_auto_save: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_version_history_content_id", "content_id"),
        Index("ix_version_history_org_id", "org_id"),
        Index("ix_version_history_user_id", "user_id"),
        Index("ix_version_history_version_number", "version_number"),
        Index("ix_version_history_created_at", "created_at"),
        UniqueConstraint("content_id", "version_number", name="uq_version_history_content_version"),
    )

    def get_diff(self) -> Dict[str, Any]:
        """Get diff as a dictionary."""
        try:
            return json.loads(self.diff_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_diff(self, diff: Dict[str, Any]) -> None:
        """Set diff from a dictionary."""
        self.diff_json = json.dumps(diff)


class CollaborationSession(Base):
    """Active collaboration sessions for real-time editing."""
    __tablename__ = "collaboration_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # Clerk user ID
    
    # Session details
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    cursor_position: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON cursor info
    last_activity: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_collaboration_sessions_content_id", "content_id"),
        Index("ix_collaboration_sessions_org_id", "org_id"),
        Index("ix_collaboration_sessions_user_id", "user_id"),
        Index("ix_collaboration_sessions_last_activity", "last_activity"),
        UniqueConstraint("content_id", "user_id", name="uq_collaboration_sessions_content_user"),
    )

    def get_cursor_position(self) -> Dict[str, Any]:
        """Get cursor position as a dictionary."""
        if not self.cursor_position:
            return {}
        try:
            return json.loads(self.cursor_position)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_cursor_position(self, position: Dict[str, Any]) -> None:
        """Set cursor position from a dictionary."""
        self.cursor_position = json.dumps(position)

    def is_active(self, timeout_minutes: int = 5) -> bool:
        """Check if session is still active."""
        timeout = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        return self.last_activity > timeout


class ContentLock(Base):
    """Content locking for preventing conflicts during editing."""
    __tablename__ = "content_locks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, unique=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # Clerk user ID
    
    # Lock details
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    lock_type: Mapped[str] = mapped_column(String(50), nullable=False)  # edit, review, approve, etc.
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_content_locks_content_id", "content_id"),
        Index("ix_content_locks_org_id", "org_id"),
        Index("ix_content_locks_user_id", "user_id"),
        Index("ix_content_locks_expires_at", "expires_at"),
    )

    def is_expired(self) -> bool:
        """Check if lock has expired."""
        return datetime.utcnow() > self.expires_at

    def extend_lock(self, minutes: int = 30) -> None:
        """Extend lock expiration time."""
        self.expires_at = datetime.utcnow() + timedelta(minutes=minutes)


class Notification(Base):
    """Notifications for collaboration events."""
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # Clerk user ID
    
    # Notification details
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # comment, mention, version, etc.
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Related entities
    content_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    comment_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    # Status
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_notifications_org_id", "org_id"),
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_content_id", "content_id"),
        Index("ix_notifications_type", "type"),
        Index("ix_notifications_is_read", "is_read"),
        Index("ix_notifications_created_at", "created_at"),
    )


# Collaboration actions
class CollaborationActions:
    """Available collaboration actions."""
    
    COMMENT_CREATED = "comment_created"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_RESOLVED = "comment_resolved"
    MENTION = "mention"
    VERSION_CREATED = "version_created"
    CONTENT_LOCKED = "content_locked"
    CONTENT_UNLOCKED = "content_unlocked"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    
    ALL_ACTIONS = [
        COMMENT_CREATED, COMMENT_UPDATED, COMMENT_RESOLVED,
        MENTION, VERSION_CREATED, CONTENT_LOCKED, CONTENT_UNLOCKED,
        USER_JOINED, USER_LEFT
    ]


# Lock types
class LockTypes:
    """Available lock types."""
    
    EDIT = "edit"
    REVIEW = "review"
    APPROVE = "approve"
    PUBLISH = "publish"
    
    ALL_TYPES = [EDIT, REVIEW, APPROVE, PUBLISH]


# Notification types
class NotificationTypes:
    """Available notification types."""
    
    COMMENT = "comment"
    MENTION = "mention"
    VERSION = "version"
    LOCK = "lock"
    COLLABORATION = "collaboration"
    
    ALL_TYPES = [COMMENT, MENTION, VERSION, LOCK, COLLABORATION]
