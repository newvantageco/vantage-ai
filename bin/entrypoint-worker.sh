#!/bin/bash
set -e

echo "👷 Starting VANTAGE AI Celery Worker..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python scripts/wait-for-db.py wait-only

# Ensure migrations are up to date
echo "🔄 Ensuring database migrations are up to date..."
alembic upgrade head

# Start Celery worker
echo "🚀 Starting Celery worker..."
exec celery -A app.workers.celery_app worker -l INFO
