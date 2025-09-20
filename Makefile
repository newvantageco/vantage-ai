# VANTAGE AI - Development Makefile
# Single-truth dev stack commands

.PHONY: help up down logs api web test clean build

# Default target
help:
	@echo "VANTAGE AI Development Commands:"
	@echo ""
	@echo "  make up          - Start all services (db, redis, api, worker, web)"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - Show logs for all services"
	@echo "  make api         - Start only API service"
	@echo "  make web         - Start only web service"
	@echo "  make test        - Run all tests"
	@echo "  make test-unit   - Run unit tests only"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make test-ai     - Run AI content tests"
	@echo "  make test-cms    - Run CMS tests"
	@echo "  make test-publishing - Run publishing tests"
	@echo "  make test-analytics - Run analytics tests"
	@echo "  make test-billing - Run billing tests"
	@echo "  make test-collaboration - Run collaboration tests"
	@echo "  make test-privacy - Run privacy tests"
	@echo "  make test-whatsapp - Run WhatsApp tests"
	@echo "  make test-local  - Run tests locally (without Docker)"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make build       - Build all Docker images"
	@echo ""

# Start all services
up:
	@echo "🚀 Starting VANTAGE AI development stack..."
	docker-compose -f docker-compose.simple.yml up -d
	@echo "✅ Services started! Access:"
	@echo "   🌐 Web: http://localhost:3000"
	@echo "   🔧 API: http://localhost:8000"
	@echo "   📊 API Docs: http://localhost:8000/docs"
	@echo "   🗄️  Database: localhost:5432"
	@echo "   🔴 Redis: localhost:6379"

# Stop all services
down:
	@echo "🛑 Stopping VANTAGE AI development stack..."
	docker-compose -f docker-compose.simple.yml down
	@echo "✅ Services stopped!"

# Show logs for all services
logs:
	@echo "📋 Showing logs for all services..."
	docker-compose -f docker-compose.simple.yml logs -f

# Start only API service
api:
	@echo "🔧 Starting API service..."
	docker-compose -f docker-compose.simple.yml up -d db redis
	@echo "⏳ Waiting for database to be ready..."
	sleep 5
	docker-compose -f docker-compose.simple.yml up api
	@echo "✅ API service started at http://localhost:8000"

# Start only web service
web:
	@echo "🌐 Starting web service..."
	docker-compose -f docker-compose.simple.yml up -d db redis api
	@echo "⏳ Waiting for API to be ready..."
	sleep 10
	docker-compose -f docker-compose.simple.yml up web
	@echo "✅ Web service started at http://localhost:3000"

# Run all tests
test:
	@echo "🧪 Running all tests..."
	@echo "📊 Backend tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -v
	@echo "🌐 Frontend tests..."
	docker-compose -f docker-compose.simple.yml exec web npm test
	@echo "✅ All tests completed!"

# Test commands
test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ --cov=app --cov-report=html --cov-report=term

test-ai: ## Run AI content tests
	@echo "🧪 Running AI content tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -k 'test_ai_content' -v

test-cms: ## Run CMS tests
	@echo "🧪 Running CMS tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -k 'test_cms' -v

test-publishing: ## Run publishing tests
	@echo "🧪 Running publishing tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -k 'test_publishing' -v

test-analytics: ## Run analytics tests
	@echo "🧪 Running analytics tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -k 'test_analytics' -v

test-billing: ## Run billing tests
	@echo "🧪 Running billing tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -k 'test_billing' -v

test-collaboration: ## Run collaboration tests
	@echo "🧪 Running collaboration tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -k 'test_collaboration' -v

test-privacy: ## Run privacy tests
	@echo "🧪 Running privacy tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -k 'test_privacy' -v

test-whatsapp: ## Run WhatsApp tests
	@echo "🧪 Running WhatsApp tests..."
	docker-compose -f docker-compose.simple.yml exec api pytest tests/ -k 'test_whatsapp' -v

test-local: ## Run tests locally (without Docker)
	@echo "🧪 Running tests locally..."
	python run_tests.py

# Clean up containers and volumes
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose -f docker-compose.simple.yml down -v
	docker system prune -f
	@echo "✅ Cleanup completed!"

# Build all Docker images
build:
	@echo "🔨 Building all Docker images..."
	docker-compose -f docker-compose.simple.yml build
	@echo "✅ All images built!"

# Development helpers
dev-setup:
	@echo "🛠️  Setting up development environment..."
	@echo "📝 Creating .env file if it doesn't exist..."
	@if [ ! -f .env ]; then cp env.sample .env; echo "✅ Created .env from env.sample"; fi
	@echo "📝 Creating web/.env.local if it doesn't exist..."
	@if [ ! -f web/.env.local ]; then cp web/env.sample web/.env.local; echo "✅ Created web/.env.local from web/env.sample"; fi
	@echo "✅ Development setup completed!"

# Database operations
db-migrate:
	@echo "🔄 Running database migrations..."
	docker-compose -f docker-compose.simple.yml exec api alembic upgrade head
	@echo "✅ Database migrations completed!"

db-reset:
	@echo "🔄 Resetting database..."
	docker-compose -f docker-compose.simple.yml down -v
	docker-compose -f docker-compose.simple.yml up -d db
	@echo "⏳ Waiting for database to be ready..."
	sleep 10
	docker-compose -f docker-compose.simple.yml exec api alembic upgrade head
	@echo "✅ Database reset completed!"

# Service status
status:
	@echo "📊 Service Status:"
	docker-compose -f docker-compose.simple.yml ps

# Health checks
health:
	@echo "🏥 Checking service health..."
	@echo "🗄️  Database:"
	@docker-compose -f docker-compose.simple.yml exec db pg_isready -U dev -d vantage || echo "❌ Database not ready"
	@echo "🔴 Redis:"
	@docker-compose -f docker-compose.simple.yml exec redis redis-cli ping || echo "❌ Redis not ready"
	@echo "🔧 API:"
	@curl -f http://localhost:8000/api/v1/health || echo "❌ API not ready"
	@echo "🌐 Web:"
	@curl -f http://localhost:3000 || echo "❌ Web not ready"

# Quick start (setup + up)
quickstart: dev-setup up
	@echo "🎉 VANTAGE AI is ready!"
	@echo "   🌐 Web: http://localhost:3000"
	@echo "   🔧 API: http://localhost:8000"
	@echo "   📊 API Docs: http://localhost:8000/docs"