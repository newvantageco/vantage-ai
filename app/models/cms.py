"""
CMS Models
Handles content management, campaigns, brand guides, and scheduling
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    locale = Column(String(10), default="en-US")
    
    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    subscription_status = Column(String(50), default="trial")
    plan = Column(String(50), default="starter")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("UserAccount", back_populates="organization")
    campaigns = relationship("Campaign", back_populates="organization")
    content_items = relationship("ContentItem", back_populates="organization")
    brand_guides = relationship("BrandGuide", back_populates="organization")
    schedules = relationship("Schedule", back_populates="organization")
    media_items = relationship("MediaItem", back_populates="organization")
    ai_requests = relationship("AIRequest", back_populates="organization")
    ai_batch_jobs = relationship("AIBatchJob", back_populates="organization")
    ai_optimizations = relationship("AIOptimization", back_populates="organization")


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Clerk integration
    clerk_user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Role-based access
    role = Column(String(20), default="editor")  # owner, admin, editor, analyst
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC")
    
    # Status
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    campaigns = relationship("Campaign", back_populates="created_by")
    content_items = relationship("ContentItem", back_populates="created_by")
    media_items = relationship("MediaItem", back_populates="user")
    ai_requests = relationship("AIRequest", back_populates="user")
    ai_batch_jobs = relationship("AIBatchJob", back_populates="user")
    ai_optimizations = relationship("AIOptimization", back_populates="user")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Campaign details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Schedule
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Settings
    target_audience = Column(JSON, nullable=True)
    goals = Column(JSON, nullable=True)
    budget = Column(Integer, nullable=True)  # In cents
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="campaigns")
    created_by = relationship("UserAccount", back_populates="campaigns")
    content_items = relationship("ContentItem", back_populates="campaign")


class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    brand_guide_id = Column(Integer, ForeignKey("brand_guides.id"), nullable=True)
    
    # Content details
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, image, video, carousel
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    
    # Media
    media_urls = Column(JSON, nullable=True)  # Array of media URLs
    hashtags = Column(JSON, nullable=True)  # Array of hashtags
    mentions = Column(JSON, nullable=True)  # Array of mentions
    
    # Platform-specific content
    platform_content = Column(JSON, nullable=True)  # Platform-specific variations
    
    # Metadata
    tags = Column(JSON, nullable=True)  # Array of tags
    content_metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="content_items")
    created_by = relationship("UserAccount", back_populates="content_items")
    campaign = relationship("Campaign", back_populates="content_items")
    brand_guide = relationship("BrandGuide", back_populates="content_items")
    schedules = relationship("Schedule", back_populates="content_item")
    media_items = relationship("MediaItem", back_populates="content_item")


class BrandGuide(Base):
    __tablename__ = "brand_guides"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Brand details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Brand guidelines
    tone_of_voice = Column(Text, nullable=True)
    writing_style = Column(Text, nullable=True)
    do_and_donts = Column(JSON, nullable=True)
    
    # Visual guidelines
    color_palette = Column(JSON, nullable=True)
    font_guidelines = Column(JSON, nullable=True)
    logo_usage = Column(Text, nullable=True)
    
    # Content guidelines
    hashtag_guidelines = Column(Text, nullable=True)
    mention_guidelines = Column(Text, nullable=True)
    platform_specific = Column(JSON, nullable=True)
    
    # AI prompts
    ai_prompts = Column(JSON, nullable=True)  # Custom AI prompts for this brand
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="brand_guides")
    content_items = relationship("ContentItem", back_populates="brand_guide")
    ai_requests = relationship("AIRequest", back_populates="brand_guide")
    ai_batch_jobs = relationship("AIBatchJob", back_populates="brand_guide")
    ai_optimizations = relationship("AIOptimization", back_populates="brand_guide")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    
    # Schedule details
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    platforms = Column(JSON, nullable=False)  # Array of platforms to publish to
    
    # Status
    status = Column(String(20), default="scheduled")  # scheduled, published, failed, cancelled
    error_message = Column(Text, nullable=True)
    
    # Publishing results
    external_references = Column(JSON, nullable=True)  # Platform-specific post IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="schedules")
    content_item = relationship("ContentItem", back_populates="schedules")
