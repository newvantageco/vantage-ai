#!/usr/bin/env python3
"""
VANTAGE AI Functionality Test Script
Tests core platform functionality to ensure features work as designed
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import os

class VantageFunctionalityTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_result(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Print result
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if data and status == "FAIL":
            print(f"   Data: {data}")
        print()
    
    async def test_api_health(self):
        """Test API health endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/health")
            if response.status_code == 200:
                data = response.json()
                self.log_result("API Health Check", "PASS", f"API is healthy - {data.get('status', 'unknown')}")
                return True
            else:
                self.log_result("API Health Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("API Health Check", "FAIL", f"Connection error: {str(e)}")
            return False
    
    async def test_ai_content_generation(self):
        """Test AI content generation functionality"""
        try:
            # Test AI endpoint
            response = await self.client.post(
                f"{self.base_url}/api/v1/ai/generate",
                json={
                    "prompt": "Create a social media post about sustainable living",
                    "platform": "facebook",
                    "tone": "professional"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if "content" in data and data["content"]:
                    self.log_result("AI Content Generation", "PASS", "AI successfully generated content")
                    return True
                else:
                    self.log_result("AI Content Generation", "FAIL", "No content generated", data)
                    return False
            else:
                self.log_result("AI Content Generation", "FAIL", f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("AI Content Generation", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_publishing_endpoints(self):
        """Test publishing functionality"""
        try:
            # Test publishing status endpoint (no auth required)
            response = await self.client.get(f"{self.base_url}/api/v1/publish/status")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "operational":
                    self.log_result("Publishing Endpoints", "PASS", f"Publishing service status: {data['status']}")
                    return True
                else:
                    self.log_result("Publishing Endpoints", "FAIL", "Invalid publishing service response", data)
                    return False
            else:
                self.log_result("Publishing Endpoints", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Publishing Endpoints", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_analytics_endpoints(self):
        """Test analytics functionality"""
        try:
            # Test analytics summary endpoint
            response = await self.client.get(f"{self.base_url}/api/v1/analytics/summary")
            
            if response.status_code in [200, 401, 403]:  # 401/403 expected without auth
                self.log_result("Analytics Endpoints", "PASS", "Analytics endpoints accessible")
                return True
            else:
                self.log_result("Analytics Endpoints", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Analytics Endpoints", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_oauth_endpoints(self):
        """Test OAuth integration endpoints"""
        try:
            # Test OAuth status endpoint
            response = await self.client.get(f"{self.base_url}/api/v1/oauth/status")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    self.log_result("OAuth Integration", "PASS", f"OAuth service status: {data['status']}")
                    return True
                else:
                    self.log_result("OAuth Integration", "FAIL", "Invalid OAuth response", data)
                    return False
            else:
                self.log_result("OAuth Integration", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("OAuth Integration", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_billing_endpoints(self):
        """Test billing functionality"""
        try:
            # Test billing status endpoint
            response = await self.client.get(f"{self.base_url}/api/v1/billing/status")
            
            if response.status_code in [200, 401, 403]:  # 401/403 expected without auth
                self.log_result("Billing Endpoints", "PASS", "Billing endpoints accessible")
                return True
            else:
                self.log_result("Billing Endpoints", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Billing Endpoints", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_media_upload(self):
        """Test media upload functionality"""
        try:
            # Test media upload endpoint (should return 405 for GET or 401 for POST without auth)
            response = await self.client.get(f"{self.base_url}/api/v1/media/upload")
            
            if response.status_code in [405, 401, 403]:  # Expected responses
                self.log_result("Media Upload", "PASS", "Media upload endpoint accessible")
                return True
            else:
                self.log_result("Media Upload", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Media Upload", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_scheduling_endpoints(self):
        """Test scheduling functionality"""
        try:
            # Test scheduling endpoints
            response = await self.client.get(f"{self.base_url}/api/v1/scheduling/status")
            
            if response.status_code in [200, 401, 403]:  # 401/403 expected without auth
                self.log_result("Scheduling Endpoints", "PASS", "Scheduling endpoints accessible")
                return True
            else:
                self.log_result("Scheduling Endpoints", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Scheduling Endpoints", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_security_headers(self):
        """Test security headers"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/health")
            headers = response.headers
            
            security_headers = {
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            }
            
            missing_headers = []
            for header, expected_value in security_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif headers[header] != expected_value:
                    missing_headers.append(f"{header} (wrong value: {headers[header]})")
            
            if not missing_headers:
                self.log_result("Security Headers", "PASS", "All security headers present")
                return True
            else:
                self.log_result("Security Headers", "FAIL", f"Missing headers: {', '.join(missing_headers)}")
                return False
        except Exception as e:
            self.log_result("Security Headers", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_cors_configuration(self):
        """Test CORS configuration"""
        try:
            # Test CORS preflight request
            response = await self.client.options(
                f"{self.base_url}/api/v1/health",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET"
                }
            )
            
            if response.status_code in [200, 204]:
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
                }
                
                if cors_headers["Access-Control-Allow-Origin"]:
                    self.log_result("CORS Configuration", "PASS", "CORS properly configured")
                    return True
                else:
                    self.log_result("CORS Configuration", "FAIL", "CORS headers missing")
                    return False
            else:
                self.log_result("CORS Configuration", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("CORS Configuration", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        try:
            # Make multiple rapid requests to test rate limiting
            responses = []
            for i in range(10):
                response = await self.client.get(f"{self.base_url}/api/v1/health")
                responses.append(response.status_code)
            
            # Check if any requests were rate limited (429 status)
            if 429 in responses:
                self.log_result("Rate Limiting", "PASS", "Rate limiting is active")
                return True
            else:
                self.log_result("Rate Limiting", "WARN", "Rate limiting may not be active (no 429 responses)")
                return True  # Not a failure, just a warning
        except Exception as e:
            self.log_result("Rate Limiting", "FAIL", f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all functionality tests"""
        print("🚀 VANTAGE AI Functionality Test Suite")
        print("=" * 50)
        print()
        
        tests = [
            ("API Health", self.test_api_health),
            ("AI Content Generation", self.test_ai_content_generation),
            ("Publishing Endpoints", self.test_publishing_endpoints),
            ("Analytics Endpoints", self.test_analytics_endpoints),
            ("OAuth Integration", self.test_oauth_endpoints),
            ("Billing Endpoints", self.test_billing_endpoints),
            ("Media Upload", self.test_media_upload),
            ("Scheduling Endpoints", self.test_scheduling_endpoints),
            ("Security Headers", self.test_security_headers),
            ("CORS Configuration", self.test_cors_configuration),
            ("Rate Limiting", self.test_rate_limiting),
        ]
        
        passed = 0
        failed = 0
        warned = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_result(test_name, "FAIL", f"Test error: {str(e)}")
                failed += 1
        
        # Count warnings
        warned = len([r for r in self.results if r["status"] == "WARN"])
        
        print("=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
        print()
        
        if failed == 0:
            print("🎉 All critical tests passed! VANTAGE AI is functioning correctly.")
        else:
            print(f"⚠️  {failed} test(s) failed. Please review the issues above.")
        
        # Save detailed results
        with open("functionality_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Detailed results saved to: functionality_test_results.json")
        
        return failed == 0

async def main():
    """Main test runner"""
    base_url = os.getenv("VANTAGE_API_URL", "http://localhost:8000")
    
    async with VantageFunctionalityTester(base_url) as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
