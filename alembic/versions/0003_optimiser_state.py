"""Add optimiser_state and schedule_metrics tables

Revision ID: 0003_optimiser_state
Revises: 0002_content_models
Create Date: 2025-09-15 01:15:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_optimiser_state"
down_revision = "0002_content_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
	# optimiser_state
	op.create_table(
		"optimiser_state",
		sa.Column("id", sa.String(length=36), primary_key=True),
		sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
		sa.Column("key", sa.String(length=128), nullable=False),
		sa.Column("pulls", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("rewards", sa.Float(), nullable=False, server_default="0"),
		sa.Column("last_action_at", sa.DateTime(), nullable=True),
		sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
	)
	op.create_index("ix_optimiser_state_org_id", "optimiser_state", ["org_id"])
	op.create_index("ix_optimiser_state_key", "optimiser_state", ["key"])
	op.create_unique_constraint("uq_optimiser_org_key", "optimiser_state", ["org_id", "key"])

	# schedule_metrics
	op.create_table(
		"schedule_metrics",
		sa.Column("schedule_id", sa.String(length=36), primary_key=True),
		sa.Column("ctr", sa.Float(), nullable=True),
		sa.Column("engagement_rate", sa.Float(), nullable=True),
		sa.Column("reach_norm", sa.Float(), nullable=True),
		sa.Column("conv_rate", sa.Float(), nullable=True),
		sa.Column("applied", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
		sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
	)


def downgrade() -> None:
	# Add-only migration; no DROP operations.
	pass


