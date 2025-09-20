"""
WhatsApp Business Models
Handles WhatsApp messaging, templates, and webhook events
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    TEMPLATE = "template"


class MessageStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    
    # Message details
    message_type = Column(Enum(MessageType), nullable=False)
    to_phone_number = Column(String(20), nullable=False)
    from_phone_number = Column(String(20), nullable=True)
    
    # Content
    text_content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    media_caption = Column(Text, nullable=True)
    template_name = Column(String(100), nullable=True)
    template_params = Column(JSON, nullable=True)
    
    # WhatsApp details
    whatsapp_message_id = Column(String(255), nullable=True, index=True)
    whatsapp_business_account_id = Column(String(255), nullable=True)
    
    # Status
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("UserAccount")


class WhatsAppTemplate(Base):
    __tablename__ = "whatsapp_templates"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Template details
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # AUTHENTICATION, MARKETING, UTILITY
    language = Column(String(10), nullable=False)
    
    # Template content
    header = Column(JSON, nullable=True)
    body = Column(JSON, nullable=False)
    footer = Column(JSON, nullable=True)
    buttons = Column(JSON, nullable=True)
    
    # WhatsApp details
    whatsapp_template_id = Column(String(255), nullable=True, index=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected, disabled
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")


class WhatsAppWebhookEvent(Base):
    __tablename__ = "whatsapp_webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # messages, message_status, etc.
    whatsapp_event_id = Column(String(255), nullable=True, index=True)
    
    # Event data
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)
    
    # Processing status
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")


class WhatsAppContact(Base):
    __tablename__ = "whatsapp_contacts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Contact details
    phone_number = Column(String(20), nullable=False, index=True)
    whatsapp_id = Column(String(255), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    
    # Contact status
    is_blocked = Column(Boolean, default=False)
    is_opted_in = Column(Boolean, default=True)
    opt_in_date = Column(DateTime(timezone=True), nullable=True)
    opt_out_date = Column(DateTime(timezone=True), nullable=True)
    
    # Message statistics
    total_messages_sent = Column(Integer, default=0)
    total_messages_received = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")


class WhatsAppBusinessAccount(Base):
    __tablename__ = "whatsapp_business_accounts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Account details
    whatsapp_business_account_id = Column(String(255), unique=True, nullable=False, index=True)
    business_name = Column(String(255), nullable=True)
    phone_number_id = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # Credentials
    access_token = Column(String(500), nullable=True)  # Encrypted
    verify_token = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # Webhook configuration
    webhook_url = Column(String(500), nullable=True)
    webhook_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
