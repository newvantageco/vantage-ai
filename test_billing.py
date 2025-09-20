#!/usr/bin/env python3
"""
Test script for Billing System
Tests the real billing API endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_billing_status():
    """Test billing service status"""
    print("💳 Testing Billing Service Status...")
    
    try:
        response = requests.get(f"{API_BASE}/billing/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Billing Service Status:")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Features: {', '.join(status_data.get('features', []))}")
            print(f"   Plans: {', '.join(status_data.get('supported_plans', []))}")
            print(f"   Payment Methods: {', '.join(status_data.get('payment_methods', []))}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_available_plans():
    """Test getting available subscription plans"""
    print("📋 Testing Available Plans...")
    
    try:
        response = requests.get(f"{API_BASE}/billing/plans", timeout=10)
        if response.status_code == 200:
            plans_data = response.json()
            print("✅ Available Plans:")
            for plan in plans_data:
                print(f"   📦 {plan['name']} Plan:")
                print(f"      Price: ${plan['price_monthly']/100:.2f}/month, ${plan['price_yearly']/100:.2f}/year")
                print(f"      Features: {len(plan['features'])} features")
                print(f"      AI Requests: {plan['limits']['ai_requests']}")
                print(f"      Posts: {plan['limits']['posts']}")
                print(f"      Team Members: {plan['limits']['team_members']}")
                print(f"      Storage: {plan['limits']['storage_mb']/1024:.1f}GB")
            return True
        else:
            print(f"❌ Plans check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Plans check error: {e}")
        return False

def test_billing_summary():
    """Test getting billing summary"""
    print("📊 Testing Billing Summary...")
    
    try:
        response = requests.get(f"{API_BASE}/billing/subscription", timeout=10)
        if response.status_code == 200:
            summary_data = response.json()
            subscription = summary_data.get('subscription', {})
            usage = summary_data.get('usage', {})
            
            print("✅ Billing Summary:")
            print(f"   Plan: {subscription.get('plan_id', 'N/A')}")
            print(f"   Status: {subscription.get('status', 'N/A')}")
            print(f"   Next Billing: {summary_data.get('next_billing_date', 'N/A')}")
            print(f"   Amount Due: ${summary_data.get('amount_due', 0)/100:.2f}")
            print(f"   AI Usage: {usage.get('ai_requests', 0)}/{usage.get('ai_requests_limit', 0)}")
            print(f"   Posts: {usage.get('posts_published', 0)}/{usage.get('posts_limit', 0)}")
            print(f"   Team: {usage.get('team_members', 0)}/{usage.get('team_members_limit', 0)}")
            print(f"   Storage: {usage.get('storage_used', 0)/1024:.1f}GB/{usage.get('storage_limit', 0)/1024:.1f}GB")
            return True
        else:
            print(f"❌ Billing summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Billing summary error: {e}")
        return False

def test_usage_details():
    """Test getting detailed usage information"""
    print("📈 Testing Usage Details...")
    
    try:
        response = requests.get(f"{API_BASE}/billing/usage", timeout=10)
        if response.status_code == 200:
            usage_data = response.json()
            print("✅ Usage Details:")
            
            # AI Usage
            ai_usage = usage_data.get('ai_usage', {})
            print(f"   🤖 AI Usage:")
            print(f"      Requests: {ai_usage.get('requests_used', 0)}/{ai_usage.get('requests_limit', 0)} ({ai_usage.get('percentage_used', 0):.1f}%)")
            print(f"      Cost: ${ai_usage.get('cost_this_period', 0)/100:.2f}")
            
            # Publishing Usage
            pub_usage = usage_data.get('publishing_usage', {})
            print(f"   📱 Publishing Usage:")
            print(f"      Posts: {pub_usage.get('posts_published', 0)}/{pub_usage.get('posts_limit', 0)} ({pub_usage.get('percentage_used', 0):.1f}%)")
            print(f"      Platforms: {', '.join(pub_usage.get('platforms_used', []))}")
            
            # Team Usage
            team_usage = usage_data.get('team_usage', {})
            print(f"   👥 Team Usage:")
            print(f"      Members: {team_usage.get('active_members', 0)}/{team_usage.get('members_limit', 0)} ({team_usage.get('percentage_used', 0):.1f}%)")
            
            # Storage Usage
            storage_usage = usage_data.get('storage_usage', {})
            print(f"   💾 Storage Usage:")
            print(f"      Used: {storage_usage.get('used_mb', 0)/1024:.1f}GB/{storage_usage.get('limit_mb', 0)/1024:.1f}GB ({storage_usage.get('percentage_used', 0):.1f}%)")
            print(f"      Files: {storage_usage.get('files_count', 0)}")
            
            return True
        else:
            print(f"❌ Usage details failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Usage details error: {e}")
        return False

def test_checkout_session():
    """Test creating checkout session"""
    print("🛒 Testing Checkout Session Creation...")
    
    try:
        # Test different plans and billing cycles
        test_cases = [
            {"plan_id": "starter", "billing_cycle": "monthly"},
            {"plan_id": "growth", "billing_cycle": "yearly"},
            {"plan_id": "pro", "billing_cycle": "monthly"}
        ]
        
        for test_case in test_cases:
            print(f"   📦 Testing {test_case['plan_id']} plan ({test_case['billing_cycle']})...")
            response = requests.post(
                f"{API_BASE}/billing/checkout",
                params=test_case,
                timeout=15
            )
            
            if response.status_code == 200:
                checkout_data = response.json()
                session = checkout_data.get('checkout_session', {})
                print(f"      ✅ Session created: {session.get('session_id', 'N/A')}")
                print(f"      URL: {session.get('url', 'N/A')[:50]}...")
            else:
                print(f"      ❌ Failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Checkout session error: {e}")
        return False

def test_customer_portal():
    """Test creating customer portal session"""
    print("🏢 Testing Customer Portal...")
    
    try:
        response = requests.post(f"{API_BASE}/billing/portal", timeout=15)
        if response.status_code == 200:
            portal_data = response.json()
            session = portal_data.get('portal_session', {})
            print("✅ Customer Portal:")
            print(f"   URL: {session.get('url', 'N/A')[:50]}...")
            print(f"   Expires: {session.get('expires_at', 'N/A')}")
            return True
        else:
            print(f"❌ Customer portal failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Customer portal error: {e}")
        return False

def test_invoices():
    """Test getting billing history"""
    print("📄 Testing Billing History...")
    
    try:
        response = requests.get(f"{API_BASE}/billing/invoices?limit=5", timeout=10)
        if response.status_code == 200:
            invoices_data = response.json()
            invoices = invoices_data.get('invoices', [])
            print("✅ Billing History:")
            print(f"   Total Invoices: {invoices_data.get('total_count', 0)}")
            print(f"   Showing: {len(invoices)} invoices")
            
            for i, invoice in enumerate(invoices, 1):
                print(f"   {i}. {invoice.get('number', 'N/A')}:")
                print(f"      Date: {invoice.get('date', 'N/A')}")
                print(f"      Amount: ${invoice.get('amount', 0)/100:.2f}")
                print(f"      Status: {invoice.get('status', 'N/A')}")
                print(f"      Description: {invoice.get('description', 'N/A')}")
            
            return True
        else:
            print(f"❌ Invoices failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invoices error: {e}")
        return False

def main():
    """Run all billing tests"""
    print("🚀 VANTAGE AI - Billing System Test Suite")
    print("=" * 60)
    
    # Test 1: Service Status
    status_ok = test_billing_status()
    print()
    
    # Test 2: Available Plans
    plans_ok = test_available_plans()
    print()
    
    # Test 3: Billing Summary
    summary_ok = test_billing_summary()
    print()
    
    # Test 4: Usage Details
    usage_ok = test_usage_details()
    print()
    
    # Test 5: Checkout Session
    checkout_ok = test_checkout_session()
    print()
    
    # Test 6: Customer Portal
    portal_ok = test_customer_portal()
    print()
    
    # Test 7: Billing History
    invoices_ok = test_invoices()
    print()
    
    # Summary
    print("📋 Billing Test Summary:")
    print(f"✅ Service Status: {'PASS' if status_ok else 'FAIL'}")
    print(f"✅ Available Plans: {'PASS' if plans_ok else 'FAIL'}")
    print(f"✅ Billing Summary: {'PASS' if summary_ok else 'FAIL'}")
    print(f"✅ Usage Details: {'PASS' if usage_ok else 'FAIL'}")
    print(f"✅ Checkout Session: {'PASS' if checkout_ok else 'FAIL'}")
    print(f"✅ Customer Portal: {'PASS' if portal_ok else 'FAIL'}")
    print(f"✅ Billing History: {'PASS' if invoices_ok else 'FAIL'}")
    
    if all([status_ok, plans_ok, summary_ok, usage_ok, checkout_ok, portal_ok, invoices_ok]):
        print("\n🎉 All billing tests passed! Billing system is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
