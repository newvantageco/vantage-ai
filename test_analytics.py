#!/usr/bin/env python3
"""
Test script for Analytics Integration
Tests the real analytics API endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_analytics_status():
    """Test analytics service status"""
    print("📊 Testing Analytics Service Status...")
    
    try:
        response = requests.get(f"{API_BASE}/analytics/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Analytics Service Status:")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Features: {', '.join(status_data.get('features', []))}")
            print(f"   Platforms: {', '.join(status_data.get('supported_platforms', []))}")
            print(f"   Data Sources: {', '.join(status_data.get('data_sources', []))}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_platform_analytics():
    """Test platform analytics capabilities"""
    print("🌐 Testing Platform Analytics Capabilities...")
    
    try:
        response = requests.get(f"{API_BASE}/analytics/platforms", timeout=10)
        if response.status_code == 200:
            platforms_data = response.json()
            platforms = platforms_data.get('platforms', [])
            print("✅ Platform Analytics:")
            for platform in platforms:
                print(f"   📱 {platform['platform'].title()}:")
                print(f"      Metrics: {', '.join(platform['metrics_available'])}")
                print(f"      Retention: {platform['data_retention']}")
                print(f"      Update: {platform['update_frequency']}")
                print(f"      Status: {platform['status']}")
            return True
        else:
            print(f"❌ Platform analytics check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Platform analytics check error: {e}")
        return False

def test_analytics_summary():
    """Test analytics summary for different periods"""
    print("📈 Testing Analytics Summary...")
    
    periods = ["last_7d", "last_30d"]
    
    for period in periods:
        try:
            print(f"   📅 Testing {period} summary...")
            response = requests.get(f"{API_BASE}/analytics/summary?period={period}", timeout=15)
            
            if response.status_code == 200:
                summary_data = response.json()
                print(f"   ✅ {period.upper()} Summary:")
                print(f"      Total Posts: {summary_data.get('total_posts')}")
                print(f"      Total Impressions: {summary_data.get('total_impressions'):,}")
                print(f"      Total Engagement: {summary_data.get('total_engagement'):,}")
                print(f"      Avg Engagement Rate: {summary_data.get('average_engagement_rate'):.2f}%")
                print(f"      Platforms: {len(summary_data.get('platforms', []))}")
                print(f"      Top Posts: {len(summary_data.get('top_performing_posts', []))}")
                
                # Show platform breakdown
                for platform in summary_data.get('platforms', []):
                    print(f"         📱 {platform['platform'].title()}: {platform['total_posts']} posts, {platform['engagement_rate']:.2f}% engagement")
            else:
                print(f"   ❌ {period} summary failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ {period} summary error: {e}")
            return False
    
    return True

def test_platform_filtered_summary():
    """Test analytics summary with platform filter"""
    print("🔍 Testing Platform-Filtered Analytics...")
    
    try:
        response = requests.get(f"{API_BASE}/analytics/summary?period=last_7d&platform=instagram", timeout=15)
        
        if response.status_code == 200:
            summary_data = response.json()
            print("✅ Instagram-Filtered Summary:")
            print(f"   Total Posts: {summary_data.get('total_posts')}")
            print(f"   Total Impressions: {summary_data.get('total_impressions'):,}")
            print(f"   Total Engagement: {summary_data.get('total_engagement'):,}")
            print(f"   Platforms: {len(summary_data.get('platforms', []))}")
            
            # Should only have Instagram data
            for platform in summary_data.get('platforms', []):
                if platform['platform'] == 'instagram':
                    print(f"   📱 Instagram Metrics:")
                    for metric in platform.get('metrics', []):
                        print(f"      {metric['name']}: {metric['value']:,} ({metric['change_percent']:+.1f}%)")
            return True
        else:
            print(f"❌ Platform-filtered summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Platform-filtered summary error: {e}")
        return False

def test_post_performance():
    """Test individual post performance data"""
    print("📊 Testing Post Performance Data...")
    
    try:
        response = requests.get(f"{API_BASE}/analytics/posts?limit=5", timeout=15)
        
        if response.status_code == 200:
            posts_data = response.json()
            print("✅ Post Performance Data:")
            print(f"   Total Posts: {len(posts_data)}")
            
            for i, post in enumerate(posts_data, 1):
                print(f"   {i}. {post['platform'].title()} Post:")
                print(f"      Content: {post['content_preview'][:50]}...")
                print(f"      Published: {post['published_at']}")
                print(f"      Impressions: {post['impressions']:,}")
                print(f"      Engagement: {post['engagement']} ({post['engagement_rate']:.2f}%)")
                print(f"      Likes: {post['likes']}, Comments: {post['comments']}, Shares: {post['shares']}")
            return True
        else:
            print(f"❌ Post performance failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Post performance error: {e}")
        return False

def test_platform_filtered_posts():
    """Test post performance with platform filter"""
    print("🔍 Testing Platform-Filtered Post Performance...")
    
    try:
        response = requests.get(f"{API_BASE}/analytics/posts?platform=facebook&limit=3", timeout=15)
        
        if response.status_code == 200:
            posts_data = response.json()
            print("✅ Facebook-Filtered Posts:")
            print(f"   Total Posts: {len(posts_data)}")
            
            for i, post in enumerate(posts_data, 1):
                print(f"   {i}. Facebook Post:")
                print(f"      Content: {post['content_preview'][:50]}...")
                print(f"      Impressions: {post['impressions']:,}")
                print(f"      Engagement Rate: {post['engagement_rate']:.2f}%")
            
            # Verify all posts are from Facebook
            all_facebook = all(post['platform'] == 'facebook' for post in posts_data)
            if all_facebook:
                print("   ✅ All posts are from Facebook (filter working correctly)")
            else:
                print("   ❌ Filter not working correctly - mixed platforms found")
                return False
            
            return True
        else:
            print(f"❌ Platform-filtered posts failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Platform-filtered posts error: {e}")
        return False

def main():
    """Run all analytics tests"""
    print("🚀 VANTAGE AI - Analytics Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Service Status
    status_ok = test_analytics_status()
    print()
    
    # Test 2: Platform Analytics
    platforms_ok = test_platform_analytics()
    print()
    
    # Test 3: Analytics Summary
    summary_ok = test_analytics_summary()
    print()
    
    # Test 4: Platform-Filtered Summary
    filtered_summary_ok = test_platform_filtered_summary()
    print()
    
    # Test 5: Post Performance
    posts_ok = test_post_performance()
    print()
    
    # Test 6: Platform-Filtered Posts
    filtered_posts_ok = test_platform_filtered_posts()
    print()
    
    # Summary
    print("📋 Analytics Test Summary:")
    print(f"✅ Service Status: {'PASS' if status_ok else 'FAIL'}")
    print(f"✅ Platform Analytics: {'PASS' if platforms_ok else 'FAIL'}")
    print(f"✅ Analytics Summary: {'PASS' if summary_ok else 'FAIL'}")
    print(f"✅ Filtered Summary: {'PASS' if filtered_summary_ok else 'FAIL'}")
    print(f"✅ Post Performance: {'PASS' if posts_ok else 'FAIL'}")
    print(f"✅ Filtered Posts: {'PASS' if filtered_posts_ok else 'FAIL'}")
    
    if all([status_ok, platforms_ok, summary_ok, filtered_summary_ok, posts_ok, filtered_posts_ok]):
        print("\n🎉 All analytics tests passed! Analytics integration is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
