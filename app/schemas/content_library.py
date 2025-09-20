"""
Content Library Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ContentLibraryFilter(BaseModel):
    """Filter for content library search"""
    field: str = Field(..., description="Field to filter on")
    value: Any = Field(..., description="Filter value")
    operator: str = Field("eq", description="Filter operator: eq, ne, gt, gte, lt, lte, in, contains")


class ContentLibrarySort(BaseModel):
    """Sorting for content library search"""
    field: str = Field(..., description="Field to sort by")
    direction: str = Field("desc", description="Sort direction: asc, desc")


class ContentLibrarySearchRequest(BaseModel):
    """Request for content library search"""
    query: Optional[str] = Field(None, description="Search query")
    filters: List[ContentLibraryFilter] = Field(default_factory=list)
    sort: Optional[ContentLibrarySort] = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")


class ContentLibraryItem(BaseModel):
    """Content item in library"""
    id: int
    title: str
    content: str
    content_type: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    created_by: str
    campaign_name: Optional[str]
    brand_guide_name: Optional[str]
    tags: List[str]
    media_count: int
    hashtags: List[str]
    mentions: List[str]


class ContentLibrarySearchResponse(BaseModel):
    """Response for content library search"""
    items: List[ContentLibraryItem]
    total: int
    page: int
    size: int
    total_pages: int
    filters_applied: int
    search_query: Optional[str]


class ContentLibraryStats(BaseModel):
    """Content library statistics"""
    total_content: int
    status_breakdown: Dict[str, int]
    type_breakdown: Dict[str, int]
    recent_content: int
    recent_published: int
    top_creators: List[Dict[str, Any]]


class ContentLibraryCollection(BaseModel):
    """Content collection"""
    id: int
    name: str
    description: Optional[str]
    content_count: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    content_ids: List[int]


class ContentLibraryCollectionCreate(BaseModel):
    """Request to create a content collection"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    content_ids: List[int] = Field(default_factory=list)


class ContentLibraryCollectionUpdate(BaseModel):
    """Request to update a content collection"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    content_ids: Optional[List[int]] = None


class ContentLibraryCollectionResponse(BaseModel):
    """Response for content collection operations"""
    success: bool
    collection: Optional[ContentLibraryCollection] = None
    error: Optional[str] = None


class ContentLibraryExportRequest(BaseModel):
    """Request to export content library"""
    content_ids: Optional[List[int]] = None
    collection_id: Optional[int] = None
    export_format: str = Field("json", description="Export format: json, csv, xlsx")
    include_media: bool = Field(False, description="Include media files")
    include_metadata: bool = Field(True, description="Include metadata")


class ContentLibraryExportResponse(BaseModel):
    """Response for content library export"""
    export_id: str
    download_url: str
    file_size: int
    expires_at: datetime


class ContentLibraryImportRequest(BaseModel):
    """Request to import content library"""
    file_url: str = Field(..., description="URL of the import file")
    import_format: str = Field("json", description="Import format: json, csv, xlsx")
    collection_id: Optional[int] = Field(None, description="Add to specific collection")
    duplicate_handling: str = Field("skip", description="How to handle duplicates: skip, update, or create")


class ContentLibraryImportResponse(BaseModel):
    """Response for content library import"""
    import_id: str
    status: str
    total_items: int
    imported_count: int
    skipped_count: int
    failed_count: int
    failed_items: List[Dict[str, Any]] = Field(default_factory=list)
    new_content_ids: List[int] = Field(default_factory=list)


class ContentLibraryTagRequest(BaseModel):
    """Request to tag content items"""
    content_ids: List[int] = Field(..., min_items=1)
    tags: List[str] = Field(..., min_items=1)
    action: str = Field("add", description="Action: add, remove, or replace")


class ContentLibraryTagResponse(BaseModel):
    """Response for content tagging"""
    success: bool
    updated_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)


class ContentLibraryArchiveRequest(BaseModel):
    """Request to archive content items"""
    content_ids: List[int] = Field(..., min_items=1)
    archive_reason: Optional[str] = Field(None, max_length=500)


class ContentLibraryArchiveResponse(BaseModel):
    """Response for content archiving"""
    success: bool
    archived_count: int
    failed_count: int
    failed_ids: List[int] = Field(default_factory=list)
