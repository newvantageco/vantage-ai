# Migration History and Safety Documentation

This document tracks the migration history and identifies superseded migrations with destructive operations.

## Migration Safety Policy

- **No destructive operations** in production migrations
- **Additive-only approach** - only create, never drop
- **Backward compatibility** - maintain existing data structures
- **Safe rollbacks** - downgrade operations are safe

## Superseded Migrations (DESTRUCTIVE - DO NOT USE)

### ⚠️ Migration 0004_billing_models.py (SUPERSEDED)
- **Status**: SUPERSEDED by 0011_safe_billing_models.py
- **Reason**: Contains destructive DROP operations in downgrade()
- **Destructive Operations**:
  - `DROP TABLE organization_billing`
  - `DROP TYPE billing_status CASCADE`
  - `DROP TYPE plan_tier CASCADE`
- **Safe Alternative**: Use migration 0011_safe_billing_models.py

### ⚠️ Migration 0005_templates_conversations.py (SUPERSEDED)
- **Status**: SUPERSEDED by 0012_safe_templates_conversations.py
- **Reason**: Contains destructive DROP operations in downgrade()
- **Destructive Operations**:
  - `DROP TABLE messages`
  - `DROP TABLE conversations`
  - `DROP TABLE template_usage`
  - `DROP TABLE asset_templates`
  - `DROP TYPE template_type`
- **Safe Alternative**: Use migration 0012_safe_templates_conversations.py

### ⚠️ Migration 0009_ai_budget.py (SUPERSEDED)
- **Status**: SUPERSEDED by 0013_safe_ai_budget.py
- **Reason**: Contains destructive DROP operations in downgrade()
- **Destructive Operations**:
  - `DROP TABLE ai_budgets`
- **Safe Alternative**: Use migration 0013_safe_ai_budget.py

### ⚠️ Migration 0010_enhanced_billing.py (SUPERSEDED)
- **Status**: SUPERSEDED by 0011_safe_billing_models.py
- **Reason**: Contains destructive DROP operations in downgrade()
- **Destructive Operations**:
  - `DROP TABLE billing_history`
  - `DROP TABLE coupons`
  - Multiple `DROP COLUMN` operations on `organization_billing`
  - `DROP TYPE plan_tier CASCADE`
- **Safe Alternative**: Use migration 0011_safe_billing_models.py

## Safe Migrations (RECOMMENDED)

### ✅ Migration 0011_safe_billing_models.py
- **Status**: SAFE - Additive only
- **Purpose**: Ensures billing models exist without data loss
- **Operations**: CREATE TABLE IF NOT EXISTS, ADD COLUMN IF NOT EXISTS
- **Rollback**: Safe (no destructive operations)

### ✅ Migration 0012_safe_templates_conversations.py
- **Status**: SAFE - Additive only
- **Purpose**: Ensures templates and conversations tables exist without data loss
- **Operations**: CREATE TABLE IF NOT EXISTS, CREATE INDEX IF NOT EXISTS
- **Rollback**: Safe (no destructive operations)

### ✅ Migration 0013_safe_ai_budget.py
- **Status**: SAFE - Additive only
- **Purpose**: Ensures AI budget tracking exists without data loss
- **Operations**: CREATE TABLE IF NOT EXISTS, CREATE INDEX IF NOT EXISTS
- **Rollback**: Safe (no destructive operations)

## Migration Execution Order

```bash
# Safe migration sequence (recommended)
alembic upgrade 0011_safe_billing_models
alembic upgrade 0012_safe_templates_conversations
alembic upgrade 0013_safe_ai_budget
```

## SQL Preview

Before applying the safe migrations, here's what SQL will be executed:

