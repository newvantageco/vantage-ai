"""
Publishing Models
Handles content publishing, external references, and platform integrations
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class PublishingStatus(str, enum.Enum):
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PlatformType(str, enum.Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    GOOGLE_GBP = "google_gbp"
    TIKTOK_ADS = "tiktok_ads"
    GOOGLE_ADS = "google_ads"
    WHATSAPP = "whatsapp"


class ExternalReference(Base):
    __tablename__ = "external_references"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    
    # Platform details
    platform = Column(Enum(PlatformType), nullable=False)
    external_id = Column(String(255), nullable=False)  # Platform-specific post ID
    external_url = Column(String(500), nullable=True)  # URL to the published post
    
    # Publishing details
    status = Column(Enum(PublishingStatus), default=PublishingStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Platform-specific data
    platform_data = Column(JSON, nullable=True)  # Additional platform-specific data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    content_item = relationship("ContentItem")
    schedule = relationship("Schedule")


class PublishingJob(Base):
    __tablename__ = "publishing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    
    # Job details
    job_id = Column(String(100), unique=True, nullable=False, index=True)
    platforms = Column(JSON, nullable=False)  # Array of platforms to publish to
    
    # Status
    status = Column(Enum(PublishingStatus), default=PublishingStatus.PENDING)
    total_platforms = Column(Integer, nullable=False)
    completed_platforms = Column(Integer, default=0)
    failed_platforms = Column(Integer, default=0)
    
    # Results
    results = Column(JSON, nullable=True)  # Publishing results per platform
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    content_item = relationship("ContentItem")


class PlatformIntegration(Base):
    __tablename__ = "platform_integrations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Platform details
    platform = Column(Enum(PlatformType), nullable=False)
    account_id = Column(String(255), nullable=True)  # Platform account ID
    account_name = Column(String(255), nullable=True)  # Human-readable account name
    
    # Credentials (encrypted)
    credentials = Column(JSON, nullable=True)  # Encrypted platform credentials
    
    # Status
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Platform-specific settings
    settings = Column(JSON, nullable=True)  # Platform-specific configuration
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")


class PublishingPreview(Base):
    __tablename__ = "publishing_previews"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=True)
    
    # Preview details
    platform = Column(Enum(PlatformType), nullable=False)
    original_content = Column(Text, nullable=False)
    sanitized_content = Column(Text, nullable=True)
    
    # Validation results
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    
    # Platform constraints applied
    constraints_applied = Column(JSON, nullable=True)
    character_count = Column(Integer, nullable=True)
    hashtag_count = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    content_item = relationship("ContentItem")
