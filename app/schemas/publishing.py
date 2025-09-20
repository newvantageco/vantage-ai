"""
Publishing Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    GOOGLE_GBP = "google_gbp"
    TIKTOK_ADS = "tiktok_ads"
    GOOGLE_ADS = "google_ads"
    WHATSAPP = "whatsapp"


class PublishingStatus(str, Enum):
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Publish Preview Schemas
class PublishPreviewRequest(BaseModel):
    content_id: int = Field(..., description="Content item ID")
    platform: str = Field(..., description="Target platform")


class PublishPreviewResponse(BaseModel):
    content_id: int
    platform: str
    sanitized_content: str
    is_valid: bool
    validation_errors: List[str]
    warnings: List[str]
    constraints_applied: Dict[str, Any]
    character_count: int
    hashtag_count: int


# Publish Send Schemas
class PublishSendRequest(BaseModel):
    content_id: int = Field(..., description="Content item ID")
    platforms: List[str] = Field(..., description="Platforms to publish to")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled publish time")


class PublishSendResponse(BaseModel):
    job_id: str
    content_id: int
    platforms: List[str]
    status: str
    status_url: str


# Publishing Job Schemas
class PublishingJobResponse(BaseModel):
    id: int
    organization_id: int
    content_item_id: int
    job_id: str
    platforms: List[str]
    status: PublishingStatus
    total_platforms: int
    completed_platforms: int
    failed_platforms: int
    results: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# External Reference Schemas
class ExternalReferenceResponse(BaseModel):
    id: int
    organization_id: int
    content_item_id: Optional[int]
    schedule_id: Optional[int]
    platform: PlatformType
    external_id: str
    external_url: Optional[str]
    status: PublishingStatus
    error_message: Optional[str]
    platform_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


# Platform Integration Schemas
class PlatformIntegrationResponse(BaseModel):
    id: int
    organization_id: int
    platform: PlatformType
    account_id: Optional[str]
    account_name: Optional[str]
    is_active: bool
    is_connected: bool
    last_sync_at: Optional[datetime]
    error_message: Optional[str]
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PlatformIntegrationCreate(BaseModel):
    platform: PlatformType
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class PlatformIntegrationUpdate(BaseModel):
    account_name: Optional[str] = None
    is_active: Optional[bool] = None
    credentials: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


# Publishing Preview Schemas
class PublishingPreviewResponse(BaseModel):
    id: int
    organization_id: int
    content_item_id: Optional[int]
    platform: PlatformType
    original_content: str
    sanitized_content: Optional[str]
    is_valid: bool
    validation_errors: Optional[List[str]]
    warnings: Optional[List[str]]
    constraints_applied: Optional[Dict[str, Any]]
    character_count: Optional[int]
    hashtag_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Platform Status Schemas
class PlatformStatusResponse(BaseModel):
    platform: str
    account_name: Optional[str]
    is_connected: bool
    is_active: bool
    last_sync_at: Optional[datetime]
    error_message: Optional[str]


# Publishing Statistics Schemas
class PublishingStatsResponse(BaseModel):
    total_posts: int
    published_posts: int
    failed_posts: int
    pending_posts: int
    platforms_breakdown: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


# Bulk Publishing Schemas
class BulkPublishRequest(BaseModel):
    content_ids: List[int] = Field(..., description="Content item IDs to publish")
    platforms: List[str] = Field(..., description="Platforms to publish to")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled publish time")


class BulkPublishResponse(BaseModel):
    job_ids: List[str]
    total_content: int
    total_platforms: int
    status: str
    status_url: str
