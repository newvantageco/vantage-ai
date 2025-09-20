# Social Media Integration Documentation

## Overview

The Vantage AI social media integration provides comprehensive support for publishing content to major social media platforms including Facebook, Instagram, LinkedIn, and Google My Business. The system includes OAuth authentication, content publishing, webhook processing, and analytics integration.

## Architecture

### Components

1. **OAuth Integrations** - Handle authentication with social media platforms
2. **Publisher Classes** - Platform-specific content publishing logic
3. **Webhook Processing** - Handle incoming events from platforms
4. **HTTP Client** - Robust API client with rate limiting and error handling

### Supported Platforms

| Platform | OAuth | Publishing | Webhooks | Status |
|----------|-------|------------|----------|--------|
| Facebook | ✅ | ✅ | ✅ | Complete |
| Instagram | ✅ | ✅ | ✅ | Complete |
| LinkedIn | ✅ | ✅ | ✅ | Complete |
| Google My Business | ✅ | ✅ | ✅ | Complete |
| TikTok Ads | ⚠️ | ⚠️ | ⚠️ | Partial |
| WhatsApp | ⚠️ | ⚠️ | ⚠️ | Partial |

## OAuth Integration

### Facebook/Meta OAuth

**Endpoint**: `/api/v1/oauth/meta/authorize`

**Required Environment Variables**:
```bash
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_REDIRECT_URI=https://your-domain.com/oauth/meta/callback
META_PAGE_ID=your_facebook_page_id
META_IG_BUSINESS_ID=your_instagram_business_id
```

**OAuth Flow**:
1. User clicks "Connect Facebook" button
2. Redirected to Facebook OAuth with required scopes
3. User authorizes the application
4. Callback receives authorization code
5. Code exchanged for access token
6. Token stored encrypted in database

**Required Scopes**:
- `pages_manage_metadata`
- `pages_read_engagement`
- `instagram_basic`
- `instagram_manage_comments`
- `pages_manage_posts`

### LinkedIn OAuth

**Endpoint**: `/api/v1/oauth/linkedin/authorize`

**Required Environment Variables**:
```bash
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URL=https://your-domain.com/oauth/linkedin/callback
LINKEDIN_PAGE_URN=urn:li:organization:123456
```

**Required Scopes**:
- `r_liteprofile`
- `r_emailaddress`
- `w_member_social`

### Google My Business OAuth

**Endpoint**: `/api/v1/oauth/google/authorize`

**Required Environment Variables**:
```bash
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URL=https://your-domain.com/oauth/google/callback
GOOGLE_BUSINESS_LOCATION_ID=123456789
```

## Publisher Classes

### MetaPublisher (Facebook/Instagram)

**Features**:
- Text posts with character limit validation (2,200 chars)
- Image and video media support
- Scheduled posting
- Hashtag optimization
- Engagement analytics

**Usage**:
```python
from app.services.publishers.meta import MetaPublisher

publisher = MetaPublisher()
platform_opts = PlatformOptions(
    account_id="user_123",
    settings={
        "access_token": "encrypted_token",
        "page_id": "123456789"
    }
)

# Preview content
preview = await publisher.preview(content, media, platform_opts)

# Publish content
result = await publisher.publish(content, media, platform_opts)
```

**Content Validation**:
- Maximum 2,200 characters
- Maximum 10 media items
- Hashtag count warnings (>30 hashtags)
- Media type validation (image, video)

### LinkedInPublisher

**Features**:
- Professional content optimization
- Text posts with character limit (3,000 chars)
- Image media support
- Hashtag recommendations (max 5)
- Professional tone validation

**Usage**:
```python
from app.services.publishers.linkedin import LinkedInPublisher

publisher = LinkedInPublisher()
platform_opts = PlatformOptions(
    account_id="user_123",
    settings={
        "access_token": "encrypted_token",
        "person_urn": "urn:li:person:123456"
    }
)
```

**Content Validation**:
- Maximum 3,000 characters
- Maximum 9 media items
- Maximum 5 hashtags recommended
- Professional tone warnings

### GoogleGBPPublisher

**Features**:
- Local business optimization
- Text posts with character limit (1,500 chars)
- Image and video media support
- Call-to-action buttons
- Local keyword suggestions

**Usage**:
```python
from app.services.publishers.google_gbp import GoogleGBPPublisher

publisher = GoogleGBPPublisher()
platform_opts = PlatformOptions(
    account_id="user_123",
    settings={
        "access_token": "encrypted_token",
        "account_id": "123456789",
        "location_id": "987654321",
        "cta_url": "https://example.com"
    }
)
```

**Content Validation**:
- Maximum 1,500 characters
- Maximum 10 media items
- Maximum 3 hashtags recommended
- Local business keyword suggestions

## HTTP Client

### SocialMediaClient

**Features**:
- Rate limiting per platform
- Automatic retry with exponential backoff
- Error handling and logging
- Authentication header management
- Request/response logging

