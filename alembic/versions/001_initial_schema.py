"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-12-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=True, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('locale', sa.String(10), default='en-US'),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('subscription_status', sa.String(50), default='trial'),
        sa.Column('plan', sa.String(50), default='starter'),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    
    # Create user_accounts table
    op.create_table(
        'user_accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('clerk_user_id', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('role', sa.String(20), default='editor'),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    
    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('user_accounts.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('budget', sa.Numeric(10, 2), nullable=True),
        sa.Column('target_audience', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    
    # Create content_items table
    op.create_table(
        'content_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('user_accounts.id'), nullable=False),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(50), default='text'),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String(100)), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), default=False),
        sa.Column('ai_prompt', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    
    # Create brand_guides table
    op.create_table(
        'brand_guides',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('voice', sa.Text(), nullable=True),
        sa.Column('tone', sa.Text(), nullable=True),
        sa.Column('audience', sa.Text(), nullable=True),
        sa.Column('pillars', sa.ARRAY(sa.String(200)), nullable=True),
        sa.Column('keywords', sa.ARRAY(sa.String(100)), nullable=True),
        sa.Column('avoid_words', sa.ARRAY(sa.String(100)), nullable=True),
        sa.Column('style_guide', sa.JSON(), nullable=True),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    
    # Create schedules table
    op.create_table(
        'schedules',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('content_items.id'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    
    # Create indexes
    op.create_index('ix_organizations_id', 'organizations', ['id'])
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])
    op.create_index('ix_organizations_stripe_customer_id', 'organizations', ['stripe_customer_id'])
    op.create_index('ix_user_accounts_organization_id', 'user_accounts', ['organization_id'])
    op.create_index('ix_user_accounts_clerk_user_id', 'user_accounts', ['clerk_user_id'])
    op.create_index('ix_user_accounts_email', 'user_accounts', ['email'])
    op.create_index('ix_campaigns_organization_id', 'campaigns', ['organization_id'])
    op.create_index('ix_campaigns_created_by_id', 'campaigns', ['created_by_id'])
    op.create_index('ix_campaigns_status', 'campaigns', ['status'])
    op.create_index('ix_content_items_organization_id', 'content_items', ['organization_id'])
    op.create_index('ix_content_items_created_by_id', 'content_items', ['created_by_id'])
    op.create_index('ix_content_items_campaign_id', 'content_items', ['campaign_id'])
    op.create_index('ix_content_items_status', 'content_items', ['status'])
    op.create_index('ix_content_items_scheduled_at', 'content_items', ['scheduled_at'])
    op.create_index('ix_brand_guides_organization_id', 'brand_guides', ['organization_id'])
    op.create_index('ix_schedules_organization_id', 'schedules', ['organization_id'])
    op.create_index('ix_schedules_content_id', 'schedules', ['content_id'])
    op.create_index('ix_schedules_platform', 'schedules', ['platform'])
    op.create_index('ix_schedules_scheduled_at', 'schedules', ['scheduled_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_schedules_scheduled_at', table_name='schedules')
    op.drop_index('ix_schedules_platform', table_name='schedules')
    op.drop_index('ix_schedules_content_id', table_name='schedules')
    op.drop_index('ix_schedules_organization_id', table_name='schedules')
    op.drop_index('ix_brand_guides_organization_id', table_name='brand_guides')
    op.drop_index('ix_content_items_scheduled_at', table_name='content_items')
    op.drop_index('ix_content_items_status', table_name='content_items')
    op.drop_index('ix_content_items_campaign_id', table_name='content_items')
    op.drop_index('ix_content_items_created_by_id', table_name='content_items')
    op.drop_index('ix_content_items_organization_id', table_name='content_items')
    op.drop_index('ix_campaigns_status', table_name='campaigns')
    op.drop_index('ix_campaigns_created_by_id', table_name='campaigns')
    op.drop_index('ix_campaigns_organization_id', table_name='campaigns')
    op.drop_index('ix_user_accounts_email', table_name='user_accounts')
    op.drop_index('ix_user_accounts_clerk_user_id', table_name='user_accounts')
    op.drop_index('ix_user_accounts_organization_id', table_name='user_accounts')
    op.drop_index('ix_organizations_stripe_customer_id', table_name='organizations')
    op.drop_index('ix_organizations_slug', table_name='organizations')
    op.drop_index('ix_organizations_id', table_name='organizations')
    
    # Drop tables
    op.drop_table('schedules')
    op.drop_table('brand_guides')
    op.drop_table('content_items')
    op.drop_table('campaigns')
    op.drop_table('user_accounts')
    op.drop_table('organizations')
    
    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS vector')
