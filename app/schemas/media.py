"""
Media Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class MediaProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class MediaItem(BaseModel):
    """Media item model"""
    id: str
    organization_id: int
    user_id: int
    content_id: Optional[int] = None
    
    # File details
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_hash: str
    
    # Media properties
    media_type: MediaType
    status: MediaProcessingStatus
    
    # Processing metadata
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None


class MediaUploadResponse(BaseModel):
    """Response for media upload"""
    success: bool
    media_id: Optional[str] = None
    filename: Optional[str] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    media_type: Optional[MediaType] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    processing_status: Optional[MediaProcessingStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MediaListResponse(BaseModel):
    """Response for media list"""
    items: List[MediaItem]
    total: int
    page: int
    size: int
    total_pages: int


class MediaSearchRequest(BaseModel):
    """Request for media search"""
    query: Optional[str] = None
    media_type: Optional[MediaType] = None
    content_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class MediaBulkDeleteRequest(BaseModel):
    """Request for bulk media deletion"""
    media_ids: List[str] = Field(..., min_items=1, max_items=100)


class MediaBulkDeleteResponse(BaseModel):
    """Response for bulk media deletion"""
    deleted_count: int
    failed_count: int
    failed_ids: List[str] = Field(default_factory=list)


class MediaUpdateRequest(BaseModel):
    """Request for updating media metadata"""
    content_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
