# VANTAGE AI - Marketing SaaS Platform

A comprehensive marketing automation platform built with FastAPI, Next.js, and AI-powered content generation. Manage your social media presence across multiple platforms with intelligent content creation, scheduling, and analytics.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### One-Command Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd vantage-ai

# Copy environment file
cp env.example .env

# Start the entire development environment
docker compose up --build
```

This will start:
- **PostgreSQL 16** with pgvector extension (port 5432)
- **Redis** for caching and task queue (port 6379)
- **FastAPI** backend with health checks (port 8000)
- **Celery** workers for background tasks
- **Next.js** frontend with hot reload (port 3000)

### Access the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/v1/health
- **Web Health Check**: http://localhost:3000/healthz

### Available Commands

```bash
# Docker Compose commands
docker compose up --build    # Start all services with build
docker compose up -d         # Start all services in background
docker compose down          # Stop all services
docker compose logs -f       # Follow logs for all services
docker compose ps            # Check service status

# Individual service commands
docker compose up db redis   # Start only database and Redis
docker compose up api        # Start only API service
docker compose up web        # Start only web service
docker compose up worker     # Start only worker service

# Development commands
docker compose exec api alembic upgrade head  # Run database migrations
docker compose exec api python -m pytest     # Run tests
docker compose exec web npm run build        # Build frontend
```

## 🏗️ Architecture

### Backend (FastAPI)
- **API Server**: FastAPI with automatic OpenAPI documentation
- **Database**: PostgreSQL 16 with pgvector extension for AI embeddings
- **Cache**: Redis for session storage and task queue
- **Background Tasks**: Celery workers for async processing
- **Authentication**: Clerk integration with JWT tokens
- **AI Services**: OpenAI, Anthropic, and Ollama integration with fallbacks

### Frontend (Next.js)
- **Framework**: Next.js 14.2.12 with App Router
- **UI Library**: Tailwind CSS + shadcn/ui + Radix UI
- **Authentication**: Clerk with middleware protection
- **State Management**: TanStack Query for server state
- **Charts**: Recharts for analytics visualization

### Key Features
- **AI Content Generation**: Multi-provider AI with intelligent fallbacks
- **Social Media Management**: Meta, LinkedIn, Google, TikTok, WhatsApp
- **Content Scheduling**: Calendar-based content planning
- **Analytics**: Real-time performance metrics and insights
- **Billing**: Stripe integration with subscription management
- **Multi-tenant**: Organization-based user management

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Copy production environment file
   cp env.production.example .env
   
   # Configure all required environment variables
   # See docs/ENV.md for complete list
   ```

2. **Database Migration**
   ```bash
   # Run migrations
   docker compose exec api alembic upgrade head
   ```

3. **Start Production Services**
   ```bash
   # Set production build target
   export BUILD_TARGET=production
   
   # Start all services
   docker compose up -d
   ```

4. **Health Checks**
   ```bash
   # Check API health
   curl http://localhost:8000/api/v1/health
   
   # Check web health
   curl http://localhost:3000/healthz
   ```

### Environment Variables

See [docs/ENV.md](docs/ENV.md) for complete environment variable documentation.

### Required for Production
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key
- `CLERK_SECRET_KEY` - Clerk authentication secret
- `CLERK_PUBLISHABLE_KEY` - Clerk public key
- `STRIPE_SECRET_KEY` - Stripe payment secret
- `STRIPE_PUBLISHABLE_KEY` - Stripe public key

### Optional Integrations
- `OPENAI_API_KEY` - OpenAI for content generation
- `ANTHROPIC_API_KEY` - Anthropic Claude models
- Social media API keys (Meta, LinkedIn, Google, etc.)

## 🧪 Testing

### Run All Tests
```bash
# Backend tests
docker compose exec api python -m pytest

# Frontend tests
docker compose exec web npm run test:e2e

# Integration tests
docker compose exec api python -m pytest tests/integration/
```

### CI/CD Pipeline
The application includes a comprehensive CI/CD pipeline with:
- Automated testing (unit, integration, e2e)
- Code quality checks (linting, type checking)
- Security scanning
- Docker image building
- Staging deployment

