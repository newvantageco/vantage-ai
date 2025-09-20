"""
Privacy Models
Handles data export, deletion, and privacy compliance
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class ExportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class DeletionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class PrivacyRequestType(str, enum.Enum):
    EXPORT = "export"
    DELETION = "deletion"


class PrivacyRequestStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    EXPIRED = "expired"


class PrivacyRequest(Base):
    """Unified privacy request model for both export and deletion requests"""
    __tablename__ = "privacy_requests"
    
    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    requested_by = Column(String(36), nullable=False)  # User ID who requested
    
    # Request details
    request_type = Column(Enum(PrivacyRequestType), nullable=False)
    status = Column(Enum(PrivacyRequestStatus), default=PrivacyRequestStatus.PENDING)
    
    # Verification
    verification_token = Column(String(255), nullable=True, unique=True)
    
    # Request-specific data
    data_categories = Column(JSON, nullable=True)  # For export requests
    reason = Column(Text, nullable=True)  # For deletion requests
    specific_data = Column(JSON, nullable=True)  # Additional request data
    
    # Processing details
    celery_job_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # File details (for export requests)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Scheduling (for deletion requests)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    
    # Cancellation details
    canceled_by = Column(String(36), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")


class DataExport(Base):
    """Data export requests and tracking"""
    __tablename__ = "data_exports"
    
    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    requested_by = Column(String(36), nullable=False)  # User ID who requested export
    
    # Export details
    format_type = Column(String(20), nullable=False)  # json, csv, zip
    status = Column(Enum(ExportStatus), default=ExportStatus.PENDING)
    
    # File details
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Processing details
    celery_job_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    organization = relationship("Organization")


class DeletionRequest(Base):
    """Data deletion requests and tracking"""
    __tablename__ = "deletion_requests"
    
    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    requested_by = Column(String(36), nullable=False)  # User ID who requested deletion
    
    # Deletion details
    reason = Column(Text, nullable=True)
    status = Column(Enum(DeletionStatus), default=DeletionStatus.PENDING)
    
    # Processing details
    celery_job_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    
    # Cancellation details
    canceled_by = Column(String(36), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")


class PrivacyEvent(Base):
    """Privacy-related events for audit trail"""
    __tablename__ = "privacy_events"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # data_export_requested, deletion_requested, etc.
    event_data = Column(JSON, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")


class DataRetentionPolicy(Base):
    """Data retention policies for different data types"""
    __tablename__ = "data_retention_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(100), nullable=False, unique=True)  # user_data, analytics, billing, etc.
    retention_days = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ConsentRecord(Base):
    """User consent records for data processing"""
    __tablename__ = "consent_records"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    
    # Consent details
    consent_type = Column(String(100), nullable=False)  # data_processing, marketing, analytics, etc.
    granted = Column(Boolean, nullable=False)
    consent_text = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    granted_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")


class DataProcessingActivity(Base):
    """Records of data processing activities for GDPR compliance"""
    __tablename__ = "data_processing_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    # Processing details
    activity_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    legal_basis = Column(String(100), nullable=False)  # consent, contract, legitimate_interest, etc.
    data_categories = Column(JSON, nullable=True)  # List of data categories processed
    purposes = Column(JSON, nullable=True)  # List of processing purposes
    
    # Data subjects
    data_subject_categories = Column(JSON, nullable=True)  # customers, employees, etc.
    
    # Retention
    retention_period = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")


class PrivacySettings(Base):
    """Organization privacy settings and preferences"""
    __tablename__ = "privacy_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, unique=True)
    
    # Data processing settings
    allow_analytics = Column(Boolean, default=True)
    allow_marketing = Column(Boolean, default=False)
    allow_data_sharing = Column(Boolean, default=False)
    
    # Retention settings
    data_retention_days = Column(Integer, default=2555)  # 7 years default
    
    # Notification settings
    notify_on_export = Column(Boolean, default=True)
    notify_on_deletion = Column(Boolean, default=True)
    notify_on_breach = Column(Boolean, default=True)
    
    # Compliance settings
    gdpr_compliant = Column(Boolean, default=True)
    ccpa_compliant = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")


class DataBreach(Base):
    """Data breach incident records"""
    __tablename__ = "data_breaches"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    reported_by = Column(String(36), nullable=False)
    
    # Breach details
    breach_type = Column(String(100), nullable=False)  # unauthorized_access, data_loss, etc.
    description = Column(Text, nullable=False)
    affected_data_categories = Column(JSON, nullable=True)
    affected_records_count = Column(Integer, nullable=True)
    
    # Timeline
    discovered_at = Column(DateTime(timezone=True), nullable=False)
    contained_at = Column(DateTime(timezone=True), nullable=True)
    notified_authorities_at = Column(DateTime(timezone=True), nullable=True)
    notified_individuals_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(50), default="investigating")  # investigating, contained, resolved
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")