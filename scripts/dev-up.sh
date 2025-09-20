#!/bin/bash
# VANTAGE AI Development Environment Startup Script

set -e

echo "🚀 Starting VANTAGE AI Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.sample .env
    echo "⚠️  Please edit .env file with your actual configuration values"
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis

# Start services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python scripts/wait-for-db.py wait-only

# Start API service
echo "🔧 Starting API service..."
docker-compose -f docker-compose.dev.yml up -d api

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
timeout=60
counter=0
while ! curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        echo "❌ API failed to start within $timeout seconds"
        exit 1
    fi
    echo "Waiting for API... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

# Start Celery workers
echo "👷 Starting Celery workers..."
docker-compose -f docker-compose.dev.yml up -d celery celery-beat

# Start web frontend
echo "🌐 Starting web frontend..."
docker-compose -f docker-compose.dev.yml up -d web

# Optional: Start nginx (uncomment if needed)
# echo "🔀 Starting nginx..."
# docker-compose -f docker-compose.dev.yml --profile nginx up -d nginx

echo "✅ VANTAGE AI Development Environment is ready!"
echo ""
echo "📊 Services:"
echo "  - API: http://localhost:8000"
echo "  - Web: http://localhost:3000"
echo "  - Database: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "🔍 Health checks:"
echo "  - API Health: http://localhost:8000/api/v1/health"
echo "  - Web Health: http://localhost:3000"
echo ""
echo "📝 Logs:"
echo "  - View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  - API logs: docker-compose -f docker-compose.dev.yml logs -f api"
echo "  - Web logs: docker-compose -f docker-compose.dev.yml logs -f web"
echo ""
echo "🛑 To stop: docker-compose -f docker-compose.dev.yml down"
