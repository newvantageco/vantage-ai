"""Add templates and conversations tables

Revision ID: 0005
Revises: 0004
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004_billing_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create template_type enum with idempotency check
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'template_type') THEN
            CREATE TYPE template_type AS ENUM ('image', 'video');
        END IF;
    END $$;
    """)
    
    # Create asset_templates table using raw SQL to avoid enum creation conflicts
    op.execute("""
    CREATE TABLE IF NOT EXISTS asset_templates (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        org_id VARCHAR(36),
        name VARCHAR(255) NOT NULL,
        description TEXT,
        type template_type NOT NULL,
        spec JSON NOT NULL,
        is_public BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(36),
        CONSTRAINT fk_asset_templates_org_id FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
        CONSTRAINT fk_asset_templates_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
        CONSTRAINT uq_asset_templates_org_created_by UNIQUE (org_id, created_by)
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_asset_templates_org_id ON asset_templates (org_id)")

    # Create template_usage table
    op.execute("""
    CREATE TABLE IF NOT EXISTS template_usage (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        template_id VARCHAR(36) NOT NULL,
        org_id VARCHAR(36) NOT NULL,
        content_item_id VARCHAR(36),
        used_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        inputs JSON,
        CONSTRAINT fk_template_usage_template_id FOREIGN KEY (template_id) REFERENCES asset_templates(id) ON DELETE CASCADE,
        CONSTRAINT fk_template_usage_org_id FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
        CONSTRAINT fk_template_usage_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items(id) ON DELETE SET NULL
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_template_usage_template_id ON template_usage (template_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_template_usage_org_id ON template_usage (org_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_template_usage_content_item_id ON template_usage (content_item_id)")

    # Create conversations table
    op.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        org_id VARCHAR(36) NOT NULL,
        channel VARCHAR(32) NOT NULL,
        peer_id VARCHAR(255) NOT NULL,
        last_message_at TIMESTAMP WITHOUT TIME ZONE,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_conversations_org_id FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_conversations_org_id ON conversations (org_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_conversations_peer_id ON conversations (peer_id)")

    # Create messages table
    op.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        conversation_id VARCHAR(36) NOT NULL,
        direction VARCHAR(16) NOT NULL,
        text TEXT,
        media_url VARCHAR(500),
        metadata JSON,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_messages_conversation_id FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id)")


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')
    
    op.drop_index(op.f('ix_conversations_peer_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_org_id'), table_name='conversations')
    op.drop_table('conversations')
    
    op.drop_index(op.f('ix_template_usage_content_item_id'), table_name='template_usage')
    op.drop_index(op.f('ix_template_usage_org_id'), table_name='template_usage')
    op.drop_index(op.f('ix_template_usage_template_id'), table_name='template_usage')
    op.drop_table('template_usage')
    
    op.drop_index(op.f('ix_asset_templates_org_id'), table_name='asset_templates')
    op.drop_table('asset_templates')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS template_type CASCADE')
