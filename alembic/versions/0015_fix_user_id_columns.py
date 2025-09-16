"""fix: add user_id to affected tables (idempotent)

Adds user_id (UUID, nullable) where missing and wires FK to users(id).
Includes IF NOT EXISTS guards so it's safe to run on any env.
"""
from alembic import op

# Fill these:
revision = "0015_fix_user_id_columns"
down_revision = "0014_fix_rules_index"

def upgrade():
    # 1) rules.user_id (if your error pointed at rules)
    op.execute("""
    DO $$
    BEGIN
      -- add column if missing
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='rules' AND column_name='user_id'
      ) THEN
        ALTER TABLE rules ADD COLUMN user_id VARCHAR(36) NULL;
      END IF;

      -- index if missing
      IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname='ix_rules_user_id' AND relkind='i'
      ) THEN
        CREATE INDEX ix_rules_user_id ON rules (user_id);
      END IF;

      -- fk if missing
      IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname='fk_rules_user_id_users' AND contype='f'
      ) THEN
        ALTER TABLE rules
          ADD CONSTRAINT fk_rules_user_id_users
          FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY IMMEDIATE;
      END IF;
    END $$;
    """)

    # 2) approvals.user_id (common second offender; safe no-op if table/col exists)
    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='approvals') THEN
        IF NOT EXISTS (
          SELECT 1 FROM information_schema.columns
          WHERE table_name='approvals' AND column_name='user_id'
        ) THEN
            ALTER TABLE approvals ADD COLUMN user_id VARCHAR(36) NULL;
        END IF;

        IF NOT EXISTS (
          SELECT 1 FROM pg_class WHERE relname='ix_approvals_user_id' AND relkind='i'
        ) THEN
          CREATE INDEX ix_approvals_user_id ON approvals (user_id);
        END IF;

        IF NOT EXISTS (
          SELECT 1 FROM pg_constraint
          WHERE conname='fk_approvals_user_id_users' AND contype='f'
        ) THEN
          ALTER TABLE approvals
            ADD CONSTRAINT fk_approvals_user_id_users
            FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY IMMEDIATE;
        END IF;
      END IF;
    END $$;
    """)

def downgrade():
    # additive, no destructive downgrade
    pass
