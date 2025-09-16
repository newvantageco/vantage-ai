#!/bin/bash

# =============================================================================
# VANTAGE AI - Docker Deployment Script
# =============================================================================

set -e  # Exit on any error

echo "🚀 Starting VANTAGE AI Docker Deployment..."

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_status "Docker environment check passed ✅"

# Create production environment file if it doesn't exist
if [ ! -f .env.production ]; then
    print_warning "Creating .env.production from template..."
    cp env.production.example .env.production
    print_warning "Please edit .env.production with your actual production values before deploying!"
    print_warning "Especially update:"
    print_warning "  - API keys (OpenAI, Stripe, etc.)"
    print_warning "  - Database passwords"
    print_warning "  - Domain names"
    print_warning "  - Secret keys"
    echo ""
    read -p "Press Enter to continue after updating .env.production, or Ctrl+C to exit..."
fi

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Build all images
print_status "Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start the services
print_status "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check API health
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    print_success "API service is healthy ✅"
else
    print_error "API service is not responding ❌"
    docker-compose -f docker-compose.prod.yml logs api
    exit 1
fi

# Check Web health
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Web service is healthy ✅"
else
    print_error "Web service is not responding ❌"
    docker-compose -f docker-compose.prod.yml logs web
    exit 1
fi

# Check database connection
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U vantage_user -d vantage_ai > /dev/null 2>&1; then
    print_success "Database is healthy ✅"
else
    print_error "Database is not responding ❌"
    docker-compose -f docker-compose.prod.yml logs postgres
    exit 1
fi

# Check Redis connection
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is healthy ✅"
else
    print_error "Redis is not responding ❌"
    docker-compose -f docker-compose.prod.yml logs redis
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head

print_success "🎉 VANTAGE AI deployment completed successfully!"
echo ""
print_status "Services are running on:"
print_status "  🌐 Web Frontend: http://localhost:3000"
print_status "  🔌 API: http://localhost:8000"
print_status "  📊 API Health: http://localhost:8000/api/v1/health"
print_status "  🗄️  Database: localhost:5432"
print_status "  🔴 Redis: localhost:6379"
echo ""
print_status "To view logs:"
print_status "  docker-compose -f docker-compose.prod.yml logs -f [service_name]"
echo ""
print_status "To stop services:"
print_status "  docker-compose -f docker-compose.prod.yml down"
echo ""
print_status "To update and redeploy:"
print_status "  ./deploy-docker.sh"
