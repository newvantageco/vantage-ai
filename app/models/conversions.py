from __future__ import annotations

from datetime import datetime
from typing import Optional
import secrets

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Conversion(Base):
    """Track conversions (form fills, purchases) and attribute them."""
    __tablename__ = "conversions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Attribution
    schedule_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)  # If from scheduled post
    ad_run_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)  # If from ad campaign
    
    # Conversion details
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # organic, paid, email, direct, etc.
    conversion_type: Mapped[str] = mapped_column(String(100), nullable=False)  # form_fill, purchase, signup, etc.
    value_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Conversion value in cents
    user_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # User identifier
    
    # Attribution data
    utm_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_term: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_content: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Additional metadata
    page_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    referrer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_conversions_org_id", "org_id"),
        Index("ix_conversions_schedule_id", "schedule_id"),
        Index("ix_conversions_ad_run_id", "ad_run_id"),
        Index("ix_conversions_user_ref", "user_ref"),
        Index("ix_conversions_source", "source"),
        Index("ix_conversions_conversion_type", "conversion_type"),
        Index("ix_conversions_created_at", "created_at"),
        Index("ix_conversions_utm_source", "utm_source"),
        Index("ix_conversions_utm_campaign", "utm_campaign"),
    )


class ConversionGoal(Base):
    """Define conversion goals for tracking."""
    __tablename__ = "conversion_goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Goal details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    conversion_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Tracking configuration
    tracking_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)  # Unique tracking code
    value_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Default value
    
    # Attribution settings
    attribution_window_days: Mapped[int] = mapped_column(default=30, nullable=False)  # How long to attribute conversions
    require_utm: Mapped[bool] = mapped_column(default=False, nullable=False)  # Require UTM parameters
    
    # Status
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_conversion_goals_org_id", "org_id"),
        Index("ix_conversion_goals_tracking_code", "tracking_code"),
        Index("ix_conversion_goals_conversion_type", "conversion_type"),
        Index("ix_conversion_goals_is_active", "is_active"),
    )

    @classmethod
    def generate_tracking_code(cls) -> str:
        """Generate a unique tracking code."""
        return f"conv_{secrets.token_urlsafe(8)}"


class ConversionAttribution(Base):
    """Track attribution between content and conversions."""
    __tablename__ = "conversion_attributions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversion_id: Mapped[str] = mapped_column(ForeignKey("conversions.id", ondelete="CASCADE"), index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Attribution details
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # schedule, ad, email, etc.
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    # Attribution metrics
    attribution_weight: Mapped[float] = mapped_column(default=1.0, nullable=False)  # Weight of this attribution
    time_to_conversion_hours: Mapped[Optional[int]] = mapped_column(nullable=True)  # Hours between content and conversion
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_conversion_attributions_conversion_id", "conversion_id"),
        Index("ix_conversion_attributions_org_id", "org_id"),
        Index("ix_conversion_attributions_content_id", "content_id"),
        Index("ix_conversion_attributions_content_type", "content_type"),
    )


# Conversion types
class ConversionTypes:
    """Available conversion types."""
    
    FORM_FILL = "form_fill"
    PURCHASE = "purchase"
    SIGNUP = "signup"
    DOWNLOAD = "download"
    CLICK = "click"
    VIEW = "view"
    CUSTOM = "custom"
    
    ALL_TYPES = [FORM_FILL, PURCHASE, SIGNUP, DOWNLOAD, CLICK, VIEW, CUSTOM]
    
    @classmethod
    def validate_type(cls, conversion_type: str) -> bool:
        """Validate that a conversion type is valid."""
        return conversion_type in cls.ALL_TYPES


# Conversion sources
class ConversionSources:
    """Available conversion sources."""
    
    ORGANIC = "organic"
    PAID = "paid"
    EMAIL = "email"
    DIRECT = "direct"
    REFERRAL = "referral"
    SOCIAL = "social"
    CUSTOM = "custom"
    
    ALL_SOURCES = [ORGANIC, PAID, EMAIL, DIRECT, REFERRAL, SOCIAL, CUSTOM]
    
    @classmethod
    def validate_source(cls, source: str) -> bool:
        """Validate that a conversion source is valid."""
        return source in cls.ALL_SOURCES
