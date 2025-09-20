#!/bin/bash

# =============================================================================
# VANTAGE AI - Health Check Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏥 VANTAGE AI Health Check${NC}"
echo -e "${BLUE}=========================${NC}"

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ $name: Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Unhealthy${NC}"
        return 1
    fi
}

# Check main services
echo -e "${YELLOW}🔍 Checking main services...${NC}"
check_service "API" "http://localhost/api/v1/health"
check_service "Web" "http://localhost/healthz"

# Check monitoring services
echo -e "${YELLOW}📊 Checking monitoring services...${NC}"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3001/api/health"
check_service "Jaeger" "http://localhost:16686"

# Check database
echo -e "${YELLOW}🗄️ Checking database...${NC}"
if docker exec vantage-db-prod pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database: Healthy${NC}"
else
    echo -e "${RED}❌ Database: Unhealthy${NC}"
fi

# Check Redis
echo -e "${YELLOW}🔴 Checking Redis...${NC}"
if docker exec vantage-redis-prod redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis: Healthy${NC}"
else
    echo -e "${RED}❌ Redis: Unhealthy${NC}"
fi

echo -e "${BLUE}🏥 Health check completed${NC}"
