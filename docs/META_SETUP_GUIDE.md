# 🚀 Meta/Facebook API Setup Guide

This guide will help you set up real Facebook/Meta API integration for your VANTAGE AI platform.

## 📋 Prerequisites

1. **Facebook Developer Account** - Sign up at [developers.facebook.com](https://developers.facebook.com)
2. **Facebook Page** - You need a Facebook page to publish content
3. **Instagram Business Account** (optional) - For Instagram publishing

## 🔧 Step 1: Create Meta App

### 1.1 Create New App
1. Go to [Facebook Developers](https://developers.facebook.com/apps/)
2. Click **"Create App"**
3. Select **"Business"** as app type
4. Fill in app details:
   - **App Name**: `VANTAGE AI` (or your preferred name)
   - **App Contact Email**: Your email
   - **Business Account**: Select or create one

### 1.2 Configure App Settings
1. In your app dashboard, go to **Settings > Basic**
2. Note down:
   - **App ID** (you'll need this)
   - **App Secret** (click "Show" to reveal)

### 1.3 Add Products
1. In your app dashboard, click **"Add Product"**
2. Add these products:
   - **Facebook Login** (for OAuth)
   - **Instagram Basic Display** (for Instagram)
   - **Marketing API** (for publishing)

## 🔐 Step 2: Configure OAuth

### 2.1 Facebook Login Setup
1. Go to **Facebook Login > Settings**
2. Add these **Valid OAuth Redirect URIs**:
   ```
   http://localhost:8000/api/v1/oauth/meta/callback
   https://your-domain.com/api/v1/oauth/meta/callback
   ```
3. Add these **Valid OAuth Redirect URIs** for web:
   ```
   http://localhost:3000/oauth/meta/callback
   https://your-domain.com/oauth/meta/callback
   ```

### 2.2 App Review (Important!)
1. Go to **App Review > Permissions and Features**
2. Request these permissions:
   - `pages_manage_metadata`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_manage_comments`

**Note**: For development, you can add yourself as a **Test User** to test without app review.

## 📄 Step 3: Get Page Access

### 3.1 Get Page ID
1. Go to your Facebook page
2. Go to **Settings > Page Info**
3. Scroll down to find **Page ID**

### 3.2 Get Instagram Business Account ID
1. Go to your Instagram Business account
2. Go to **Settings > Account > Linked Accounts**
3. Note the **Instagram Business Account ID**

## 🔧 Step 4: Configure Environment Variables

Create a `.env` file in your project root with these values:

```bash
# Meta/Facebook Configuration
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
META_REDIRECT_URI=http://localhost:8000/api/v1/oauth/meta/callback
META_GRAPH_VERSION=20.0
META_PAGE_ID=your_facebook_page_id_here
META_IG_BUSINESS_ID=your_instagram_business_id_here

# Development settings
DRY_RUN=false
DEBUG=true
```

## 🧪 Step 5: Test the Integration

### 5.1 Start Your Application
```bash
# Start the development environment
docker compose up --build

# Or start individual services
docker compose up db redis api web
```

### 5.2 Test OAuth Flow
1. Go to `http://localhost:3000/integrations`
2. Click **"Connect Facebook"**
3. Complete the OAuth flow
4. Verify the connection is successful

### 5.3 Test Publishing
1. Go to `http://localhost:3000/composer`
2. Create a test post
3. Select Facebook as platform
4. Publish the post
5. Check your Facebook page for the published content

## 🔍 Step 6: Verify Integration

### 6.1 Check API Logs
```bash
# View API logs
docker compose logs -f api

# Look for successful OAuth and publishing logs
```

### 6.2 Test API Endpoints
```bash
# Test OAuth authorization
curl "http://localhost:8000/api/v1/oauth/meta/authorize?state=test"

# Test pages endpoint (after OAuth)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/oauth/meta/pages"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. "App Not Setup" Error
- **Cause**: App is in development mode
- **Solution**: Add test users or submit for app review

#### 2. "Invalid Redirect URI" Error
- **Cause**: Redirect URI not configured correctly
- **Solution**: Check OAuth redirect URIs in app settings

#### 3. "Insufficient Permissions" Error
- **Cause**: Missing required permissions
- **Solution**: Request permissions in App Review

#### 4. "Page Not Found" Error
- **Cause**: Incorrect page ID or no page access
- **Solution**: Verify page ID and ensure app has page access

### Debug Mode
Enable debug mode to see detailed logs:
```bash
DEBUG=true docker compose up api
```

## 📚 Next Steps

Once Meta integration is working:

1. **Set up LinkedIn integration** (similar process)
2. **Configure Instagram publishing** (requires Instagram Business account)
3. **Set up webhooks** for real-time updates
4. **Implement analytics** data collection
5. **Add error handling** and retry logic

## 🔒 Security Notes

- **Never commit** your `.env` file to version control
- **Use environment variables** in production
- **Rotate tokens** regularly
- **Monitor API usage** to avoid rate limits
- **Use HTTPS** in production

## 📞 Support

If you encounter issues:
1. Check the [Facebook Developers Documentation](https://developers.facebook.com/docs/)
2. Review the [Graph API Reference](https://developers.facebook.com/docs/graph-api/)
3. Check your app's error logs in the Facebook Developer Console
