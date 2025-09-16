# Installation

This guide will help you install and set up VANTAGE AI on your system.

## Prerequisites

Before installing VANTAGE AI, make sure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **PostgreSQL 14+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 6+** - [Download Redis](https://redis.io/download)
- **Docker** (optional) - [Download Docker](https://www.docker.com/get-started)

## Installation Methods

### Method 1: Docker Compose (Recommended)

The easiest way to get started is using Docker Compose:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vantage-ai/vantage-ai.git
   cd vantage-ai
   ```

2. **Copy environment file**:
   ```bash
   cp env.example .env
   ```

3. **Edit environment variables**:
   ```bash
   nano .env
   ```
   
   Update the following variables:
   ```env
   # Database
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vantage_ai
   
   # Redis
   REDIS_URL=redis://localhost:6379
   
   # AI API Keys
   OPENAI_API_KEY=your_openai_api_key
   
   # Social Media API Keys
   META_APP_ID=your_meta_app_id
   META_APP_SECRET=your_meta_app_secret
   LINKEDIN_CLIENT_ID=your_linkedin_client_id
   LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
   
   # Stripe (for billing)
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   ```

4. **Start the services**:
   ```bash
   docker-compose -f infra/docker-compose.dev.yml up -d
   ```

5. **Run database migrations**:
   ```bash
   docker-compose -f infra/docker-compose.dev.yml exec api alembic upgrade head
   ```

6. **Access the application**:
   - API: http://localhost:8000
   - Web UI: http://localhost:3000
   - Grafana: http://localhost:3001

### Method 2: Manual Installation

If you prefer to install manually:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vantage-ai/vantage-ai.git
   cd vantage-ai
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   cd web
   npm install
   cd ..
   ```

4. **Set up the database**:
   ```bash
   createdb vantage_ai
   alembic upgrade head
   ```

5. **Start Redis**:
   ```bash
   redis-server
   ```

6. **Start the API server**:
   ```bash
   python -m app.main
   ```

7. **Start the web UI** (in a new terminal):
   ```bash
   cd web
   npm run dev
   ```

## Configuration

### Environment Variables

VANTAGE AI uses environment variables for configuration. Here are the key variables:

#### Database
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

#### AI Services
- `OPENAI_API_KEY` - OpenAI API key for content generation
- `ANTHROPIC_API_KEY` - Anthropic API key (optional)

#### Social Media APIs
- `META_APP_ID` - Facebook/Instagram App ID
- `META_APP_SECRET` - Facebook/Instagram App Secret
- `LINKEDIN_CLIENT_ID` - LinkedIn Client ID
- `LINKEDIN_CLIENT_SECRET` - LinkedIn Client Secret
- `GOOGLE_CLIENT_ID` - Google OAuth Client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth Client Secret

#### Billing
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret

#### Security
- `SECRET_KEY` - Secret key for JWT tokens
- `SECRET_KEY_VERSION` - Version for secret rotation

### Database Setup

1. **Create the database**:
   ```bash
   createdb vantage_ai
   ```

2. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Seed initial data** (optional):
   ```bash
   python scripts/seed_demo.sh
   ```

## Verification

After installation, verify everything is working:

1. **Check API health**:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. **Check web UI**:
   Open http://localhost:3000 in your browser

3. **Check database connection**:
   ```bash
   psql vantage_ai -c "SELECT COUNT(*) FROM organizations;"
   ```

## Troubleshooting

### Common Issues

#### Database Connection Error
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solution**: Make sure PostgreSQL is running and the connection string is correct.

#### Redis Connection Error
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

**Solution**: Make sure Redis is running on the correct port.

#### Port Already in Use
```
OSError: [Errno 48] Address already in use
```

**Solution**: Change the port in your configuration or stop the conflicting service.

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](/docs/guides/troubleshooting)
2. Search [GitHub Issues](https://github.com/vantage-ai/vantage-ai/issues)
3. Join our [Discord Community](https://discord.gg/vantage-ai)
4. Contact [Support](https://support.vantageai.com)

## Next Steps

Once you have VANTAGE AI installed:

1. **[Quick Start Guide](/docs/getting-started/quickstart)** - Create your first campaign
2. **[Configuration](/docs/getting-started/configuration)** - Customize your settings
3. **[First Campaign](/docs/getting-started/first-campaign)** - Launch your first campaign

## Production Deployment

For production deployment, see our [Deployment Guide](/docs/deployment/docker) for detailed instructions on:

- Docker containerization
- Kubernetes orchestration
- AWS deployment
- Monitoring and observability
