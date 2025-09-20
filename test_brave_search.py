"""
Test script for Brave Search integration
"""

import asyncio
import os
from app.integrations.brave_search import (
    BraveSearchClient,
    search_web,
    search_news,
    search_images,
    get_ai_summary
)

async def test_brave_search():
    """Test Brave Search functionality"""
    
    # Set the API key
    os.environ["BRAVE_API_KEY"] = "BSAso6On09fy4xKCg9FDG58TkRSqMWd"
    
    try:
        print("🔍 Testing Brave Search Integration...")
        
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
        
        # Test 3: Image Search
        print("\n3. Testing Image Search...")
        image_results = await search_images(
            query="digital marketing infographic",
            count=3
        )
        
        print(f"✅ Image Search Results: {len(image_results.results)} results")
        print(f"   Query: {image_results.query}")
        
        # Show first image result
        if image_results.results:
            first_image = image_results.results[0]
            print(f"   First Image: {first_image.title}")
            print(f"   URL: {first_image.url}")
            if first_image.thumbnail:
                print(f"   Thumbnail: {first_image.thumbnail}")
        
        # Test 4: AI Summary (if we have a summary key)
        if web_results.summary_key:
            print("\n4. Testing AI Summary...")
            try:
                summary = await get_ai_summary(web_results.summary_key)
                print(f"✅ AI Summary Generated: {len(summary)} characters")
                print(f"   Summary: {summary[:300]}...")
            except Exception as e:
                print(f"❌ AI Summary failed: {e}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_health_check():
    """Test health check functionality"""
    print("\n🏥 Testing Health Check...")
    
    try:
        async with BraveSearchClient() as client:
            # This will test the API key and connection
            await client.web_search("test", count=1)
        print("✅ Health check passed - API key is valid")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Brave Search Integration Tests")
    print("=" * 50)
    
    # Run the tests
    asyncio.run(test_brave_search())
    asyncio.run(test_health_check())
    
    print("\n" + "=" * 50)
    print("✨ Test suite completed!")
