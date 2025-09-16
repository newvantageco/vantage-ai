from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import ipaddress

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Integer, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IPAllowlist(Base):
    """IP allowlist for organizations."""
    __tablename__ = "ip_allowlists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Allowlist details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cidrs: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of CIDR blocks
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_ip_allowlists_org_id", "org_id"),
        Index("ix_ip_allowlists_is_active", "is_active"),
    )

    def get_cidrs(self) -> List[str]:
        """Get CIDR blocks as a list."""
        try:
            return json.loads(self.cidrs)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_cidrs(self, cidrs: List[str]) -> None:
        """Set CIDR blocks from a list."""
        self.cidrs = json.dumps(cidrs)

    def add_cidr(self, cidr: str) -> None:
        """Add a CIDR block."""
        cidrs = self.get_cidrs()
        if cidr not in cidrs:
            cidrs.append(cidr)
            self.set_cidrs(cidrs)

    def remove_cidr(self, cidr: str) -> None:
        """Remove a CIDR block."""
        cidrs = self.get_cidrs()
        if cidr in cidrs:
            cidrs.remove(cidr)
            self.set_cidrs(cidrs)

    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if an IP address is allowed."""
        try:
            ip = ipaddress.ip_address(ip_address)
            for cidr_str in self.get_cidrs():
                try:
                    network = ipaddress.ip_network(cidr_str, strict=False)
                    if ip in network:
                        return True
                except ValueError:
                    continue
            return False
        except ValueError:
            return False


class RateLimit(Base):
    """Rate limiting configuration for organizations."""
    __tablename__ = "rate_limits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Rate limit details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Rate limiting rules
    requests_per_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    requests_per_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    requests_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Scope
    scope: Mapped[str] = mapped_column(String(50), nullable=False)  # user, org, ip, endpoint
    scope_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # specific value for scope
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_rate_limits_org_id", "org_id"),
        Index("ix_rate_limits_scope", "scope"),
        Index("ix_rate_limits_is_active", "is_active"),
    )


class RateLimitUsage(Base):
    """Track rate limit usage."""
    __tablename__ = "rate_limit_usage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    rate_limit_id: Mapped[str] = mapped_column(ForeignKey("rate_limits.id", ondelete="CASCADE"), index=True)
    
    # Usage tracking
    scope_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # user_id, ip, etc.
    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    window_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Counters
    requests_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_rate_limit_usage_org_id", "org_id"),
        Index("ix_rate_limit_usage_rate_limit_id", "rate_limit_id"),
        Index("ix_rate_limit_usage_scope_key", "scope_key"),
        Index("ix_rate_limit_usage_window_start", "window_start"),
        Index("ix_rate_limit_usage_window_end", "window_end"),
        UniqueConstraint("rate_limit_id", "scope_key", "window_start", name="uq_rate_limit_usage_limit_scope_window"),
    )

    def is_expired(self) -> bool:
        """Check if this usage window has expired."""
        return datetime.utcnow() > self.window_end

    def get_remaining_requests(self, rate_limit: RateLimit) -> int:
        """Get remaining requests for this window."""
        if self.is_expired():
            return rate_limit.requests_per_minute  # Reset to full limit
        
        # Determine which limit to use based on window duration
        window_duration = self.window_end - self.window_start
        
        if window_duration <= timedelta(minutes=1):
            return max(0, rate_limit.requests_per_minute - self.requests_count)
        elif window_duration <= timedelta(hours=1):
            return max(0, rate_limit.requests_per_hour - self.requests_count)
        else:
            return max(0, rate_limit.requests_per_day - self.requests_count)


class RateLimitViolation(Base):
    """Track rate limit violations."""
    __tablename__ = "rate_limit_violations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    rate_limit_id: Mapped[str] = mapped_column(ForeignKey("rate_limits.id", ondelete="CASCADE"), index=True)
    
    # Violation details
    scope_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Violation data
    requests_count: Mapped[int] = mapped_column(Integer, nullable=False)
    limit_exceeded: Mapped[int] = mapped_column(Integer, nullable=False)
    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Response
    response_status: Mapped[int] = mapped_column(Integer, default=429, nullable=False)
    response_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_rate_limit_violations_org_id", "org_id"),
        Index("ix_rate_limit_violations_rate_limit_id", "rate_limit_id"),
        Index("ix_rate_limit_violations_scope_key", "scope_key"),
        Index("ix_rate_limit_violations_ip_address", "ip_address"),
        Index("ix_rate_limit_violations_created_at", "created_at"),
    )


# Rate limit scopes
class RateLimitScopes:
    """Available rate limit scopes."""
    
    USER = "user"
    ORG = "org"
    IP = "ip"
    ENDPOINT = "endpoint"
    GLOBAL = "global"
    
    ALL_SCOPES = [USER, ORG, IP, ENDPOINT, GLOBAL]
    
    @classmethod
    def validate_scope(cls, scope: str) -> bool:
        """Validate that a scope is valid."""
        return scope in cls.ALL_SCOPES


# Default rate limits
DEFAULT_RATE_LIMITS = {
    "free": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "requests_per_day": 10000
    },
    "pro": {
        "requests_per_minute": 300,
        "requests_per_hour": 10000,
        "requests_per_day": 100000
    },
    "enterprise": {
        "requests_per_minute": 1000,
        "requests_per_hour": 50000,
        "requests_per_day": 500000
    }
}
