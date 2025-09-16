# Vantage AI - Development Makefile
# Provides convenient commands for local development

.PHONY: help dev dev-up dev-down dev-logs dev-clean seed-demo test lint format install

# Default target
help:
	@echo "Vantage AI - Development Commands"
	@echo "================================="
	@echo ""
	@echo "Development:"
	@echo "  dev-up      Start all services with Docker Compose"
	@echo "  dev-down    Stop all services and clean up"
	@echo "  dev-logs    Show logs for all services"
	@echo "  dev-clean   Stop services, remove volumes, and clean up images"
	@echo "  seed-demo   Create demo data (requires running services)"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        Run linting checks (Python + TypeScript)"
	@echo "  format      Format code (Python + TypeScript)"
	@echo "  test        Run test suites"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install dependencies for local development"
	@echo "  setup       Initial setup (copy env, install deps)"
	@echo ""

# Development commands
dev-up:
	@echo "🚀 Starting development environment..."
	@./scripts/dev_up.sh

dev-down:
	@echo "🛑 Stopping development environment..."
	@./scripts/dev_down.sh

dev-logs:
	@echo "📊 Showing logs for all services..."
	@docker compose -f infra/docker-compose.dev.yml logs -f

dev-clean:
	@echo "🧹 Cleaning up development environment..."
	@docker compose -f infra/docker-compose.dev.yml down -v --remove-orphans
	@docker system prune -f
	@docker volume prune -f

seed-demo:
	@echo "🌱 Seeding demo data..."
	@./scripts/seed_demo.sh

# Code quality commands
lint:
	@echo "🔍 Running linting checks..."
	@echo "Python linting..."
	@ruff check app/ workers/ tests/
	@black --check app/ workers/ tests/
	@echo "TypeScript linting..."
	@cd web && pnpm lint
	@cd web && pnpm typecheck

format:
	@echo "✨ Formatting code..."
	@echo "Python formatting..."
	@ruff check --fix app/ workers/ tests/
	@black app/ workers/ tests/

test:
	@echo "🧪 Running tests..."
	@echo "Python tests..."
	@pytest tests/ -v
	@echo "TypeScript tests..."
	@cd web && pnpm test:e2e

# Setup commands
install:
	@echo "📦 Installing dependencies..."
	@echo "Python dependencies..."
	@pip install -r requirements.txt
	@echo "Node.js dependencies..."
	@cd web && pnpm install

setup: install
	@echo "⚙️  Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "📝 Created .env file from template. Please edit with your credentials."; \
	fi
	@echo "✅ Setup complete! Run 'make dev-up' to start development environment."

# Docker commands
docker-build:
	@echo "🐳 Building Docker images..."
	@docker compose -f infra/docker-compose.dev.yml build

docker-push:
	@echo "📤 Pushing Docker images..."
	@docker compose -f infra/docker-compose.dev.yml push

# Database commands
db-migrate:
	@echo "🗄️  Running database migrations..."
	@alembic upgrade head

db-reset:
	@echo "🔄 Resetting database..."
	@alembic downgrade base
	@alembic upgrade head

# Utility commands
status:
	@echo "📊 Development environment status:"
	@docker compose -f infra/docker-compose.dev.yml ps

logs-api:
	@echo "📊 API logs:"
	@docker compose -f infra/docker-compose.dev.yml logs -f api

logs-web:
	@echo "📊 Web logs:"
	@docker compose -f infra/docker-compose.dev.yml logs -f web

logs-workers:
	@echo "📊 Worker logs:"
	@docker compose -f infra/docker-compose.dev.yml logs -f worker-scheduler worker-optimiser

# CI/CD simulation
ci-lint:
	@echo "🔍 Running CI linting checks..."
	@ruff check app/ workers/ tests/ --output-format=github
	@black --check app/ workers/ tests/
	@cd web && pnpm lint
	@cd web && pnpm typecheck

ci-test:
	@echo "🧪 Running CI test suite..."
	@pytest tests/ -v --cov=app --cov-report=xml
	@cd web && pnpm test:e2e
