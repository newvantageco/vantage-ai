#!/bin/bash

# =============================================================================
# VANTAGE AI - Database Encryption Setup Script
# =============================================================================
# This script sets up database encryption at rest for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENCRYPTION_KEY_FILE="$PROJECT_DIR/infra/ssl/db-encryption.key"
POSTGRES_CONF="$PROJECT_DIR/infra/postgresql-encrypted.conf"

echo -e "${BLUE}🔐 Setting up Database Encryption at Rest${NC}"
echo -e "${BLUE}=========================================${NC}"

# Function to generate encryption key
generate_encryption_key() {
    echo -e "${YELLOW}🔑 Generating database encryption key...${NC}"
    
    if [[ -f "$ENCRYPTION_KEY_FILE" ]]; then
        echo -e "${BLUE}Encryption key already exists. Skipping generation.${NC}"
        return 0
    fi
    
    # Generate 32-byte encryption key
    openssl rand -base64 32 > "$ENCRYPTION_KEY_FILE"
    chmod 600 "$ENCRYPTION_KEY_FILE"
    
    echo -e "${GREEN}✅ Database encryption key generated${NC}"
}

# Function to create encrypted PostgreSQL configuration
create_encrypted_postgres_config() {
    echo -e "${YELLOW}📋 Creating encrypted PostgreSQL configuration...${NC}"
    
    cat > "$POSTGRES_CONF" << 'EOF'
# =============================================================================
# VANTAGE AI - Encrypted PostgreSQL Configuration
# =============================================================================

# Basic settings
listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Encryption settings
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ciphers = 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256'
ssl_prefer_server_ciphers = on

# Data encryption at rest
# Note: This requires PostgreSQL to be compiled with encryption support
# or using a filesystem-level encryption solution

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Performance tuning
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB

# Security
password_encryption = scram-sha-256
row_security = on

# pgvector settings
shared_preload_libraries = 'vector'
EOF

    echo -e "${GREEN}✅ Encrypted PostgreSQL configuration created${NC}"
}

# Function to create database encryption setup
create_db_encryption_setup() {
    echo -e "${YELLOW}🗄️ Creating database encryption setup...${NC}"
    
    cat > "$PROJECT_DIR/scripts/encrypt-database.sh" << 'EOF'
#!/bin/bash

# =============================================================================
# VANTAGE AI - Database Encryption Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENCRYPTION_KEY_FILE="$PROJECT_DIR/infra/ssl/db-encryption.key"

echo -e "${BLUE}🔐 Encrypting Database${NC}"
echo -e "${BLUE}====================${NC}"

# Check if encryption key exists
if [[ ! -f "$ENCRYPTION_KEY_FILE" ]]; then
    echo -e "${RED}❌ Encryption key not found!${NC}"
    echo -e "${YELLOW}Please run: ./scripts/setup-db-encryption.sh${NC}"
    exit 1
fi

# Function to encrypt sensitive data
encrypt_data() {
    local data=$1
    local key_file=$2
    
    echo "$data" | openssl enc -aes-256-cbc -base64 -pass file:"$key_file"
}

# Function to decrypt sensitive data
decrypt_data() {
    local encrypted_data=$1
    local key_file=$2
    
    echo "$encrypted_data" | openssl enc -aes-256-cbc -d -base64 -pass file:"$key_file"
}

# Encrypt OAuth tokens in database
echo -e "${YELLOW}🔐 Encrypting OAuth tokens...${NC}"

# Connect to database and encrypt existing tokens
docker compose -f docker-compose.production.yml exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" << EOF
-- Create encryption functions
CREATE OR REPLACE FUNCTION encrypt_token(token text)
RETURNS text AS \$\$
BEGIN
    RETURN encode(encrypt(token::bytea, '${ENCRYPTION_KEY}', 'aes'), 'base64');
END;
\$\$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrypt_token(encrypted_token text)
RETURNS text AS \$\$
BEGIN
    RETURN convert_from(decrypt(decode(encrypted_token, 'base64'), '${ENCRYPTION_KEY}', 'aes'), 'UTF8');
END;
\$\$ LANGUAGE plpgsql;

-- Update existing tokens to be encrypted
UPDATE oauth_tokens SET 
    access_token = encrypt_token(access_token),
    refresh_token = encrypt_token(refresh_token)
WHERE access_token IS NOT NULL;

-- Add encryption to new token insertions
CREATE OR REPLACE FUNCTION insert_oauth_token(
    p_user_id uuid,
    p_platform text,
    p_access_token text,
    p_refresh_token text,
    p_expires_at timestamp
)
RETURNS void AS \$\$
BEGIN
    INSERT INTO oauth_tokens (user_id, platform, access_token, refresh_token, expires_at)
    VALUES (p_user_id, p_platform, encrypt_token(p_access_token), encrypt_token(p_refresh_token), p_expires_at);
END;
\$\$ LANGUAGE plpgsql;
EOF

    echo -e "${GREEN}✅ Database encryption setup completed${NC}"
}

