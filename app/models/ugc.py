from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UGCStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"


class UGCRequestStatus(str, Enum):
    sent = "sent"
    responded = "responded"
    failed = "failed"
    expired = "expired"


class UGCChannel(str, Enum):
    instagram_dm = "instagram_dm"
    facebook_dm = "facebook_dm"
    linkedin_dm = "linkedin_dm"
    email = "email"
    whatsapp = "whatsapp"


class UGCAsset(Base):
    """User Generated Content assets (photos, reels, testimonials)."""
    __tablename__ = "ugc_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Asset details
    source_url: Mapped[str] = mapped_column(Text, nullable=False)  # Original platform URL
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)  # photo, video, testimonial
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # instagram, facebook, tiktok, etc.
    platform_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Platform post ID
    
    # Rights and consent
    status: Mapped[UGCStatus] = mapped_column(SAEnum(UGCStatus), default=UGCStatus.pending, nullable=False)
    rights_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, granted, denied, expired
    rights_proof_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Screenshot of consent
    
    # Content metadata
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hashtags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_profile_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Media URLs
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_width: Mapped[Optional[int]] = mapped_column(nullable=True)
    media_height: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    rights_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_ugc_assets_org_id", "org_id"),
        Index("ix_ugc_assets_status", "status"),
        Index("ix_ugc_assets_rights_status", "rights_status"),
        Index("ix_ugc_assets_platform", "platform"),
        Index("ix_ugc_assets_created_at", "created_at"),
        Index("ix_ugc_assets_platform_id", "platform_id"),
    )


class UGCRequest(Base):
    """Consent requests sent to content creators."""
    __tablename__ = "ugc_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("ugc_assets.id", ondelete="CASCADE"), index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Request details
    message: Mapped[str] = mapped_column(Text, nullable=False)  # Custom message to creator
    channel: Mapped[UGCChannel] = mapped_column(SAEnum(UGCChannel), nullable=False)
    status: Mapped[UGCRequestStatus] = mapped_column(SAEnum(UGCRequestStatus), default=UGCRequestStatus.sent, nullable=False)
    
    # Platform-specific identifiers
    platform_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # DM/email ID
    platform_thread_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Conversation thread
    
    # Response tracking
    response_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Creator's response
    response_choice: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # YES, NO, MAYBE
    
    # Timestamps
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ugc_requests_asset_id", "asset_id"),
        Index("ix_ugc_requests_org_id", "org_id"),
        Index("ix_ugc_requests_status", "status"),
        Index("ix_ugc_requests_channel", "channel"),
        Index("ix_ugc_requests_sent_at", "sent_at"),
        Index("ix_ugc_requests_platform_message_id", "platform_message_id"),
    )


class UGCUsage(Base):
    """Track usage of approved UGC assets in campaigns."""
    __tablename__ = "ugc_usage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("ugc_assets.id", ondelete="CASCADE"), index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Usage details
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # If part of campaign
    schedule_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # If scheduled post
    usage_type: Mapped[str] = mapped_column(String(50), nullable=False)  # organic_post, ad_creative, story, etc.
    
    # Platform where it was used
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_post_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    platform_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Performance metrics (if available)
    impressions: Mapped[Optional[int]] = mapped_column(nullable=True)
    engagement: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Timestamps
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ugc_usage_asset_id", "asset_id"),
        Index("ix_ugc_usage_org_id", "org_id"),
        Index("ix_ugc_usage_campaign_id", "campaign_id"),
        Index("ix_ugc_usage_schedule_id", "schedule_id"),
        Index("ix_ugc_usage_platform", "platform"),
        Index("ix_ugc_usage_used_at", "used_at"),
    )
