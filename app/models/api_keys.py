from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List
import secrets
import hashlib

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class APIKey(Base):
    """API keys for agency/partner access."""
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)  # Clerk user ID who created the key
    
    # Key details
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)  # SHA-256 hash of the key
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Human-readable name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scopes and permissions
    scopes: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of scopes
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Rate limiting
    rate_limit_per_hour: Mapped[int] = mapped_column(default=1000, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_used_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 compatible

    __table_args__ = (
        Index("ix_api_keys_org_id", "org_id"),
        Index("ix_api_keys_user_id", "user_id"),
        Index("ix_api_keys_key_hash", "key_hash"),
        Index("ix_api_keys_is_active", "is_active"),
        Index("ix_api_keys_created_at", "created_at"),
    )

    @classmethod
    def generate_key(cls) -> str:
        """Generate a new API key."""
        return f"vai_{secrets.token_urlsafe(32)}"

    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    def verify_key(self, key: str) -> bool:
        """Verify if the provided key matches this API key."""
        return self.key_hash == self.hash_key(key)

    def is_expired(self) -> bool:
        """Check if the API key has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    def get_scopes(self) -> List[str]:
        """Get scopes as a list."""
        import json
        try:
            return json.loads(self.scopes)
        except (json.JSONDecodeError, TypeError):
            return []

    def has_scope(self, scope: str) -> bool:
        """Check if the API key has a specific scope."""
        return scope in self.get_scopes()

    def record_usage(self, ip_address: Optional[str] = None) -> None:
        """Record API key usage."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        if ip_address:
            self.last_used_ip = ip_address


class APIKeyUsage(Base):
    """Track API key usage for analytics and rate limiting."""
    __tablename__ = "api_key_usage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    api_key_id: Mapped[str] = mapped_column(ForeignKey("api_keys.id", ondelete="CASCADE"), index=True)
    
    # Request details
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(nullable=False)
    response_time_ms: Mapped[int] = mapped_column(nullable=False)
    
    # Request metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)
    response_size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_api_key_usage_api_key_id", "api_key_id"),
        Index("ix_api_key_usage_endpoint", "endpoint"),
        Index("ix_api_key_usage_status_code", "status_code"),
        Index("ix_api_key_usage_created_at", "created_at"),
    )


class APIRateLimit(Base):
    """Track rate limiting for API keys."""
    __tablename__ = "api_rate_limits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    api_key_id: Mapped[str] = mapped_column(ForeignKey("api_keys.id", ondelete="CASCADE"), index=True)
    
    # Rate limiting window
    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Usage counts
    request_count: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("api_key_id", "window_start", name="uq_api_rate_limits_key_window"),
        Index("ix_api_rate_limits_api_key_id", "api_key_id"),
        Index("ix_api_rate_limits_window_start", "window_start"),
        Index("ix_api_rate_limits_window_end", "window_end"),
    )

    @classmethod
    def get_current_window(cls) -> tuple[datetime, datetime]:
        """Get the current rate limiting window (1 hour)."""
        now = datetime.utcnow()
        window_start = now.replace(minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(hours=1)
        return window_start, window_end

    def is_expired(self) -> bool:
        """Check if this rate limit window has expired."""
        return datetime.utcnow() > self.window_end


# API Scopes
class APIScopes:
    """Available API scopes."""
    
    # Content management
    CONTENT_READ = "content:read"
    CONTENT_WRITE = "content:write"
    CONTENT_DELETE = "content:delete"
    
    # Scheduling
    SCHEDULE_READ = "schedule:read"
    SCHEDULE_WRITE = "schedule:write"
    SCHEDULE_DELETE = "schedule:delete"
    
    # Analytics
    ANALYTICS_READ = "analytics:read"
    METRICS_READ = "metrics:read"
    
    # Channels
    CHANNELS_READ = "channels:read"
    CHANNELS_WRITE = "channels:write"
    
    # Organizations
    ORG_READ = "org:read"
    ORG_WRITE = "org:write"
    
    # Users
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    
    # Billing
    BILLING_READ = "billing:read"
    
    # All scopes
    ALL_SCOPES = [
        CONTENT_READ, CONTENT_WRITE, CONTENT_DELETE,
        SCHEDULE_READ, SCHEDULE_WRITE, SCHEDULE_DELETE,
        ANALYTICS_READ, METRICS_READ,
        CHANNELS_READ, CHANNELS_WRITE,
        ORG_READ, ORG_WRITE,
        USERS_READ, USERS_WRITE,
        BILLING_READ,
    ]
    
    # Scope groups for easier management
    CONTENT_SCOPES = [CONTENT_READ, CONTENT_WRITE, CONTENT_DELETE]
    SCHEDULE_SCOPES = [SCHEDULE_READ, SCHEDULE_WRITE, SCHEDULE_DELETE]
    ANALYTICS_SCOPES = [ANALYTICS_READ, METRICS_READ]
    CHANNEL_SCOPES = [CHANNELS_READ, CHANNELS_WRITE]
    ORG_SCOPES = [ORG_READ, ORG_WRITE]
    USER_SCOPES = [USERS_READ, USERS_WRITE]
    BILLING_SCOPES = [BILLING_READ]
    
    @classmethod
    def validate_scopes(cls, scopes: List[str]) -> bool:
        """Validate that all scopes are valid."""
        return all(scope in cls.ALL_SCOPES for scope in scopes)
    
    @classmethod
    def get_scope_groups(cls) -> dict[str, List[str]]:
        """Get available scope groups."""
        return {
            "content": cls.CONTENT_SCOPES,
            "schedule": cls.SCHEDULE_SCOPES,
            "analytics": cls.ANALYTICS_SCOPES,
            "channels": cls.CHANNEL_SCOPES,
            "organization": cls.ORG_SCOPES,
            "users": cls.USER_SCOPES,
            "billing": cls.BILLING_SCOPES,
        }