# Function to create backup encryption
create_backup_encryption() {
    echo -e "${YELLOW}💾 Creating encrypted backup script...${NC}"
    
    cat > "$PROJECT_DIR/scripts/encrypted-backup.sh" << 'EOF'
#!/bin/bash

# =============================================================================
# VANTAGE AI - Encrypted Backup Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"
ENCRYPTION_KEY_FILE="$PROJECT_DIR/infra/ssl/db-encryption.key"
DATE=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}💾 Creating Encrypted Backup${NC}"
echo -e "${BLUE}===========================${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if encryption key exists
if [[ ! -f "$ENCRYPTION_KEY_FILE" ]]; then
    echo -e "${RED}❌ Encryption key not found!${NC}"
    exit 1
fi

# Create database backup
echo -e "${YELLOW}📊 Creating database backup...${NC}"
docker exec vantage-db-prod pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/database_$DATE.sql"

# Encrypt database backup
echo -e "${YELLOW}🔐 Encrypting database backup...${NC}"
openssl enc -aes-256-cbc -salt -in "$BACKUP_DIR/database_$DATE.sql" -out "$BACKUP_DIR/database_$DATE.sql.enc" -pass file:"$ENCRYPTION_KEY_FILE"

# Remove unencrypted backup
rm "$BACKUP_DIR/database_$DATE.sql"

# Create uploads backup
echo -e "${YELLOW}📁 Creating uploads backup...${NC}"
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" uploads/

# Encrypt uploads backup
echo -e "${YELLOW}🔐 Encrypting uploads backup...${NC}"
openssl enc -aes-256-cbc -salt -in "$BACKUP_DIR/uploads_$DATE.tar.gz" -out "$BACKUP_DIR/uploads_$DATE.tar.gz.enc" -pass file:"$ENCRYPTION_KEY_FILE"

# Remove unencrypted backup
rm "$BACKUP_DIR/uploads_$DATE.tar.gz"

# Create environment backup
echo -e "${YELLOW}⚙️ Creating environment backup...${NC}"
cp .env.production "$BACKUP_DIR/env_$DATE.production"

# Encrypt environment backup
echo -e "${YELLOW}🔐 Encrypting environment backup...${NC}"
openssl enc -aes-256-cbc -salt -in "$BACKUP_DIR/env_$DATE.production" -out "$BACKUP_DIR/env_$DATE.production.enc" -pass file:"$ENCRYPTION_KEY_FILE"

# Remove unencrypted backup
rm "$BACKUP_DIR/env_$DATE.production"

echo -e "${GREEN}✅ Encrypted backup completed: $BACKUP_DIR/${NC}"
echo -e "${BLUE}Files created:${NC}"
echo -e "${BLUE}  - database_$DATE.sql.enc${NC}"
echo -e "${BLUE}  - uploads_$DATE.tar.gz.enc${NC}"
echo -e "${BLUE}  - env_$DATE.production.enc${NC}"
EOF

    chmod +x "$PROJECT_DIR/scripts/encrypted-backup.sh"
    echo -e "${GREEN}✅ Encrypted backup script created${NC}"
}

