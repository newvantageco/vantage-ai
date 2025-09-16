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
    # Create rule_status enum with idempotency check
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rule_status') THEN
            CREATE TYPE rule_status AS ENUM ('pending', 'running', 'success', 'failed', 'skipped');
        END IF;
    END $$;
    """)
    
    # Skip creating rules table - it already exists from manual migration
    # The rules table was created in the manual migration process
    
    # Create rule_runs table using raw SQL to avoid enum creation conflicts
    op.execute("""
    CREATE TABLE IF NOT EXISTS rule_runs (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        rule_id VARCHAR(36) NOT NULL,
        status rule_status NOT NULL DEFAULT 'pending',
        last_run_at TIMESTAMP WITHOUT TIME ZONE,
        meta_json JSONB,
        started_at TIMESTAMP WITHOUT TIME ZONE,
        completed_at TIMESTAMP WITHOUT TIME ZONE,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_rule_runs_rule_id FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
    );
    """)
    
    # Create indexes using raw SQL
    op.execute("CREATE INDEX IF NOT EXISTS ix_rule_runs_rule_id ON rule_runs (rule_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rule_runs_status ON rule_runs (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rule_runs_last_run_at ON rule_runs (last_run_at)")


def downgrade() -> None:
    # Add-only migration; no DROP operations.
    pass
