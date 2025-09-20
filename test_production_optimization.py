#!/usr/bin/env python3
"""
Test script for Production Optimization System
Tests the real production optimization API endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_production_status():
    """Test production status endpoint"""
    print("🏭 Testing Production Status...")
    
    try:
        response = requests.get(f"{API_BASE}/production/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Production Status:")
            print(f"   Environment: {status_data.get('environment', 'N/A')}")
            print(f"   Version: {status_data.get('version', 'N/A')}")
            print(f"   Build Date: {status_data.get('build_date', 'N/A')}")
            print(f"   Deployment ID: {status_data.get('deployment_id', 'N/A')}")
            
            # System Health
            system_health = status_data.get('system_health', {})
            print(f"   System Health: {system_health.get('status', 'N/A')}")
            print(f"   Memory Usage: {system_health.get('memory_usage', 0):.1f}%")
            print(f"   CPU Usage: {system_health.get('cpu_usage', 0):.1f}%")
            print(f"   Disk Usage: {system_health.get('disk_usage', 0):.1f}%")
            
            # Database Health
            db_health = status_data.get('database_health', {})
            print(f"   Database Status: {db_health.get('status', 'N/A')}")
            
            # Cache Health
            cache_health = status_data.get('cache_health', {})
            print(f"   Cache Status: {cache_health.get('status', 'N/A')}")
            print(f"   Redis Connected: {cache_health.get('redis_connected', False)}")
            
            # API Performance
            api_perf = status_data.get('api_performance', {})
            print(f"   API Status: {api_perf.get('status', 'N/A')}")
            print(f"   Avg Response Time: {api_perf.get('response_time_avg', 0):.1f}ms")
            print(f"   Requests/min: {api_perf.get('requests_per_minute', 0)}")
            
            # Security Status
            security = status_data.get('security_status', {})
            print(f"   Security Status: {security.get('status', 'N/A')}")
            print(f"   SSL Enabled: {security.get('ssl_enabled', False)}")
            print(f"   Rate Limiting: {security.get('rate_limiting', False)}")
            
            return True
        else:
            print(f"❌ Production status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Production status check error: {e}")
        return False

def test_system_health():
    """Test system health endpoint"""
    print("💻 Testing System Health...")
    
    try:
        response = requests.get(f"{API_BASE}/production/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ System Health:")
            print(f"   Status: {health_data.get('status', 'N/A')}")
            print(f"   Uptime: {health_data.get('uptime', 0):.1f} seconds")
            print(f"   Memory Usage: {health_data.get('memory_usage', 0):.1f}%")
            print(f"   CPU Usage: {health_data.get('cpu_usage', 0):.1f}%")
            print(f"   Disk Usage: {health_data.get('disk_usage', 0):.1f}%")
            print(f"   Active Connections: {health_data.get('active_connections', 0)}")
            return True
        else:
            print(f"❌ System health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ System health check error: {e}")
        return False

def test_database_health():
    """Test database health endpoint"""
    print("🗄️ Testing Database Health...")
    
    try:
        response = requests.get(f"{API_BASE}/production/database", timeout=10)
        if response.status_code == 200:
            db_data = response.json()
            print("✅ Database Health:")
            print(f"   Status: {db_data.get('status', 'N/A')}")
            
            # Connection Pool
            pool = db_data.get('connection_pool', {})
            print(f"   Connection Pool:")
            print(f"      Active: {pool.get('active', 0)}")
            print(f"      Idle: {pool.get('idle', 0)}")
            print(f"      Max: {pool.get('max', 0)}")
            print(f"      Waiting: {pool.get('waiting', 0)}")
            
            # Query Performance
            perf = db_data.get('query_performance', {})
            print(f"   Query Performance:")
            print(f"      Avg Response Time: {perf.get('avg_response_time', 0):.1f}ms")
            print(f"      Slow Queries: {perf.get('slow_queries', 0)}")
            print(f"      Total Queries: {perf.get('total_queries', 0)}")
            
            print(f"   Last Backup: {db_data.get('last_backup', 'N/A')}")
            print(f"   Replication: {db_data.get('replication_status', 'N/A')}")
            
            return True
        else:
            print(f"❌ Database health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database health check error: {e}")
        return False

def test_cache_health():
    """Test cache health endpoint"""
    print("⚡ Testing Cache Health...")
    
    try:
        response = requests.get(f"{API_BASE}/production/cache", timeout=10)
        if response.status_code == 200:
            cache_data = response.json()
            print("✅ Cache Health:")
            print(f"   Status: {cache_data.get('status', 'N/A')}")
            print(f"   Redis Connected: {cache_data.get('redis_connected', False)}")
            print(f"   Memory Usage: {cache_data.get('memory_usage', 0):.1f}%")
            print(f"   Hit Rate: {cache_data.get('hit_rate', 0):.1f}%")
            print(f"   Active Keys: {cache_data.get('active_keys', 0)}")
            print(f"   Eviction Policy: {cache_data.get('eviction_policy', 'N/A')}")
            return True
        else:
            print(f"❌ Cache health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cache health check error: {e}")
        return False

def test_api_performance():
    """Test API performance endpoint"""
    print("🚀 Testing API Performance...")
    
    try:
        response = requests.get(f"{API_BASE}/production/performance", timeout=10)
        if response.status_code == 200:
            perf_data = response.json()
            print("✅ API Performance:")
            print(f"   Status: {perf_data.get('status', 'N/A')}")
            print(f"   Avg Response Time: {perf_data.get('response_time_avg', 0):.1f}ms")
            print(f"   Requests/min: {perf_data.get('requests_per_minute', 0)}")
            print(f"   Error Rate: {perf_data.get('error_rate', 0):.1f}%")
            print(f"   Active Endpoints: {perf_data.get('active_endpoints', 0)}")
            
            # Rate Limits
            limits = perf_data.get('rate_limits', {})
            print(f"   Rate Limits:")
            print(f"      Per Minute: {limits.get('per_minute', 0)}")
            print(f"      Per Hour: {limits.get('per_hour', 0)}")
            print(f"      Per Day: {limits.get('per_day', 0)}")
            
            return True
        else:
            print(f"❌ API performance check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API performance check error: {e}")
        return False

def test_security_status():
    """Test security status endpoint"""
    print("🔒 Testing Security Status...")
    
    try:
        response = requests.get(f"{API_BASE}/production/security", timeout=10)
        if response.status_code == 200:
            security_data = response.json()
            print("✅ Security Status:")
            print(f"   Status: {security_data.get('status', 'N/A')}")
            print(f"   SSL Enabled: {security_data.get('ssl_enabled', False)}")
            print(f"   CORS Configured: {security_data.get('cors_configured', False)}")
            print(f"   Rate Limiting: {security_data.get('rate_limiting', False)}")
            print(f"   Authentication: {security_data.get('authentication', False)}")
            print(f"   Last Security Scan: {security_data.get('last_security_scan', 'N/A')}")
            print(f"   Vulnerabilities: {security_data.get('vulnerabilities', 0)}")
            return True
        else:
            print(f"❌ Security status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Security status check error: {e}")
        return False

def test_optimization_recommendations():
    """Test optimization recommendations endpoint"""
    print("📈 Testing Optimization Recommendations...")
    
    try:
        response = requests.get(f"{API_BASE}/production/optimizations", timeout=10)
        if response.status_code == 200:
            opt_data = response.json()
            print("✅ Optimization Recommendations:")
            print(f"   Status: {opt_data.get('status', 'N/A')}")
            print(f"   Features: {', '.join(opt_data.get('features', []))}")
            
            # Performance Metrics
            metrics = opt_data.get('performance_metrics', {})
            print(f"   Performance Metrics:")
            print(f"      Total Recommendations: {metrics.get('total_recommendations', 0)}")
            print(f"      High Priority: {metrics.get('high_priority', 0)}")
            print(f"      Medium Priority: {metrics.get('medium_priority', 0)}")
            print(f"      Low Priority: {metrics.get('low_priority', 0)}")
            print(f"      Completed: {metrics.get('completed', 0)}")
            print(f"      In Progress: {metrics.get('in_progress', 0)}")
            print(f"      Pending: {metrics.get('pending', 0)}")
            
            # Recommendations
            recommendations = opt_data.get('optimizations', [])
            print(f"   Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                print(f"      {i}. {rec['title']} ({rec['priority']} priority)")
                print(f"         Category: {rec['category']}")
                print(f"         Impact: {rec['impact']}")
                print(f"         Status: {rec['status']}")
            
            return True
        else:
            print(f"❌ Optimization recommendations check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Optimization recommendations check error: {e}")
        return False

def test_optimization_application():
    """Test optimization application endpoint"""
    print("🔧 Testing Optimization Application...")
    
    try:
        # Test different optimization categories and actions
        test_cases = [
            {"category": "performance", "action": "enable"},
            {"category": "security", "action": "configure"},
            {"category": "caching", "action": "optimize"},
            {"category": "database", "action": "disable"}
        ]
        
        for test_case in test_cases:
            print(f"   🔧 Testing {test_case['category']} - {test_case['action']}...")
            
            response = requests.post(
                f"{API_BASE}/production/optimize",
                params=test_case,
                timeout=15
            )
            
            if response.status_code == 200:
                opt_data = response.json()
                if opt_data.get('success'):
                    print(f"      ✅ {test_case['category'].title()} optimization applied:")
                    print(f"         Action: {opt_data.get('action', 'N/A')}")
                    print(f"         Message: {opt_data.get('message', 'N/A')}")
                else:
                    print(f"      ❌ {test_case['category']} optimization failed: {opt_data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"      ❌ {test_case['category']} optimization failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Optimization application error: {e}")
        return False

def main():
    """Run all production optimization tests"""
    print("🚀 VANTAGE AI - Production Optimization System Test Suite")
    print("=" * 60)
    
    # Test 1: Production Status
    status_ok = test_production_status()
    print()
    
    # Test 2: System Health
    health_ok = test_system_health()
    print()
    
    # Test 3: Database Health
    db_ok = test_database_health()
    print()
    
    # Test 4: Cache Health
    cache_ok = test_cache_health()
    print()
    
    # Test 5: API Performance
    perf_ok = test_api_performance()
    print()
    
    # Test 6: Security Status
    security_ok = test_security_status()
    print()
    
    # Test 7: Optimization Recommendations
    opt_rec_ok = test_optimization_recommendations()
    print()
    
    # Test 8: Optimization Application
    opt_app_ok = test_optimization_application()
    print()
    
    # Summary
    print("📋 Production Optimization Test Summary:")
    print(f"✅ Production Status: {'PASS' if status_ok else 'FAIL'}")
    print(f"✅ System Health: {'PASS' if health_ok else 'FAIL'}")
    print(f"✅ Database Health: {'PASS' if db_ok else 'FAIL'}")
    print(f"✅ Cache Health: {'PASS' if cache_ok else 'FAIL'}")
    print(f"✅ API Performance: {'PASS' if perf_ok else 'FAIL'}")
    print(f"✅ Security Status: {'PASS' if security_ok else 'FAIL'}")
    print(f"✅ Optimization Recommendations: {'PASS' if opt_rec_ok else 'FAIL'}")
    print(f"✅ Optimization Application: {'PASS' if opt_app_ok else 'FAIL'}")
    
    if all([status_ok, health_ok, db_ok, cache_ok, perf_ok, security_ok, opt_rec_ok, opt_app_ok]):
        print("\n🎉 All production optimization tests passed! Production system is ready!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
