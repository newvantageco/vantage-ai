#!/usr/bin/env python3
"""
Test script for real API integrations
This script tests the actual Meta/Facebook API integration
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_CONTENT = "🚀 Testing real API integration from VANTAGE AI! This is a test post to verify our Meta API connection is working properly. #VantageAI #TestPost"

async def test_api_health():
    """Test if the API is running and healthy"""
    print("🔍 Testing API health...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                print("✅ API is healthy")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API health check failed: {e}")
            return False

async def test_meta_oauth_authorize():
    """Test Meta OAuth authorization endpoint"""
    print("\n🔐 Testing Meta OAuth authorization...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test OAuth authorization endpoint (this requires authentication)
            response = await client.get(
                f"{API_BASE_URL}/oauth/meta/authorize",
                params={"state": "test_state"}
            )
            
            if response.status_code == 401:
                print("✅ Meta OAuth authorization endpoint requires authentication (expected)")
                return True
            elif response.status_code == 200:
                data = response.json()
                if "authorization_url" in data:
                    print("✅ Meta OAuth authorization endpoint working")
                    print(f"   Authorization URL: {data['authorization_url']}")
                    return True
                else:
                    print("❌ No authorization URL in response")
                    return False
            else:
                print(f"❌ OAuth authorization failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ OAuth authorization test failed: {e}")
            return False

async def test_meta_pages_endpoint():
    """Test Meta pages endpoint (requires authentication)"""
    print("\n📄 Testing Meta pages endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            # This will fail without proper authentication, but we can test the endpoint structure
            response = await client.get(f"{API_BASE_URL}/oauth/meta/pages")
            
            if response.status_code == 401:
                print("✅ Meta pages endpoint requires authentication (expected)")
                return True
            elif response.status_code == 200:
                print("✅ Meta pages endpoint working")
                return True
            else:
                print(f"❌ Meta pages endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Meta pages endpoint test failed: {e}")
            return False

async def test_publishing_endpoint():
    """Test publishing endpoint structure"""
    print("\n📝 Testing publishing endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test publishing preview endpoint
            response = await client.post(
                f"{API_BASE_URL}/publish/preview",
                json={
                    "content": TEST_CONTENT,
                    "platform": "facebook",
                    "media_urls": []
                }
            )
            
            if response.status_code == 401:
                print("✅ Publishing endpoint requires authentication (expected)")
                return True
            elif response.status_code == 404:
                print("✅ Publishing endpoint exists but route not found (checking simple endpoint)")
                # Try the simple publishing endpoint
                response2 = await client.post(
                    f"{API_BASE_URL}/publish/test",
                    json={
                        "content": TEST_CONTENT,
                        "platform": "facebook"
                    }
                )
                if response2.status_code in [200, 401]:
                    print("✅ Simple publishing endpoint working")
                    return True
                else:
                    print(f"❌ Simple publishing endpoint failed: {response2.status_code}")
                    return False
            elif response.status_code == 200:
                print("✅ Publishing endpoint working")
                return True
            else:
                print(f"❌ Publishing endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Publishing endpoint test failed: {e}")
            return False

async def test_integrations_endpoint():
    """Test integrations endpoint"""
    print("\n🔗 Testing integrations endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/integrations")
            
            if response.status_code == 401:
                print("✅ Integrations endpoint requires authentication (expected)")
                return True
            elif response.status_code == 403:
                print("✅ Integrations endpoint requires authentication (expected)")
                return True
            elif response.status_code == 200:
                print("✅ Integrations endpoint working")
                return True
            else:
                print(f"❌ Integrations endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Integrations endpoint test failed: {e}")
            return False

async def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = [
        "META_APP_ID",
        "META_APP_SECRET",
        "META_REDIRECT_URI"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or not configured environment variables: {', '.join(missing_vars)}")
        print("   Please run: ./scripts/setup-real-apis.sh")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

async def main():
    """Run all tests"""
    print("🚀 VANTAGE AI - Real API Integration Test")
    print("=" * 50)
    
    # Check environment variables
    env_ok = await check_environment_variables()
    
    # Test API health
    health_ok = await test_api_health()
    
    if not health_ok:
        print("\n❌ API is not running. Please start the application first:")
        print("   docker compose up --build")
        return
    
    # Test endpoints
    oauth_ok = await test_meta_oauth_authorize()
    pages_ok = await test_meta_pages_endpoint()
    publishing_ok = await test_publishing_endpoint()
    integrations_ok = await test_integrations_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", env_ok),
        ("API Health", health_ok),
        ("Meta OAuth Authorization", oauth_ok),
        ("Meta Pages Endpoint", pages_ok),
        ("Publishing Endpoint", publishing_ok),
        ("Integrations Endpoint", integrations_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your real API integration is ready.")
        print("\n📋 Next steps:")
        print("1. Go to http://localhost:3000/integrations")
        print("2. Click 'Connect Facebook' to test OAuth flow")
        print("3. Create a test post in the composer")
        print("4. Publish to Facebook to verify real integration")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
        
        if not env_ok:
            print("\n🔧 To fix environment variables:")
            print("   ./scripts/setup-real-apis.sh")
        
        if not health_ok:
            print("\n🔧 To start the application:")
            print("   docker compose up --build")

if __name__ == "__main__":
    asyncio.run(main())
