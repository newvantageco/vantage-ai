#!/bin/bash

# =============================================================================
# VANTAGE AI - Production Environment Setup Script
# =============================================================================
# This script sets up the production environment with all necessary configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
PROD_ENV_FILE="$PROJECT_DIR/.env.production"

echo -e "${BLUE}🚀 Setting up VANTAGE AI Production Environment${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate secure random string
generate_secret() {
    local length=${1:-32}
    if command_exists openssl; then
        openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
    else
        # Fallback to /dev/urandom
        head -c $length /dev/urandom | base64 | tr -d "=+/" | cut -c1-$length
    fi
}

# Function to validate email
validate_email() {
    local email=$1
    if [[ $email =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate domain
validate_domain() {
    local domain=$1
    if [[ $domain =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to setup environment variables
setup_environment() {
    echo -e "${YELLOW}📋 Setting up environment variables...${NC}"
    
    # Check if .env.production exists
    if [[ -f "$PROD_ENV_FILE" ]]; then
        echo -e "${BLUE}Found existing .env.production file${NC}"
        read -p "Do you want to overwrite it? (y/N): " overwrite
        if [[ $overwrite != "y" && $overwrite != "Y" ]]; then
            echo -e "${GREEN}Using existing .env.production file${NC}"
            return 0
        fi
    fi
    
    # Get user input
    echo -e "${BLUE}Please provide the following information:${NC}"
    echo ""
    
    # Domain configuration
    read -p "Enter your domain (e.g., vantage-ai.com): " DOMAIN
    while ! validate_domain "$DOMAIN"; do
        echo -e "${RED}❌ Invalid domain format. Please try again.${NC}"
        read -p "Enter your domain (e.g., vantage-ai.com): " DOMAIN
    done
    
    read -p "Enter your API subdomain (e.g., api.vantage-ai.com): " API_DOMAIN
    while ! validate_domain "$API_DOMAIN"; do
        echo -e "${RED}❌ Invalid domain format. Please try again.${NC}"
        read -p "Enter your API subdomain (e.g., api.vantage-ai.com): " API_DOMAIN
    done
    
    # Email configuration
    read -p "Enter your email for SSL certificates: " EMAIL
    while ! validate_email "$EMAIL"; do
        echo -e "${RED}❌ Invalid email format. Please try again.${NC}"
        read -p "Enter your email for SSL certificates: " EMAIL
    done
    
    # Database configuration
    read -p "Enter database name (default: vantage): " DB_NAME
    DB_NAME=${DB_NAME:-vantage}
    
    read -p "Enter database user (default: vantage_user): " DB_USER
    DB_USER=${DB_USER:-vantage_user}
    
    read -s -p "Enter database password: " DB_PASSWORD
    echo ""
    while [[ ${#DB_PASSWORD} -lt 8 ]]; do
        echo -e "${RED}❌ Password must be at least 8 characters long.${NC}"
        read -s -p "Enter database password: " DB_PASSWORD
        echo ""
    done
    
    # Generate secrets
    SECRET_KEY=$(generate_secret 32)
    JWT_SECRET=$(generate_secret 32)
    
    echo -e "${YELLOW}🔐 Generated secure secrets${NC}"
    
    # Create production environment file
    cat > "$PROD_ENV_FILE" << EOF
# =============================================================================
# VANTAGE AI - PRODUCTION Environment Configuration
# =============================================================================
# Generated on: $(date)
# Domain: $DOMAIN
# API Domain: $API_DOMAIN

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=$DB_NAME
DATABASE_URL=postgresql+psycopg://$DB_USER:$DB_PASSWORD@db:5432/$DB_NAME

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_URL=redis://redis:6379/0

# =============================================================================
# AUTHENTICATION (Clerk) - PRODUCTION KEYS
# =============================================================================
# Get these from your Clerk dashboard: https://dashboard.clerk.com
CLERK_SECRET_KEY=sk_live_your_production_key_here
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_your_production_key_here

# =============================================================================
# SECURITY & GENERAL CONFIGURATION - PRODUCTION
# =============================================================================
SECRET_KEY=$SECRET_KEY
JWT_SECRET=$JWT_SECRET

# CORS Configuration - PRODUCTION (NO WILDCARDS!)
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,https://$API_DOMAIN
CORS_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
CORS_HEADERS=Content-Type,Authorization,X-Requested-With,Accept,Origin

# Production mode settings
DRY_RUN=false
DEBUG=false
ENVIRONMENT=production

# =============================================================================
# API CONFIGURATION
# =============================================================================
API_BASE=https://$API_DOMAIN/api/v1
NEXT_PUBLIC_API_URL=https://$API_DOMAIN

# =============================================================================
# STRIPE CONFIGURATION - PRODUCTION
# =============================================================================
# Stripe API Keys (get from: https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_live_your_production_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_production_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret

# =============================================================================
# AI MODEL CONFIGURATION - PRODUCTION
# =============================================================================
# OpenAI API Key (get from: https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your_production_openai_key

# Anthropic API Key (get from: https://console.anthropic.com/)
ANTHROPIC_API_KEY=sk-ant-your_production_anthropic_key

# =============================================================================
# MONITORING & OBSERVABILITY
# =============================================================================
OTEL_SERVICE_NAME=vantage-ai-production
ENABLE_PROMETHEUS_METRICS=true

# =============================================================================
# FRONTEND CONFIGURATION
# =============================================================================
NODE_ENV=production
NEXT_PUBLIC_DEV_MODE=false

# =============================================================================
# SECURITY HEADERS & RATE LIMITING
# =============================================================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST_LIMIT=200

# Security headers
SECURITY_HEADERS_ENABLED=true
HSTS_MAX_AGE=31536000
CSP_REPORT_URI=https://$DOMAIN/csp-report

# =============================================================================
# SOCIAL MEDIA INTEGRATIONS (Optional)
# =============================================================================
# Meta/Facebook Integration
META_APP_ID=your_production_meta_app_id
META_APP_SECRET=your_production_meta_app_secret
META_REDIRECT_URI=https://$DOMAIN/oauth/meta/callback

# LinkedIn Integration
LINKEDIN_CLIENT_ID=your_production_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_production_linkedin_client_secret
LINKEDIN_REDIRECT_URL=https://$DOMAIN/oauth/linkedin/callback

# Google Integration
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret
GOOGLE_REDIRECT_URI=https://$DOMAIN/oauth/google/callback

# TikTok Integration
TIKTOK_CLIENT_KEY=your_production_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_production_tiktok_client_secret
TIKTOK_REDIRECT_URI=https://$DOMAIN/oauth/tiktok/callback

# WhatsApp Business Integration
WHATSAPP_ACCESS_TOKEN=your_production_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_production_whatsapp_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_production_whatsapp_business_id
EOF
    
    echo -e "${GREEN}✅ Production environment file created: $PROD_ENV_FILE${NC}"
}

# Function to setup SSL certificates
setup_ssl() {
    echo -e "${YELLOW}🔒 Setting up SSL certificates...${NC}"
    
    if [[ -f "$PROJECT_DIR/scripts/setup-ssl.sh" ]]; then
        chmod +x "$PROJECT_DIR/scripts/setup-ssl.sh"
        "$PROJECT_DIR/scripts/setup-ssl.sh" "$DOMAIN" "$API_DOMAIN" "$EMAIL"
    else
        echo -e "${RED}❌ SSL setup script not found!${NC}"
        exit 1
    fi
}

# Function to setup monitoring
setup_monitoring() {
    echo -e "${YELLOW}📊 Setting up monitoring configuration...${NC}"
    
    # Create monitoring directory
    mkdir -p "$PROJECT_DIR/monitoring"
    
    # Create Prometheus configuration
    cat > "$PROJECT_DIR/monitoring/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'vantage-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'vantage-web'
    static_configs:
      - targets: ['web:3000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
EOF
    
    # Create Grafana datasource configuration
    cat > "$PROJECT_DIR/monitoring/grafana-datasource.yml" << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF
    
    echo -e "${GREEN}✅ Monitoring configuration created${NC}"
}

# Function to create production startup script
create_startup_script() {
    echo -e "${YELLOW}🚀 Creating production startup script...${NC}"
    
    cat > "$PROJECT_DIR/start-production.sh" << 'EOF'
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
if curl -f http://localhost/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API health check failed${NC}"
fi

# Check Web health
if curl -f http://localhost/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Web is healthy${NC}"
else
    echo -e "${RED}❌ Web health check failed${NC}"
fi

echo -e "${GREEN}🎉 VANTAGE AI Production Environment Started!${NC}"
echo -e "${BLUE}Web: https://your-domain.com${NC}"
echo -e "${BLUE}API: https://api.your-domain.com${NC}"
echo -e "${BLUE}API Docs: https://api.your-domain.com/docs${NC}"
EOF
    
    chmod +x "$PROJECT_DIR/start-production.sh"
    echo -e "${GREEN}✅ Production startup script created${NC}"
}

# Function to create backup script
create_backup_script() {
    echo -e "${YELLOW}💾 Creating backup script...${NC}"
    
    cat > "$PROJECT_DIR/scripts/backup-production.sh" << 'EOF'
#!/bin/bash

# =============================================================================
# VANTAGE AI - Production Backup Script
# =============================================================================

set -e

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="vantage-db-prod"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Database backup
echo "Creating database backup..."
docker exec "$DB_CONTAINER" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/database_$DATE.sql"

# Uploads backup
echo "Creating uploads backup..."
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" uploads/

# Environment backup
echo "Creating environment backup..."
cp .env.production "$BACKUP_DIR/env_$DATE.production"

echo "Backup completed: $BACKUP_DIR/"
EOF
    
    chmod +x "$PROJECT_DIR/scripts/backup-production.sh"
    echo -e "${GREEN}✅ Backup script created${NC}"
}

# Main setup function
main() {
    echo -e "${BLUE}🚀 VANTAGE AI Production Setup${NC}"
    echo -e "${BLUE}=============================${NC}"
    echo ""
    
    # Check prerequisites
    if ! command_exists docker; then
        echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
        exit 1
    fi
    
    # Setup environment
    setup_environment
    
    # Setup SSL
    setup_ssl
    
    # Setup monitoring
    setup_monitoring
    
    # Create startup script
    create_startup_script
    
    # Create backup script
    create_backup_script
    
    echo -e "${GREEN}🎉 Production setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo -e "${BLUE}1. Update your DNS to point to this server${NC}"
    echo -e "${BLUE}2. Configure your API keys in .env.production${NC}"
    echo -e "${BLUE}3. Run: ./start-production.sh${NC}"
    echo -e "${BLUE}4. Test your deployment${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Important: Update all placeholder values in .env.production${NC}"
    echo -e "${YELLOW}⚠️  Important: Set up SSL certificate auto-renewal${NC}"
}

# Run main function
main "$@"