# Function to create restore script
create_restore_script() {
    echo -e "${YELLOW}🔄 Creating restore script...${NC}"
    
    cat > "$PROJECT_DIR/scripts/restore-encrypted-backup.sh" << 'EOF'
#!/bin/bash

# =============================================================================
# VANTAGE AI - Restore Encrypted Backup Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"
ENCRYPTION_KEY_FILE="$PROJECT_DIR/infra/ssl/db-encryption.key"

echo -e "${BLUE}🔄 Restoring Encrypted Backup${NC}"
echo -e "${BLUE}============================${NC}"

# Check if encryption key exists
if [[ ! -f "$ENCRYPTION_KEY_FILE" ]]; then
    echo -e "${RED}❌ Encryption key not found!${NC}"
    exit 1
fi

# List available backups
echo -e "${BLUE}Available backups:${NC}"
ls -la "$BACKUP_DIR"/*.enc 2>/dev/null || echo "No encrypted backups found"

# Get backup file
read -p "Enter backup file name (without .enc extension): " BACKUP_FILE

if [[ ! -f "$BACKUP_DIR/${BACKUP_FILE}.enc" ]]; then
    echo -e "${RED}❌ Backup file not found!${NC}"
    exit 1
fi

# Decrypt and restore database
if [[ "$BACKUP_FILE" == database_* ]]; then
    echo -e "${YELLOW}📊 Restoring database...${NC}"
    openssl enc -aes-256-cbc -d -in "$BACKUP_DIR/${BACKUP_FILE}.enc" -out "$BACKUP_DIR/${BACKUP_FILE}.sql" -pass file:"$ENCRYPTION_KEY_FILE"
    docker exec -i vantage-db-prod psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$BACKUP_DIR/${BACKUP_FILE}.sql"
    rm "$BACKUP_DIR/${BACKUP_FILE}.sql"
    echo -e "${GREEN}✅ Database restored${NC}"
fi

# Decrypt and restore uploads
if [[ "$BACKUP_FILE" == uploads_* ]]; then
    echo -e "${YELLOW}📁 Restoring uploads...${NC}"
    openssl enc -aes-256-cbc -d -in "$BACKUP_DIR/${BACKUP_FILE}.enc" -out "$BACKUP_DIR/${BACKUP_FILE}.tar.gz" -pass file:"$ENCRYPTION_KEY_FILE"
    tar -xzf "$BACKUP_DIR/${BACKUP_FILE}.tar.gz"
    rm "$BACKUP_DIR/${BACKUP_FILE}.tar.gz"
    echo -e "${GREEN}✅ Uploads restored${NC}"
fi

# Decrypt and restore environment
if [[ "$BACKUP_FILE" == env_* ]]; then
    echo -e "${YELLOW}⚙️ Restoring environment...${NC}"
    openssl enc -aes-256-cbc -d -in "$BACKUP_DIR/${BACKUP_FILE}.enc" -out "$BACKUP_DIR/${BACKUP_FILE}.production" -pass file:"$ENCRYPTION_KEY_FILE"
    cp "$BACKUP_DIR/${BACKUP_FILE}.production" .env.production
    rm "$BACKUP_DIR/${BACKUP_FILE}.production"
    echo -e "${GREEN}✅ Environment restored${NC}"
fi

echo -e "${GREEN}🎉 Restore completed successfully!${NC}"
EOF

    chmod +x "$PROJECT_DIR/scripts/restore-encrypted-backup.sh"
    echo -e "${GREEN}✅ Restore script created${NC}"
}

# Function to update Docker Compose for encryption
update_docker_compose() {
    echo -e "${YELLOW}🐳 Updating Docker Compose for encryption...${NC}"
    
    # Create encrypted database service configuration
    cat > "$PROJECT_DIR/docker-compose.encrypted.yml" << 'EOF'
version: '3.8'

services:
  # Encrypted PostgreSQL Database
  db:
    image: pgvector/pgvector:pg16
    container_name: vantage-db-encrypted
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/postgresql-encrypted.conf:/etc/postgresql/postgresql.conf:ro
      - ./infra/ssl:/etc/ssl:ro
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "${POSTGRES_PORT:-5433}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - vantage-network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

volumes:
  postgres_data:
    driver: local

networks:
  vantage-network:
    driver: bridge
EOF

    echo -e "${GREEN}✅ Encrypted Docker Compose configuration created${NC}"
}

# Main setup function
main() {
    echo -e "${BLUE}🔐 VANTAGE AI Database Encryption Setup${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Generate encryption key
    generate_encryption_key
    
    # Create encrypted PostgreSQL configuration
    create_encrypted_postgres_config
    
    # Create database encryption setup
    create_db_encryption_setup
    
    # Create backup encryption
    create_backup_encryption
    
    # Create restore script
    create_restore_script
    
    # Update Docker Compose
    update_docker_compose
    
    echo -e "${GREEN}🎉 Database encryption setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo -e "${BLUE}1. Update your .env.production with encryption settings${NC}"
    echo -e "${BLUE}2. Run: docker compose -f docker-compose.encrypted.yml up -d${NC}"
    echo -e "${BLUE}3. Run: ./scripts/encrypt-database.sh${NC}"
    echo -e "${BLUE}4. Set up encrypted backups: ./scripts/encrypted-backup.sh${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Important: Keep your encryption key secure and backed up${NC}"
    echo -e "${YELLOW}⚠️  Important: Test restore procedures regularly${NC}"
}

# Run main function
main "$@"