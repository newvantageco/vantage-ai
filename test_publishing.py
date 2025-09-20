#!/usr/bin/env python3
"""
Test script for Social Media Publishing
Tests the real publishing API endpoints
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

def test_publishing_status():
    """Test publishing service status"""
    print("📊 Testing Publishing Service Status...")
    
    try:
        response = requests.get(f"{API_BASE}/publish/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Publishing Service Status:")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Platforms: {', '.join(status_data.get('supported_platforms', []))}")
            print(f"   Features: {', '.join(status_data.get('features', []))}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_supported_platforms():
    """Test getting supported platforms"""
    print("🌐 Testing Supported Platforms...")
    
    try:
        response = requests.get(f"{API_BASE}/publish/platforms", timeout=10)
        if response.status_code == 200:
            platforms_data = response.json()
            platforms = platforms_data.get('platforms', [])
            print("✅ Supported Platforms:")
            for platform in platforms:
                print(f"   📱 {platform['name']} ({platform['id']})")
                print(f"      Max text: {platform['max_text_length']} chars")
                print(f"      Max media: {platform['max_media_items']} items")
                print(f"      Media types: {', '.join(platform['supported_media'])}")
            return True
        else:
            print(f"❌ Platforms check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Platforms check error: {e}")
        return False

def test_content_preview():
    """Test content preview functionality"""
    print("👀 Testing Content Preview...")
    
    # Test content
    test_content = """🚀 Exciting news! We're launching our new AI-powered marketing platform that helps businesses automate their content creation and social media management.

Key features:
✨ AI content generation
📱 Multi-platform publishing
📊 Real-time analytics
🎯 Audience targeting

Ready to transform your marketing strategy? Let's get started! 💪

#AI #Marketing #Automation #SocialMedia #Business"""

    preview_payload = {
        "content": test_content,
        "platform": "facebook",
        "media": [
            {
                "url": "https://example.com/image.jpg",
                "type": "image",
                "caption": "AI Marketing Platform"
            }
        ]
    }
    
    try:
        print(f"📝 Testing preview for Facebook...")
        print(f"Content length: {len(test_content)} characters")
        
        response = requests.post(
            f"{API_BASE}/publish/preview",
            json=preview_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            preview_data = response.json()
            print("✅ Content Preview Results:")
            print(f"   Valid: {preview_data.get('is_valid')}")
            print(f"   Character count: {preview_data.get('character_count')}")
            print(f"   Warnings: {len(preview_data.get('warnings', []))}")
            print(f"   Errors: {len(preview_data.get('errors', []))}")
            
            if preview_data.get('warnings'):
                print("   ⚠️ Warnings:")
                for warning in preview_data['warnings']:
                    print(f"      - {warning}")
            
            if preview_data.get('errors'):
                print("   ❌ Errors:")
                for error in preview_data['errors']:
                    print(f"      - {error}")
            
            return preview_data.get('is_valid', False)
        else:
            print(f"❌ Preview failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Preview error: {e}")
        return False

def test_publish_validation():
    """Test publishing validation (dry run)"""
    print("🧪 Testing Publish Validation (Dry Run)...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return False
    
    # Test content
    test_content = """🎉 Just launched our new AI marketing platform! 

Transform your social media strategy with:
🤖 AI-powered content creation
📱 Multi-platform publishing
📊 Real-time performance analytics
🎯 Smart audience targeting

Join thousands of businesses already using AI to scale their marketing! 

#AI #Marketing #SocialMedia #Business #Innovation"""

    publish_payload = {
        "content": test_content,
        "platform": "linkedin",
        "media": [],
        "page_id": "test_page_123",
        "access_token": "test_token_123"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print(f"📝 Testing publish validation for LinkedIn...")
        
        response = requests.post(
            f"{API_BASE}/publish/test",
            json=publish_payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            publish_data = response.json()
            print("✅ Publish Validation Results:")
            print(f"   Success: {publish_data.get('success')}")
            print(f"   Platform: {publish_data.get('platform')}")
            print(f"   Message: {publish_data.get('message')}")
            
            if publish_data.get('post_id'):
                print(f"   Post ID: {publish_data.get('post_id')}")
                print(f"   URL: {publish_data.get('url')}")
            
            if publish_data.get('errors'):
                print("   ❌ Errors:")
                for error in publish_data['errors']:
                    print(f"      - {error}")
            
            return publish_data.get('success', False)
        else:
            print(f"❌ Publish validation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Publish validation error: {e}")
        return False

def main():
    """Run all publishing tests"""
    print("🚀 VANTAGE AI - Social Media Publishing Test Suite")
    print("=" * 60)
    
    # Test 1: Service Status
    status_ok = test_publishing_status()
    print()
    
    # Test 2: Supported Platforms
    platforms_ok = test_supported_platforms()
    print()
    
    # Test 3: Content Preview
    preview_ok = test_content_preview()
    print()
    
    # Test 4: Publish Validation
    publish_ok = test_publish_validation()
    print()
    
    # Summary
    print("📋 Publishing Test Summary:")
    print(f"✅ Service Status: {'PASS' if status_ok else 'FAIL'}")
    print(f"✅ Supported Platforms: {'PASS' if platforms_ok else 'FAIL'}")
    print(f"✅ Content Preview: {'PASS' if preview_ok else 'FAIL'}")
    print(f"✅ Publish Validation: {'PASS' if publish_ok else 'FAIL'}")
    
    if all([status_ok, platforms_ok, preview_ok, publish_ok]):
        print("\n🎉 All publishing tests passed! Social media publishing is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
