"""
Simple test script for Brave Search integration
Tests only the working endpoints
"""

import asyncio
import os
from app.integrations.brave_search import search_web, search_news

async def test_simple_brave_search():
    """Test only the working Brave Search functionality"""
    
    # Set the API key
    os.environ["BRAVE_API_KEY"] = "BSAso6On09fy4xKCg9FDG58TkRSqMWd"
    
    try:
        print("🔍 Testing Brave Search Integration (Simple)...")
        
        # Test 1: Web Search
        print("\n1. Testing Web Search...")
        web_results = await search_web(
            query="artificial intelligence marketing trends 2024",
            count=5,
            summary=True
        )
        
        print(f"✅ Web Search Results: {len(web_results.results)} results")
        print(f"   Query: {web_results.query}")
        print(f"   Total Results: {web_results.total_results}")
        print(f"   Search Time: {web_results.search_time}s")
        
        if web_results.summary:
            print(f"   AI Summary: {web_results.summary[:200]}...")
        
        # Show first result
        if web_results.results:
            first_result = web_results.results[0]
            print(f"   First Result: {first_result.title}")
            print(f"   URL: {first_result.url}")
        
        # Test 2: News Search
        print("\n2. Testing News Search...")
        news_results = await search_news(
            query="AI marketing automation",
            count=3,
            freshness="pd"  # past day
        )
        
        print(f"✅ News Search Results: {len(news_results.results)} results")
        print(f"   Query: {news_results.query}")
        print(f"   Total Results: {news_results.total_results}")
        
        # Show first news result
        if news_results.results:
            first_news = news_results.results[0]
            print(f"   First News: {first_news.title}")
            print(f"   Source: {first_news.source}")
            print(f"   Published: {first_news.published_date}")
        
        print("\n🎉 Basic tests completed successfully!")
        print("   Note: Some endpoints (images, videos, local) may not be available on the free plan")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Simple Brave Search Integration Test")
    print("=" * 50)
    
    # Run the tests
    asyncio.run(test_simple_brave_search())
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")
