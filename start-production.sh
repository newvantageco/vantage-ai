#!/bin/bash

# =============================================================================
# VANTAGE AI - Production Startup Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting VANTAGE AI Production Environment${NC}"
echo -e "${BLUE}==============================================${NC}"

# Check if .env.production exists
if [[ ! -f ".env.production" ]]; then
    echo -e "${RED}❌ Production environment file not found!${NC}"
    echo -e "${YELLOW}Please run: ./scripts/setup-production.sh${NC}"
    exit 1
fi

# Copy production environment
echo -e "${YELLOW}📋 Setting up environment...${NC}"
cp .env.production .env

# Check if SSL certificates exist
if [[ ! -d "infra/ssl" ]] || [[ ! -f "infra/ssl/cert.pem" ]]; then
    echo -e "${RED}❌ SSL certificates not found!${NC}"
    echo -e "${YELLOW}Please run: ./scripts/setup-ssl.sh${NC}"
    exit 1
fi

# Start services
echo -e "${YELLOW}🐳 Starting Docker services...${NC}"
docker compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 30

# Check service health
echo -e "${YELLOW}🔍 Checking service health...${NC}"

# Check API health
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API health check failed${NC}"
fi

# Check Web health
if curl -f http://localhost:3000/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Web is healthy${NC}"
else
    echo -e "${RED}❌ Web health check failed${NC}"
fi

echo -e "${GREEN}🎉 VANTAGE AI Production Environment Started!${NC}"
echo -e "${BLUE}Web: http://localhost:3000${NC}"
echo -e "${BLUE}API: http://localhost:8000${NC}"
echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
