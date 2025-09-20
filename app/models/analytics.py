"""
Analytics Models
Handles metrics collection, reporting, and data export
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class PostMetrics(Base):
    __tablename__ = "post_metrics"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    external_reference_id = Column(Integer, ForeignKey("external_references.id"), nullable=True)
    
    # Platform details
    platform = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=False)  # Platform-specific post ID
    
    # Metrics
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)  # Click-through rate
    engagements = Column(Integer, default=0)  # Total engagements (likes, comments, shares)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    
    # Conversion metrics
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    cost_per_click = Column(Float, default=0.0)
    cost_per_conversion = Column(Float, default=0.0)
    
    # Video metrics (if applicable)
    video_views = Column(Integer, default=0)
    video_completion_rate = Column(Float, default=0.0)
    
    # Engagement rate calculation
    engagement_rate = Column(Float, default=0.0)
    
    # Data source
    data_source = Column(String(50), default="api")  # api, webhook, manual
    is_estimated = Column(Boolean, default=False)  # Whether metrics are estimated
    
    # Timestamps
    metric_date = Column(DateTime(timezone=True), nullable=False)  # Date the metrics are for
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    external_reference = relationship("ExternalReference")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_post_metrics_org_platform_date', 'organization_id', 'platform', 'metric_date'),
        Index('idx_post_metrics_external_id', 'external_id'),
        Index('idx_post_metrics_metric_date', 'metric_date'),
    )


class AnalyticsSummary(Base):
    __tablename__ = "analytics_summary"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Summary period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Aggregated metrics
    total_impressions = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    total_engagements = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    
    # Average rates
    avg_ctr = Column(Float, default=0.0)
    avg_engagement_rate = Column(Float, default=0.0)
    avg_conversion_rate = Column(Float, default=0.0)
    
    # Platform breakdown
    platform_breakdown = Column(JSON, nullable=True)  # Metrics per platform
    
    # Top performing content
    top_content = Column(JSON, nullable=True)  # Top performing content items
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    
    # Indexes
    __table_args__ = (
        Index('idx_analytics_summary_org_period', 'organization_id', 'period_start', 'period_end'),
    )


class AnalyticsExport(Base):
    __tablename__ = "analytics_exports"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Export details
    export_type = Column(String(50), nullable=False)  # csv, excel, json
    date_range_start = Column(DateTime(timezone=True), nullable=False)
    date_range_end = Column(DateTime(timezone=True), nullable=False)
    platforms = Column(JSON, nullable=True)  # Specific platforms to include
    metrics = Column(JSON, nullable=True)  # Specific metrics to include
    
    # Export status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    file_url = Column(String(500), nullable=True)  # URL to download the export
    file_size = Column(Integer, nullable=True)  # File size in bytes
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # When the export expires
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("UserAccount")
