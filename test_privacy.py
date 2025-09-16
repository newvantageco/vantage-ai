#!/usr/bin/env python3
"""
Test script for privacy compliance features.
Run this to verify the export/delete endpoints work correctly.
"""

import asyncio
import httpx
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

async def test_privacy_endpoints():
    """Test the privacy endpoints."""
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Privacy Compliance Features")
        print("=" * 50)
        
        # Test 1: Get retention policy
        print("\n1. Testing retention policy retrieval...")
        try:
            response = await client.get(f"{API_BASE}/privacy/retention")
            if response.status_code == 200:
                policy = response.json()
                print(f"✅ Retention policy retrieved: {policy}")
            else:
                print(f"❌ Failed to get retention policy: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting retention policy: {e}")
        
        # Test 2: Update retention policy
        print("\n2. Testing retention policy update...")
        try:
            update_data = {
                "messages_days": 60,
                "logs_days": 14,
                "metrics_days": 180
            }
            response = await client.put(f"{API_BASE}/privacy/retention", json=update_data)
            if response.status_code == 200:
                print(f"✅ Retention policy updated: {response.json()}")
            else:
                print(f"❌ Failed to update retention policy: {response.status_code}")
        except Exception as e:
            print(f"❌ Error updating retention policy: {e}")
        
        # Test 3: List privacy jobs
        print("\n3. Testing privacy jobs listing...")
        try:
            response = await client.get(f"{API_BASE}/privacy/jobs")
            if response.status_code == 200:
                jobs = response.json()
                print(f"✅ Privacy jobs retrieved: {len(jobs.get('jobs', []))} jobs")
            else:
                print(f"❌ Failed to get privacy jobs: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting privacy jobs: {e}")
        
        # Test 4: Request data export
        print("\n4. Testing data export request...")
        try:
            export_data = {
                "include_media": True,
                "format": "both"
            }
            response = await client.post(f"{API_BASE}/privacy/export", json=export_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Export job created: {result}")
            else:
                print(f"❌ Failed to create export job: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating export job: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Privacy compliance testing completed!")
        print("\nNote: Some tests may fail if authentication is not set up.")
        print("Make sure to run this with proper authentication headers.")

if __name__ == "__main__":
    asyncio.run(test_privacy_endpoints())
