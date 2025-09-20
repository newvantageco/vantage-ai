"""
CMS Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ContentStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    ANALYST = "analyst"


# Organization Schemas
class OrganizationBase(BaseModel):
    name: str = Field(..., description="Organization name")
    description: Optional[str] = Field(None, description="Organization description")
    timezone: str = Field("UTC", description="Organization timezone")
    locale: str = Field("en-US", description="Organization locale")


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    id: int
    slug: str
    stripe_customer_id: Optional[str]
    subscription_status: str
    plan: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# User Account Schemas
class UserAccountBase(BaseModel):
    email: str = Field(..., description="User email")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    role: UserRole = Field(UserRole.EDITOR, description="User role")
    timezone: str = Field("UTC", description="User timezone")


class UserAccountCreate(UserAccountBase):
    clerk_user_id: str = Field(..., description="Clerk user ID")


class UserAccountUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class UserAccountResponse(UserAccountBase):
    id: int
    organization_id: int
    clerk_user_id: str
    avatar_url: Optional[str]
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Campaign Schemas
class CampaignBase(BaseModel):
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    start_date: Optional[datetime] = Field(None, description="Campaign start date")
    end_date: Optional[datetime] = Field(None, description="Campaign end date")
    target_audience: Optional[Dict[str, Any]] = Field(None, description="Target audience settings")
    goals: Optional[Dict[str, Any]] = Field(None, description="Campaign goals")
    budget: Optional[int] = Field(None, description="Campaign budget in cents")


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None
    goals: Optional[Dict[str, Any]] = None
    budget: Optional[int] = None


class CampaignResponse(CampaignBase):
    id: int
    organization_id: int
    created_by_id: int
    status: CampaignStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Content Item Schemas
class ContentItemBase(BaseModel):
    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Content text")
    content_type: str = Field("text", description="Content type")
    media_urls: Optional[List[str]] = Field(None, description="Media URLs")
    hashtags: Optional[List[str]] = Field(None, description="Hashtags")
    mentions: Optional[List[str]] = Field(None, description="Mentions")
    platform_content: Optional[Dict[str, Any]] = Field(None, description="Platform-specific content")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ContentItemCreate(ContentItemBase):
    campaign_id: Optional[int] = Field(None, description="Campaign ID")
    brand_guide_id: Optional[int] = Field(None, description="Brand guide ID")


class ContentItemUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[ContentStatus] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    platform_content: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    campaign_id: Optional[int] = None
    brand_guide_id: Optional[int] = None


class ContentItemResponse(ContentItemBase):
    id: int
    organization_id: int
    created_by_id: int
    campaign_id: Optional[int]
    brand_guide_id: Optional[int]
    status: ContentStatus
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


# Brand Guide Schemas
class BrandGuideBase(BaseModel):
    name: str = Field(..., description="Brand guide name")
    description: Optional[str] = Field(None, description="Brand guide description")
    tone_of_voice: Optional[str] = Field(None, description="Tone of voice guidelines")
    writing_style: Optional[str] = Field(None, description="Writing style guidelines")
    do_and_donts: Optional[Dict[str, Any]] = Field(None, description="Do's and don'ts")
    color_palette: Optional[Dict[str, Any]] = Field(None, description="Color palette")
    font_guidelines: Optional[Dict[str, Any]] = Field(None, description="Font guidelines")
    logo_usage: Optional[str] = Field(None, description="Logo usage guidelines")
    hashtag_guidelines: Optional[str] = Field(None, description="Hashtag guidelines")
    mention_guidelines: Optional[str] = Field(None, description="Mention guidelines")
    platform_specific: Optional[Dict[str, Any]] = Field(None, description="Platform-specific guidelines")
    ai_prompts: Optional[Dict[str, Any]] = Field(None, description="AI prompts for this brand")


class BrandGuideCreate(BrandGuideBase):
    pass


class BrandGuideUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tone_of_voice: Optional[str] = None
    writing_style: Optional[str] = None
    do_and_donts: Optional[Dict[str, Any]] = None
    color_palette: Optional[Dict[str, Any]] = None
    font_guidelines: Optional[Dict[str, Any]] = None
    logo_usage: Optional[str] = None
    hashtag_guidelines: Optional[str] = None
    mention_guidelines: Optional[str] = None
    platform_specific: Optional[Dict[str, Any]] = None
    ai_prompts: Optional[Dict[str, Any]] = None


class BrandGuideResponse(BrandGuideBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Schedule Schemas
class ScheduleBase(BaseModel):
    scheduled_at: datetime = Field(..., description="Scheduled publish time")
    platforms: List[str] = Field(..., description="Platforms to publish to")


class ScheduleCreate(ScheduleBase):
    content_item_id: int = Field(..., description="Content item ID")


class ScheduleUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    platforms: Optional[List[str]] = None
    status: Optional[str] = None


class ScheduleResponse(ScheduleBase):
    id: int
    organization_id: int
    content_item_id: int
    status: str
    error_message: Optional[str]
    external_references: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


# Calendar Schemas
class CalendarRequest(BaseModel):
    start_date: datetime = Field(..., description="Start date for calendar")
    end_date: datetime = Field(..., description="End date for calendar")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")


class CalendarItem(BaseModel):
    id: int
    title: str
    content: str
    scheduled_at: datetime
    platforms: List[str]
    status: str
    content_type: str
    created_by: str

    class Config:
        from_attributes = True


class CalendarResponse(BaseModel):
    items: List[CalendarItem]
    total: int
    page: int
    size: int
    total_pages: int
