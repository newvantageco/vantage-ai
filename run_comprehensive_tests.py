#!/usr/bin/env python3
"""
Comprehensive test runner for systematic line-by-line testing.
Runs all comprehensive test suites and reports results.
"""

import sys
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def run_test_file(test_file: str) -> dict:
    """Run a single test file and return results."""
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Run pytest on the specific file
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            test_file, 
            '-v', 
            '--tb=short',
            '--disable-warnings'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        duration = time.time() - start_time
        
        return {
            'file': test_file,
            'success': result.returncode == 0,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
    except Exception as e:
        duration = time.time() - start_time
        return {
            'file': test_file,
            'success': False,
            'duration': duration,
            'stdout': '',
            'stderr': str(e),
            'returncode': 1
        }

def run_existing_tests() -> dict:
    """Run existing test files."""
    print(f"\n{'='*60}")
    print("Running existing test files")
    print(f"{'='*60}")
    
    existing_tests = [
        'tests/test_bandit.py',
        'tests/test_model_router.py',
        'tests/test_safety.py',
        'tests/test_optimiser_worker.py',
        'tests/test_scheduler.py',
        'tests/test_weekly_brief.py',
        'tests/test_reward_calculation.py',
        'tests/test_post_metrics_upsert.py',
        'tests/test_e2e_mocks.py'
    ]
    
    results = []
    for test_file in existing_tests:
        if os.path.exists(test_file):
            result = run_test_file(test_file)
            results.append(result)
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    return results

def run_comprehensive_tests() -> dict:
    """Run comprehensive test files."""
    print(f"\n{'='*60}")
    print("Running comprehensive test files")
    print(f"{'='*60}")
    
    comprehensive_tests = [
        'tests/test_enhanced_router_comprehensive.py',
        'tests/test_budget_guard_comprehensive.py',
        'tests/test_safety_comprehensive.py',
        'tests/test_rules_engine_comprehensive.py',
        'tests/test_publishers_comprehensive.py'
    ]
    
    results = []
    for test_file in comprehensive_tests:
        if os.path.exists(test_file):
            result = run_test_file(test_file)
            results.append(result)
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    return results

def run_ai_optimization_tests() -> dict:
    """Run AI optimization specific tests."""
    print(f"\n{'='*60}")
    print("Running AI optimization tests")
    print(f"{'='*60}")
    
    ai_tests = [
        'test_ai_optimization.py',
        'test_privacy.py'
    ]
    
    results = []
    for test_file in ai_tests:
        if os.path.exists(test_file):
            print(f"\nRunning {test_file}...")
            start_time = time.time()
            
            try:
                result = subprocess.run([
                    sys.executable, test_file
                ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
                
                duration = time.time() - start_time
                
                results.append({
                    'file': test_file,
                    'success': result.returncode == 0,
                    'duration': duration,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                })
                
            except Exception as e:
                duration = time.time() - start_time
                results.append({
                    'file': test_file,
                    'success': False,
                    'duration': duration,
                    'stdout': '',
                    'stderr': str(e),
                    'returncode': 1
                })
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    return results

def print_summary(all_results: list):
    """Print test summary."""
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"Total test files: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    total_duration = sum(r['duration'] for r in all_results)
    print(f"Total duration: {total_duration:.2f} seconds")
    
    if failed_tests > 0:
        print(f"\n{'='*60}")
        print("FAILED TESTS")
        print(f"{'='*60}")
        
        for result in all_results:
            if not result['success']:
                print(f"\n❌ {result['file']}")
                print(f"   Duration: {result['duration']:.2f}s")
                print(f"   Return code: {result['returncode']}")
                if result['stderr']:
                    print(f"   Error: {result['stderr'][:200]}...")
    
    print(f"\n{'='*60}")
    print("DETAILED RESULTS")
    print(f"{'='*60}")
    
    for result in all_results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {result['file']:<50} ({result['duration']:.2f}s)")
        
        if not result['success'] and result['stderr']:
            print(f"    Error: {result['stderr'][:100]}...")

def main():
    """Main test runner function."""
    print("🚀 Starting Comprehensive Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Run existing tests
    existing_results = run_existing_tests()
    all_results.extend(existing_results)
    
    # Run comprehensive tests
    comprehensive_results = run_comprehensive_tests()
    all_results.extend(comprehensive_results)
    
    # Run AI optimization tests
    ai_results = run_ai_optimization_tests()
    all_results.extend(ai_results)
    
    # Print summary
    print_summary(all_results)
    
    # Return exit code
    failed_count = sum(1 for r in all_results if not r['success'])
    return 1 if failed_count > 0 else 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
