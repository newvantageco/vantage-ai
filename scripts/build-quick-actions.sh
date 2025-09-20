#!/bin/bash

# Quick Actions Docker Build Script
# Builds and tests Docker containers with Quick Actions functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.quick-actions.yml"
BUILD_TARGET=${1:-"all"}
CLEAN_BUILD=${2:-"false"}

echo -e "${BLUE}🚀 Quick Actions Docker Build Script${NC}"
echo -e "${BLUE}=====================================${NC}\n"

# Function to print section headers
print_section() {
    echo -e "\n${MAGENTA}📦 $1${NC}"
    echo -e "${MAGENTA}$(printf '=%.0s' {1..50})${NC}"
}

# Function to clean up previous builds
clean_build() {
    print_section "Cleaning Previous Builds"
    
    echo -e "${YELLOW}Stopping existing containers...${NC}"
    docker-compose -f $COMPOSE_FILE down --remove-orphans || true
    
    echo -e "${YELLOW}Removing unused images...${NC}"
    docker image prune -f || true
    
    echo -e "${YELLOW}Removing unused volumes...${NC}"
    docker volume prune -f || true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Function to build specific service
build_service() {
    local service=$1
    local target=${2:-"development"}
    
    print_section "Building $service Service"
    
    echo -e "${YELLOW}Building $service with target: $target${NC}"
    
    if docker-compose -f $COMPOSE_FILE build --no-cache $service; then
        echo -e "${GREEN}✅ $service built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build $service${NC}"
        return 1
    fi
}

# Function to test Quick Actions functionality
test_quick_actions() {
    print_section "Testing Quick Actions Functionality"
    
    echo -e "${YELLOW}Starting services for testing...${NC}"
    docker-compose -f $COMPOSE_FILE up -d db redis api web
    
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 30
    
    echo -e "${YELLOW}Running Quick Actions health check...${NC}"
    if ./scripts/health-check-quick-actions.sh; then
        echo -e "${GREEN}✅ Quick Actions health check passed${NC}"
    else
        echo -e "${RED}❌ Quick Actions health check failed${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Running Quick Actions tests...${NC}"
    if docker-compose -f $COMPOSE_FILE run --rm test-runner; then
        echo -e "${GREEN}✅ Quick Actions tests passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Quick Actions tests failed or not configured${NC}"
    fi
}

# Function to build all services
build_all() {
    print_section "Building All Services"
    
    echo -e "${YELLOW}Building all services with Quick Actions support...${NC}"
    
    if docker-compose -f $COMPOSE_FILE build --no-cache; then
        echo -e "${GREEN}✅ All services built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build some services${NC}"
        return 1
    fi
}

# Function to start services
start_services() {
    print_section "Starting Services"
    
    echo -e "${YELLOW}Starting all services...${NC}"
    
    if docker-compose -f $COMPOSE_FILE up -d; then
        echo -e "${GREEN}✅ All services started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start some services${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 60
    
    echo -e "${GREEN}🎉 Quick Actions services are running!${NC}"
    echo -e "${BLUE}Web Frontend: http://localhost:3000${NC}"
    echo -e "${BLUE}API Backend: http://localhost:8000${NC}"
    echo -e "${BLUE}Database: localhost:5432${NC}"
    echo -e "${BLUE}Redis: localhost:6379${NC}"
}

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage: $0 [BUILD_TARGET] [CLEAN_BUILD]${NC}"
    echo -e "${YELLOW}Build Targets:${NC}"
    echo -e "  all          - Build all services (default)"
    echo -e "  web          - Build only web frontend"
    echo -e "  api          - Build only API backend"
    echo -e "  test         - Build and test Quick Actions"
    echo -e "  start        - Start all services"
    echo -e "  stop         - Stop all services"
    echo -e "  clean        - Clean up and rebuild"
    echo -e ""
    echo -e "${YELLOW}Clean Build:${NC}"
    echo -e "  true         - Clean previous builds first"
    echo -e "  false        - Keep previous builds (default)"
    echo -e ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 all true     # Clean build all services"
    echo -e "  $0 web false    # Build only web frontend"
    echo -e "  $0 test true    # Clean build and test"
    echo -e "  $0 start        # Start all services"
}

# Function to stop services
stop_services() {
    print_section "Stopping Services"
    
    echo -e "${YELLOW}Stopping all services...${NC}"
    
    if docker-compose -f $COMPOSE_FILE down; then
        echo -e "${GREEN}✅ All services stopped successfully${NC}"
    else
        echo -e "${RED}❌ Failed to stop some services${NC}"
        return 1
    fi
}

# Main execution
main() {
    case $BUILD_TARGET in
        "all")
            if [ "$CLEAN_BUILD" = "true" ]; then
                clean_build
            fi
            build_all
            ;;
        "web")
            if [ "$CLEAN_BUILD" = "true" ]; then
                clean_build
            fi
            build_service "web" "development"
            ;;
        "api")
            if [ "$CLEAN_BUILD" = "true" ]; then
                clean_build
            fi
            build_service "api" "production"
            ;;
        "test")
            if [ "$CLEAN_BUILD" = "true" ]; then
                clean_build
            fi
            build_all
            test_quick_actions
            ;;
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "clean")
            clean_build
            build_all
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown build target: $BUILD_TARGET${NC}"
            show_usage
            exit 1
            ;;
    esac
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed. Please install it first.${NC}"
    exit 1
fi

# Run main function
main "$@"
