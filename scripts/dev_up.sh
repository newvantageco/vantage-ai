#!/bin/bash

# Vantage AI - Development Environment Startup Script
# This script starts all services using Docker Compose

set -e

echo "🚀 Starting Vantage AI development environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your actual credentials before continuing."
    echo "   See infra/readme.md for detailed setup instructions."
    read -p "Press Enter to continue with default values, or Ctrl+C to exit and configure .env first..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start services
echo "🐳 Starting Docker services..."
docker compose -f infra/docker-compose.dev.yml up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."

# Wait for API health check
echo "   Checking API health..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "   ✅ API is healthy"
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "   ⚠️  API health check timed out, but services are starting..."
fi

# Wait for web service
echo "   Checking web service..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo "   ✅ Web service is healthy"
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "   ⚠️  Web service health check timed out, but services are starting..."
fi

echo ""
echo "🎉 Development environment is starting up!"
echo ""
echo "📱 Web App:     http://localhost:3000"
echo "🔧 API:         http://localhost:8000"
echo "🏥 API Health:  http://localhost:8000/api/v1/health"
echo ""
echo "📊 To view logs:"
echo "   docker compose -f infra/docker-compose.dev.yml logs -f [service_name]"
echo ""
echo "🛑 To stop:     ./scripts/dev_down.sh"
echo ""

# Show running containers
echo "🐳 Running containers:"
docker compose -f infra/docker-compose.dev.yml ps
