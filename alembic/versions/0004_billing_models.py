"""Add billing models

Revision ID: 0004_billing_models
Revises: 0003_optimiser_state
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0004_billing_models'
down_revision = '0003_optimiser_state'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create plan_tier enum
    plan_tier_enum = postgresql.ENUM('starter', 'growth', 'pro', name='plan_tier')
    plan_tier_enum.create(op.get_bind())
    
    # Create billing_status enum
    billing_status_enum = postgresql.ENUM(
        'active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing',
        name='billing_status'
    )
    billing_status_enum.create(op.get_bind())
    
    # Create organization_billing table
    op.create_table('organization_billing',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('plan', plan_tier_enum, nullable=False, server_default='starter'),
        sa.Column('status', billing_status_enum, nullable=False, server_default='active'),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_id')
    )
    
    # Create indexes
    op.create_index('ix_organization_billing_org_id', 'organization_billing', ['org_id'])
    op.create_index('ix_organization_billing_stripe_customer_id', 'organization_billing', ['stripe_customer_id'])
    op.create_index('ix_organization_billing_stripe_subscription_id', 'organization_billing', ['stripe_subscription_id'])


def downgrade() -> None:
    # Drop table
    op.drop_table('organization_billing')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS billing_status CASCADE')
    op.execute('DROP TYPE IF EXISTS plan_tier CASCADE')
