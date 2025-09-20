#!/bin/bash
echo "📊 VANTAGE AI Performance Monitoring"

# Get container stats
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" vantage-api-prod vantage-web-prod vantage-db-prod vantage-redis-prod

# Test API response times
echo "🔍 Testing API response times..."
time curl -s -o /dev/null -w "Health: %{time_total}s\n" http://localhost:8000/api/v1/health
time curl -s -o /dev/null -w "Dashboard: %{time_total}s\n" http://localhost:8000/api/v1/dashboard
