"""
WhatsApp Business Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    TEMPLATE = "template"


class MessageStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class TemplateCategory(str, Enum):
    AUTHENTICATION = "AUTHENTICATION"
    MARKETING = "MARKETING"
    UTILITY = "UTILITY"


class TemplateStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISABLED = "disabled"


# WhatsApp Message Schemas
class WhatsAppMessageCreate(BaseModel):
    to_phone_number: str = Field(..., description="Recipient's phone number")
    message_type: MessageType = Field(..., description="Type of message")
    text_content: Optional[str] = Field(None, description="Text content for text messages")
    media_url: Optional[str] = Field(None, description="Media URL for media messages")
    media_caption: Optional[str] = Field(None, description="Caption for media messages")
    template_name: Optional[str] = Field(None, description="Template name for template messages")
    template_params: Optional[Dict[str, Any]] = Field(None, description="Template parameters")


class WhatsAppMessageResponse(BaseModel):
    id: int
    organization_id: int
    user_id: Optional[int]
    message_type: MessageType
    to_phone_number: str
    from_phone_number: Optional[str]
    text_content: Optional[str]
    media_url: Optional[str]
    media_caption: Optional[str]
    template_name: Optional[str]
    template_params: Optional[Dict[str, Any]]
    whatsapp_message_id: Optional[str]
    whatsapp_business_account_id: Optional[str]
    status: MessageStatus
    error_message: Optional[str]
    error_code: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


# WhatsApp Template Schemas
class WhatsAppTemplateCreate(BaseModel):
    name: str = Field(..., description="Template name")
    category: TemplateCategory = Field(..., description="Template category")
    language: str = Field(..., description="Template language code")
    header: Optional[Dict[str, Any]] = Field(None, description="Template header")
    body: Dict[str, Any] = Field(..., description="Template body")
    footer: Optional[Dict[str, Any]] = Field(None, description="Template footer")
    buttons: Optional[Dict[str, Any]] = Field(None, description="Template buttons")


class WhatsAppTemplateResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    category: TemplateCategory
    language: str
    header: Optional[Dict[str, Any]]
    body: Dict[str, Any]
    footer: Optional[Dict[str, Any]]
    buttons: Optional[Dict[str, Any]]
    whatsapp_template_id: Optional[str]
    status: TemplateStatus
    usage_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


# WhatsApp Webhook Event Schemas
class WhatsAppWebhookEventResponse(BaseModel):
    id: int
    organization_id: int
    event_type: str
    whatsapp_event_id: Optional[str]
    payload: Dict[str, Any]
    headers: Optional[Dict[str, Any]]
    processed: bool
    processed_at: Optional[datetime]
    error_message: Optional[str]
    received_at: datetime

    class Config:
        from_attributes = True


# WhatsApp Contact Schemas
class WhatsAppContactResponse(BaseModel):
    id: int
    organization_id: int
    phone_number: str
    whatsapp_id: Optional[str]
    name: Optional[str]
    profile_picture_url: Optional[str]
    is_blocked: bool
    is_opted_in: bool
    opt_in_date: Optional[datetime]
    opt_out_date: Optional[datetime]
    total_messages_sent: int
    total_messages_received: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# WhatsApp Business Account Schemas
class WhatsAppBusinessAccountCreate(BaseModel):
    whatsapp_business_account_id: str = Field(..., description="WhatsApp Business Account ID")
    business_name: Optional[str] = Field(None, description="Business name")
    phone_number_id: Optional[str] = Field(None, description="Phone number ID")
    phone_number: Optional[str] = Field(None, description="Phone number")
    access_token: Optional[str] = Field(None, description="Access token")
    verify_token: Optional[str] = Field(None, description="Verify token")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")


class WhatsAppBusinessAccountResponse(BaseModel):
    id: int
    organization_id: int
    whatsapp_business_account_id: str
    business_name: Optional[str]
    phone_number_id: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    is_verified: bool
    last_sync_at: Optional[datetime]
    webhook_url: Optional[str]
    webhook_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# WhatsApp Analytics Schemas
class WhatsAppAnalyticsResponse(BaseModel):
    total_messages_sent: int
    total_messages_received: int
    delivery_rate: float
    read_rate: float
    response_rate: float
    active_contacts: int
    blocked_contacts: int
    opted_out_contacts: int
    top_templates: List[Dict[str, Any]]
    message_volume_by_day: List[Dict[str, Any]]
    response_time_avg: float


# WhatsApp Campaign Schemas
class WhatsAppCampaignCreate(BaseModel):
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    template_name: str = Field(..., description="Template to use")
    target_contacts: List[str] = Field(..., description="Target phone numbers")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")
    template_params: Optional[Dict[str, Any]] = Field(None, description="Template parameters")


class WhatsAppCampaignResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    description: Optional[str]
    template_name: str
    target_contacts: List[str]
    scheduled_at: Optional[datetime]
    template_params: Optional[Dict[str, Any]]
    status: str
    total_contacts: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# WhatsApp Broadcast Schemas
class WhatsAppBroadcastCreate(BaseModel):
    name: str = Field(..., description="Broadcast name")
    message_type: MessageType = Field(..., description="Message type")
    text_content: Optional[str] = Field(None, description="Text content")
    media_url: Optional[str] = Field(None, description="Media URL")
    media_caption: Optional[str] = Field(None, description="Media caption")
    target_contacts: List[str] = Field(..., description="Target phone numbers")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")


class WhatsAppBroadcastResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    message_type: MessageType
    text_content: Optional[str]
    media_url: Optional[str]
    media_caption: Optional[str]
    target_contacts: List[str]
    scheduled_at: Optional[datetime]
    status: str
    total_contacts: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# WhatsApp Media Schemas
class WhatsAppMediaUploadResponse(BaseModel):
    media_id: str
    media_url: str
    file_size: int
    mime_type: str
    sha256: str
    created_at: datetime


class WhatsAppMediaDownloadResponse(BaseModel):
    media_url: str
    file_size: int
    mime_type: str
    sha256: str
    expires_at: datetime


# WhatsApp Webhook Verification Schemas
class WhatsAppWebhookVerificationRequest(BaseModel):
    hub_mode: str
    hub_verify_token: str
    hub_challenge: str


class WhatsAppWebhookVerificationResponse(BaseModel):
    challenge: str
    verified: bool


# WhatsApp Error Schemas
class WhatsAppErrorResponse(BaseModel):
    error: str
    error_description: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# WhatsApp Rate Limit Schemas
class WhatsAppRateLimitResponse(BaseModel):
    limit: int
    remaining: int
    reset_time: datetime
    window_size: int


# WhatsApp Business Profile Schemas
class WhatsAppBusinessProfileResponse(BaseModel):
    business_name: str
    business_description: str
    business_email: Optional[str]
    business_website: Optional[str]
    business_address: Optional[str]
    business_hours: Optional[Dict[str, Any]]
    profile_picture_url: Optional[str]
    cover_photo_url: Optional[str]


# WhatsApp Message Template Components
class WhatsAppTemplateComponent(BaseModel):
    type: str
    text: Optional[str] = None
    format: Optional[str] = None
    example: Optional[Dict[str, Any]] = None


class WhatsAppTemplateStructure(BaseModel):
    header: Optional[List[WhatsAppTemplateComponent]] = None
    body: List[WhatsAppTemplateComponent]
    footer: Optional[List[WhatsAppTemplateComponent]] = None
    buttons: Optional[List[WhatsAppTemplateComponent]] = None
