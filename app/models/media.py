"""
Media Models
Handles media file storage and metadata
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class MediaProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class MediaItem(Base):
    """Media item model for database storage"""
    __tablename__ = "media_items"

    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=True, index=True)
    
    # File details
    original_filename = Column(String(500), nullable=False)
    stored_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash
    
    # Media properties
    media_type = Column(Enum(MediaType), nullable=False)
    status = Column(Enum(MediaProcessingStatus), default=MediaProcessingStatus.PENDING, nullable=False)
    
    # Processing metadata
    processing_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="media_items")
    user = relationship("UserAccount", back_populates="media_items")
    content_item = relationship("ContentItem", back_populates="media_items")


class MediaProcessingJob(Base):
    """Media processing job tracking"""
    __tablename__ = "media_processing_jobs"

    id = Column(String(36), primary_key=True, index=True)
    media_item_id = Column(String(36), ForeignKey("media_items.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Job details
    job_type = Column(String(50), nullable=False)  # thumbnail, optimization, conversion
    status = Column(Enum(MediaProcessingStatus), default=MediaProcessingStatus.PENDING, nullable=False)
    progress_percent = Column(Integer, default=0, nullable=False)
    
    # Processing parameters
    parameters = Column(JSON, nullable=True)
    
    # Results
    output_path = Column(String(1000), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    media_item = relationship("MediaItem")
    organization = relationship("Organization")
