#!/usr/bin/env python3
"""
Test script for OAuth Integration System
Tests the real OAuth integration API endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_oauth_status():
    """Test OAuth integration service status"""
    print("🔗 Testing OAuth Integration Service Status...")
    
    try:
        response = requests.get(f"{API_BASE}/oauth/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ OAuth Integration Service Status:")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Features: {', '.join(status_data.get('features', []))}")
            print(f"   Platforms: {', '.join(status_data.get('supported_platforms', []))}")
            print(f"   OAuth Flows: {', '.join(status_data.get('oauth_flows', []))}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_oauth_platforms():
    """Test getting OAuth platforms and their connection status"""
    print("📱 Testing OAuth Platforms...")
    
    try:
        response = requests.get(f"{API_BASE}/oauth/platforms", timeout=10)
        if response.status_code == 200:
            platforms_data = response.json()
            print("✅ OAuth Platforms:")
            print(f"   Total Platforms: {len(platforms_data)}")
            
            for platform in platforms_data:
                print(f"   📱 {platform['name']} ({platform['platform']}):")
                print(f"      Status: {platform['status']}")
                print(f"      Description: {platform['description']}")
                if platform.get('connected_at'):
                    print(f"      Connected: {platform['connected_at']}")
                if platform.get('expires_at'):
                    print(f"      Expires: {platform['expires_at']}")
                if platform.get('scopes'):
                    print(f"      Scopes: {', '.join(platform['scopes'])}")
                if platform.get('account_info'):
                    print(f"      Account: {platform['account_info']}")
            
            return True
        else:
            print(f"❌ OAuth platforms check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OAuth platforms check error: {e}")
        return False

def test_oauth_connection_initiation():
    """Test initiating OAuth connections"""
    print("🔐 Testing OAuth Connection Initiation...")
    
    try:
        # Test different platforms
        test_platforms = ["facebook", "linkedin", "instagram", "google_gbp"]
        
        for platform in test_platforms:
            print(f"   📱 Testing {platform} connection...")
            
            connection_request = {
                "platform": platform,
                "redirect_uri": f"http://localhost:3000/oauth/{platform}/callback"
            }
            
            response = requests.post(
                f"{API_BASE}/oauth/connect",
                json=connection_request,
                timeout=15
            )
            
            if response.status_code == 200:
                connection_data = response.json()
                if connection_data.get('success'):
                    print(f"      ✅ {platform.title()} connection initiated:")
                    print(f"         Auth URL: {connection_data.get('authorization_url', 'N/A')[:50]}...")
                    print(f"         State: {connection_data.get('state', 'N/A')}")
                    print(f"         Message: {connection_data.get('message', 'N/A')}")
                else:
                    print(f"      ❌ {platform.title()} connection failed: {connection_data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"      ❌ {platform.title()} connection failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ OAuth connection initiation error: {e}")
        return False

def test_oauth_callback_handling():
    """Test OAuth callback handling"""
    print("🔄 Testing OAuth Callback Handling...")
    
    try:
        # Test different platforms
        test_platforms = ["facebook", "linkedin", "instagram", "google_gbp"]
        
        for platform in test_platforms:
            print(f"   📱 Testing {platform} callback...")
            
            callback_request = {
                "code": f"mock_auth_code_{platform}_123",
                "state": f"mock_state_{platform}_456",
                "platform": platform
            }
            
            response = requests.post(
                f"{API_BASE}/oauth/callback",
                json=callback_request,
                timeout=15
            )
            
            if response.status_code == 200:
                callback_data = response.json()
                if callback_data.get('success'):
                    print(f"      ✅ {platform.title()} callback handled:")
                    print(f"         Platform: {callback_data.get('platform', 'N/A')}")
                    print(f"         Message: {callback_data.get('message', 'N/A')}")
                    if callback_data.get('account_info'):
                        account_info = callback_data['account_info']
                        print(f"         Account Info: {list(account_info.keys())}")
                else:
                    print(f"      ❌ {platform.title()} callback failed: {callback_data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"      ❌ {platform.title()} callback failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ OAuth callback handling error: {e}")
        return False

def test_oauth_account_info():
    """Test getting OAuth account information"""
    print("👤 Testing OAuth Account Information...")
    
    try:
        # Test platforms that have account info
        test_platforms = ["facebook", "linkedin"]
        
        for platform in test_platforms:
            print(f"   📱 Testing {platform} account info...")
            
            response = requests.get(f"{API_BASE}/oauth/account/{platform}", timeout=10)
            
            if response.status_code == 200:
                account_data = response.json()
                if account_data.get('success'):
                    print(f"      ✅ {platform.title()} account info:")
                    print(f"         Platform: {account_data.get('platform', 'N/A')}")
                    account_info = account_data.get('account_info', {})
                    print(f"         Account: {account_info.get('page_name', account_info.get('company_name', 'N/A'))}")
                    print(f"         Followers: {account_info.get('followers_count', 'N/A')}")
                    print(f"         Connected: {account_info.get('connected_at', 'N/A')}")
                else:
                    print(f"      ❌ {platform.title()} account info failed: {account_data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"      ❌ {platform.title()} account info failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ OAuth account info error: {e}")
        return False

def test_oauth_token_refresh():
    """Test OAuth token refresh"""
    print("🔄 Testing OAuth Token Refresh...")
    
    try:
        # Test platforms that support token refresh
        test_platforms = ["facebook", "linkedin", "google_gbp"]
        
        for platform in test_platforms:
            print(f"   📱 Testing {platform} token refresh...")
            
            response = requests.get(f"{API_BASE}/oauth/refresh/{platform}", timeout=10)
            
            if response.status_code == 200:
                refresh_data = response.json()
                if refresh_data.get('success'):
                    print(f"      ✅ {platform.title()} token refreshed:")
                    print(f"         Platform: {refresh_data.get('platform', 'N/A')}")
                    print(f"         New Expires: {refresh_data.get('new_expires_at', 'N/A')}")
                    print(f"         Message: {refresh_data.get('message', 'N/A')}")
                else:
                    print(f"      ❌ {platform.title()} token refresh failed: {refresh_data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"      ❌ {platform.title()} token refresh failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ OAuth token refresh error: {e}")
        return False

def test_oauth_disconnection():
    """Test OAuth platform disconnection"""
    print("❌ Testing OAuth Platform Disconnection...")
    
    try:
        # Test disconnecting platforms
        test_platforms = ["facebook", "linkedin", "instagram", "google_gbp"]
        
        for platform in test_platforms:
            print(f"   📱 Testing {platform} disconnection...")
            
            response = requests.delete(f"{API_BASE}/oauth/disconnect/{platform}", timeout=10)
            
            if response.status_code == 200:
                disconnect_data = response.json()
                if disconnect_data.get('success'):
                    print(f"      ✅ {platform.title()} disconnected:")
                    print(f"         Platform: {disconnect_data.get('platform', 'N/A')}")
                    print(f"         Message: {disconnect_data.get('message', 'N/A')}")
                else:
                    print(f"      ❌ {platform.title()} disconnection failed: {disconnect_data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"      ❌ {platform.title()} disconnection failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ OAuth disconnection error: {e}")
        return False

def main():
    """Run all OAuth integration tests"""
    print("🚀 VANTAGE AI - OAuth Integration System Test Suite")
    print("=" * 60)
    
    # Test 1: Service Status
    status_ok = test_oauth_status()
    print()
    
    # Test 2: OAuth Platforms
    platforms_ok = test_oauth_platforms()
    print()
    
    # Test 3: OAuth Connection Initiation
    connection_ok = test_oauth_connection_initiation()
    print()
    
    # Test 4: OAuth Callback Handling
    callback_ok = test_oauth_callback_handling()
    print()
    
    # Test 5: OAuth Account Information
    account_info_ok = test_oauth_account_info()
    print()
    
    # Test 6: OAuth Token Refresh
    refresh_ok = test_oauth_token_refresh()
    print()
    
    # Test 7: OAuth Disconnection
    disconnection_ok = test_oauth_disconnection()
    print()
    
    # Summary
    print("📋 OAuth Integration Test Summary:")
    print(f"✅ Service Status: {'PASS' if status_ok else 'FAIL'}")
    print(f"✅ OAuth Platforms: {'PASS' if platforms_ok else 'FAIL'}")
    print(f"✅ Connection Initiation: {'PASS' if connection_ok else 'FAIL'}")
    print(f"✅ Callback Handling: {'PASS' if callback_ok else 'FAIL'}")
    print(f"✅ Account Information: {'PASS' if account_info_ok else 'FAIL'}")
    print(f"✅ Token Refresh: {'PASS' if refresh_ok else 'FAIL'}")
    print(f"✅ Platform Disconnection: {'PASS' if disconnection_ok else 'FAIL'}")
    
    if all([status_ok, platforms_ok, connection_ok, callback_ok, account_info_ok, refresh_ok, disconnection_ok]):
        print("\n🎉 All OAuth integration tests passed! OAuth system is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