### Migration 0011_safe_billing_models.py
```sql
-- Create enums if they don't exist
CREATE TYPE IF NOT EXISTS plan_tier AS ENUM ('starter', 'growth', 'pro');
CREATE TYPE IF NOT EXISTS billing_status AS ENUM ('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing');

-- Create organization_billing table if it doesn't exist
CREATE TABLE IF NOT EXISTS organization_billing (
    id VARCHAR(36) NOT NULL,
    org_id VARCHAR(36) NOT NULL,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    plan plan_tier NOT NULL DEFAULT 'starter',
    status billing_status NOT NULL DEFAULT 'active',
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    trial_start TIMESTAMP,
    trial_end TIMESTAMP,
    trial_used BOOLEAN NOT NULL DEFAULT false,
    coupon_code VARCHAR(100),
    coupon_discount_percent INTEGER,
    coupon_discount_amount_cents INTEGER,
    coupon_expires_at TIMESTAMP,
    last_payment_date TIMESTAMP,
    last_payment_amount_cents INTEGER,
    next_payment_date TIMESTAMP,
    next_payment_amount_cents INTEGER,
    notes TEXT,
    PRIMARY KEY (id),
    UNIQUE (org_id),
    FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_organization_billing_org_id ON organization_billing (org_id);
CREATE INDEX IF NOT EXISTS ix_organization_billing_stripe_customer_id ON organization_billing (stripe_customer_id);
CREATE INDEX IF NOT EXISTS ix_organization_billing_stripe_subscription_id ON organization_billing (stripe_subscription_id);
CREATE INDEX IF NOT EXISTS ix_organization_billing_coupon_code ON organization_billing (coupon_code);

-- Create coupons table if it doesn't exist
CREATE TABLE IF NOT EXISTS coupons (
    id VARCHAR(36) NOT NULL,
    code VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL,
    discount_value INTEGER NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP,
    max_uses INTEGER,
    used_count INTEGER NOT NULL DEFAULT 0,
    applicable_plans TEXT,
    min_amount_cents INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_coupons_code ON coupons (code);
CREATE INDEX IF NOT EXISTS ix_coupons_is_active ON coupons (is_active);

-- Create billing_history table if it doesn't exist
CREATE TABLE IF NOT EXISTS billing_history (
    id VARCHAR(36) NOT NULL,
    org_id VARCHAR(36) NOT NULL,
    stripe_payment_intent_id VARCHAR(255),
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'usd',
    description VARCHAR(500) NOT NULL,
    plan plan_tier NOT NULL,
    status VARCHAR(20) NOT NULL,
    coupon_code VARCHAR(100),
    discount_amount_cents INTEGER,
    created_at TIMESTAMP NOT NULL,
    processed_at TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_billing_history_org_id ON billing_history (org_id);
CREATE INDEX IF NOT EXISTS ix_billing_history_stripe_payment_intent_id ON billing_history (stripe_payment_intent_id);
```

### Migration 0012_safe_templates_conversations.py
```sql
-- Create template_type enum if it doesn't exist
CREATE TYPE IF NOT EXISTS template_type AS ENUM ('image', 'video');

-- Create asset_templates table if it doesn't exist
CREATE TABLE IF NOT EXISTS asset_templates (
    id VARCHAR(36) NOT NULL,
    org_id VARCHAR(36),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type template_type NOT NULL,
    spec JSON NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL,
    created_by VARCHAR(36),
    PRIMARY KEY (id),
    UNIQUE (org_id, created_by),
    FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE,
    FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_asset_templates_org_id ON asset_templates (org_id);

-- Create template_usage table if it doesn't exist
CREATE TABLE IF NOT EXISTS template_usage (
    id VARCHAR(36) NOT NULL,
    template_id VARCHAR(36) NOT NULL,
    org_id VARCHAR(36) NOT NULL,
    content_item_id VARCHAR(36),
    used_at TIMESTAMP NOT NULL,
    inputs JSON,
    PRIMARY KEY (id),
    FOREIGN KEY(template_id) REFERENCES asset_templates (id) ON DELETE CASCADE,
    FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE,
    FOREIGN KEY(content_item_id) REFERENCES content_items (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_template_usage_template_id ON template_usage (template_id);
CREATE INDEX IF NOT EXISTS ix_template_usage_org_id ON template_usage (org_id);
CREATE INDEX IF NOT EXISTS ix_template_usage_content_item_id ON template_usage (content_item_id);

-- Create conversations table if it doesn't exist
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(36) NOT NULL,
    org_id VARCHAR(36) NOT NULL,
    channel VARCHAR(32) NOT NULL,
    peer_id VARCHAR(255) NOT NULL,
    last_message_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_conversations_org_id ON conversations (org_id);
CREATE INDEX IF NOT EXISTS ix_conversations_peer_id ON conversations (peer_id);

-- Create messages table if it doesn't exist
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(36) NOT NULL,
    conversation_id VARCHAR(36) NOT NULL,
    direction VARCHAR(16) NOT NULL,
    text TEXT,
    media_url VARCHAR(500),
    metadata JSON,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id);
```

### Migration 0013_safe_ai_budget.py
```sql
-- Create ai_budgets table if it doesn't exist
CREATE TABLE IF NOT EXISTS ai_budgets (
    id VARCHAR(36) NOT NULL,
    org_id VARCHAR(36) NOT NULL,
    daily_token_limit INTEGER NOT NULL DEFAULT 100000,
    daily_cost_limit_gbp FLOAT NOT NULL DEFAULT 50.0,
    current_date DATE NOT NULL DEFAULT CURRENT_DATE,
    tokens_used_today INTEGER NOT NULL DEFAULT 0,
    cost_gbp_today FLOAT NOT NULL DEFAULT 0.0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_ai_budgets_org_id ON ai_budgets (org_id);
```

## Best Practices

1. **Always use safe migrations** for production deployments
2. **Test migrations** in staging environment first
3. **Backup database** before applying migrations
4. **Monitor migration progress** and rollback if issues occur
5. **Document any custom migration logic** for future reference

## Emergency Procedures

If a destructive migration has been applied:

1. **Stop all application traffic** immediately
2. **Restore from backup** if data loss is detected
3. **Apply safe migrations** to restore functionality
4. **Verify data integrity** before resuming operations
5. **Update deployment procedures** to prevent future issues
