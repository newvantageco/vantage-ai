"""Add AI budget tracking

Revision ID: 0009_ai_budget
Revises: 0008_rules_automation
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0009_ai_budget'
down_revision = '0008_rules_automation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_budgets table
    op.create_table('ai_budgets',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('daily_token_limit', sa.Integer(), nullable=False, default=100000),
        sa.Column('daily_cost_limit_gbp', sa.Float(), nullable=False, default=50.0),
        sa.Column('current_date', sa.Date(), nullable=False, default=sa.func.current_date()),
        sa.Column('tokens_used_today', sa.Integer(), nullable=False, default=0),
        sa.Column('cost_gbp_today', sa.Float(), nullable=False, default=0.0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on org_id for performance
    op.create_index('ix_ai_budgets_org_id', 'ai_budgets', ['org_id'])


def downgrade() -> None:
    # Drop ai_budgets table
    op.drop_index('ix_ai_budgets_org_id', table_name='ai_budgets')
    op.drop_table('ai_budgets')
