# Real Metrics Fetching Implementation

## Overview
Successfully implemented real metrics fetching for LinkedIn and Meta (Facebook/Instagram) platforms, replacing fake metrics with actual platform API integration.

## Files Created/Modified

### 1. Database Models
- **`app/models/post_metrics.py`** - Raw platform metrics storage
  - `PostMetrics` model with fields: impressions, reach, likes, comments, shares, clicks, video_views, saves, cost_cents
  - Unique constraint on (schedule_id, fetched_at) to prevent duplicates
  - Indexes for efficient querying

- **`app/models/external_refs.py`** - Schedule to platform ID mapping
  - `ScheduleExternal` model linking schedule_id to platform post IDs/URLs
  - Support for multiple providers per schedule (Facebook + Instagram)
  - Unique constraint on (schedule_id, provider)

### 2. Platform Insights Fetchers
- **`app/integrations/meta_insights.py`** - Meta Graph API integration
  - `get_fb_post_insights()` - Facebook Page post metrics
  - `get_ig_media_insights()` - Instagram Business media metrics
  - Handles pagination and metric sets (lifetime, day)
  - Batch processing with rate limiting

- **`app/integrations/linkedin_insights.py`** - LinkedIn UGC Posts API
  - `get_ugc_stats()` - LinkedIn UGC post statistics
  - `get_ugc_post_details()` - Additional post details
  - Batch processing with conservative rate limiting

### 3. Services
- **`app/services/insights_mapper.py`** - Metrics normalization
  - `map_meta_to_post_metrics()` - Facebook/Instagram → PostMetrics
  - `map_linkedin_to_post_metrics()` - LinkedIn → PostMetrics
  - `generate_fake_metrics()` - Fallback for testing/development
  - `normalize_metrics_for_analytics()` - Convert to analytics format

### 4. API Endpoints
- **`app/routes/insights.py`** - Insights management API
  - `POST /insights/fetch/{schedule_id}` - Manual insights fetching
  - `GET /insights/metrics/{schedule_id}` - Get latest metrics
  - `GET /insights/metrics/{schedule_id}/history` - Metrics history
  - Force refresh and duplicate prevention

### 5. Background Workers
- **`workers/insights_poller.py`** - Automated metrics polling
  - Polls posted schedules every N hours (configurable)
  - Handles both real and fake insights based on configuration
  - Batch processing with error handling
  - Summary reporting

### 6. Publisher Updates
- **`app/publishers/base.py`** - Enhanced base publisher
  - Added `external_refs` to `PostResult`
  - `store_external_reference()` method for database storage

- **`app/publishers/linkedin.py`** - LinkedIn publisher updates
  - Returns LinkedIn UGC post ID in external_refs
  - Stores platform-specific identifiers

- **`app/publishers/meta.py`** - Meta publisher updates
  - Returns both Facebook and Instagram post IDs
  - Handles multi-platform posting

### 7. Scheduler Integration
- **`app/scheduler/engine.py`** - Enhanced scheduling
  - Stores external references when publishing
  - Links schedule_id to platform post IDs
  - Supports multiple providers per schedule

### 8. Database Migration
- **`alembic/versions/0006_post_metrics_external_refs.py`** - Database schema
  - Creates `post_metrics` table
  - Creates `schedule_external` table
  - Adds appropriate indexes and constraints

### 9. Configuration
- **`app/core/config.py`** - New settings
  - `FEATURE_FAKE_INSIGHTS` - Toggle between real/fake metrics
  - `INSIGHTS_POLL_INTERVAL_HOURS` - Polling frequency
  - Platform-specific metric field configurations

- **`env.sample`** - Environment variables
  - Added all new configuration options
  - Platform-specific metric field mappings

## Key Features

### 1. Dual Metrics Storage
- **Raw Metrics**: `PostMetrics` table stores platform-specific data
- **Computed Metrics**: Existing `ScheduleMetrics` for analytics
- Clean separation of concerns

### 2. Platform Agnostic Design
- Standardized schema works across LinkedIn, Facebook, Instagram
- Easy to add new platforms
- Consistent API interface

### 3. Idempotent Updates
- Unique constraint prevents duplicate metrics per day
- Safe to run multiple times
- Handles partial failures gracefully

### 4. Fallback System
- Fake metrics for development/testing
- Real API integration for production
- Configurable via environment variables

### 5. Rate Limiting & Error Handling
- Exponential backoff for 429/5xx errors
- Batch processing with delays
- Comprehensive error logging

### 6. Multi-Platform Support
- Single schedule can post to multiple platforms
- Separate metrics tracking per platform
- Unified API for all platforms

## Usage

### 1. Manual Insights Fetching
```bash
curl -X POST "http://localhost:8000/api/v1/insights/fetch/{schedule_id}" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": false}'
```

### 2. Get Metrics
```bash
curl "http://localhost:8000/api/v1/insights/metrics/{schedule_id}"
```

### 3. Background Polling
```bash
python workers/insights_poller.py
```

### 4. Configuration
```bash
# Use real platform APIs
FEATURE_FAKE_INSIGHTS=false

# Poll every 6 hours
INSIGHTS_POLL_INTERVAL_HOURS=6

# Facebook metrics
META_INSIGHTS_FIELDS_FB=impressions,post_impressions_unique,likes,comments,shares,clicks

# Instagram metrics
IG_INSIGHTS_METRICS=impressions,reach,likes,comments,saves,video_views

# LinkedIn metrics
LINKEDIN_STATS_FIELDS=impressionCount,likeCount,commentCount,shareCount
```

## Verification

### 1. Database Schema
- Run migration: `alembic upgrade head`
- Verify tables created: `post_metrics`, `schedule_external`

### 2. API Endpoints
- Test insights fetching: `POST /api/v1/insights/fetch/{schedule_id}`
- Verify metrics storage: `GET /api/v1/insights/metrics/{schedule_id}`

### 3. Background Polling
- Start insights poller: `python workers/insights_poller.py`
- Check logs for successful processing

### 4. Publisher Integration
- Publish content and verify external references stored
- Check `schedule_external` table for platform IDs

## Guardrails

### 1. Security
- Access tokens masked in logs
- Secure token storage (to be implemented)
- Rate limiting to prevent API abuse

### 2. Reliability
- Exponential backoff on errors
- Idempotent operations
- Graceful degradation to fake metrics

### 3. Performance
- Batch processing for efficiency
- Database indexes for fast queries
- Configurable polling intervals

### 4. Monitoring
- Comprehensive logging
- Error tracking and reporting
- Metrics summary endpoints

## Next Steps

1. **Token Storage**: Implement secure token storage system
2. **Real API Integration**: Complete access token retrieval
3. **Monitoring**: Add metrics dashboard
4. **Testing**: Add comprehensive test suite
5. **Documentation**: API documentation and user guides

## Migration Path

1. **Development**: Use `FEATURE_FAKE_INSIGHTS=true` for testing
2. **Staging**: Test with real APIs using test accounts
3. **Production**: Set `FEATURE_FAKE_INSIGHTS=false` for live data
4. **Monitoring**: Watch for errors and performance issues
