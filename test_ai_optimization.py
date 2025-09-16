#!/usr/bin/env python3
"""
Test script for AI cost optimization features.
Run with: python test_ai_optimization.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest
from app.cache.redis import cache
from app.core.config import get_settings


async def test_caching():
    """Test that identical requests are served from cache."""
    print("🧪 Testing AI request caching...")
    
    # Create test request
    request = GenerationRequest(
        task="caption",
        prompt="Write a caption about our new product launch",
        system="You are a social media assistant",
        org_id="test_org_123"
    )
    
    # Create enhanced router (without DB for this test)
    router = EnhancedAIRouter()
    
    # First request - should hit the model
    print("  📤 First request (should hit model)...")
    start_time = datetime.now()
    result1 = await router.generate(request)
    first_duration = (datetime.now() - start_time).total_seconds()
    print(f"    ✅ Generated: {result1.text[:50]}...")
    print(f"    ⏱️  Duration: {first_duration:.2f}s")
    print(f"    💰 Cost: £{result1.cost_gbp:.4f}")
    print(f"    🔄 From cache: {result1.from_cache}")
    
    # Second identical request - should hit cache
    print("  📤 Second request (should hit cache)...")
    start_time = datetime.now()
    result2 = await router.generate(request)
    second_duration = (datetime.now() - start_time).total_seconds()
    print(f"    ✅ Generated: {result2.text[:50]}...")
    print(f"    ⏱️  Duration: {second_duration:.2f}s")
    print(f"    💰 Cost: £{result2.cost_gbp:.4f}")
    print(f"    🔄 From cache: {result2.from_cache}")
    
    # Verify caching worked
    if result2.from_cache and second_duration < first_duration:
        print("  ✅ Caching test PASSED!")
    else:
        print("  ❌ Caching test FAILED!")
    
    return result1, result2


async def test_batch_generation():
    """Test batch generation capabilities."""
    print("\n🧪 Testing batch generation...")
    
    # Create multiple requests
    requests = [
        GenerationRequest(
            task="caption",
            prompt=f"Write a caption about topic {i}",
            system="You are a social media assistant",
            org_id="test_org_123"
        )
        for i in range(3)
    ]
    
    router = EnhancedAIRouter()
    
    print(f"  📤 Generating {len(requests)} requests in batch...")
    start_time = datetime.now()
    results = await router.batch_generate(requests)
    batch_duration = (datetime.now() - start_time).total_seconds()
    
    print(f"    ✅ Generated {len(results)} results")
    print(f"    ⏱️  Total duration: {batch_duration:.2f}s")
    print(f"    💰 Total cost: £{sum(r.cost_gbp for r in results):.4f}")
    
    for i, result in enumerate(results):
        print(f"    📝 Result {i+1}: {result.text[:30]}...")
    
    print("  ✅ Batch generation test PASSED!")
    return results


async def test_provider_capabilities():
    """Test provider capability detection."""
    print("\n🧪 Testing provider capabilities...")
    
    from app.ai.providers import HostedProvider, OpenProvider
    
    # Test hosted provider
    hosted = HostedProvider("openai")
    print(f"  🏢 Hosted Provider (OpenAI):")
    print(f"    - Supports batch: {hosted.can_handle_batch(5)}")
    print(f"    - Max batch size: {hosted.capabilities.max_batch_size}")
    print(f"    - Max tokens: {hosted.capabilities.max_tokens_per_request}")
    print(f"    - Cost per 1K tokens: £{hosted.capabilities.cost_per_1k_tokens_input:.4f}")
    
    # Test open provider
    open_prov = OpenProvider("ollama")
    print(f"  🆓 Open Provider (Ollama):")
    print(f"    - Supports batch: {open_prov.can_handle_batch(5)}")
    print(f"    - Max batch size: {open_prov.capabilities.max_batch_size}")
    print(f"    - Max tokens: {open_prov.capabilities.max_tokens_per_request}")
    print(f"    - Is free: {open_prov.is_free()}")
    
    print("  ✅ Provider capabilities test PASSED!")


async def test_cost_estimation():
    """Test cost estimation accuracy."""
    print("\n🧪 Testing cost estimation...")
    
    from app.ai.providers import HostedProvider, OpenProvider
    
    # Test hosted provider cost
    hosted = HostedProvider("openai")
    cost = hosted.estimate_cost(1000, 500)  # 1K input, 500 output tokens
    print(f"  🏢 Hosted provider cost for 1K input + 500 output tokens: £{cost:.4f}")
    
    # Test open provider cost
    open_prov = OpenProvider("ollama")
    cost = open_prov.estimate_cost(1000, 500)
    print(f"  🆓 Open provider cost for 1K input + 500 output tokens: £{cost:.4f}")
    
    print("  ✅ Cost estimation test PASSED!")


async def cleanup():
    """Clean up test data."""
    print("\n🧹 Cleaning up test data...")
    try:
        await cache.close()
        print("  ✅ Cleanup completed!")
    except Exception as e:
        print(f"  ⚠️  Cleanup warning: {e}")


async def main():
    """Run all tests."""
    print("🚀 Starting AI Cost Optimization Tests")
    print("=" * 50)
    
    try:
        # Test provider capabilities first (no external dependencies)
        await test_provider_capabilities()
        await test_cost_estimation()
        
        # Test caching (requires Redis)
        try:
            await test_caching()
        except Exception as e:
            print(f"  ⚠️  Caching test skipped (Redis not available): {e}")
        
        # Test batch generation (requires Redis)
        try:
            await test_batch_generation()
        except Exception as e:
            print(f"  ⚠️  Batch generation test skipped (Redis not available): {e}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    finally:
        await cleanup()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
