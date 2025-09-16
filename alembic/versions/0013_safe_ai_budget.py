"""Safe AI budget tracking - additive only

Revision ID: 0013_safe_ai_budget
Revises: 0012_safe_templates_conversations
Create Date: 2024-01-15 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0013_safe_ai_budget'
down_revision = '0012_safe_templates_conversations'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    This migration ensures AI budget tracking table exists safely.
    It only creates tables/columns if they don't already exist.
    No destructive operations are performed.
    """
    
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # Create ai_budgets table if it doesn't exist
    if 'ai_budgets' not in inspector.get_table_names():
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
    """
    This migration is designed to be safe and additive only.
    No downgrade operations are performed to prevent data loss.
    """
    pass
