"""Add privacy and retention tables

Revision ID: 0007_privacy_retention
Revises: 0006_post_metrics_external_refs
Create Date: 2025-01-27 12:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0007_privacy_retention"
down_revision = "0006_post_metrics_external_refs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # org_retention table
    op.create_table(
        "org_retention",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("messages_days", sa.Integer(), nullable=False, default=90),
        sa.Column("logs_days", sa.Integer(), nullable=False, default=30),
        sa.Column("metrics_days", sa.Integer(), nullable=False, default=365),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    
    # Indexes for org_retention
    op.create_index("ix_org_retention_org_id", "org_retention", ["org_id"])
    
    # privacy_jobs table
    op.create_table(
        "privacy_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, default="pending"),
        sa.Column("requested_by", sa.String(length=36), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    
    # Indexes for privacy_jobs
    op.create_index("ix_privacy_jobs_org_id", "privacy_jobs", ["org_id"])
    op.create_index("ix_privacy_jobs_status", "privacy_jobs", ["status"])
    op.create_index("ix_privacy_jobs_job_type", "privacy_jobs", ["job_type"])
    op.create_index("ix_privacy_jobs_created_at", "privacy_jobs", ["created_at"])


def downgrade() -> None:
    # Add-only migration; no DROP operations.
    pass
