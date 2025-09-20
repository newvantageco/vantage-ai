#!/usr/bin/env python3
"""
Test script for AI Content Generation
Tests the real AI API endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get authentication token"""
    print("🔐 Getting authentication token...")
    
    login_payload = {
        "email": "admin@vantage.ai",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/simple/login",
            json=login_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Authentication successful!")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_ai_generation():
    """Test AI content generation endpoint"""
    print("🤖 Testing AI Content Generation...")
    
    # Get auth token first
    token = get_auth_token()
    if not token:
        return False
    
    # Test data
    test_prompt = "Create a social media post about a new AI-powered marketing tool that helps businesses automate their content creation"
    
    payload = {
        "prompt": test_prompt,
        "content_type": "social_post",
        "platform": "facebook",
        "brand_voice": "professional",
        "locale": "en-US",
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print(f"📝 Prompt: {test_prompt}")
        print("🚀 Sending request to AI API...")
        
        response = requests.post(
            f"{API_BASE}/ai/generate",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Generation Successful!")
            print(f"📄 Generated Content: {result.get('content', 'No content')}")
            print(f"💰 Cost: ${result.get('cost_usd', 0):.4f}")
            print(f"🔢 Tokens: {result.get('tokens_used', 0)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_health():
    """Test API health endpoint"""
    print("🔍 Testing API Health...")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API Health Check Passed!")
            print(f"📊 Status: {health_data.get('status')}")
            print(f"🗄️ Database: {health_data.get('database')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 VANTAGE AI - AI Generation Test Suite")
    print("=" * 50)
    
    # Test 1: API Health
    health_ok = test_api_health()
    print()
    
    if not health_ok:
        print("❌ API is not healthy. Please check the backend.")
        return
    
    # Test 2: AI Generation
    ai_ok = test_ai_generation()
    print()
    
    # Summary
    print("📋 Test Summary:")
    print(f"✅ API Health: {'PASS' if health_ok else 'FAIL'}")
    print(f"🤖 AI Generation: {'PASS' if ai_ok else 'FAIL'}")
    
    if health_ok and ai_ok:
        print("\n🎉 All tests passed! AI generation is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
