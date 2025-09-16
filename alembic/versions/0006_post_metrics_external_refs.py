"""Add post_metrics and schedule_external tables

Revision ID: 0006_post_metrics_external_refs
Revises: 0005_templates_conversations
Create Date: 2025-01-27 10:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0006_post_metrics_external_refs"
down_revision = "0005_templates_conversations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # post_metrics table
    op.create_table(
        "post_metrics",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("schedule_id", sa.String(length=36), sa.ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("reach", sa.Integer(), nullable=True),
        sa.Column("likes", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Integer(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=True),
        sa.Column("video_views", sa.Integer(), nullable=True),
        sa.Column("saves", sa.Integer(), nullable=True),
        sa.Column("cost_cents", sa.Integer(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    
    # Indexes for post_metrics
    op.create_index("ix_post_metrics_schedule_id", "post_metrics", ["schedule_id"])
    op.create_index("ix_post_metrics_fetched_at", "post_metrics", ["fetched_at"])
    op.create_unique_constraint("uq_post_metrics_schedule_fetched", "post_metrics", ["schedule_id", "fetched_at"])

    # schedule_external table
    op.create_table(
        "schedule_external",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("schedule_id", sa.String(length=36), sa.ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ref_id", sa.String(length=255), nullable=False),
        sa.Column("ref_url", sa.String(length=500), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    
    # Indexes for schedule_external
    op.create_index("ix_schedule_external_schedule_id", "schedule_external", ["schedule_id"])
    op.create_index("ix_schedule_external_provider", "schedule_external", ["provider"])
    op.create_index("ix_schedule_external_ref_id", "schedule_external", ["ref_id"])
    op.create_unique_constraint("uq_schedule_external_schedule_provider", "schedule_external", ["schedule_id", "provider"])


def downgrade() -> None:
    # Add-only migration; no DROP operations.
    pass
