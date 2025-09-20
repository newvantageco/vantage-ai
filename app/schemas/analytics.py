"""
Analytics Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ExportType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class ExportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Analytics Summary Schemas
class AnalyticsSummaryResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_impressions: int
    total_reach: int
    total_clicks: int
    total_engagements: int
    total_conversions: int
    avg_ctr: float
    avg_engagement_rate: float
    avg_conversion_rate: float
    platform_breakdown: Dict[str, Dict[str, int]]


# Timeseries Schemas
class TimeseriesDataPoint(BaseModel):
    platform: str
    date: Optional[str]
    value: float


class TimeseriesResponse(BaseModel):
    metric: str
    group_by: str
    data: List[TimeseriesDataPoint]
    from_date: datetime
    to_date: datetime


# Post Metrics Schemas
class PostMetricsResponse(BaseModel):
    id: int
    organization_id: int
    external_reference_id: Optional[int]
    platform: str
    external_id: str
    impressions: int
    reach: int
    clicks: int
    ctr: float
    engagements: int
    likes: int
    comments: int
    shares: int
    saves: int
    conversions: int
    conversion_rate: float
    cost_per_click: float
    cost_per_conversion: float
    video_views: int
    video_completion_rate: float
    engagement_rate: float
    data_source: str
    is_estimated: bool
    metric_date: datetime
    collected_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Analytics Export Schemas
class AnalyticsExportCreate(BaseModel):
    export_type: ExportType = Field(..., description="Export format")
    date_range_start: datetime = Field(..., description="Start date for export")
    date_range_end: datetime = Field(..., description="End date for export")
    platforms: Optional[List[str]] = Field(None, description="Platforms to include")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to include")


class AnalyticsExportResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    export_type: ExportType
    date_range_start: datetime
    date_range_end: datetime
    platforms: Optional[List[str]]
    metrics: Optional[List[str]]
    status: ExportStatus
    file_url: Optional[str]
    file_size: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# Platform Breakdown Schemas
class PlatformBreakdownResponse(BaseModel):
    platform: str
    impressions: int
    reach: int
    clicks: int
    engagements: int
    conversions: int
    ctr: float
    engagement_rate: float
    conversion_rate: float


# Analytics Dashboard Schemas
class AnalyticsDashboardResponse(BaseModel):
    summary: AnalyticsSummaryResponse
    top_posts: List[PostMetricsResponse]
    platform_breakdown: List[PlatformBreakdownResponse]
    recent_activity: List[Dict[str, Any]]


# Metrics Collection Schemas
class MetricsCollectionRequest(BaseModel):
    platform: str = Field(..., description="Platform to collect metrics from")
    start_date: datetime = Field(..., description="Start date for collection")
    end_date: datetime = Field(..., description="End date for collection")
    force_refresh: bool = Field(False, description="Force refresh even if data exists")


class MetricsCollectionResponse(BaseModel):
    task_id: str
    platform: str
    start_date: datetime
    end_date: datetime
    status: str
    message: str


# Analytics Filters Schemas
class AnalyticsFilters(BaseModel):
    platforms: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    campaigns: Optional[List[int]] = None
    date_range: Optional[Dict[str, datetime]] = None
    metrics: Optional[List[str]] = None


# Performance Metrics Schemas
class PerformanceMetricsResponse(BaseModel):
    total_posts: int
    avg_impressions: float
    avg_engagement_rate: float
    best_performing_platform: str
    worst_performing_platform: str
    top_hashtags: List[Dict[str, Any]]
    engagement_trend: List[Dict[str, Any]]


# Real-time Analytics Schemas
class RealTimeMetricsResponse(BaseModel):
    current_impressions: int
    current_engagements: int
    current_clicks: int
    live_posts: int
    recent_activity: List[Dict[str, Any]]
    last_updated: datetime


# Analytics Comparison Schemas
class AnalyticsComparisonRequest(BaseModel):
    period1_start: datetime
    period1_end: datetime
    period2_start: datetime
    period2_end: datetime
    platforms: Optional[List[str]] = None
    metrics: Optional[List[str]] = None


class AnalyticsComparisonResponse(BaseModel):
    period1: AnalyticsSummaryResponse
    period2: AnalyticsSummaryResponse
    changes: Dict[str, float]  # Percentage changes
    insights: List[str]  # AI-generated insights


# Custom Report Schemas
class CustomReportRequest(BaseModel):
    name: str
    description: Optional[str] = None
    filters: AnalyticsFilters
    metrics: List[str]
    group_by: List[str]
    schedule: Optional[Dict[str, Any]] = None  # For scheduled reports


class CustomReportResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    filters: AnalyticsFilters
    metrics: List[str]
    group_by: List[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_generated: Optional[datetime]

    class Config:
        from_attributes = True