**Rate Limits**:
- Meta: 200 requests/hour
- LinkedIn: 100 requests/hour
- Google: 1,000 requests/hour
- TikTok: 100 requests/hour

**Usage**:
```python
from app.utils.social_media_client import SocialMediaClient

async with SocialMediaClient("meta", "https://graph.facebook.com/v18.0") as client:
    response = await client.get("/me", access_token="token")
    data = await client.post("/feed", data={"message": "Hello"}, access_token="token")
```

## Webhook Processing

### Supported Webhooks

1. **Meta Webhooks** - `/api/v1/webhooks/meta`
   - Post engagement (likes, comments, shares)
   - Comment notifications
   - Page updates

2. **LinkedIn Webhooks** - `/api/v1/webhooks/linkedin`
   - Post creation/updates
   - Engagement metrics
   - Profile updates

3. **Google My Business Webhooks** - `/api/v1/webhooks/google`
   - Post status updates
   - Review notifications
   - Business information changes

4. **WhatsApp Webhooks** - `/api/v1/webhooks/whatsapp`
   - Message notifications
   - Status updates
   - Template updates

### Webhook Processing

Webhooks are processed asynchronously using Celery tasks:

```python
@celery_app.task(bind=True, max_retries=3)
def process_platform_webhook(self, webhook_id: str, platform: str, payload: Dict[str, Any], signature: str):
    # Process webhook based on platform
    # Update analytics and metrics
    # Handle errors with retry logic
```

**Processing Features**:
- Signature verification
- Duplicate detection
- Error handling and retries
- Analytics integration
- Database updates

## Error Handling

### Error Types

1. **AuthenticationError** - Invalid or expired tokens
2. **ValidationError** - Content validation failures
3. **PublishingError** - Platform-specific publishing errors
4. **APIError** - HTTP/API related errors
5. **RateLimitError** - Rate limit exceeded

### Error Recovery

- Automatic token refresh
- Exponential backoff retry
- Graceful degradation
- User-friendly error messages

## Security

### Token Management

- All tokens encrypted at rest using Fernet encryption
- Automatic token refresh before expiration
- Secure token storage in database
- No plaintext token logging

### Webhook Security

- Signature verification for all webhooks
- IP whitelisting (recommended)
- Rate limiting on webhook endpoints
- Input validation and sanitization

## Monitoring and Analytics

### Metrics Tracked

- Publishing success/failure rates
- API response times
- Rate limit usage
- Webhook processing times
- Error rates by platform

### Logging

- Structured logging with correlation IDs
- Platform-specific log levels
- Error tracking and alerting
- Performance monitoring

## Testing

### Test Coverage

- Unit tests for all publisher classes
- Integration tests for OAuth flows
- Webhook processing tests
- Error handling tests
- Rate limiting tests

### Running Tests

```bash
# Run all social media integration tests
python test_social_media_integration.py

# Run specific test class
pytest test_social_media_integration.py::TestMetaPublisher

# Run with coverage
pytest --cov=app.services.publishers test_social_media_integration.py
```

## Configuration

### Environment Variables

See `env.example` for complete list of required environment variables.

### Database Schema

Required tables:
- `platform_integrations` - OAuth tokens and settings
- `external_references` - Published content references
- `webhook_events` - Webhook event logs

### Redis Configuration

Used for:
- Rate limiting counters
- Caching API responses
- Session management

## Deployment

### Prerequisites

1. Social media app registrations
2. OAuth redirect URLs configured
3. Webhook endpoints registered
4. SSL certificates for webhooks
5. Database migrations applied

### Environment Setup

1. Copy `env.example` to `.env`
2. Configure all required environment variables
3. Set up Redis instance
4. Configure database connection
5. Run database migrations

### Monitoring

- Set up logging aggregation
- Configure error alerting
- Monitor API rate limits
- Track webhook delivery rates

## Troubleshooting

### Common Issues

1. **OAuth Token Expired**
   - Check token refresh logic
   - Verify OAuth app configuration
   - Check token storage encryption

2. **Rate Limit Exceeded**
   - Check rate limiting configuration
   - Implement request queuing
   - Monitor API usage patterns

3. **Webhook Not Receiving**
   - Verify webhook URL configuration
   - Check signature verification
   - Verify SSL certificate

4. **Publishing Failures**
   - Check content validation
   - Verify platform credentials
   - Check API endpoint URLs

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export SOCIAL_MEDIA_DEBUG=true
```

## Future Enhancements

### Planned Features

1. **Additional Platforms**
   - Twitter/X integration
   - YouTube Shorts
   - Pinterest
   - Snapchat

2. **Advanced Features**
   - AI-powered content optimization
   - Cross-platform scheduling
   - Advanced analytics dashboard
   - A/B testing for posts

3. **Performance Improvements**
   - Bulk publishing
   - Async media processing
   - Caching optimizations
   - Database query optimization

## Support

For issues and questions:
- Check the troubleshooting section
- Review logs for error details
- Contact the development team
- Create GitHub issues for bugs
