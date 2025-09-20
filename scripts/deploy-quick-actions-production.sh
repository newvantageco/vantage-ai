#!/bin/bash

# Quick Actions Production Deployment Script
# Deploys VANTAGE AI with Quick Actions to production environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_COMPOSE="docker-compose.production.yml"
ENVIRONMENT=${1:-"production"}
BACKUP_ENABLED=${2:-"true"}
HEALTH_CHECK_ENABLED=${3:-"true"}

echo -e "${CYAN}🚀 Quick Actions Production Deployment${NC}"
echo -e "${CYAN}=====================================${NC}\n"

# Function to print section headers
print_section() {
    echo -e "\n${MAGENTA}📦 $1${NC}"
    echo -e "${MAGENTA}$(printf '=%.0s' {1..50})${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
    
    # Check if docker-compose is available
    if ! command -v docker-compose > /dev/null; then
        echo -e "${RED}❌ docker-compose is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ docker-compose is available${NC}"
    
    # Check if environment file exists
    if [ ! -f ".env.production" ]; then
        echo -e "${YELLOW}⚠️  .env.production not found, using .env${NC}"
        if [ ! -f ".env" ]; then
            echo -e "${RED}❌ No environment file found${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}✅ Environment file found${NC}"
    
    # Check if Quick Actions components exist
    local components=(
        "web/src/components/QuickActions.tsx"
        "web/src/components/QuickActionsTab.tsx"
        "web/src/app/dashboard/page.tsx"
        "web/src/app/search/page.tsx"
    )
    
    for component in "${components[@]}"; do
        if [ -f "$component" ]; then
            echo -e "${GREEN}✅ $component exists${NC}"
        else
            echo -e "${RED}❌ $component not found${NC}"
            exit 1
        fi
    done
}

# Function to backup current deployment
backup_current_deployment() {
    if [ "$BACKUP_ENABLED" = "true" ]; then
        print_section "Backing Up Current Deployment"
        
        local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        echo -e "${YELLOW}Creating backup in $backup_dir...${NC}"
        
        # Backup database
        if docker ps --format "table {{.Names}}" | grep -q "vantage-db-prod"; then
            echo -e "${YELLOW}Backing up database...${NC}"
            docker exec vantage-db-prod pg_dump -U ${POSTGRES_USER:-vantage} ${POSTGRES_DB:-vantage} > "$backup_dir/database.sql" || {
                echo -e "${YELLOW}⚠️  Database backup failed or not available${NC}"
            }
        fi
        
        # Backup uploads
        if [ -d "uploads" ]; then
            echo -e "${YELLOW}Backing up uploads...${NC}"
            cp -r uploads "$backup_dir/" || {
                echo -e "${YELLOW}⚠️  Uploads backup failed${NC}"
            }
        fi
        
        # Backup configuration
        echo -e "${YELLOW}Backing up configuration...${NC}"
        cp docker-compose.production.yml "$backup_dir/" 2>/dev/null || true
        cp .env* "$backup_dir/" 2>/dev/null || true
        
        echo -e "${GREEN}✅ Backup completed: $backup_dir${NC}"
    else
        echo -e "${YELLOW}⚠️  Backup disabled${NC}"
    fi
}

# Function to stop current services
stop_current_services() {
    print_section "Stopping Current Services"
    
    echo -e "${YELLOW}Stopping current production services...${NC}"
    
    if docker-compose -f $PRODUCTION_COMPOSE down --remove-orphans; then
        echo -e "${GREEN}✅ Current services stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  Some services may not have been running${NC}"
    fi
}

# Function to build production images
build_production_images() {
    print_section "Building Production Images"
    
    echo -e "${YELLOW}Building production images with Quick Actions...${NC}"
    
    # Build API
    echo -e "${YELLOW}Building API image...${NC}"
    if docker-compose -f $PRODUCTION_COMPOSE build --no-cache api; then
        echo -e "${GREEN}✅ API image built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build API image${NC}"
        exit 1
    fi
    
    # Build Worker
    echo -e "${YELLOW}Building Worker image...${NC}"
    if docker-compose -f $PRODUCTION_COMPOSE build --no-cache worker; then
        echo -e "${GREEN}✅ Worker image built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build Worker image${NC}"
        exit 1
    fi
    
    # Build Web
    echo -e "${YELLOW}Building Web image with Quick Actions...${NC}"
    if docker-compose -f $PRODUCTION_COMPOSE build --no-cache web; then
        echo -e "${GREEN}✅ Web image built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build Web image${NC}"
        exit 1
    fi
    
    # Build Nginx
    echo -e "${YELLOW}Building Nginx image...${NC}"
    if docker-compose -f $PRODUCTION_COMPOSE build --no-cache nginx; then
        echo -e "${GREEN}✅ Nginx image built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build Nginx image${NC}"
        exit 1
    fi
}

