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

    # Create billing_history table using raw SQL to avoid enum creation conflicts
    op.execute("""
    CREATE TABLE IF NOT EXISTS billing_history (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        org_id VARCHAR(36) NOT NULL,
        stripe_payment_intent_id VARCHAR(255),
        amount_cents INTEGER NOT NULL,
        currency VARCHAR(3) NOT NULL DEFAULT 'usd',
        description VARCHAR(500) NOT NULL,
        plan plan_tier NOT NULL,
        status VARCHAR(20) NOT NULL,
        coupon_code VARCHAR(100),
        discount_amount_cents INTEGER,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP WITHOUT TIME ZONE,
        CONSTRAINT fk_billing_history_org_id FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_billing_history_org_id ON billing_history (org_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_billing_history_stripe_payment_intent_id ON billing_history (stripe_payment_intent_id)")

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
