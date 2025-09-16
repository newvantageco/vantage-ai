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
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create template_type enum
    template_type_enum = postgresql.ENUM('image', 'video', name='template_type')
    template_type_enum.create(op.get_bind())
    
    # Create asset_templates table
    op.create_table('asset_templates',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', template_type_enum, nullable=False),
        sa.Column('spec', sa.JSON(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_id', 'user_id', name='uq_user_org_role')
    )
    op.create_index(op.f('ix_asset_templates_org_id'), 'asset_templates', ['org_id'], unique=False)

    # Create template_usage table
    op.create_table('template_usage',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('template_id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('content_item_id', sa.String(36), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=False),
        sa.Column('inputs', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['asset_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['content_item_id'], ['content_items.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_template_usage_template_id'), 'template_usage', ['template_id'], unique=False)
    op.create_index(op.f('ix_template_usage_org_id'), 'template_usage', ['org_id'], unique=False)
    op.create_index(op.f('ix_template_usage_content_item_id'), 'template_usage', ['content_item_id'], unique=False)

    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('channel', sa.String(32), nullable=False),
        sa.Column('peer_id', sa.String(255), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_org_id'), 'conversations', ['org_id'], unique=False)
    op.create_index(op.f('ix_conversations_peer_id'), 'conversations', ['peer_id'], unique=False)

    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('conversation_id', sa.String(36), nullable=False),
        sa.Column('direction', sa.String(16), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('media_url', sa.String(500), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)


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
