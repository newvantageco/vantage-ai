#!/usr/bin/env python3
"""
Test script for Content Scheduling
Tests the real scheduling API endpoints
"""

import requests
import json
import time
from datetime import datetime, timedelta

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

def test_scheduling_status():
    """Test scheduling service status"""
    print("📊 Testing Scheduling Service Status...")
    
    try:
        response = requests.get(f"{API_BASE}/scheduling/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Scheduling Service Status:")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Features: {', '.join(status_data.get('features', []))}")
            print(f"   Platforms: {', '.join(status_data.get('supported_platforms', []))}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_optimal_times():
    """Test getting optimal posting times"""
    print("⏰ Testing Optimal Posting Times...")
    
    try:
        response = requests.get(f"{API_BASE}/scheduling/optimal-times", timeout=10)
        if response.status_code == 200:
            times_data = response.json()
            print("✅ Optimal Posting Times:")
            for platform, data in times_data.items():
                print(f"   📱 {platform.title()}:")
                print(f"      Best times: {', '.join(data['best_times'])}")
                print(f"      Best days: {', '.join(data['best_days'])}")
            return True
        else:
            print(f"❌ Optimal times check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Optimal times check error: {e}")
        return False

def test_create_schedule():
    """Test creating a new schedule"""
    print("📅 Testing Schedule Creation...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return False
    
    # Create a schedule for 1 hour from now
    future_time = datetime.now() + timedelta(hours=1)
    scheduled_at = future_time.isoformat() + "Z"
    
    # Test content
    test_content = """🎉 Just scheduled our first AI-powered post!

This content was automatically scheduled using VANTAGE AI's intelligent scheduling system. 

Key benefits:
⏰ Optimal timing for maximum engagement
📱 Multi-platform publishing
🤖 AI-powered content optimization
📊 Performance tracking

Ready to transform your social media strategy? Let's get started! 💪

#AI #Scheduling #SocialMedia #Marketing #Automation"""

    schedule_payload = {
        "content": test_content,
        "platforms": ["facebook", "linkedin"],
        "scheduled_at": scheduled_at,
        "media": [],
        "timezone": "UTC"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print(f"📝 Creating schedule for {scheduled_at}...")
        print(f"Platforms: {', '.join(schedule_payload['platforms'])}")
        
        response = requests.post(
            f"{API_BASE}/schedule/create",
            json=schedule_payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            schedule_data = response.json()
            print("✅ Schedule Creation Results:")
            print(f"   Success: {schedule_data.get('success')}")
            print(f"   Schedule ID: {schedule_data.get('schedule_id')}")
            print(f"   Scheduled At: {schedule_data.get('scheduled_at')}")
            print(f"   Platforms: {', '.join(schedule_data.get('platforms', []))}")
            print(f"   Message: {schedule_data.get('message')}")
            
            if schedule_data.get('errors'):
                print("   ❌ Errors:")
                for error in schedule_data['errors']:
                    print(f"      - {error}")
            
            return schedule_data.get('success', False), schedule_data.get('schedule_id')
        else:
            print(f"❌ Schedule creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Schedule creation error: {e}")
        return False, None

def test_schedule_status(schedule_id):
    """Test getting schedule status"""
    print(f"📋 Testing Schedule Status for {schedule_id}...")
    
    try:
        response = requests.get(f"{API_BASE}/schedule/{schedule_id}", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Schedule Status:")
            print(f"   Schedule ID: {status_data.get('schedule_id')}")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Scheduled At: {status_data.get('scheduled_at')}")
            print(f"   Platforms: {', '.join(status_data.get('platforms', []))}")
            print(f"   Content Preview: {status_data.get('content_preview', '')[:50]}...")
            
            if status_data.get('published_at'):
                print(f"   Published At: {status_data.get('published_at')}")
            
            if status_data.get('error_message'):
                print(f"   Error: {status_data.get('error_message')}")
            
            return True
        else:
            print(f"❌ Schedule status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Schedule status error: {e}")
        return False

def test_list_schedules():
    """Test listing schedules"""
    print("📋 Testing Schedule List...")
    
    try:
        response = requests.get(f"{API_BASE}/schedule/list?page=1&size=5", timeout=10)
        if response.status_code == 200:
            list_data = response.json()
            schedules = list_data.get('schedules', [])
            print("✅ Schedule List:")
            print(f"   Total: {list_data.get('total')}")
            print(f"   Page: {list_data.get('page')}")
            print(f"   Size: {list_data.get('size')}")
            print(f"   Schedules: {len(schedules)}")
            
            for i, schedule in enumerate(schedules, 1):
                print(f"   {i}. {schedule['schedule_id']} - {schedule['status']} - {schedule['scheduled_at']}")
            
            return True
        else:
            print(f"❌ Schedule list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Schedule list error: {e}")
        return False

def test_cancel_schedule(schedule_id):
    """Test cancelling a schedule"""
    print(f"❌ Testing Schedule Cancellation for {schedule_id}...")
    
    try:
        response = requests.delete(f"{API_BASE}/schedule/{schedule_id}", timeout=10)
        if response.status_code == 200:
            cancel_data = response.json()
            print("✅ Schedule Cancellation:")
            print(f"   Success: {cancel_data.get('success')}")
            print(f"   Message: {cancel_data.get('message')}")
            return True
        else:
            print(f"❌ Schedule cancellation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Schedule cancellation error: {e}")
        return False

def main():
    """Run all scheduling tests"""
    print("🚀 VANTAGE AI - Content Scheduling Test Suite")
    print("=" * 60)
    
    # Test 1: Service Status
    status_ok = test_scheduling_status()
    print()
    
    # Test 2: Optimal Times
    times_ok = test_optimal_times()
    print()
    
    # Test 3: Create Schedule
    create_ok, schedule_id = test_create_schedule()
    print()
    
    # Test 4: Schedule Status (using existing mock schedule ID)
    status_check_ok = test_schedule_status("schedule_1703123456")
    print()
    
    # Test 5: List Schedules
    list_ok = test_list_schedules()
    print()
    
    # Test 6: Cancel Schedule (using existing mock schedule ID)
    cancel_ok = test_cancel_schedule("schedule_1703123456")
    print()
    
    # Summary
    print("📋 Scheduling Test Summary:")
    print(f"✅ Service Status: {'PASS' if status_ok else 'FAIL'}")
    print(f"✅ Optimal Times: {'PASS' if times_ok else 'FAIL'}")
    print(f"✅ Create Schedule: {'PASS' if create_ok else 'FAIL'}")
    print(f"✅ Schedule Status: {'PASS' if status_check_ok else 'FAIL'}")
    print(f"✅ List Schedules: {'PASS' if list_ok else 'FAIL'}")
    print(f"✅ Cancel Schedule: {'PASS' if cancel_ok else 'FAIL'}")
    
    if all([status_ok, times_ok, create_ok, status_check_ok, list_ok, cancel_ok]):
        print("\n🎉 All scheduling tests passed! Content scheduling is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
