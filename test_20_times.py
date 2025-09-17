#!/usr/bin/env python3
"""Test each function 20 times to ensure 100% reliability before Docker push."""

import subprocess
import sys
import time
import requests
import json
from datetime import datetime
from typing import List, Tuple, Dict

class ComprehensiveTester:
    def __init__(self):
        self.api_base = "http://localhost:8001"
        self.web_base = "http://localhost:3000"
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test_suite(self, test_name: str, iterations: int = 20) -> Tuple[int, int]:
        """Run a test suite multiple times and return (passed, failed)."""
        self.log(f"Starting {test_name} - {iterations} iterations")
        passed = 0
        failed = 0
        
        for i in range(iterations):
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", test_name, "-v", "--tb=short", "-x"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    passed += 1
                    self.log(f"  ✓ Iteration {i+1}/{iterations} PASSED", "SUCCESS")
                else:
                    failed += 1
                    self.log(f"  ✗ Iteration {i+1}/{iterations} FAILED", "ERROR")
                    if i < 5:  # Show details for first 5 failures
                        self.log(f"    Error: {result.stderr[:200]}...", "ERROR")
                
                # Small delay between iterations
                time.sleep(0.1)
                
            except subprocess.TimeoutExpired:
                failed += 1
                self.log(f"  ⏰ Iteration {i+1}/{iterations} TIMEOUT", "ERROR")
            except Exception as e:
                failed += 1
                self.log(f"  💥 Iteration {i+1}/{iterations} ERROR: {str(e)}", "ERROR")
        
        self.log(f"Completed {test_name}: {passed} passed, {failed} failed")
        return passed, failed

    def test_api_endpoints(self, iterations: int = 20) -> Tuple[int, int]:
        """Test API endpoints multiple times."""
        self.log(f"Testing API endpoints - {iterations} iterations")
        passed = 0
        failed = 0
        
        endpoints = [
            "/api/v1/health",
            "/docs",
            "/api/v1/orgs",
            "/api/v1/privacy/retention",
            "/api/v1/privacy/jobs"
        ]
        
        for i in range(iterations):
            iteration_passed = True
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.api_base}{endpoint}", timeout=5)
                    if response.status_code in [200, 403, 404]:  # 403/404 are expected for some endpoints
                        self.log(f"  ✓ {endpoint} - Status {response.status_code}", "SUCCESS")
                    else:
                        self.log(f"  ✗ {endpoint} - Unexpected status {response.status_code}", "ERROR")
                        iteration_passed = False
                except Exception as e:
                    self.log(f"  ✗ {endpoint} - Error: {str(e)}", "ERROR")
                    iteration_passed = False
            
            if iteration_passed:
                passed += 1
                self.log(f"  ✓ API iteration {i+1}/{iterations} PASSED", "SUCCESS")
            else:
                failed += 1
                self.log(f"  ✗ API iteration {i+1}/{iterations} FAILED", "ERROR")
            
            time.sleep(0.1)
        
        return passed, failed

    def test_web_endpoints(self, iterations: int = 20) -> Tuple[int, int]:
        """Test web endpoints multiple times."""
        self.log(f"Testing web endpoints - {iterations} iterations")
        passed = 0
        failed = 0
        
        for i in range(iterations):
            try:
                response = requests.get(self.web_base, timeout=5)
                if response.status_code == 200:
                    passed += 1
                    self.log(f"  ✓ Web iteration {i+1}/{iterations} PASSED", "SUCCESS")
                else:
                    failed += 1
                    self.log(f"  ✗ Web iteration {i+1}/{iterations} - Status {response.status_code}", "ERROR")
            except Exception as e:
                failed += 1
                self.log(f"  ✗ Web iteration {i+1}/{iterations} - Error: {str(e)}", "ERROR")
            
            time.sleep(0.1)
        
        return passed, failed

    def test_database_operations(self, iterations: int = 20) -> Tuple[int, int]:
        """Test database operations multiple times."""
        self.log(f"Testing database operations - {iterations} iterations")
        passed = 0
        failed = 0
        
        for i in range(iterations):
            try:
                # Test database connection through API
                response = requests.get(f"{self.api_base}/api/v1/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("database") == "connected":
                        passed += 1
                        self.log(f"  ✓ DB iteration {i+1}/{iterations} PASSED", "SUCCESS")
                    else:
                        failed += 1
                        self.log(f"  ✗ DB iteration {i+1}/{iterations} - DB status: {health_data.get('database', 'unknown')}", "ERROR")
                else:
                    failed += 1
                    self.log(f"  ✗ DB iteration {i+1}/{iterations} - Status {response.status_code}", "ERROR")
            except Exception as e:
                failed += 1
                self.log(f"  ✗ DB iteration {i+1}/{iterations} - Error: {str(e)}", "ERROR")
            
            time.sleep(0.1)
        
        return passed, failed

    def run_comprehensive_tests(self):
        """Run all comprehensive tests."""
        self.log("🚀 Starting Comprehensive 20x Testing Suite")
        self.log("=" * 80)
        
        # Test suites to run 20 times each
        test_suites = [
            "tests/test_bandit.py",
            "tests/test_model_router.py", 
            "tests/test_safety.py",
            "tests/test_optimiser_worker.py",
            "tests/test_scheduler.py",
            "tests/test_weekly_brief.py",
            "tests/test_reward_calculation.py",
            "test_ai_optimization.py",
            "test_privacy.py"
        ]
        
        # Run each test suite 20 times
        for test_suite in test_suites:
            passed, failed = self.run_test_suite(test_suite, 20)
            self.test_results[test_suite] = {"passed": passed, "failed": failed}
            self.total_tests += 20
            self.passed_tests += passed
            self.failed_tests += failed
        
        # Test API endpoints 20 times
        api_passed, api_failed = self.test_api_endpoints(20)
        self.test_results["API Endpoints"] = {"passed": api_passed, "failed": api_failed}
        self.total_tests += 20
        self.passed_tests += api_passed
        self.failed_tests += api_failed
        
        # Test web endpoints 20 times
        web_passed, web_failed = self.test_web_endpoints(20)
        self.test_results["Web Endpoints"] = {"passed": web_passed, "failed": web_failed}
        self.total_tests += 20
        self.passed_tests += web_passed
        self.failed_tests += web_failed
        
        # Test database operations 20 times
        db_passed, db_failed = self.test_database_operations(20)
        self.test_results["Database Operations"] = {"passed": db_passed, "failed": db_failed}
        self.total_tests += 20
        self.passed_tests += db_passed
        self.failed_tests += db_failed
        
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary."""
        self.log("=" * 80)
        self.log("COMPREHENSIVE TEST SUMMARY")
        self.log("=" * 80)
        
        for test_name, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            success_rate = (passed / total * 100) if total > 0 else 0
            status = "✅" if failed == 0 else "❌"
            
            self.log(f"{status} {test_name:<30} {passed:>3}/{total:<3} ({success_rate:>5.1f}%)")
        
        overall_success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        self.log("=" * 80)
        self.log(f"TOTAL TESTS: {self.total_tests}")
        self.log(f"PASSED: {self.passed_tests}")
        self.log(f"FAILED: {self.failed_tests}")
        self.log(f"SUCCESS RATE: {overall_success_rate:.1f}%")
        self.log("=" * 80)
        
        if self.failed_tests == 0:
            self.log("🎉 ALL TESTS PASSED! READY FOR DOCKER PUSH! 🎉", "SUCCESS")
            return True
        else:
            self.log(f"❌ {self.failed_tests} tests failed. NOT READY FOR DOCKER PUSH.", "ERROR")
            return False

def main():
    """Main function to run comprehensive tests."""
    tester = ComprehensiveTester()
    
    # Check if services are running
    try:
        response = requests.get("http://localhost:8001/api/v1/health", timeout=5)
        if response.status_code != 200:
            tester.log("API server not running. Please start the application first.", "ERROR")
            return 1
    except:
        tester.log("API server not accessible. Please start the application first.", "ERROR")
        return 1
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code != 200:
            tester.log("Web server not running. Please start the web application first.", "ERROR")
            return 1
    except:
        tester.log("Web server not accessible. Please start the web application first.", "ERROR")
        return 1
    
    # Run comprehensive tests
    success = tester.run_comprehensive_tests()
    
    if success:
        tester.log("All tests passed! Proceeding with Docker push...", "SUCCESS")
        return 0
    else:
        tester.log("Tests failed! Cannot proceed with Docker push.", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())
