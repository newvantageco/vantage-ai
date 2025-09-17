"""Add performance indexes

Revision ID: 20241220_add_performance_indexes
Revises: 
Create Date: 2024-12-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241220_add_performance_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if tables exist before creating indexes
    connection = op.get_bind()
    
    # Add indexes for conversations table (if exists)
    try:
        connection.execute(sa.text("SELECT 1 FROM conversations LIMIT 1"))
        op.create_index('ix_conversations_org_channel', 'conversations', ['org_id', 'channel'])
        op.create_index('ix_conversations_last_message', 'conversations', ['last_message_at'])
        op.create_index('ix_conversations_peer_id', 'conversations', ['peer_id'])
    except Exception:
        pass  # Table doesn't exist yet
    
    # Add indexes for messages table (if exists)
    try:
        connection.execute(sa.text("SELECT 1 FROM messages LIMIT 1"))
        op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])
        op.create_index('ix_messages_direction', 'messages', ['direction'])
    except Exception:
        pass  # Table doesn't exist yet
    
    # Add indexes for schedules table (if exists)
    try:
        connection.execute(sa.text("SELECT 1 FROM schedules LIMIT 1"))
        op.create_index('ix_schedules_org_status', 'schedules', ['org_id', 'status'])
        op.create_index('ix_schedules_scheduled_at', 'schedules', ['scheduled_at'])
    except Exception:
        pass  # Table doesn't exist yet
    
    # Add indexes for content_items table (if exists)
    try:
        connection.execute(sa.text("SELECT 1 FROM content_items LIMIT 1"))
        op.create_index('ix_content_items_org_status', 'content_items', ['org_id', 'status'])
        op.create_index('ix_content_items_created_at', 'content_items', ['created_at'])
    except Exception:
        pass  # Table doesn't exist yet


def downgrade() -> None:
    # Drop indexes for conversations table
    op.drop_index('ix_conversations_org_channel', table_name='conversations')
    op.drop_index('ix_conversations_last_message', table_name='conversations')
    op.drop_index('ix_conversations_peer_id', table_name='conversations')
    
    # Drop indexes for messages table
    op.drop_index('ix_messages_conversation_created', table_name='messages')
    op.drop_index('ix_messages_direction', table_name='messages')
    
    # Drop indexes for schedules table (if exists)
    try:
        op.drop_index('ix_schedules_org_status', table_name='schedules')
        op.drop_index('ix_schedules_scheduled_at', table_name='schedules')
    except Exception:
        pass  # Table might not exist yet
    
    # Drop indexes for content_items table (if exists)
    try:
        op.drop_index('ix_content_items_org_status', table_name='content_items')
        op.drop_index('ix_content_items_created_at', table_name='content_items')
    except Exception:
        pass  # Table might not exist yet
