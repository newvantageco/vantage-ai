# Environment Variables Configuration

This document lists all required environment variables for the VANTAGE AI application.

## Quick Start

Copy the sample environment file and configure your variables:

```bash
cp env.example .env
# Edit .env with your actual values
```

## Required Environment Variables

### Database Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://user:pass@localhost:5432/vantage` | ✅ |
| `POSTGRES_USER` | Database username | `dev` | ✅ |
| `POSTGRES_PASSWORD` | Database password | `dev` | ✅ |
| `POSTGRES_DB` | Database name | `vantage` | ✅ |
| `POSTGRES_PORT` | Database port | `5433` | ❌ (default: 5433) |

### Redis Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` | ✅ |

### Application Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Application environment | `development`, `staging`, `production` | ✅ |
| `DEBUG` | Debug mode | `true`, `false` | ❌ (default: false) |
| `SECRET_KEY` | Application secret key | `your-secret-key-here` | ✅ |
| `API_PORT` | API server port | `8000` | ❌ (default: 8000) |
| `WEB_PORT` | Web server port | `3000` | ❌ (default: 3000) |

### Authentication (Clerk)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `CLERK_SECRET_KEY` | Clerk secret key | `sk_test_...` | ✅ |
| `CLERK_PUBLISHABLE_KEY` | Clerk publishable key | `pk_test_...` | ✅ |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Frontend Clerk key | `pk_test_...` | ✅ |

### Payment Processing (Stripe)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` | ✅ |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_test_...` | ✅ |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | `whsec_...` | ✅ |
| `STRIPE_PRICE_ID_STARTER` | Starter plan price ID | `price_...` | ❌ |
| `STRIPE_PRICE_ID_GROWTH` | Growth plan price ID | `price_...` | ❌ |
| `STRIPE_PRICE_ID_PRO` | Pro plan price ID | `price_...` | ❌ |

### AI Services

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | ✅ |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` | ❌ |
| `COHERE_API_KEY` | Cohere API key | `...` | ❌ |

### Social Media Integrations

#### Meta (Facebook/Instagram)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `META_APP_ID` | Meta app ID | `123456789` | ❌ |
| `META_APP_SECRET` | Meta app secret | `...` | ❌ |
| `META_REDIRECT_URI` | OAuth redirect URI | `https://yourapp.com/auth/meta/callback` | ❌ |
| `META_PAGE_ID` | Facebook page ID | `123456789` | ❌ |
| `META_IG_BUSINESS_ID` | Instagram business ID | `123456789` | ❌ |

#### LinkedIn

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `LINKEDIN_CLIENT_ID` | LinkedIn client ID | `...` | ❌ |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn client secret | `...` | ❌ |
| `LINKEDIN_REDIRECT_URL` | OAuth redirect URL | `https://yourapp.com/auth/linkedin/callback` | ❌ |
| `LINKEDIN_PAGE_URN` | LinkedIn page URN | `urn:li:organization:123456` | ❌ |

#### Google

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GOOGLE_CLIENT_ID` | Google client ID | `...` | ❌ |
| `GOOGLE_CLIENT_SECRET` | Google client secret | `...` | ❌ |
| `GOOGLE_REDIRECT_URL` | OAuth redirect URL | `https://yourapp.com/auth/google/callback` | ❌ |
| `GOOGLE_BUSINESS_LOCATION_ID` | Google Business location ID | `123456789` | ❌ |

#### WhatsApp

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `WHATSAPP_VERIFY_TOKEN` | WhatsApp verify token | `your-verify-token` | ❌ |
| `WHATSAPP_PHONE_ID` | WhatsApp phone number ID | `123456789` | ❌ |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp access token | `...` | ❌ |

### Advertising Platforms

#### TikTok Ads

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `TIKTOK_ACCESS_TOKEN` | TikTok access token | `...` | ❌ |
| `TIKTOK_ADVERTISER_ID` | TikTok advertiser ID | `123456789` | ❌ |

