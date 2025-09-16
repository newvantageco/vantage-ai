"""Add rules automation system

Revision ID: 0008_rules_automation
Revises: 0007_privacy_retention
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0008_rules_automation'
down_revision = '0007_privacy_retention'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create rule_status enum
    rule_status_enum = postgresql.ENUM(
        'pending', 'running', 'success', 'failed', 'skipped',
        name='rule_status'
    )
    rule_status_enum.create(op.get_bind())
    
    # Create rules table
    op.create_table('rules',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trigger', sa.String(100), nullable=False),
        sa.Column('condition_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('action_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create rule_runs table
    op.create_table('rule_runs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('rule_id', sa.String(36), nullable=False),
        sa.Column('status', rule_status_enum, nullable=False, server_default='pending'),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('meta_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_rules_org_id', 'rules', ['org_id'])
    op.create_index('ix_rules_trigger', 'rules', ['trigger'])
    op.create_index('ix_rules_enabled', 'rules', ['enabled'])
    
    op.create_index('ix_rule_runs_rule_id', 'rule_runs', ['rule_id'])
    op.create_index('ix_rule_runs_status', 'rule_runs', ['status'])
    op.create_index('ix_rule_runs_last_run_at', 'rule_runs', ['last_run_at'])


def downgrade() -> None:
    # Add-only migration; no DROP operations.
    pass
