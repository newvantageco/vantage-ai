from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExportStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ExportTarget(str, Enum):
    bigquery = "bigquery"
    snowflake = "snowflake"
    s3 = "s3"
    csv = "csv"


class ExportJob(Base):
    """Export jobs for data warehouse integration."""
    __tablename__ = "export_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)  # User who initiated the export
    
    # Export configuration
    target: Mapped[ExportTarget] = mapped_column(SAEnum(ExportTarget), nullable=False)
    target_config: Mapped[str] = mapped_column(Text, nullable=False)  # JSON config for target
    tables: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of tables to export
    
    # Status and progress
    status: Mapped[ExportStatus] = mapped_column(SAEnum(ExportStatus), default=ExportStatus.pending, nullable=False)
    progress_percent: Mapped[int] = mapped_column(default=0, nullable=False)
    current_table: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Results
    records_exported: Mapped[int] = mapped_column(default=0, nullable=False)
    total_records: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # File information
    file_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)
    download_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_export_jobs_org_id", "org_id"),
        Index("ix_export_jobs_user_id", "user_id"),
        Index("ix_export_jobs_target", "target"),
        Index("ix_export_jobs_status", "status"),
        Index("ix_export_jobs_created_at", "created_at"),
    )

    def get_target_config(self) -> Dict[str, Any]:
        """Get target configuration as a dictionary."""
        try:
            return json.loads(self.target_config)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_target_config(self, config: Dict[str, Any]) -> None:
        """Set target configuration from a dictionary."""
        self.target_config = json.dumps(config)

    def get_tables(self) -> list[str]:
        """Get tables to export as a list."""
        try:
            return json.loads(self.tables)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tables(self, tables: list[str]) -> None:
        """Set tables to export from a list."""
        self.tables = json.dumps(tables)

    def is_expired(self) -> bool:
        """Check if the export job has expired (older than 7 days)."""
        if not self.created_at:
            return False
        return (datetime.utcnow() - self.created_at).days > 7

    def get_duration_seconds(self) -> Optional[int]:
        """Get the duration of the export job in seconds."""
        if not self.started_at:
            return None
        end_time = self.finished_at or datetime.utcnow()
        return int((end_time - self.started_at).total_seconds())


class ExportTable(Base):
    """Configuration for exportable tables."""
    __tablename__ = "export_tables"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    table_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Table metadata
    schema_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON schema
    primary_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_export_tables_table_name", "table_name"),
    )

    def get_schema(self) -> Dict[str, Any]:
        """Get table schema as a dictionary."""
        try:
            return json.loads(self.schema_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_schema(self, schema: Dict[str, Any]) -> None:
        """Set table schema from a dictionary."""
        self.schema_json = json.dumps(schema)


class ExportCredential(Base):
    """Stored credentials for export targets."""
    __tablename__ = "export_credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Credential details
    target: Mapped[ExportTarget] = mapped_column(SAEnum(ExportTarget), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Human-readable name
    encrypted_credentials: Mapped[str] = mapped_column(Text, nullable=False)  # Encrypted credentials
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("org_id", "target", "name", name="uq_export_credentials_org_target_name"),
        Index("ix_export_credentials_org_id", "org_id"),
        Index("ix_export_credentials_target", "target"),
        Index("ix_export_credentials_is_active", "is_active"),
    )

    def get_credentials(self) -> Dict[str, Any]:
        """Get decrypted credentials as a dictionary."""
        # In a real implementation, this would decrypt the credentials
        try:
            return json.loads(self.encrypted_credentials)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_credentials(self, credentials: Dict[str, Any]) -> None:
        """Set encrypted credentials from a dictionary."""
        # In a real implementation, this would encrypt the credentials
        self.encrypted_credentials = json.dumps(credentials)


# Available export tables
EXPORT_TABLES = {
    "schedules": {
        "display_name": "Schedules",
        "description": "Content scheduling data",
        "schema": {
            "id": "string",
            "org_id": "string",
            "content_item_id": "string",
            "channel_id": "string",
            "scheduled_at": "datetime",
            "status": "string",
            "error_message": "string",
            "created_at": "datetime"
        },
        "primary_key": "id"
    },
    "post_metrics": {
        "display_name": "Post Metrics",
        "description": "Social media post performance metrics",
        "schema": {
            "id": "string",
            "schedule_id": "string",
            "impressions": "integer",
            "reach": "integer",
            "likes": "integer",
            "comments": "integer",
            "shares": "integer",
            "clicks": "integer",
            "video_views": "integer",
            "saves": "integer",
            "cost_cents": "integer",
            "fetched_at": "datetime",
            "created_at": "datetime"
        },
        "primary_key": "id"
    },
    "conversations": {
        "display_name": "Conversations",
        "description": "Customer conversation data",
        "schema": {
            "id": "string",
            "org_id": "string",
            "channel_id": "string",
            "platform_message_id": "string",
            "sender_id": "string",
            "sender_name": "string",
            "message_text": "string",
            "message_type": "string",
            "is_from_customer": "boolean",
            "created_at": "datetime"
        },
        "primary_key": "id"
    },
    "ad_metrics": {
        "display_name": "Ad Metrics",
        "description": "Advertising campaign performance data",
        "schema": {
            "id": "string",
            "org_id": "string",
            "campaign_id": "string",
            "ad_group_id": "string",
            "ad_id": "string",
            "platform": "string",
            "impressions": "integer",
            "clicks": "integer",
            "spend_cents": "integer",
            "conversions": "integer",
            "date": "date",
            "created_at": "datetime"
        },
        "primary_key": "id"
    }
}