#### Google Ads

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GOOGLE_ADS_ACCESS_TOKEN` | Google Ads access token | `...` | ❌ |
| `GOOGLE_ADS_CUSTOMER_ID` | Google Ads customer ID | `123-456-7890` | ❌ |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads developer token | `...` | ❌ |

### Push Notifications (PWA)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `VAPID_PUBLIC_KEY` | VAPID public key | `...` | ❌ |
| `VAPID_PRIVATE_KEY` | VAPID private key | `...` | ❌ |
| `VAPID_EMAIL` | VAPID email | `admin@yourapp.com` | ❌ |

### Rate Limiting

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true`, `false` | ❌ (default: true) |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Requests per minute | `60` | ❌ (default: 60) |
| `RATE_LIMIT_BURST` | Burst limit | `100` | ❌ (default: 100) |
| `RATE_LIMIT_STORAGE_URL` | Redis URL for distributed rate limiting | `redis://localhost:6379` | ❌ |

### CORS Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:3000,https://yourapp.com` | ❌ |
| `CORS_METHODS` | Allowed methods (comma-separated) | `GET,POST,PUT,DELETE,PATCH,OPTIONS` | ❌ |
| `CORS_HEADERS` | Allowed headers (comma-separated) | `Content-Type,Authorization,X-Requested-With` | ❌ |

### Frontend Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_URL` | API base URL for frontend | `http://localhost:8000` | ✅ |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Frontend Clerk key | `pk_test_...` | ✅ |
| `NODE_ENV` | Node.js environment | `development`, `production` | ❌ (default: development) |

## Environment-Specific Configuration

### Development

For local development, you can use these minimal settings:

```bash
# Database
DATABASE_URL=postgresql+psycopg://dev:dev@localhost:5433/vantage
REDIS_URL=redis://localhost:6379

# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-development-secret-key

# Authentication (use test keys)
CLERK_SECRET_KEY=sk_test_development_key_placeholder
CLERK_PUBLISHABLE_KEY=pk_test_development_key_placeholder
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_development_key_placeholder

# AI Services (optional for development)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Stripe (use test keys)
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production

For production, ensure all required variables are set with real values:

```bash
# Database (use production database)
DATABASE_URL=postgresql+psycopg://user:password@prod-db:5432/vantage
REDIS_URL=redis://prod-redis:6379

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key

# Authentication (use production keys)
CLERK_SECRET_KEY=sk_live_your_production_key
CLERK_PUBLISHABLE_KEY=pk_live_your_production_key
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_your_production_key

# AI Services
OPENAI_API_KEY=sk-your-production-openai-key
ANTHROPIC_API_KEY=sk-ant-your-production-anthropic-key

# Stripe (use live keys)
STRIPE_SECRET_KEY=sk_live_your_production_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_production_key
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret

# Social Media Integrations (configure as needed)
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
# ... other integrations

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourapp.com
```

## Validation

The application validates environment variables on startup using pydantic-settings. Missing required variables will cause the application to fail fast with a clear error message.

## Security Notes

1. **Never commit `.env` files** to version control
2. **Use strong, unique secret keys** in production
3. **Rotate API keys regularly** for security
4. **Use environment-specific keys** (test vs live)
5. **Store sensitive variables** in secure secret management systems

## Troubleshooting

### Common Issues

1. **Database connection errors**: Check `DATABASE_URL` format and database availability
2. **Redis connection errors**: Verify `REDIS_URL` and Redis server status
3. **Authentication errors**: Ensure Clerk keys are valid and properly configured
4. **API errors**: Check that all required environment variables are set
5. **Frontend errors**: Verify `NEXT_PUBLIC_*` variables are set correctly

### Validation Errors

If you see validation errors on startup, check:

1. Required variables are set
2. Variable formats are correct (e.g., URLs, keys)
3. No typos in variable names
4. Values are not empty or placeholder text

### Getting Help

For additional help with environment configuration:

1. Check the application logs for specific error messages
2. Verify your `.env` file format and syntax
3. Test individual services (database, Redis, external APIs)
4. Consult the service-specific documentation for API keys and configuration