#!/bin/bash

# Vantage AI - Development Environment Verification Script
# This script verifies the development environment is working correctly

set -e

echo "🔍 Vantage AI Development Environment Verification"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Docker is running
echo "1. Checking Docker status..."
if docker ps > /dev/null 2>&1; then
    print_status 0 "Docker is running"
else
    print_status 1 "Docker is not running. Please start Docker Desktop and try again."
    echo "   To start Docker Desktop:"
    echo "   - macOS: Open Docker Desktop from Applications"
    echo "   - Linux: sudo systemctl start docker"
    echo "   - Windows: Start Docker Desktop from Start Menu"
    exit 1
fi

# Check if .env file exists
echo ""
echo "2. Checking environment configuration..."
if [ -f ".env" ]; then
    print_status 0 ".env file exists"
else
    print_warning ".env file not found, creating from sample..."
    cp app/env.sample .env
    print_status 0 ".env file created from sample"
fi

# Start Docker Compose services
echo ""
echo "3. Starting Docker Compose services..."
if docker compose -f infra/docker-compose.dev.yml up -d; then
    print_status 0 "Docker Compose services started"
else
    print_status 1 "Failed to start Docker Compose services"
    exit 1
fi

# Wait for services to be ready
echo ""
echo "4. Waiting for services to be ready..."
sleep 10

# Check API health
echo ""
echo "5. Checking API health..."
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    print_status 0 "API health check passed"
else
    print_warning "API health check failed, waiting longer..."
    sleep 10
    if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_status 0 "API health check passed (after retry)"
    else
        print_status 1 "API health check failed after retry"
        echo "   Check API logs: docker compose -f infra/docker-compose.dev.yml logs api"
    fi
fi

# Check API readyz endpoint
echo ""
echo "6. Checking API readyz endpoint..."
if curl -f http://localhost:8000/api/v1/readyz > /dev/null 2>&1; then
    print_status 0 "API readyz check passed"
else
    print_warning "API readyz check failed (endpoint may not exist yet)"
fi

# Check Web interface
echo ""
echo "7. Checking Web interface..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status 0 "Web interface is accessible"
else
    print_warning "Web interface not accessible, waiting longer..."
    sleep 10
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_status 0 "Web interface is accessible (after retry)"
    else
        print_status 1 "Web interface not accessible after retry"
        echo "   Check web logs: docker compose -f infra/docker-compose.dev.yml logs web"
    fi
fi

# Check scheduler health
echo ""
echo "8. Checking scheduler health..."
if curl -f http://localhost:8000/api/v1/schedule/health > /dev/null 2>&1; then
    print_status 0 "Scheduler health check passed"
else
    print_warning "Scheduler health check failed (endpoint may not exist yet)"
fi

# Seed demo data
echo ""
echo "9. Seeding demo data..."
if ./scripts/seed_demo.sh; then
    print_status 0 "Demo data seeded successfully"
else
    print_warning "Demo data seeding failed (expected in demo environment)"
fi

# Check worker logs
echo ""
echo "10. Checking worker status..."
echo "   Scheduler worker logs:"
docker compose -f infra/docker-compose.dev.yml logs --tail=10 worker-scheduler

echo ""
echo "   Optimiser worker logs:"
docker compose -f infra/docker-compose.dev.yml logs --tail=10 worker-optimiser

# Final status
echo ""
echo "🎉 Development Environment Verification Complete!"
echo "=================================================="
echo ""
echo "📊 Service Status:"
echo "   - API: http://localhost:8000"
echo "   - Web: http://localhost:3000"
echo "   - Database: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "🔧 Useful Commands:"
echo "   - View all logs: docker compose -f infra/docker-compose.dev.yml logs -f"
echo "   - View API logs: docker compose -f infra/docker-compose.dev.yml logs -f api"
echo "   - View worker logs: docker compose -f infra/docker-compose.dev.yml logs -f worker-scheduler"
echo "   - Stop services: docker compose -f infra/docker-compose.dev.yml down"
echo "   - Restart services: docker compose -f infra/docker-compose.dev.yml restart"
echo ""
echo "🧪 Test Commands:"
echo "   - Run scheduler tests: python -m pytest tests/test_scheduler.py -v"
echo "   - Test API endpoints: curl http://localhost:8000/api/v1/health"
echo "   - Test scheduler: curl -X POST http://localhost:8000/api/v1/schedule/run"
echo ""
echo "📝 Next Steps:"
echo "   1. Visit http://localhost:3000 to see the web app"
echo "   2. Check the dashboard for demo data"
echo "   3. Monitor worker logs for scheduled posts"
echo "   4. Run the QA checklist: docs/qa_checklist.md"