## 📊 Monitoring

### Health Endpoints
- **API Health**: `GET /api/v1/health`
- **Web Health**: `GET /healthz`

### Logging
- Structured logging with configurable levels
- Production logs written to `app.log`
- Console output for development

### Metrics
- Database connection status
- Redis connectivity
- AI service availability
- Background task queue status

## 🔧 Development

### Local Development
1. Clone the repository
2. Copy `env.example` to `.env`
3. Run `docker compose up --build`
4. Access the application at http://localhost:3000

### Code Structure
```
├── app/                    # FastAPI backend
│   ├── api/v1/            # API routes
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── workers/           # Background tasks
├── web/                   # Next.js frontend
│   ├── src/app/           # App Router pages
│   ├── src/components/    # React components
│   └── src/lib/           # Utilities and API client
├── docs/                  # Documentation
└── docker-compose.yml     # Development environment
```

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running: `docker compose ps`
   - Verify DATABASE_URL in .env file
   - Run migrations: `docker compose exec api alembic upgrade head`

2. **Frontend 500 Errors**
   - Check if API is running: `curl http://localhost:8000/api/v1/health`
   - Verify NEXT_PUBLIC_API_URL in .env
   - Check browser console for errors

3. **Authentication Issues**
   - Verify Clerk keys are set correctly
   - Check middleware configuration
   - Ensure public routes are properly configured

4. **AI Services Not Working**
   - Check API keys are set in environment
   - Verify fallback providers are available
   - Check logs for specific error messages

### Getting Help
- Check the logs: `docker compose logs -f [service]`
- Review environment configuration in `docs/ENV.md`
- Check health endpoints for service status

### Manual Setup (Alternative)

```bash
# 1. Setup environment files
make dev-setup

# 2. Start services
make up

# 3. Access the application
# Web: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 📋 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ | `postgresql+psycopg://dev:dev@localhost:5432/vantage` |
| `REDIS_URL` | Redis connection string | ✅ | `redis://localhost:6379` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | ✅ | - |
| `STRIPE_SECRET_KEY` | Stripe payment processing | ✅ | - |
| `CLERK_JWKS_URL` | Authentication service JWKS URL | ✅ | - |
| `CLERK_ISSUER` | Authentication service issuer | ✅ | - |
| `META_APP_ID` | Facebook/Instagram App ID | ❌ | - |
| `META_APP_SECRET` | Facebook/Instagram App Secret | ❌ | - |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp Business API token | ❌ | - |
| `ENVIRONMENT` | Deployment environment | ❌ | `development` |
| `DEBUG` | Enable debug mode | ❌ | `true` |
| `CORS_ORIGINS` | Allowed CORS origins | ❌ | `http://localhost:3000` |

## 🛠️ API Endpoints

### Core Endpoints
- `GET /api/v1/health` - Health check (unauthenticated)
- `GET /api/v1/dashboard` - Dashboard overview
- `GET /api/v1/analytics` - Analytics and metrics

### Content Management
- `POST /api/v1/cms/content` - Create content
- `GET /api/v1/cms/content` - List content
- `PUT /api/v1/cms/content/{id}` - Update content
- `DELETE /api/v1/cms/content/{id}` - Delete content

### Publishing
- `POST /api/v1/publishing/publish` - Publish content
- `GET /api/v1/publishing/publishes` - Publishing history
- `POST /api/v1/publishing/bulk-publish` - Bulk publishing

### WhatsApp Business
- `POST /api/v1/whatsapp/send` - Send message
- `GET /api/v1/whatsapp/templates` - List templates
- `POST /api/v1/whatsapp/webhook` - Webhook handler

### Integrations
- `GET /api/v1/integrations` - List integrations
- `POST /api/v1/integrations` - Create integration
- `GET /api/v1/integrations/{id}/test` - Test integration

### AI Content
- `POST /api/v1/ai/generate` - Generate AI content
- `GET /api/v1/ai/usage` - AI usage statistics
- `POST /api/v1/ai/optimize` - Optimize content

