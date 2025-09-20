#!/bin/bash
# =============================================================================
# VANTAGE AI - Production Deployment Script
# =============================================================================
# This script helps deploy Vantage AI in production mode
# Run this script to deploy the application with production settings

set -e  # Exit on any error

echo "🚀 Starting Vantage AI Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Consider using a non-root user for security."
fi

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from production template..."
    if [ -f "env.production.ready" ]; then
        cp env.production.ready .env
        print_warning "Please edit .env file with your production values before continuing!"
        print_warning "Required changes:"
        echo "  - Set POSTGRES_PASSWORD to a secure password"
        echo "  - Set SECRET_KEY to a secure random string (32+ characters)"
        echo "  - Add your Clerk API keys"
        echo "  - Add your AI provider API keys (OpenAI, Anthropic)"
        echo "  - Configure your social media platform credentials"
        echo "  - Set your domain in CORS_ORIGINS"
        echo ""
        read -p "Have you configured the .env file? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Please configure the .env file first and run this script again."
            exit 1
        fi
    else
        print_error "Production environment template not found. Please create .env file manually."
        exit 1
    fi
fi

# Validate critical environment variables
print_status "Validating environment configuration..."
source .env

REQUIRED_VARS=(
    "POSTGRES_PASSWORD"
    "SECRET_KEY"
    "CLERK_SECRET_KEY"
    "OPENAI_API_KEY"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "CHANGE_ME_SECURE_PASSWORD" ] || [ "${!var}" = "CHANGE_ME_SECURE_SECRET_KEY_32_CHARS_MINIMUM" ] || [ "${!var}" = "sk-YOUR_PRODUCTION_OPENAI_API_KEY" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    print_error "Missing or placeholder values for required environment variables:"
    printf '%s\n' "${MISSING_VARS[@]}"
    exit 1
fi

print_success "Environment validation passed!"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p uploads/media
mkdir -p logs
mkdir -p backups

# Set proper permissions
chmod 755 uploads
chmod 755 logs
chmod 755 backups

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down --remove-orphans || true

# Pull latest images
print_status "Pulling latest Docker images..."
docker-compose pull

# Build the application
print_status "Building application containers..."
docker-compose build --no-cache

# Start the database first and wait for it to be ready
print_status "Starting database..."
docker-compose up -d db redis

print_status "Waiting for database to be ready..."
sleep 10

# Run database migrations
print_status "Running database migrations..."
docker-compose run --rm api python -m alembic upgrade head

# Start all services
print_status "Starting all services..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 30

# Check service health
print_status "Checking service health..."
SERVICES=("api" "web" "worker")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    if docker-compose ps "$service" | grep -q "healthy\|Up"; then
        print_success "$service is running"
    else
        print_error "$service is not healthy"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = true ]; then
    print_success "🎉 Deployment completed successfully!"
    echo ""
    echo "Your Vantage AI application is now running in production mode:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Next steps:"
    echo "  1. Set up SSL certificates (see infra/ssl/)"
    echo "  2. Configure your reverse proxy (nginx config in infra/)"
    echo "  3. Set up monitoring (see monitoring/)"
    echo "  4. Configure backups (see scripts/)"
    echo ""
    print_warning "Important: This deployment uses HTTP. For production, set up SSL/HTTPS!"
else
    print_error "Deployment completed with errors. Check the logs:"
    echo "  docker-compose logs api"
    echo "  docker-compose logs web"
    echo "  docker-compose logs worker"
    exit 1
fi
