#!/bin/bash

# =============================================================================
# VANTAGE AI - Monitoring Startup Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 Starting VANTAGE AI Monitoring Stack${NC}"
echo -e "${BLUE}======================================${NC}"

# Check if main services are running
if ! docker compose ps | grep -q "vantage-api-prod"; then
    echo -e "${RED}❌ Main VANTAGE AI services not running!${NC}"
    echo -e "${YELLOW}Please start main services first: ./start-production.sh${NC}"
    exit 1
fi

# Start monitoring services
echo -e "${YELLOW}🐳 Starting monitoring services...${NC}"
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for monitoring services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${YELLOW}🔍 Checking monitoring service health...${NC}"

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus is healthy${NC}"
else
    echo -e "${RED}❌ Prometheus health check failed${NC}"
fi

# Check Grafana
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana is healthy${NC}"
else
    echo -e "${RED}❌ Grafana health check failed${NC}"
fi

# Check Jaeger
if curl -f http://localhost:16686 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Jaeger is healthy${NC}"
else
    echo -e "${RED}❌ Jaeger health check failed${NC}"
fi

echo -e "${GREEN}🎉 VANTAGE AI Monitoring Stack Started!${NC}"
echo -e "${BLUE}Prometheus: http://localhost:9090${NC}"
echo -e "${BLUE}Grafana: http://localhost:3001 (admin/admin123)${NC}"
echo -e "${BLUE}Jaeger: http://localhost:16686${NC}"
echo -e "${BLUE}AlertManager: http://localhost:9093${NC}"
