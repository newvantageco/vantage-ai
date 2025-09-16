from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrgRetention(Base):
    """Retention policies for organization data.
    
    Defines how long different types of data should be kept before
    being purged or anonymized for privacy compliance.
    """
    __tablename__ = "org_retention"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, unique=True)
    messages_days: Mapped[int] = mapped_column(Integer, default=90, nullable=False)  # Keep messages for N days
    logs_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # Keep audit logs for N days
    metrics_days: Mapped[int] = mapped_column(Integer, default=365, nullable=False)  # Keep metrics for N days
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PrivacyJob(Base):
    """Track privacy-related jobs (export, delete) for audit purposes.
    
    Provides visibility into data export and deletion operations
    for compliance and debugging purposes.
    """
    __tablename__ = "privacy_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    job_type: Mapped[str] = mapped_column(String(32), nullable=False)  # "export" or "delete"
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending, processing, completed, failed
    requested_by: Mapped[str] = mapped_column(String(36), nullable=False)  # user_id who requested
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # signed URL for export files
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
