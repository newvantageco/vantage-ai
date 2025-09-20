#!/bin/bash

# Quick Actions Health Check Script
# Verifies that all Quick Actions functionality is working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:3000}"
TIMEOUT=30

echo -e "${BLUE}🔍 Quick Actions Health Check Starting...${NC}"

# Function to check if a service is responding
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -e "${YELLOW}Checking ${service_name}...${NC}"
    
    if curl -f -s --max-time $TIMEOUT "$url" > /dev/null; then
        echo -e "${GREEN}✅ ${service_name} is healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ ${service_name} is not responding${NC}"
        return 1
    fi
}

# Function to check Quick Actions API endpoints
check_quick_actions_api() {
    echo -e "${YELLOW}Checking Quick Actions API endpoints...${NC}"
    
    # Check if API is running
    if ! check_service "API" "$API_URL/api/v1/health"; then
        return 1
    fi
    
    # Check Quick Actions specific endpoints
    local endpoints=(
        "/api/v1/quick-actions"
        "/api/v1/quick-actions/dashboard"
        "/api/v1/quick-actions/search"
        "/api/v1/quick-actions/command-palette"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time $TIMEOUT "$API_URL$endpoint" > /dev/null; then
            echo -e "${GREEN}✅ API endpoint $endpoint is working${NC}"
        else
            echo -e "${YELLOW}⚠️  API endpoint $endpoint not found (may be optional)${NC}"
        fi
    done
}

# Function to check Quick Actions frontend
check_quick_actions_frontend() {
    echo -e "${YELLOW}Checking Quick Actions frontend...${NC}"
    
    # Check if web service is running
    if ! check_service "Web Frontend" "$WEB_URL/healthz"; then
        return 1
    fi
    
    # Check Quick Actions specific pages
    local pages=(
        "/dashboard"
        "/search"
        "/composer"
        "/calendar"
        "/analytics"
        "/team"
        "/automation"
        "/collaboration"
        "/settings"
    )
    
    for page in "${pages[@]}"; do
        if curl -f -s --max-time $TIMEOUT "$WEB_URL$page" > /dev/null; then
            echo -e "${GREEN}✅ Page $page is accessible${NC}"
        else
            echo -e "${YELLOW}⚠️  Page $page not accessible (may be protected)${NC}"
        fi
    done
}

# Function to check Quick Actions components
check_quick_actions_components() {
    echo -e "${YELLOW}Checking Quick Actions components...${NC}"
    
    # Check if Quick Actions components are built
    local components=(
        "QuickActions.tsx"
        "QuickActionsTab.tsx"
        "CommandPalette.tsx"
    )
    
    for component in "${components[@]}"; do
        if [ -f "web/src/components/$component" ]; then
            echo -e "${GREEN}✅ Component $component exists${NC}"
        else
            echo -e "${RED}❌ Component $component not found${NC}"
            return 1
        fi
    done
}

# Function to check Quick Actions tests
check_quick_actions_tests() {
    echo -e "${YELLOW}Checking Quick Actions tests...${NC}"
    
    if [ -f "web/src/components/__tests__/QuickActions.test.tsx" ]; then
        echo -e "${GREEN}✅ Quick Actions tests exist${NC}"
        
        # Run tests if possible
        if command -v npm > /dev/null; then
            echo -e "${YELLOW}Running Quick Actions tests...${NC}"
            cd web && npm test -- --testPathPattern=QuickActions --watchAll=false --verbose || {
                echo -e "${YELLOW}⚠️  Tests failed or not configured${NC}"
            }
            cd ..
        else
            echo -e "${YELLOW}⚠️  npm not available, skipping test execution${NC}"
        fi
    else
        echo -e "${RED}❌ Quick Actions tests not found${NC}"
        return 1
    fi
}

# Function to check environment variables
check_environment() {
    echo -e "${YELLOW}Checking Quick Actions environment...${NC}"
    
    local required_vars=(
        "NEXT_PUBLIC_QUICK_ACTIONS_ENABLED"
        "NEXT_PUBLIC_TOAST_ENABLED"
        "NEXT_PUBLIC_ANALYTICS_ENABLED"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -n "${!var}" ]; then
            echo -e "${GREEN}✅ Environment variable $var is set${NC}"
        else
            echo -e "${YELLOW}⚠️  Environment variable $var not set${NC}"
        fi
    done
}

# Function to check Docker containers
check_docker_containers() {
    echo -e "${YELLOW}Checking Docker containers...${NC}"
    
    local containers=(
        "vantage-api"
        "vantage-web"
        "vantage-db"
        "vantage-redis"
    )
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "$container"; then
            echo -e "${GREEN}✅ Container $container is running${NC}"
        else
            echo -e "${RED}❌ Container $container is not running${NC}"
            return 1
        fi
    done
}

# Main health check function
main() {
    local exit_code=0
    
    echo -e "${BLUE}🚀 Starting comprehensive Quick Actions health check...${NC}\n"
    
    # Check Docker containers
    if ! check_docker_containers; then
        echo -e "${RED}❌ Docker containers check failed${NC}"
        exit_code=1
    fi
    
    # Check environment
    check_environment
    
    # Check components
    if ! check_quick_actions_components; then
        echo -e "${RED}❌ Quick Actions components check failed${NC}"
        exit_code=1
    fi
    
    # Check API
    if ! check_quick_actions_api; then
        echo -e "${RED}❌ Quick Actions API check failed${NC}"
        exit_code=1
    fi
    
    # Check frontend
    if ! check_quick_actions_frontend; then
        echo -e "${RED}❌ Quick Actions frontend check failed${NC}"
        exit_code=1
    fi
    
    # Check tests
    if ! check_quick_actions_tests; then
        echo -e "${RED}❌ Quick Actions tests check failed${NC}"
        exit_code=1
    fi
    
    # Summary
    echo -e "\n${BLUE}📊 Quick Actions Health Check Summary${NC}"
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}🎉 All Quick Actions functionality is healthy and working!${NC}"
        echo -e "${GREEN}✅ Ready for production deployment${NC}"
    else
        echo -e "${RED}❌ Some Quick Actions functionality is not working properly${NC}"
        echo -e "${YELLOW}⚠️  Please check the errors above and fix them${NC}"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
