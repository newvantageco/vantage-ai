"""Safe billing models - additive only

Revision ID: 0011_safe_billing_models
Revises: 0010_enhanced_billing
Create Date: 2024-01-15 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0011_safe_billing_models'
down_revision = '0010_enhanced_billing'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    This migration ensures billing models exist safely.
    It only creates tables/columns if they don't already exist.
    No destructive operations are performed.
    """
    
    # Check if organization_billing table exists, create if not
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'organization_billing' not in inspector.get_table_names():
        # Create plan_tier enum if it doesn't exist
        try:
            plan_tier_enum = postgresql.ENUM('starter', 'growth', 'pro', name='plan_tier')
            plan_tier_enum.create(op.get_bind(), checkfirst=True)
        except Exception:
            pass  # Enum might already exist
        
        # Create billing_status enum if it doesn't exist
        try:
            billing_status_enum = postgresql.ENUM(
                'active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing',
                name='billing_status'
            )
            billing_status_enum.create(op.get_bind(), checkfirst=True)
        except Exception:
            pass  # Enum might already exist
        
        # Create organization_billing table
        op.create_table('organization_billing',
            sa.Column('id', sa.String(36), nullable=False),
            sa.Column('org_id', sa.String(36), nullable=False),
            sa.Column('stripe_customer_id', sa.String(255), nullable=True),
            sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
            sa.Column('plan', postgresql.ENUM('starter', 'growth', 'pro', name='plan_tier'), nullable=False, server_default='starter'),
            sa.Column('status', postgresql.ENUM('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing', name='billing_status'), nullable=False, server_default='active'),
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
    
    # Add missing columns to organization_billing if they don't exist
    if 'organization_billing' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('organization_billing')]
        
        # Add trial columns if missing
        if 'trial_start' not in columns:
            op.add_column('organization_billing', sa.Column('trial_start', sa.DateTime(), nullable=True))
        if 'trial_end' not in columns:
            op.add_column('organization_billing', sa.Column('trial_end', sa.DateTime(), nullable=True))
        if 'trial_used' not in columns:
            op.add_column('organization_billing', sa.Column('trial_used', sa.Boolean(), nullable=False, default=False))
        
        # Add coupon columns if missing
        if 'coupon_code' not in columns:
            op.add_column('organization_billing', sa.Column('coupon_code', sa.String(100), nullable=True))
        if 'coupon_discount_percent' not in columns:
            op.add_column('organization_billing', sa.Column('coupon_discount_percent', sa.Integer(), nullable=True))
        if 'coupon_discount_amount_cents' not in columns:
            op.add_column('organization_billing', sa.Column('coupon_discount_amount_cents', sa.Integer(), nullable=True))
        if 'coupon_expires_at' not in columns:
            op.add_column('organization_billing', sa.Column('coupon_expires_at', sa.DateTime(), nullable=True))
        
        # Add payment tracking columns if missing
        if 'last_payment_date' not in columns:
            op.add_column('organization_billing', sa.Column('last_payment_date', sa.DateTime(), nullable=True))
        if 'last_payment_amount_cents' not in columns:
            op.add_column('organization_billing', sa.Column('last_payment_amount_cents', sa.Integer(), nullable=True))
        if 'next_payment_date' not in columns:
            op.add_column('organization_billing', sa.Column('next_payment_date', sa.DateTime(), nullable=True))
        if 'next_payment_amount_cents' not in columns:
            op.add_column('organization_billing', sa.Column('next_payment_amount_cents', sa.Integer(), nullable=True))
        if 'notes' not in columns:
            op.add_column('organization_billing', sa.Column('notes', sa.Text(), nullable=True))
    
    # Create coupons table if it doesn't exist
    if 'coupons' not in inspector.get_table_names():
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
    
    # Create billing_history table if it doesn't exist
    if 'billing_history' not in inspector.get_table_names():
        op.create_table('billing_history',
            sa.Column('id', sa.String(36), nullable=False),
            sa.Column('org_id', sa.String(36), nullable=False),
            sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
            sa.Column('amount_cents', sa.Integer(), nullable=False),
            sa.Column('currency', sa.String(3), nullable=False, default='usd'),
            sa.Column('description', sa.String(500), nullable=False),
            sa.Column('plan', sa.Enum('STARTER', 'GROWTH', 'PRO', name='plan_tier'), nullable=False),
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
    
    # Create missing indexes
    try:
        op.create_index(op.f('ix_organization_billing_coupon_code'), 'organization_billing', ['coupon_code'], unique=False)
    except Exception:
        pass  # Index might already exist


def downgrade() -> None:
    """
    This migration is designed to be safe and additive only.
    No downgrade operations are performed to prevent data loss.
    """
    pass
