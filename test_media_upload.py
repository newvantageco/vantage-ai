#!/usr/bin/env python3
"""
Test script for Media Upload System
Tests the real media upload API endpoints
"""

import requests
import json
import time
import os
from pathlib import Path

API_BASE = "http://localhost:8000/api/v1"

def create_test_files():
    """Create test files for upload testing"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple text file
    text_file = test_dir / "test_document.txt"
    with open(text_file, 'w') as f:
        f.write("This is a test document for media upload testing.\n" * 10)
    
    # Create a simple image file (1x1 pixel PNG)
    image_file = test_dir / "test_image.png"
    # Simple PNG header for a 1x1 pixel image
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 pixel
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # bit depth, color type, etc.
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x08, 0x99, 0x01, 0x01, 0x00, 0x00, 0x00,  # compressed data
        0xFF, 0xFF, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01,  # more data
        0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,  # IEND chunk
        0xAE, 0x42, 0x60, 0x82
    ])
    with open(image_file, 'wb') as f:
        f.write(png_data)
    
    return text_file, image_file

def test_media_status():
    """Test media service status"""
    print("📁 Testing Media Service Status...")
    
    try:
        response = requests.get(f"{API_BASE}/media/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Media Service Status:")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Features: {', '.join(status_data.get('features', []))}")
            print(f"   Version: {status_data.get('version')}")
            
            # Show supported formats
            formats = status_data.get('supported_formats', {})
            print("   Supported Formats:")
            for media_type, extensions in formats.items():
                print(f"      {media_type}: {', '.join(extensions)}")
            
            # Show file size limits
            limits = status_data.get('max_file_sizes', {})
            print("   File Size Limits:")
            for media_type, size_bytes in limits.items():
                size_mb = size_bytes / (1024 * 1024)
                print(f"      {media_type}: {size_mb:.1f}MB")
            
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_media_list():
    """Test listing media files"""
    print("📋 Testing Media List...")
    
    try:
        response = requests.get(f"{API_BASE}/media/list?page=1&size=10", timeout=10)
        if response.status_code == 200:
            list_data = response.json()
            media_items = list_data.get('media_items', [])
            
            print("✅ Media List:")
            print(f"   Total: {list_data.get('total', 0)}")
            print(f"   Page: {list_data.get('page', 0)}")
            print(f"   Size: {list_data.get('size', 0)}")
            print(f"   Has More: {list_data.get('has_more', False)}")
            print(f"   Items: {len(media_items)}")
            
            for i, item in enumerate(media_items, 1):
                print(f"   {i}. {item['original_filename']}:")
                print(f"      Type: {item['media_type']}")
                print(f"      Size: {item['file_size']:,} bytes")
                print(f"      Status: {item['status']}")
                print(f"      URL: {item['url'][:50]}...")
            
            return True
        else:
            print(f"❌ Media list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Media list error: {e}")
        return False

def test_media_stats():
    """Test media statistics"""
    print("📊 Testing Media Statistics...")
    
    try:
        response = requests.get(f"{API_BASE}/media/stats", timeout=10)
        if response.status_code == 200:
            stats_data = response.json()
            
            print("✅ Media Statistics:")
            print(f"   Total Files: {stats_data.get('total_files', 0)}")
            total_size = stats_data.get('total_size', 0)
            print(f"   Total Size: {total_size:,} bytes ({total_size/(1024*1024):.1f}MB)")
            
            # By type
            by_type = stats_data.get('by_type', {})
            print("   By Type:")
            for media_type, count in by_type.items():
                print(f"      {media_type}: {count} files")
            
            # By status
            by_status = stats_data.get('by_status', {})
            print("   By Status:")
            for status, count in by_status.items():
                print(f"      {status}: {count} files")
            
            return True
        else:
            print(f"❌ Media stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Media stats error: {e}")
        return False

def test_file_upload(file_path, expected_type):
    """Test uploading a file"""
    print(f"📤 Testing {expected_type} Upload: {file_path.name}...")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            response = requests.post(f"{API_BASE}/media/upload", files=files, timeout=30)
        
        if response.status_code == 201:
            upload_data = response.json()
            if upload_data.get('success'):
                media_item = upload_data.get('media_item', {})
                print(f"   ✅ Upload successful:")
                print(f"      ID: {media_item.get('id', 'N/A')}")
                print(f"      Filename: {media_item.get('filename', 'N/A')}")
                print(f"      Size: {media_item.get('file_size', 0):,} bytes")
                print(f"      Type: {media_item.get('media_type', 'N/A')}")
                print(f"      Status: {media_item.get('status', 'N/A')}")
                print(f"      URL: {media_item.get('url', 'N/A')[:50]}...")
                return True
            else:
                print(f"   ❌ Upload failed: {upload_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return False

def test_media_filtering():
    """Test media filtering by type"""
    print("🔍 Testing Media Filtering...")
    
    try:
        # Test filtering by image type
        response = requests.get(f"{API_BASE}/media/list?media_type=image&page=1&size=5", timeout=10)
        if response.status_code == 200:
            list_data = response.json()
            media_items = list_data.get('media_items', [])
            
            print("✅ Image Filter:")
            print(f"   Found: {len(media_items)} image files")
            for item in media_items:
                if item['media_type'] != 'image':
                    print(f"   ❌ Wrong type: {item['original_filename']} is {item['media_type']}")
                    return False
            print("   All items are images ✅")
        
        # Test filtering by video type
        response = requests.get(f"{API_BASE}/media/list?media_type=video&page=1&size=5", timeout=10)
        if response.status_code == 200:
            list_data = response.json()
            media_items = list_data.get('media_items', [])
            
            print("✅ Video Filter:")
            print(f"   Found: {len(media_items)} video files")
            for item in media_items:
                if item['media_type'] != 'video':
                    print(f"   ❌ Wrong type: {item['original_filename']} is {item['media_type']}")
                    return False
            print("   All items are videos ✅")
        
        return True
    except Exception as e:
        print(f"❌ Media filtering error: {e}")
        return False

def test_media_deletion():
    """Test media deletion"""
    print("🗑️ Testing Media Deletion...")
    
    try:
        # Test deleting a mock media item
        test_media_id = "media_001"
        response = requests.delete(f"{API_BASE}/media/{test_media_id}", timeout=10)
        
        if response.status_code == 200:
            delete_data = response.json()
            if delete_data.get('success'):
                print(f"✅ Media deletion successful:")
                print(f"   Message: {delete_data.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ Deletion failed: {delete_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Deletion failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Media deletion error: {e}")
        return False

def main():
    """Run all media upload tests"""
    print("🚀 VANTAGE AI - Media Upload System Test Suite")
    print("=" * 60)
    
    # Test 1: Service Status
    status_ok = test_media_status()
    print()
    
    # Test 2: Media List
    list_ok = test_media_list()
    print()
    
    # Test 3: Media Statistics
    stats_ok = test_media_stats()
    print()
    
    # Test 4: File Upload
    print("📤 Testing File Uploads...")
    text_file, image_file = create_test_files()
    
    text_upload_ok = test_file_upload(text_file, "document")
    print()
    
    image_upload_ok = test_file_upload(image_file, "image")
    print()
    
    # Test 5: Media Filtering
    filtering_ok = test_media_filtering()
    print()
    
    # Test 6: Media Deletion
    deletion_ok = test_media_deletion()
    print()
    
    # Cleanup test files
    try:
        text_file.unlink()
        image_file.unlink()
        text_file.parent.rmdir()
        print("🧹 Cleaned up test files")
    except:
        pass
    
    # Summary
    print("📋 Media Upload Test Summary:")
    print(f"✅ Service Status: {'PASS' if status_ok else 'FAIL'}")
    print(f"✅ Media List: {'PASS' if list_ok else 'FAIL'}")
    print(f"✅ Media Statistics: {'PASS' if stats_ok else 'FAIL'}")
    print(f"✅ Document Upload: {'PASS' if text_upload_ok else 'FAIL'}")
    print(f"✅ Image Upload: {'PASS' if image_upload_ok else 'FAIL'}")
    print(f"✅ Media Filtering: {'PASS' if filtering_ok else 'FAIL'}")
    print(f"✅ Media Deletion: {'PASS' if deletion_ok else 'FAIL'}")
    
    if all([status_ok, list_ok, stats_ok, text_upload_ok, image_upload_ok, filtering_ok, deletion_ok]):
        print("\n🎉 All media upload tests passed! Media system is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
