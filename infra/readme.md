# Vantage AI - Development Infrastructure

This directory contains Docker Compose configurations and setup instructions for local development.

## Quick Start

1. **Copy environment file:**
   ```bash
   cp env.example .env
   ```

2. **Start all services:**
   ```bash
   ./scripts/dev_up.sh
   ```

3. **Access the applications:**
   - Web App: http://localhost:3000
   - API: http://localhost:8000
   - API Health: http://localhost:8000/api/v1/health

## Services

- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **api**: FastAPI backend (port 8000)
- **web**: Next.js frontend (port 3000)
- **worker-scheduler**: Background job scheduler
- **worker-optimiser**: ML optimization worker

## Setting Up OAuth Credentials

### Meta/Facebook Integration

1. **Create a Meta App:**
   - Go to https://developers.facebook.com/apps/
   - Click "Create App" → "Business" → "Next"
   - Fill in app details and create

2. **Configure OAuth:**
   - In your app dashboard, go to "Facebook Login" → "Settings"
   - Add redirect URI: `https://your-domain.com/oauth/meta/callback`
   - For local development, use ngrok or similar for HTTPS

3. **Get Page and Instagram IDs:**
   - Go to "App" → "Add Product" → "Instagram Basic Display"
   - Follow setup instructions to get Instagram Business Account ID
   - Get Page ID from your Facebook Page settings

4. **Update .env:**
   ```bash
   META_APP_ID=your_app_id_here
   META_APP_SECRET=your_app_secret_here
   META_PAGE_ID=your_page_id_here
   META_IG_BUSINESS_ID=your_ig_business_id_here
   ```

### LinkedIn Integration

1. **Create a LinkedIn App:**
   - Go to https://www.linkedin.com/developers/apps
   - Click "Create app" and fill in details
   - Request access to "Sign In with LinkedIn" and "Share on LinkedIn"

2. **Configure OAuth:**
   - In "Auth" tab, add redirect URL: `https://your-domain.com/oauth/linkedin/callback`
   - For local development, use ngrok for HTTPS

3. **Get Organization ID:**
   - Go to your LinkedIn company page
   - The organization ID is in the URL or page source

4. **Update .env:**
   ```bash
   LINKEDIN_CLIENT_ID=your_client_id_here
   LINKEDIN_CLIENT_SECRET=your_client_secret_here
   LINKEDIN_PAGE_URN=urn:li:organization:your_org_id_here
   ```

## Setting Up Stripe Billing

### Stripe Account Setup

1. **Create a Stripe Account:**
   - Go to https://dashboard.stripe.com
   - Create an account or sign in
   - Switch to test mode for development

2. **Get API Keys:**
   - In Stripe dashboard, go to "Developers" → "API keys"
   - Copy your "Secret key" (starts with `sk_test_`)

3. **Create Products and Prices:**
   - Go to "Products" → "Add product"
   - Create three products: Starter, Growth, Pro
   - For each product, add a monthly price
   - Copy the Price IDs (start with `price_`)

4. **Set up Webhooks:**
   - Go to "Developers" → "Webhooks"
   - Add endpoint: `https://your-domain.com/api/v1/billing/webhook`
   - Select events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Copy the webhook signing secret (starts with `whsec_`)

5. **Update .env:**
   ```bash
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   STRIPE_PRICE_STARTER=price_starter_monthly_id_here
   STRIPE_PRICE_GROWTH=price_growth_monthly_id_here
   STRIPE_PRICE_PRO=price_pro_monthly_id_here
   STRIPE_DRY_RUN=true  # Set to false for production
   ```

### Testing Billing

- **Dry Run Mode**: Set `STRIPE_DRY_RUN=true` to test without making actual Stripe API calls
- **Test Cards**: Use Stripe test card numbers (4242 4242 4242 4242)
- **Webhook Testing**: Use Stripe CLI or ngrok for local webhook testing

## Development Scripts

- `./scripts/dev_up.sh` - Start all services
- `./scripts/dev_down.sh` - Stop all services and remove volumes
- `./scripts/seed_demo.sh` - Create demo data

## Security Notes

- **NEVER** commit `.env` files with real secrets
- Use placeholder values in `env.example`
- For production, use proper secret management (AWS Secrets Manager, etc.)
- Rotate API keys regularly
- Use HTTPS in production for OAuth callbacks and webhooks

## Troubleshooting

### Services won't start
- Check if ports 3000, 8000, 5432, 6379 are available
- Ensure Docker is running
- Check logs: `docker compose -f infra/docker-compose.dev.yml logs [service_name]`

### Database connection issues
- Wait for postgres health check to pass
- Check DATABASE_URL in .env
- Verify postgres container is running: `docker ps`

### OAuth redirect issues
- Ensure redirect URLs match exactly (including https/http)
- For local development, use ngrok or similar for HTTPS
- Check that OAuth apps are configured correctly

### Billing issues
- Verify Stripe keys are correct and in test mode
- Check webhook endpoint is accessible
- Use dry-run mode for testing: `STRIPE_DRY_RUN=true`
- Check Stripe dashboard for failed payments or webhook errors

### Workers not processing jobs
- Check worker logs: `docker compose -f infra/docker-compose.dev.yml logs worker-scheduler`
- Ensure Redis is running and accessible
- Verify job queue configuration