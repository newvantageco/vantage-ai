#!/bin/bash

# Vantage AI - Development Environment Shutdown Script
# This script stops all services and cleans up

set -e

echo "🛑 Stopping Vantage AI development environment..."

# Stop and remove containers, networks, and volumes
echo "🐳 Stopping Docker services and cleaning up..."
docker compose -f infra/docker-compose.dev.yml down -v

# Remove any dangling images (optional)
echo "🧹 Cleaning up dangling images..."
docker image prune -f

echo ""
echo "✅ Development environment stopped and cleaned up!"
echo ""
echo "💡 To start again: ./scripts/dev_up.sh"
