#!/usr/bin/env python3
"""
Test script for Content Library System
Tests the real content library API endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_content_library_status():
    """Test content library service status"""
    print("📚 Testing Content Library Service Status...")
    
    try:
        response = requests.get(f"{API_BASE}/content/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Content Library Service Status:")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Features: {', '.join(status_data.get('features', []))}")
            print(f"   Content Types: {', '.join(status_data.get('content_types', []))}")
            print(f"   Statuses: {', '.join(status_data.get('statuses', []))}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_content_list():
    """Test listing content items"""
    print("📋 Testing Content List...")
    
    try:
        response = requests.get(f"{API_BASE}/content/list?page=1&size=10", timeout=10)
        if response.status_code == 200:
            list_data = response.json()
            content_items = list_data.get('content_items', [])
            
            print("✅ Content List:")
            print(f"   Total: {list_data.get('total', 0)}")
            print(f"   Page: {list_data.get('page', 0)}")
            print(f"   Size: {list_data.get('size', 0)}")
            print(f"   Has More: {list_data.get('has_more', False)}")
            print(f"   Items: {len(content_items)}")
            
            for i, item in enumerate(content_items, 1):
                print(f"   {i}. {item['title']}:")
                print(f"      Type: {item['content_type']}")
                print(f"      Status: {item['status']}")
                print(f"      Tags: {', '.join(item.get('tags', []))}")
                print(f"      Created: {item['created_at']}")
            
            return True
        else:
            print(f"❌ Content list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Content list error: {e}")
        return False

def test_content_filtering():
    """Test content filtering by status and type"""
    print("🔍 Testing Content Filtering...")
    
    try:
        # Test filtering by status
        response = requests.get(f"{API_BASE}/content/list?status_filter=published&page=1&size=5", timeout=10)
        if response.status_code == 200:
            list_data = response.json()
            content_items = list_data.get('content_items', [])
            
            print("✅ Published Content Filter:")
            print(f"   Found: {len(content_items)} published items")
            for item in content_items:
                if item['status'] != 'published':
                    print(f"   ❌ Wrong status: {item['title']} is {item['status']}")
                    return False
            print("   All items are published ✅")
        
        # Test filtering by content type
        response = requests.get(f"{API_BASE}/content/list?content_type=text&page=1&size=5", timeout=10)
        if response.status_code == 200:
            list_data = response.json()
            content_items = list_data.get('content_items', [])
            
            print("✅ Text Content Filter:")
            print(f"   Found: {len(content_items)} text items")
            for item in content_items:
                if item['content_type'] != 'text':
                    print(f"   ❌ Wrong type: {item['title']} is {item['content_type']}")
                    return False
            print("   All items are text content ✅")
        
        # Test search functionality
        response = requests.get(f"{API_BASE}/content/list?search=AI&page=1&size=5", timeout=10)
        if response.status_code == 200:
            list_data = response.json()
            content_items = list_data.get('content_items', [])
            
            print("✅ Search Filter (AI):")
            print(f"   Found: {len(content_items)} items containing 'AI'")
            for item in content_items:
                if 'AI' not in item['title'] and 'AI' not in item['content']:
                    print(f"   ❌ Search mismatch: {item['title']}")
                    return False
            print("   All items contain 'AI' ✅")
        
        return True
    except Exception as e:
        print(f"❌ Content filtering error: {e}")
        return False

def test_content_creation():
    """Test creating new content"""
    print("✍️ Testing Content Creation...")
    
    try:
        new_content = {
            "title": "Test Content Item",
            "content": "This is a test content item created via API. It demonstrates the content creation functionality. #Test #API #ContentCreation",
            "content_type": "text",
            "tags": ["test", "api", "demo"],
            "hashtags": ["#Test", "#API", "#ContentCreation"],
            "mentions": [],
            "media_urls": [],
            "platform_content": {
                "facebook": "This is a test content item for Facebook...",
                "linkedin": "This is a test content item for LinkedIn...",
                "instagram": "This is a test content item for Instagram..."
            },
            "campaign_id": None
        }
        
        response = requests.post(f"{API_BASE}/content/create", json=new_content, timeout=15)
        if response.status_code == 201:
            content_data = response.json()
            print("✅ Content Creation:")
            print(f"   ID: {content_data.get('id')}")
            print(f"   Title: {content_data.get('title')}")
            print(f"   Status: {content_data.get('status')}")
            print(f"   Tags: {', '.join(content_data.get('tags', []))}")
            print(f"   Created: {content_data.get('created_at')}")
            return content_data.get('id')
        else:
            print(f"❌ Content creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Content creation error: {e}")
        return None

def test_content_retrieval(content_id: str):
    """Test retrieving specific content"""
    print(f"📖 Testing Content Retrieval for {content_id}...")
    
    try:
        response = requests.get(f"{API_BASE}/content/{content_id}", timeout=10)
        if response.status_code == 200:
            content_data = response.json()
            print("✅ Content Retrieval:")
            print(f"   ID: {content_data.get('id')}")
            print(f"   Title: {content_data.get('title')}")
            print(f"   Content: {content_data.get('content')[:100]}...")
            print(f"   Status: {content_data.get('status')}")
            print(f"   Platform Content: {len(content_data.get('platform_content', {}))} platforms")
            return True
        else:
            print(f"❌ Content retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Content retrieval error: {e}")
        return False

def test_content_update(content_id: str):
    """Test updating content"""
    print(f"✏️ Testing Content Update for {content_id}...")
    
    try:
        update_data = {
            "title": "Updated Test Content Item",
            "content": "This is an updated test content item. The content has been modified to test the update functionality. #Updated #Test #API",
            "tags": ["updated", "test", "api", "modified"],
            "hashtags": ["#Updated", "#Test", "#API"],
            "status": "draft"
        }
        
        response = requests.put(f"{API_BASE}/content/{content_id}", json=update_data, timeout=15)
        if response.status_code == 200:
            content_data = response.json()
            print("✅ Content Update:")
            print(f"   Title: {content_data.get('title')}")
            print(f"   Status: {content_data.get('status')}")
            print(f"   Tags: {', '.join(content_data.get('tags', []))}")
            print(f"   Updated: {content_data.get('updated_at')}")
            return True
        else:
            print(f"❌ Content update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Content update error: {e}")
        return False

def test_content_stats():
    """Test content statistics"""
    print("📊 Testing Content Statistics...")
    
    try:
        response = requests.get(f"{API_BASE}/content/stats", timeout=10)
        if response.status_code == 200:
            stats_data = response.json()
            
            print("✅ Content Statistics:")
            print(f"   Total Content: {stats_data.get('total_content', 0)}")
            
            # By status
            by_status = stats_data.get('by_status', {})
            print("   By Status:")
            for status, count in by_status.items():
                print(f"      {status}: {count} items")
            
            # By type
            by_type = stats_data.get('by_type', {})
            print("   By Type:")
            for content_type, count in by_type.items():
                print(f"      {content_type}: {count} items")
            
            # By campaign
            by_campaign = stats_data.get('by_campaign', {})
            print("   By Campaign:")
            for campaign, count in by_campaign.items():
                print(f"      {campaign}: {count} items")
            
            # Recent activity
            recent_activity = stats_data.get('recent_activity', [])
            print(f"   Recent Activity: {len(recent_activity)} activities")
            
            return True
        else:
            print(f"❌ Content stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Content stats error: {e}")
        return False

def test_content_templates():
    """Test content templates"""
    print("📝 Testing Content Templates...")
    
    try:
        response = requests.get(f"{API_BASE}/content/templates", timeout=10)
        if response.status_code == 200:
            templates_data = response.json()
            
            print("✅ Content Templates:")
            print(f"   Total Templates: {len(templates_data)}")
            
            for i, template in enumerate(templates_data, 1):
                print(f"   {i}. {template['name']}:")
                print(f"      Description: {template['description']}")
                print(f"      Type: {template['content_type']}")
                print(f"      Tags: {', '.join(template.get('tags', []))}")
                print(f"      Usage: {template.get('usage_count', 0)} times")
                print(f"      Template: {template['content_template'][:50]}...")
            
            return True
        else:
            print(f"❌ Content templates failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Content templates error: {e}")
        return False

def test_content_deletion(content_id: str):
    """Test content deletion"""
    print(f"🗑️ Testing Content Deletion for {content_id}...")
    
    try:
        response = requests.delete(f"{API_BASE}/content/{content_id}", timeout=10)
        if response.status_code == 200:
            delete_data = response.json()
            if delete_data.get('success'):
                print("✅ Content Deletion:")
                print(f"   Message: {delete_data.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ Deletion failed: {delete_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Content deletion failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Content deletion error: {e}")
        return False

def main():
    """Run all content library tests"""
    print("🚀 VANTAGE AI - Content Library System Test Suite")
    print("=" * 60)
    
    # Test 1: Service Status
    status_ok = test_content_library_status()
    print()
    
    # Test 2: Content List
    list_ok = test_content_list()
    print()
    
    # Test 3: Content Filtering
    filtering_ok = test_content_filtering()
    print()
    
    # Test 4: Content Creation
    content_id = test_content_creation()
    print()
    
    # Test 5: Content Retrieval
    retrieval_ok = test_content_retrieval(content_id) if content_id else False
    print()
    
    # Test 6: Content Update
    update_ok = test_content_update(content_id) if content_id else False
    print()
    
    # Test 7: Content Statistics
    stats_ok = test_content_stats()
    print()
    
    # Test 8: Content Templates
    templates_ok = test_content_templates()
    print()
    
    # Test 9: Content Deletion
    deletion_ok = test_content_deletion(content_id) if content_id else False
    print()
    
    # Summary
    print("📋 Content Library Test Summary:")
    print(f"✅ Service Status: {'PASS' if status_ok else 'FAIL'}")
    print(f"✅ Content List: {'PASS' if list_ok else 'FAIL'}")
    print(f"✅ Content Filtering: {'PASS' if filtering_ok else 'FAIL'}")
    print(f"✅ Content Creation: {'PASS' if content_id else 'FAIL'}")
    print(f"✅ Content Retrieval: {'PASS' if retrieval_ok else 'FAIL'}")
    print(f"✅ Content Update: {'PASS' if update_ok else 'FAIL'}")
    print(f"✅ Content Statistics: {'PASS' if stats_ok else 'FAIL'}")
    print(f"✅ Content Templates: {'PASS' if templates_ok else 'FAIL'}")
    print(f"✅ Content Deletion: {'PASS' if deletion_ok else 'FAIL'}")
    
    if all([status_ok, list_ok, filtering_ok, content_id, retrieval_ok, update_ok, stats_ok, templates_ok, deletion_ok]):
        print("\n🎉 All content library tests passed! Content library system is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
