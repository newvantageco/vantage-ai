"""Enhanced billing models

Revision ID: 0010_enhanced_billing
Revises: 0009_ai_budget
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0010_enhanced_billing'
down_revision = '0009_ai_budget'
branch_labels = None
depends_on = None


def upgrade():
    # Create coupons table
    op.create_table('coupons',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('discount_type', sa.String(20), nullable=False),
        sa.Column('discount_value', sa.Integer(), nullable=False),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=False, default=0),
        sa.Column('applicable_plans', sa.Text(), nullable=True),
        sa.Column('min_amount_cents', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coupons_code'), 'coupons', ['code'], unique=True)
    op.create_index(op.f('ix_coupons_is_active'), 'coupons', ['is_active'], unique=False)

    # Create billing_history table
    op.create_table('billing_history',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, default='usd'),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('plan', sa.Enum('starter', 'growth', 'pro', name='plan_tier'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('coupon_code', sa.String(100), nullable=True),
        sa.Column('discount_amount_cents', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_billing_history_org_id'), 'billing_history', ['org_id'], unique=False)
    op.create_index(op.f('ix_billing_history_stripe_payment_intent_id'), 'billing_history', ['stripe_payment_intent_id'], unique=False)

    # Add new columns to organization_billing table
    op.add_column('organization_billing', sa.Column('trial_start', sa.DateTime(), nullable=True))
    op.add_column('organization_billing', sa.Column('trial_end', sa.DateTime(), nullable=True))
    op.add_column('organization_billing', sa.Column('trial_used', sa.Boolean(), nullable=False, default=False))
    op.add_column('organization_billing', sa.Column('coupon_code', sa.String(100), nullable=True))
    op.add_column('organization_billing', sa.Column('coupon_discount_percent', sa.Integer(), nullable=True))
    op.add_column('organization_billing', sa.Column('coupon_discount_amount_cents', sa.Integer(), nullable=True))
    op.add_column('organization_billing', sa.Column('coupon_expires_at', sa.DateTime(), nullable=True))
    op.add_column('organization_billing', sa.Column('last_payment_date', sa.DateTime(), nullable=True))
    op.add_column('organization_billing', sa.Column('last_payment_amount_cents', sa.Integer(), nullable=True))
    op.add_column('organization_billing', sa.Column('next_payment_date', sa.DateTime(), nullable=True))
    op.add_column('organization_billing', sa.Column('next_payment_amount_cents', sa.Integer(), nullable=True))
    op.add_column('organization_billing', sa.Column('notes', sa.Text(), nullable=True))

    # Create indexes for new columns
    op.create_index(op.f('ix_organization_billing_coupon_code'), 'organization_billing', ['coupon_code'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_organization_billing_coupon_code'), table_name='organization_billing')
    op.drop_index(op.f('ix_billing_history_stripe_payment_intent_id'), table_name='billing_history')
    op.drop_index(op.f('ix_billing_history_org_id'), table_name='billing_history')
    op.drop_index(op.f('ix_coupons_is_active'), table_name='coupons')
    op.drop_index(op.f('ix_coupons_code'), table_name='coupons')

    # Drop new columns from organization_billing
    op.drop_column('organization_billing', 'notes')
    op.drop_column('organization_billing', 'next_payment_amount_cents')
    op.drop_column('organization_billing', 'next_payment_date')
    op.drop_column('organization_billing', 'last_payment_amount_cents')
    op.drop_column('organization_billing', 'last_payment_date')
    op.drop_column('organization_billing', 'coupon_expires_at')
    op.drop_column('organization_billing', 'coupon_discount_amount_cents')
    op.drop_column('organization_billing', 'coupon_discount_percent')
    op.drop_column('organization_billing', 'coupon_code')
    op.drop_column('organization_billing', 'trial_used')
    op.drop_column('organization_billing', 'trial_end')
    op.drop_column('organization_billing', 'trial_start')

    # Drop tables
    op.drop_table('billing_history')
    op.drop_table('coupons')

    # Note: plan_tier enum is created in migration 0004, so we don't drop it here
