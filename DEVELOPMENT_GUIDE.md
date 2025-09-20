# 🚀 VANTAGE AI - Development Guide

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### One-Command Setup
```bash
# Clone and setup everything
git clone <repository-url>
cd vantage-ai
./setup.sh
```

This will:
- ✅ Set up environment files
- ✅ Install pre-commit hooks
- ✅ Build Docker images
- ✅ Start all services
- ✅ Run database migrations
- ✅ Verify everything is working

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js Web   │    │   FastAPI API   │    │   PostgreSQL    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   + pgvector    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   + Celery      │
                       └─────────────────┘
```

## 🛠️ Development Commands

### Docker Commands
```bash
# Start all services
make up

# Stop all services
make down

# View logs
make logs

# Check service status
make status

# Health check
make health
```

### Database Commands
```bash
# Run migrations
make db-migrate

# Reset database
make db-reset

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"
```

### Testing Commands
```bash
# Run all tests
make test

# Run specific test suites
make test-unit
make test-ai
make test-cms
make test-publishing
make test-analytics
make test-billing

# Run with coverage
make test-coverage
```

### Code Quality Commands
```bash
# Run linting
ruff check app/
ruff format app/

# Run type checking
mypy app/

# Run security scan
bandit -r app/

# Run all pre-commit hooks
pre-commit run --all-files
```

## 📁 Project Structure

```
vantage-ai/
├── app/                    # FastAPI backend
│   ├── api/v1/            # API routes
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   ├── workers/           # Background tasks
│   └── middleware/        # Custom middleware
├── web/                   # Next.js frontend
│   ├── src/app/           # App Router pages
│   ├── src/components/    # React components
│   └── src/lib/           # Utilities and API client
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── infra/                 # Infrastructure configs
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+psycopg://dev:dev@localhost:5433/vantage
REDIS_URL=redis://localhost:6379

# Authentication
CLERK_SECRET_KEY=your-clerk-secret-key
CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

# Security
SECRET_KEY=your-secret-key
ENVIRONMENT=development
DEBUG=true
```

#### Frontend (web/.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
NEXT_PUBLIC_DEV_MODE=true
```

## 🧪 Testing

### Test Structure
```
tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests
├── e2e/                   # End-to-end tests
└── performance/           # Performance tests
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_api.py

# With coverage
pytest --cov=app --cov-report=html

# Specific test markers
pytest -m "unit"
pytest -m "integration"
pytest -m "ai"
```

### Test Coverage
- Target: 80%+ coverage
- Reports generated in `htmlcov/`
- Coverage threshold enforced in CI

## 🔒 Security

### Security Features
- ✅ JWT authentication with Clerk
- ✅ Rate limiting per endpoint
- ✅ Security headers middleware
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ CORS configuration
- ✅ Environment variable security

### Security Checks
```bash
# Run security scan
bandit -r app/

# Check for vulnerabilities
safety check

# Run pre-commit security hooks
pre-commit run bandit
```

## 📊 Performance

### Performance Features
- ✅ Redis caching
- ✅ Database connection pooling
- ✅ Query optimization
- ✅ Async/await patterns
- ✅ Background task processing
- ✅ CDN-ready static assets

### Performance Monitoring
```bash
# Run performance tests
locust -f tests/performance/locustfile.py

# Monitor with Prometheus
# Access metrics at http://localhost:8000/metrics
```

## 🚀 Deployment

### Development
```bash
make up
```

### Staging
```bash
export BUILD_TARGET=staging
docker-compose -f docker-compose.staging.yml up -d
```

### Production
```bash
export BUILD_TARGET=production
docker-compose -f docker-compose.production.yml up -d
```

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database status
make health

# Reset database
make db-reset

# Check logs
docker-compose logs db
```

#### API Not Responding
```bash
# Check API logs
docker-compose logs api

# Restart API service
docker-compose restart api

# Check health endpoint
curl http://localhost:8000/api/v1/health
```

#### Frontend Build Issues
```bash
# Clear node_modules
docker-compose exec web rm -rf node_modules
docker-compose up web

# Check TypeScript errors
docker-compose exec web npm run typecheck
```

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
docker-compose up
```

## 📚 API Documentation

### Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/dashboard` - Dashboard data
- `POST /api/v1/cms/content` - Create content
- `GET /api/v1/analytics` - Analytics data
- `POST /api/v1/ai/generate` - AI content generation

## 🤝 Contributing

### Code Style
- Follow PEP 8 for Python
- Use TypeScript for frontend
- Write tests for new features
- Update documentation

### Git Workflow
1. Create feature branch
2. Make changes
3. Run tests and linting
4. Commit with conventional commits
5. Push and create PR

### Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📈 Monitoring

### Health Checks
- API: http://localhost:8000/api/v1/health
- Web: http://localhost:3000/healthz

### Metrics
- Prometheus: http://localhost:8000/metrics
- Grafana: http://localhost:3001 (if enabled)

### Logs
```bash
# All services
make logs

# Specific service
docker-compose logs api
docker-compose logs web
docker-compose logs db
```

## 🆘 Getting Help

1. Check this documentation
2. Look at existing issues
3. Run health checks
4. Check logs
5. Create a new issue with details

---

**Happy Coding! 🚀**
