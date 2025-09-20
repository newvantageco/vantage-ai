# Brave Search Integration for VANTAGE AI

This document describes the Brave Search API integration that has been added to the VANTAGE AI platform, providing comprehensive search capabilities for content research, competitive analysis, and market monitoring.

## Overview

The Brave Search integration adds powerful search functionality to VANTAGE AI, including:

- **Web Search** - General web search with AI-powered summaries
- **Local Business Search** - Find nearby businesses and services
- **Image Search** - Search for images with filtering options
- **Video Search** - Find videos across the web
- **News Search** - Current news articles with freshness controls
- **AI Summarizer** - Generate intelligent summaries from search results

## Features

### 🔍 Search Types

1. **Web Search** - Comprehensive web search with optional AI summaries
2. **Local Search** - Find local businesses with ratings, prices, and locations
3. **Image Search** - Visual content discovery with size, color, and type filters
4. **Video Search** - Video content search with duration filters
5. **News Search** - Current news with freshness controls and breaking news indicators

### 🤖 AI-Powered Features

- **Smart Summaries** - AI-generated summaries from search results
- **Content Research** - Automated topic research for content planning
- **Competitive Analysis** - Find and analyze competitors
- **Market Monitoring** - Track industry trends and news
- **Sentiment Analysis** - Analyze brand mentions and sentiment

## API Endpoints

### Web Search
```http
POST /api/v1/brave-search/web
Content-Type: application/json

{
  "query": "artificial intelligence marketing trends",
  "count": 10,
  "summary": true,
  "freshness": "pd"
}
```

### News Search
```http
POST /api/v1/brave-search/news
Content-Type: application/json

{
  "query": "AI marketing automation",
  "count": 20,
  "freshness": "pd"
}
```

### Image Search
```http
POST /api/v1/brave-search/images
Content-Type: application/json

{
  "query": "digital marketing infographic",
  "count": 10,
  "size": "large",
  "color": "blue"
}
```

### Local Search
```http
POST /api/v1/brave-search/local
Content-Type: application/json

{
  "query": "marketing agencies",
  "location": "San Francisco, CA",
  "count": 10
}
```

### AI Summary
```http
POST /api/v1/brave-search/summary
Content-Type: application/json

{
  "summary_key": "your_summary_key_here",
  "entity_info": true,
  "inline_references": true
}
```

### Quick Search Endpoints

For simple searches, use these GET endpoints:

```http
GET /api/v1/brave-search/quick/web?q=AI marketing&count=5&summary=true
GET /api/v1/brave-search/quick/news?q=marketing trends&count=10
```

### Health Check
```http
GET /api/v1/brave-search/health
```

## Python Integration

### Basic Usage

```python
from app.integrations.brave_search import search_web, search_news, search_images

# Web search with AI summary
results = await search_web(
    query="AI marketing trends 2024",
    count=10,
    summary=True
)

print(f"Found {len(results.results)} results")
if results.summary:
    print(f"AI Summary: {results.summary}")
```

### High-Level Service Usage

```python
from app.services.brave_search_service import (
    research_topic,
    find_competitors_for_business,
    monitor_industry,
    get_content_inspiration,
    analyze_brand_sentiment
)

# Content research
research = await research_topic(
    topic="AI marketing automation",
    include_news=True,
    include_images=True
)

# Competitor analysis
competitors = await find_competitors_for_business(
    business_name="VANTAGE AI",
    industry="marketing automation",
    location="San Francisco, CA"
)

# Industry monitoring
trends = await monitor_industry(
    industry="artificial intelligence",
    keywords=["marketing", "automation", "AI"]
)

# Content inspiration
inspiration = await get_content_inspiration(
    content_type="blog post",
    target_audience="marketers",
    industry="technology"
)

# Brand sentiment analysis
sentiment = await analyze_brand_sentiment(
    brand_name="VANTAGE AI",
    product_name="marketing platform"
)
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Brave Search API Configuration
BRAVE_API_KEY=your_brave_api_key_here
```

### API Key Setup

1. Sign up for a Brave Search API account at [https://search.brave.com/help/api](https://search.brave.com/help/api)
2. Choose a plan:
   - **Free**: 2,000 queries/month, basic web search
   - **Pro**: Enhanced features including local search, AI summaries, extra snippets
3. Generate your API key from the developer dashboard
4. Add the key to your `.env` file

## Setup Instructions

### Automatic Setup

Run the setup script:

```bash
./scripts/setup-brave-search.sh
```

### Manual Setup

1. **Add API key to environment:**
   ```bash
   echo "BRAVE_API_KEY=your_api_key_here" >> .env
   ```

2. **Install dependencies:**
   ```bash
   pip install aiohttp==3.9.1
   ```

3. **Test the integration:**
   ```bash
   python test_brave_search.py
   ```

4. **Start the server:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Use Cases in VANTAGE AI

### 1. Content Research
- Research topics for blog posts and articles
- Find trending topics in your industry
- Discover content ideas and inspiration

### 2. Competitive Analysis
- Find competitors in your market
- Analyze competitor content and strategies
- Monitor competitor mentions and news

### 3. Market Monitoring
- Track industry trends and developments
- Monitor brand mentions and sentiment
- Stay updated with relevant news

### 4. Content Planning
- Find visual inspiration for creative content
- Research topics for social media posts
- Discover trending hashtags and topics

### 5. Lead Generation
- Find local businesses in your target market
- Research potential clients and partners
- Discover industry events and conferences

## Error Handling

The integration includes comprehensive error handling:

- **API Key Validation** - Checks for valid API key on startup
- **Rate Limiting** - Respects Brave Search API rate limits
- **Network Errors** - Handles connection issues gracefully
- **Data Validation** - Validates search parameters and responses

## Rate Limits

Brave Search API has the following limits:

- **Free Plan**: 2,000 queries/month
- **Pro Plan**: Higher limits with additional features
- **Rate Limiting**: Built-in rate limiting to prevent exceeding limits

## Security Considerations

- **API Key Security** - Store API keys in environment variables
- **Input Validation** - All search parameters are validated
- **Error Sanitization** - Error messages don't expose sensitive information
- **CORS Configuration** - Proper CORS settings for web access

## Monitoring and Logging

The integration includes:

- **Health Checks** - Monitor API availability
- **Request Logging** - Log all search requests
- **Error Tracking** - Track and log errors
- **Performance Metrics** - Monitor search response times

## Troubleshooting

### Common Issues

1. **Invalid API Key**
   ```
   Error: BRAVE_API_KEY environment variable is required
   ```
   Solution: Add your API key to the `.env` file

2. **Rate Limit Exceeded**
   ```
   Error: Rate limit exceeded
   ```
   Solution: Wait before making more requests or upgrade your plan

3. **Network Errors**
   ```
   Error: Connection failed
   ```
   Solution: Check your internet connection and try again

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("app.integrations.brave_search").setLevel(logging.DEBUG)
```

## Support

For issues with the Brave Search integration:

1. Check the [Brave Search API documentation](https://search.brave.com/help/api)
2. Review the error logs in your application
3. Test with the provided test script: `python test_brave_search.py`
4. Check the health endpoint: `GET /api/v1/brave-search/health`

## Future Enhancements

Planned improvements:

- **Caching** - Cache search results for better performance
- **Analytics** - Track search usage and patterns
- **Advanced Filters** - More sophisticated search filtering
- **Batch Operations** - Support for multiple searches at once
- **Webhook Integration** - Real-time search result notifications

---

**Note**: This integration requires a valid Brave Search API key. Make sure to keep your API key secure and never commit it to version control.
