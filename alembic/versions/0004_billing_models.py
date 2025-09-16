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
    # Create plan_tier enum with idempotency check
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'plan_tier') THEN
            CREATE TYPE plan_tier AS ENUM ('starter', 'growth', 'pro');
        END IF;
    END $$;
    """)
    
    # Create billing_status enum with idempotency check
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'billing_status') THEN
            CREATE TYPE billing_status AS ENUM ('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing');
        END IF;
    END $$;
    """)
    
    # Create organization_billing table using raw SQL to avoid enum creation conflicts
    op.execute("""
    CREATE TABLE IF NOT EXISTS organization_billing (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        org_id VARCHAR(36) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        stripe_customer_id VARCHAR(255),
        stripe_subscription_id VARCHAR(255),
        plan plan_tier NOT NULL DEFAULT 'starter',
        status billing_status NOT NULL DEFAULT 'active',
        current_period_start TIMESTAMP WITHOUT TIME ZONE,
        current_period_end TIMESTAMP WITHOUT TIME ZONE,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT uq_organization_billing_org_id UNIQUE (org_id)
    );
    """)
    
    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_organization_billing_org_id ON organization_billing (org_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_organization_billing_stripe_customer_id ON organization_billing (stripe_customer_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_organization_billing_stripe_subscription_id ON organization_billing (stripe_subscription_id)")


def downgrade() -> None:
    # Drop table
    op.drop_table('organization_billing')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS billing_status CASCADE')
    op.execute('DROP TYPE IF EXISTS plan_tier CASCADE')