### Billing
- `GET /api/v1/billing/overview` - Billing overview
- `POST /api/v1/billing/subscribe` - Subscribe to plan
- `GET /api/v1/billing/invoices` - Invoice history

### Analytics
- `GET /api/v1/analytics/overview` - Analytics overview
- `GET /api/v1/analytics/content` - Content performance
- `GET /api/v1/analytics/audience` - Audience insights

### Collaboration
- `GET /api/v1/collaboration/teams` - Team management
- `POST /api/v1/collaboration/invite` - Invite team member
- `GET /api/v1/collaboration/permissions` - Permission management

## 🏗️ Architecture

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
                                │
                                ▼
                       ┌─────────────────┐
                       │  Third-party    │
                       │  Integrations   │
                       │  (Social APIs)  │
                       └─────────────────┘
```

## 🗄️ Database Migrations

The platform uses Alembic for database migrations with automatic pgvector extension setup.

### Running Migrations

```bash
# Run migrations (automatic on startup)
make db-migrate

# Or manually
docker-compose -f docker-compose.simple.yml exec api alembic upgrade head
```

### Migration Features

- **Automatic pgvector extension** creation
- **IF NOT EXISTS guards** for safe re-runs
- **Database wait logic** before migrations
- **Rollback support** with `alembic downgrade`

### Creating New Migrations

```bash
# Create a new migration
docker-compose -f docker-compose.simple.yml exec api alembic revision --autogenerate -m "Description"

# Apply the migration
docker-compose -f docker-compose.simple.yml exec api alembic upgrade head
```

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

### Frontend Tests
```bash
cd web

# Run linting
npm run lint

# Run type checking
npm run typecheck

# Run E2E tests
npm run test:e2e
```

### Performance Tests
```bash
# Install Locust
pip install locust

# Run performance tests
locust -f tests/performance/locustfile.py --host http://localhost:8000
```

## 🚀 Deployment

### Docker Compose (Development)
```bash
# Start development services
make up

# Check service status
make status

# View logs
make logs

# Stop services
make down
```

### Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check pod status
kubectl get pods

# Port forward for local access
kubectl port-forward svc/vantage-api 8000:8000
```

## 📊 Monitoring & Observability

- **Health checks** for all services
- **Structured logging** with correlation IDs
- **Metrics collection** for performance monitoring
- **Error tracking** and alerting
- **Database query monitoring**
- **API rate limiting** and usage tracking

## 🔒 Security Features

- **JWT authentication** with proper token validation
- **Role-based access control** (RBAC)
- **API rate limiting** and throttling
- **Input validation** and sanitization
- **SQL injection prevention**
- **CORS configuration**
- **Environment variable security**
- **Docker security** best practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Development Guidelines

- Follow PEP 8 for Python code style
- Use type hints for better code documentation
- Write tests for all new features
- Update documentation when adding features
- Use meaningful commit messages
- Follow the Reality-Check Matrix for TODO items

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Environment Variables](docs/ENV.md)
- [Deployment Guide](docs/deployment.md)
- [Development Setup](docs/development.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🐛 Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check if PostgreSQL is running: `make status`
   - Verify database health: `make health`
   - Check logs: `make logs`

2. **Services not starting**
   - Clean up and restart: `make clean && make up`
   - Check Docker is running
   - Verify ports 3000, 8000, 5432, 6379 are available

3. **Frontend build failed**
   - Check Node.js version (18+)
   - Clear node_modules: `docker-compose -f docker-compose.simple.yml exec web rm -rf node_modules && docker-compose -f docker-compose.simple.yml up web`
   - Check for TypeScript errors

4. **API endpoints not working**
   - Check API health: `curl http://localhost:8000/api/v1/health`
   - Verify CORS configuration in .env
   - Check authentication tokens

5. **Migrations failing**
   - Run migrations manually: `make db-migrate`
   - Check database connection: `make health`
   - Reset database: `make db-reset`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Next.js for the React framework
- PostgreSQL and pgvector for vector database
- Redis for caching and task queue
- Celery for background task processing
- All the open-source contributors

---

**Status:** Core infrastructure complete, ready for implementation  
**Last Updated:** January 2024  
**Version:** 1.0.0-alpha

