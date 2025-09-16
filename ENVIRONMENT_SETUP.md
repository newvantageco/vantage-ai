# Environment Configuration Guide

This document explains how to set up environment variables for the VANTAGE AI platform.

## Overview

The VANTAGE AI platform uses environment variables for configuration across three main components:

- **Web Frontend** (`web/`) - Next.js application
- **API Backend** (`app/`) - FastAPI application  
- **Workers** (`workers/`) - Background job processors

## Quick Setup

1. **Copy environment sample files:**
   ```bash
   # Web frontend
   cp web/env.sample web/.env.local
   
   # API backend
   cp app/env.sample app/.env
   
   # Workers
   cp workers/env.sample workers/.env
   ```

2. **Fill in your actual values** in each `.env` file
3. **Never commit** `.env` files to version control

## Environment Files

### Web Frontend (`web/.env.local`)

**Required for development:**
- `NEXT_PUBLIC_API_BASE` - API endpoint URL
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk authentication
- `CLERK_SECRET_KEY` - Clerk secret key

**Optional:**
- `NEXT_PUBLIC_VAPID_PUBLIC_KEY` - Push notifications
- `VAPID_PRIVATE_KEY` - Push notifications
- `E2E_MOCKS` - E2E testing mode

### API Backend (`app/.env`)

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (32+ characters)
- `CLERK_JWKS_URL` - Clerk authentication
- `CLERK_ISSUER` - Clerk authentication

**Platform Integrations:**
- `META_APP_ID` / `META_APP_SECRET` - Facebook/Instagram
- `LINKEDIN_CLIENT_ID` / `LINKEDIN_CLIENT_SECRET` - LinkedIn
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - Google
- `WHATSAPP_ACCESS_TOKEN` - WhatsApp Business

**AI Services:**
- `OPENAI_API_KEY` - OpenAI API access
- `MODEL_ROUTER_PRIMARY` - Primary AI model
- `MODEL_ROUTER_FALLBACK` - Fallback AI model

**Billing:**
- `STRIPE_SECRET_KEY` - Stripe payments
- `STRIPE_WEBHOOK_SECRET` - Stripe webhooks

### Workers (`workers/.env`)

**Required:**
- `API_BASE` - API endpoint URL
- `DATABASE_URL` - Database connection
- `REDIS_URL` - Redis connection

**Worker-specific:**
- `RULES_WORKER_INTERVAL_MINUTES` - Rules processing interval
- `INSIGHTS_POLL_INTERVAL_HOURS` - Metrics polling interval
- `PRIVACY_RETENTION_DAYS` - Data retention period

## Security Notes

1. **Never commit real secrets** to version control
2. **Use different keys** for development/staging/production
3. **Rotate secrets regularly** using `scripts/rotate_secrets.py`
4. **Use environment-specific** `.env` files (`.env.local`, `.env.staging`, etc.)

## Development Workflow

1. **Start with sample files** - Copy from `env.sample` files
2. **Fill in test values** - Use development/test API keys
3. **Test locally** - Ensure all services start correctly
4. **Deploy to staging** - Use staging environment variables
5. **Deploy to production** - Use production secrets

## Troubleshooting

**Common issues:**
- Missing environment variables cause startup failures
- Incorrect API keys cause authentication errors
- Database connection issues from wrong `DATABASE_URL`
- Redis connection issues from wrong `REDIS_URL`

**Debug steps:**
1. Check environment file exists and is readable
2. Verify all required variables are set
3. Test API keys with external services
4. Check database/Redis connectivity
5. Review application logs for specific errors

## Environment Variable Reference

See individual `env.sample` files for complete variable lists:

- [Web Frontend Variables](web/env.sample)
- [API Backend Variables](app/env.sample)  
- [Workers Variables](workers/env.sample)