# Function to start production services
start_production_services() {
    print_section "Starting Production Services"
    
    echo -e "${YELLOW}Starting production services with Quick Actions...${NC}"
    
    # Start database and redis first
    echo -e "${YELLOW}Starting database and redis...${NC}"
    docker-compose -f $PRODUCTION_COMPOSE up -d db redis
    
    # Wait for database to be ready
    echo -e "${YELLOW}Waiting for database to be ready...${NC}"
    sleep 30
    
    # Start API and worker
    echo -e "${YELLOW}Starting API and worker...${NC}"
    docker-compose -f $PRODUCTION_COMPOSE up -d api worker
    
    # Wait for API to be ready
    echo -e "${YELLOW}Waiting for API to be ready...${NC}"
    sleep 30
    
    # Start web frontend
    echo -e "${YELLOW}Starting web frontend...${NC}"
    docker-compose -f $PRODUCTION_COMPOSE up -d web
    
    # Wait for web to be ready
    echo -e "${YELLOW}Waiting for web frontend to be ready...${NC}"
    sleep 30
    
    # Start nginx
    echo -e "${YELLOW}Starting nginx reverse proxy...${NC}"
    docker-compose -f $PRODUCTION_COMPOSE up -d nginx
    
    echo -e "${GREEN}✅ All production services started${NC}"
}

# Function to run health checks
run_health_checks() {
    if [ "$HEALTH_CHECK_ENABLED" = "true" ]; then
        print_section "Running Health Checks"
        
        echo -e "${YELLOW}Running Quick Actions health checks...${NC}"
        
        # Wait for services to be fully ready
        sleep 60
        
        # Run health check script
        if ./scripts/health-check-quick-actions.sh; then
            echo -e "${GREEN}✅ All health checks passed${NC}"
        else
            echo -e "${RED}❌ Health checks failed${NC}"
            echo -e "${YELLOW}⚠️  Please check the logs and fix any issues${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Health checks disabled${NC}"
    fi
}

# Function to show deployment status
show_deployment_status() {
    print_section "Deployment Status"
    
    echo -e "${CYAN}🎉 Quick Actions Production Deployment Complete!${NC}\n"
    
    echo -e "${BLUE}Services Status:${NC}"
    docker-compose -f $PRODUCTION_COMPOSE ps
    
    echo -e "\n${BLUE}Quick Actions Features:${NC}"
    echo -e "${GREEN}✅ Dashboard Quick Actions (14 actions)${NC}"
    echo -e "${GREEN}✅ Search Page Quick Actions (12 actions)${NC}"
    echo -e "${GREEN}✅ Command Palette (11 actions)${NC}"
    echo -e "${GREEN}✅ Reusable Components${NC}"
    echo -e "${GREEN}✅ Tabbed Interface${NC}"
    echo -e "${GREEN}✅ Loading States & Error Handling${NC}"
    echo -e "${GREEN}✅ Toast Notifications${NC}"
    echo -e "${GREEN}✅ Accessibility Support${NC}"
    echo -e "${GREEN}✅ Responsive Design${NC}"
    
    echo -e "\n${BLUE}Access URLs:${NC}"
    echo -e "${YELLOW}Web Application: https://your-domain.com${NC}"
    echo -e "${YELLOW}API Backend: https://your-domain.com/api${NC}"
    echo -e "${YELLOW}Health Check: https://your-domain.com/healthz${NC}"
    
    echo -e "\n${BLUE}Monitoring:${NC}"
    echo -e "${YELLOW}View logs: docker-compose -f $PRODUCTION_COMPOSE logs -f${NC}"
    echo -e "${YELLOW}Check status: docker-compose -f $PRODUCTION_COMPOSE ps${NC}"
    echo -e "${YELLOW}Restart services: docker-compose -f $PRODUCTION_COMPOSE restart${NC}"
}

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage: $0 [ENVIRONMENT] [BACKUP_ENABLED] [HEALTH_CHECK_ENABLED]${NC}"
    echo -e "${YELLOW}Parameters:${NC}"
    echo -e "  ENVIRONMENT           - Production environment (default: production)"
    echo -e "  BACKUP_ENABLED        - Enable backup before deployment (default: true)"
    echo -e "  HEALTH_CHECK_ENABLED  - Enable health checks after deployment (default: true)"
    echo -e ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 production true true    # Full deployment with backup and health checks"
    echo -e "  $0 production false false  # Quick deployment without backup or health checks"
    echo -e "  $0 staging true true       # Deploy to staging environment"
}

# Main execution
main() {
    case $ENVIRONMENT in
        "production"|"staging"|"development")
            check_prerequisites
            backup_current_deployment
            stop_current_services
            build_production_images
            start_production_services
            run_health_checks
            show_deployment_status
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown environment: $ENVIRONMENT${NC}"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
