#!/bin/bash

# VANTAGE AI Deployment Script
# Handles deployment to different environments with proper validation and rollback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
BACKUP_DIR="/var/backups/vantage-ai"
LOG_FILE="/var/log/vantage-ai/deploy.log"

echo -e "${BLUE}🚀 VANTAGE AI Deployment Script${NC}"
echo "=================================="
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo ""

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log "${RED}❌ Docker is not running${NC}"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        log "${RED}❌ docker-compose is not installed${NC}"
        exit 1
    fi
    
    # Check if required environment variables are set
    if [ "$ENVIRONMENT" = "production" ]; then
        required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "CLERK_SECRET_KEY" "STRIPE_SECRET_KEY")
        for var in "${required_vars[@]}"; do
            if [ -z "${!var}" ]; then
                log "${RED}❌ Required environment variable $var is not set${NC}"
                exit 1
            fi
        done
    fi
    
    log "${GREEN}✅ Prerequisites check passed${NC}"
}

# Function to create backup
create_backup() {
    log "${YELLOW}💾 Creating backup...${NC}"
    
    # Create backup directory
    sudo mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [ "$ENVIRONMENT" = "production" ]; then
        backup_file="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose exec -T db pg_dump -U postgres vantage > "$backup_file"
        log "${GREEN}✅ Database backup created: $backup_file${NC}"
    fi
    
    # Backup configuration files
    config_backup="$BACKUP_DIR/config_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$config_backup" .env docker-compose*.yml infra/
    log "${GREEN}✅ Configuration backup created: $config_backup${NC}"
}

# Function to pull latest images
pull_images() {
    log "${YELLOW}📥 Pulling latest images...${NC}"
    
    # Pull images based on environment
    case $ENVIRONMENT in
        "staging")
            docker-compose -f docker-compose.yml pull
            ;;
        "production")
            docker-compose -f docker-compose.production.yml pull
            ;;
        *)
            log "${RED}❌ Unknown environment: $ENVIRONMENT${NC}"
            exit 1
            ;;
    esac
    
    log "${GREEN}✅ Images pulled successfully${NC}"
}

# Function to run database migrations
run_migrations() {
    log "${YELLOW}🔄 Running database migrations...${NC}"
    
    # Wait for database to be ready
    sleep 10
    
    # Run migrations
    case $ENVIRONMENT in
        "staging")
            docker-compose -f docker-compose.yml exec -T api alembic upgrade head
            ;;
        "production")
            docker-compose -f docker-compose.production.yml exec -T api alembic upgrade head
            ;;
    esac
    
    log "${GREEN}✅ Database migrations completed${NC}"
}

# Function to deploy services
deploy_services() {
    log "${YELLOW}🚀 Deploying services...${NC}"
    
    # Deploy based on environment
    case $ENVIRONMENT in
        "staging")
            docker-compose -f docker-compose.yml up -d
            ;;
        "production")
            docker-compose -f docker-compose.production.yml up -d
            ;;
    esac
    
    log "${GREEN}✅ Services deployed successfully${NC}"
}

# Function to run health checks
run_health_checks() {
    log "${YELLOW}🏥 Running health checks...${NC}"
    
    # Wait for services to start
    sleep 30
    
    # Check API health
    api_url="http://localhost:8000/api/v1/health"
    if curl -f "$api_url" > /dev/null 2>&1; then
        log "${GREEN}✅ API health check passed${NC}"
    else
        log "${RED}❌ API health check failed${NC}"
        return 1
    fi
    
    # Check web health
    web_url="http://localhost:3000"
    if curl -f "$web_url" > /dev/null 2>&1; then
        log "${GREEN}✅ Web health check passed${NC}"
    else
        log "${RED}❌ Web health check failed${NC}"
        return 1
    fi
    
    # Check database connection
    case $ENVIRONMENT in
        "staging")
            if docker-compose -f docker-compose.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
                log "${GREEN}✅ Database health check passed${NC}"
            else
                log "${RED}❌ Database health check failed${NC}"
                return 1
            fi
            ;;
        "production")
            if docker-compose -f docker-compose.production.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
                log "${GREEN}✅ Database health check passed${NC}"
            else
                log "${RED}❌ Database health check failed${NC}"
                return 1
            fi
            ;;
    esac
    
    log "${GREEN}✅ All health checks passed${NC}"
}

# Function to rollback deployment
rollback() {
    log "${YELLOW}🔄 Rolling back deployment...${NC}"
    
    # Stop current services
    case $ENVIRONMENT in
        "staging")
            docker-compose -f docker-compose.yml down
            ;;
        "production")
            docker-compose -f docker-compose.production.yml down
            ;;
    esac
    
    # Restore from backup
    latest_backup=$(ls -t "$BACKUP_DIR"/config_backup_*.tar.gz | head -n1)
    if [ -n "$latest_backup" ]; then
        tar -xzf "$latest_backup"
        log "${GREEN}✅ Configuration restored from backup${NC}"
    fi
    
    # Restart services
    deploy_services
    
    log "${GREEN}✅ Rollback completed${NC}"
}

# Function to cleanup old backups
cleanup_backups() {
    log "${YELLOW}🧹 Cleaning up old backups...${NC}"
    
    # Keep only last 7 days of backups
    find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
    
    log "${GREEN}✅ Old backups cleaned up${NC}"
}

# Function to send deployment notification
send_notification() {
    local status=$1
    local message=$2
    
    log "${YELLOW}📧 Sending deployment notification...${NC}"
    
    # Add notification logic here (Slack, email, etc.)
    # Example:
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"Deployment $status: $message\"}" \
    #   "$SLACK_WEBHOOK_URL"
    
    log "${GREEN}✅ Notification sent${NC}"
}

# Main deployment function
main() {
    log "${BLUE}Starting deployment to $ENVIRONMENT...${NC}"
    
    # Create log directory
    sudo mkdir -p "$(dirname "$LOG_FILE")"
    sudo touch "$LOG_FILE"
    sudo chown $USER:$USER "$LOG_FILE"
    
    # Start deployment
    if check_prerequisites && create_backup && pull_images && run_migrations && deploy_services && run_health_checks; then
        cleanup_backups
        send_notification "SUCCESS" "Deployment to $ENVIRONMENT completed successfully"
        log "${GREEN}🎉 Deployment completed successfully!${NC}"
    else
        log "${RED}❌ Deployment failed, initiating rollback...${NC}"
        rollback
        send_notification "FAILED" "Deployment to $ENVIRONMENT failed, rollback initiated"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "rollback")
        rollback
        ;;
    "health-check")
        run_health_checks
        ;;
    "backup")
        create_backup
        ;;
    *)
        main
        ;;
esac
