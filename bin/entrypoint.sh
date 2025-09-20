#!/bin/bash
set -e

echo "🚀 Starting VANTAGE AI API..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python scripts/wait-for-db.py wait-only

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start the API server
echo "🌐 Starting API server..."
echo "Running: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
