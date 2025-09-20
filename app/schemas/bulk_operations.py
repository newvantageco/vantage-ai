"""
Bulk Operations Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class BulkOperationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BulkOperationResponse(BaseModel):
    """Base response for bulk operations"""
    operation_id: str
    status: BulkOperationStatus
    total_items: int
    processed_items: int
    successful_items: int
    failed_items: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# Content Update Schemas
class ContentUpdateData(BaseModel):
    """Data for updating content items"""
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    platform_content: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    campaign_id: Optional[int] = None
    brand_guide_id: Optional[int] = None


class BulkContentUpdateRequest(BaseModel):
    """Request for bulk content updates"""
    content_ids: List[int] = Field(..., min_items=1, max_items=100)
    update_data: ContentUpdateData


class BulkContentUpdateResponse(BaseModel):
    """Response for bulk content updates"""
    updated_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)


# Content Delete Schemas
class BulkContentDeleteRequest(BaseModel):
    """Request for bulk content deletion"""
    content_ids: List[int] = Field(..., min_items=1, max_items=100)
    force_delete: bool = Field(False, description="Force delete even if content is scheduled")


class BulkContentDeleteResponse(BaseModel):
    """Response for bulk content deletion"""
    deleted_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)


# Content Schedule Schemas
class BulkContentScheduleRequest(BaseModel):
    """Request for bulk content scheduling"""
    content_ids: List[int] = Field(..., min_items=1, max_items=100)
    scheduled_at: datetime
    platforms: List[str] = Field(..., min_items=1)


class BulkContentScheduleResponse(BaseModel):
    """Response for bulk content scheduling"""
    scheduled_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)
    schedule_ids: List[int] = Field(default_factory=list)


# Content Status Update Schemas
class BulkContentStatusUpdateRequest(BaseModel):
    """Request for bulk content status updates"""
    content_ids: List[int] = Field(..., min_items=1, max_items=100)
    status: str = Field(..., description="New status for content items")


class BulkContentStatusUpdateResponse(BaseModel):
    """Response for bulk content status updates"""
    updated_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)


# Content Duplicate Schemas
class BulkContentDuplicateRequest(BaseModel):
    """Request for bulk content duplication"""
    content_ids: List[int] = Field(..., min_items=1, max_items=100)
    duplicate_count: int = Field(1, ge=1, le=10, description="Number of duplicates per content item")
    campaign_id: Optional[int] = Field(None, description="Assign duplicates to specific campaign")


class BulkContentDuplicateResponse(BaseModel):
    """Response for bulk content duplication"""
    duplicated_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)
    new_content_ids: List[int] = Field(default_factory=list)


# Content Archive Schemas
class BulkContentArchiveRequest(BaseModel):
    """Request for bulk content archiving"""
    content_ids: List[int] = Field(..., min_items=1, max_items=100)
    archive_reason: Optional[str] = Field(None, description="Reason for archiving")


class BulkContentArchiveResponse(BaseModel):
    """Response for bulk content archiving"""
    archived_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)


# Content Tag Schemas
class BulkContentTagRequest(BaseModel):
    """Request for bulk content tagging"""
    content_ids: List[int] = Field(..., min_items=1, max_items=100)
    tags: List[str] = Field(..., min_items=1)
    action: str = Field(..., description="add, remove, or replace")


class BulkContentTagResponse(BaseModel):
    """Response for bulk content tagging"""
    updated_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)


# Content Export Schemas
class BulkContentExportRequest(BaseModel):
    """Request for bulk content export"""
    content_ids: List[int] = Field(..., min_items=1, max_items=1000)
    export_format: str = Field("json", description="Export format: json, csv, xlsx")
    include_media: bool = Field(False, description="Include media files in export")
    include_metadata: bool = Field(True, description="Include metadata in export")


class BulkContentExportResponse(BaseModel):
    """Response for bulk content export"""
    export_id: str
    download_url: str
    file_size: int
    expires_at: datetime


# Content Import Schemas
class BulkContentImportRequest(BaseModel):
    """Request for bulk content import"""
    file_url: str = Field(..., description="URL of the import file")
    import_format: str = Field("json", description="Import format: json, csv, xlsx")
    campaign_id: Optional[int] = Field(None, description="Assign imported content to campaign")
    brand_guide_id: Optional[int] = Field(None, description="Assign imported content to brand guide")
    duplicate_handling: str = Field("skip", description="How to handle duplicates: skip, update, or create")


class BulkContentImportResponse(BaseModel):
    """Response for bulk content import"""
    import_id: str
    status: BulkOperationStatus
    total_items: int
    imported_count: int
    skipped_count: int
    failed_count: int
    failed_items: List[Dict[str, Any]] = Field(default_factory=list)
    new_content_ids: List[int] = Field(default_factory=list)
