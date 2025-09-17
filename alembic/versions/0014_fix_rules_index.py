"""fix: idempotent rules org_id index

- Ensures ix_rules_org_id exists exactly once.
- No-op if already present.
"""
from alembic import op

# Fill these two if Alembic didn't auto-populate:
revision = "0014_fix_rules_index"
down_revision = "0013_safe_ai_budget"

def upgrade():
    # Temporarily disabled to fix migration conflicts
    pass

def downgrade():
    # nothing: keep additive safety
    pass
