# 🚀 VANTAGE AI - Real API Integration Setup

This guide will help you transform your VANTAGE AI platform from mock data to real API integrations.

## 🎯 What We've Built

Your VANTAGE AI platform now has **real API integrations** instead of mock data:

- ✅ **Real Facebook/Meta API** - OAuth, publishing, analytics
- ✅ **Real LinkedIn API** - Company page publishing
- ✅ **Real Publishing System** - Actual content posting
- ✅ **Real Analytics** - Live data collection
- ✅ **Production-Ready Infrastructure** - Docker, monitoring, security

## 🚀 Quick Start (5 minutes)

### 1. Set Up Real API Credentials

```bash
# Run the automated setup script
./scripts/setup-real-apis.sh
```

This script will:
- Guide you through getting API credentials
- Configure your environment variables
- Start the application with real integrations
- Test the API connections

### 2. Test the Integration

```bash
# Test all API endpoints
python scripts/test-real-integration.py
```

### 3. Use the Real Platform

1. Go to `http://localhost:3000/integrations`
2. Click **"Connect Facebook"** to test OAuth
3. Create a test post in the composer
4. Publish to Facebook to verify real integration

## 📋 Required API Credentials

### Facebook/Meta API
1. **Create Meta App**: [developers.facebook.com](https://developers.facebook.com/apps/)
2. **Get App ID & Secret**: From your app dashboard
3. **Configure OAuth**: Add redirect URIs
4. **Get Page ID**: From your Facebook page settings
5. **Get Instagram Business ID**: From your Instagram business account

### LinkedIn API
1. **Create LinkedIn App**: [linkedin.com/developers/apps](https://www.linkedin.com/developers/apps)
2. **Get Client ID & Secret**: From your app dashboard
3. **Get Organization URN**: From your LinkedIn company page

### AI APIs
1. **OpenAI API Key**: [platform.openai.com](https://platform.openai.com/api-keys)
2. **Anthropic API Key**: [console.anthropic.com](https://console.anthropic.com/)

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### 1. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your real API credentials
nano .env
```

Required variables:
```bash
# Meta/Facebook
META_APP_ID=your_meta_app_id_here
META_APP_SECRET=your_meta_app_secret_here
META_REDIRECT_URI=http://localhost:8000/api/v1/oauth/meta/callback
META_PAGE_ID=your_facebook_page_id_here

# LinkedIn
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
LINKEDIN_REDIRECT_URL=http://localhost:8000/api/v1/oauth/linkedin/callback

# AI
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Enable real API calls
DRY_RUN=false
NEXT_PUBLIC_MOCK_MODE=false
```

### 2. Start the Application

```bash
# Start with real API integrations
docker compose up --build
```

### 3. Verify Integration

```bash
# Test API health
curl http://localhost:8000/api/v1/health

# Test OAuth endpoint
curl "http://localhost:8000/api/v1/oauth/meta/authorize?state=test"
```

## 🧪 Testing Real Integrations

### Test OAuth Flow
1. Go to `http://localhost:3000/integrations`
2. Click **"Connect Facebook"**
3. Complete Facebook OAuth
4. Verify connection status shows "Connected"

### Test Publishing
1. Go to `http://localhost:3000/composer`
2. Create a test post
3. Select Facebook as platform
4. Click **"Publish"**
5. Check your Facebook page for the published content

### Test Analytics
1. Go to `http://localhost:3000/analytics`
2. Verify real data is being collected
3. Check for live engagement metrics

## 🔍 Troubleshooting

### Common Issues

#### 1. "App Not Setup" Error
- **Cause**: Meta app is in development mode
- **Solution**: Add test users or submit for app review

#### 2. "Invalid Redirect URI" Error
- **Cause**: Redirect URI not configured in Meta app
- **Solution**: Add `http://localhost:8000/api/v1/oauth/meta/callback` to OAuth settings

#### 3. "Insufficient Permissions" Error
- **Cause**: Missing required permissions
- **Solution**: Request permissions in Meta App Review

#### 4. "Token Expired" Error
- **Cause**: Access token has expired
- **Solution**: Re-authenticate through OAuth flow

### Debug Mode

Enable debug logging:
```bash
DEBUG=true docker compose up api
```

View logs:
```bash
# API logs
docker compose logs -f api

# Web logs
docker compose logs -f web

# Worker logs
docker compose logs -f worker
```

## 📊 What's Real Now

### Before (Mock Data)
- ❌ Fake "connected" status
- ❌ Mock publishing responses
- ❌ Generated fake analytics
- ❌ No real API calls

### After (Real APIs)
- ✅ Real OAuth authentication
- ✅ Actual content publishing to Facebook/Instagram
- ✅ Live analytics data collection
- ✅ Real-time engagement metrics
- ✅ Production-ready error handling

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment
cp env.production.example .env.production

# Configure production variables
nano .env.production
```

### Security Checklist
- [ ] Use HTTPS in production
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS_ORIGINS properly
- [ ] Use production database
- [ ] Enable monitoring and logging
- [ ] Set up SSL certificates

### Deployment Commands
```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Deploy to production
docker compose -f docker-compose.prod.yml up -d
```

## 📚 API Documentation

### OAuth Endpoints
- `GET /api/v1/oauth/meta/authorize` - Start Facebook OAuth
- `GET /api/v1/oauth/meta/callback` - Handle OAuth callback
- `GET /api/v1/oauth/meta/pages` - Get Facebook pages

### Publishing Endpoints
- `POST /api/v1/publishing/publish/preview` - Preview content
- `POST /api/v1/publishing/publish/send` - Publish content
- `GET /api/v1/publishing/jobs/{job_id}` - Get publishing status

### Analytics Endpoints
- `GET /api/v1/analytics/summary` - Get analytics summary
- `GET /api/v1/analytics/timeseries` - Get time series data
- `GET /api/v1/analytics/content` - Get content performance

## 🎉 Success!

You now have a **real, production-ready** social media management platform with:

- ✅ **Real API integrations** with Facebook, Instagram, LinkedIn
- ✅ **Actual content publishing** to social media platforms
- ✅ **Live analytics** and performance tracking
- ✅ **Production-ready infrastructure** with Docker
- ✅ **Comprehensive error handling** and retry logic
- ✅ **Secure token management** and encryption

## 📞 Support

If you encounter issues:
1. Check the [Meta Setup Guide](docs/META_SETUP_GUIDE.md)
2. Review the [Social Media Integration Docs](docs/social_media_integration.md)
3. Run the test script: `python scripts/test-real-integration.py`
4. Check application logs: `docker compose logs -f api`

---

**🎯 Your VANTAGE AI platform is now a real product, not just a demo!**
