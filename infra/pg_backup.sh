#!/bin/bash
# PostgreSQL Backup Script for Vantage AI
# Creates timestamped, compressed backups of the database

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/mnt/backups}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-vantage_ai}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp for backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/vantage_ai_backup_${TIMESTAMP}.sql.gz"

# Set PGPASSWORD for non-interactive backup
export PGPASSWORD="$DB_PASSWORD"

echo "🔄 Starting database backup..."
echo "   Database: $DB_NAME"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   User: $DB_USER"
echo "   Output: $BACKUP_FILE"

# Perform the backup with compression
pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --verbose \
    --no-password \
    --format=plain \
    --no-owner \
    --no-privileges \
    --clean \
    --if-exists \
    --create \
    | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ] && [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup completed successfully!"
    echo "   File: $BACKUP_FILE"
    echo "   Size: $BACKUP_SIZE"
    
    # Keep only last 30 days of backups (optional cleanup)
    find "$BACKUP_DIR" -name "vantage_ai_backup_*.sql.gz" -mtime +30 -delete 2>/dev/null || true
    echo "🧹 Cleaned up backups older than 30 days"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Unset password for security
unset PGPASSWORD

echo "🔒 Backup process completed"
