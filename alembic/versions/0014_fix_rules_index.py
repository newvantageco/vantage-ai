"""fix: idempotent rules org_id index

- Ensures ix_rules_org_id exists exactly once.
- No-op if already present.
"""
from alembic import op

# Fill these two if Alembic didn't auto-populate:
revision = "0014_fix_rules_index"
down_revision = "0013_safe_ai_budget"

def upgrade():
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'i' AND c.relname = 'ix_rules_org_id'
      ) THEN
        -- create only if the index truly doesn't exist
        CREATE INDEX ix_rules_org_id ON rules (org_id);
      END IF;
    END $$;
    """)

def downgrade():
    # nothing: keep additive safety
    pass
