#!/bin/bash

# VANTAGE AI - Complete Setup Script
# This script sets up the entire development environment

set -e

echo "🚀 VANTAGE AI - Complete Setup Script"
echo "======================================"

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
check_docker() {
    print_status "Checking Docker installation..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Setup environment files
setup_environment() {
    print_status "Setting up environment files..."
    
    # Backend environment
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_success "Created .env from env.example"
        else
            print_warning "No env.example found, creating basic .env"
            cat > .env << EOF
# Database
POSTGRES_USER=dev
POSTGRES_PASSWORD=dev
POSTGRES_DB=vantage
POSTGRES_PORT=5433

# Redis
REDIS_PORT=6379

# API
API_PORT=8000
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true

# Clerk Authentication
CLERK_SECRET_KEY=your-clerk-secret-key
CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
EOF
        fi
    else
        print_success ".env already exists"
    fi
    
    # Frontend environment
    if [ ! -f web/.env.local ]; then
        if [ -f web/env.sample ]; then
            cp web/env.sample web/.env.local
            print_success "Created web/.env.local from web/env.sample"
        else
            print_warning "No web/env.sample found, creating basic web/.env.local"
            cat > web/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
NEXT_PUBLIC_DEV_MODE=true
EOF
        fi
    else
        print_success "web/.env.local already exists"
    fi
}

# Install pre-commit hooks
setup_precommit() {
    print_status "Setting up pre-commit hooks..."
    
    # Install pre-commit if not already installed
    if ! command -v pre-commit > /dev/null 2>&1; then
        print_status "Installing pre-commit..."
        pip install pre-commit
    fi
    
    # Install pre-commit hooks
    pre-commit install
    pre-commit install --hook-type commit-msg
    
    print_success "Pre-commit hooks installed"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    docker-compose build --parallel
    print_success "Docker images built"
}

# Start services
start_services() {
    print_status "Starting services..."
    docker-compose up -d db redis
    
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Check if database is ready
    while ! docker-compose exec -T db pg_isready -U dev -d vantage > /dev/null 2>&1; do
        print_status "Waiting for database..."
        sleep 2
    done
    
    print_success "Database is ready"
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec -T api alembic upgrade head
    
    print_success "Database migrations completed"
    
    # Start all services
    docker-compose up -d
    print_success "All services started"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    docker-compose exec -T api pytest tests/ -v --tb=short
    print_success "Tests completed"
}

# Check service health
check_health() {
    print_status "Checking service health..."
    
    # Check API health
    if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_success "API is healthy"
    else
        print_warning "API health check failed"
    fi
    
    # Check Web health
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Web is healthy"
    else
        print_warning "Web health check failed"
    fi
}

# Main setup function
main() {
    echo
    print_status "Starting VANTAGE AI setup..."
    echo
    
    check_docker
    check_docker_compose
    setup_environment
    setup_precommit
    build_images
    start_services
    
    echo
    print_success "Setup completed successfully!"
    echo
    echo "🌐 Web Application: http://localhost:3000"
    echo "🔧 API Documentation: http://localhost:8000/docs"
    echo "📊 API Health: http://localhost:8000/api/v1/health"
    echo "🗄️  Database: localhost:5433"
    echo "🔴 Redis: localhost:6379"
    echo
    echo "To run tests: make test"
    echo "To view logs: make logs"
    echo "To stop services: make down"
    echo
}

# Run main function
main "$@"
