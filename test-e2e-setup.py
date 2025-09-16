#!/usr/bin/env python3
"""
Test script to verify E2E testing setup.
Run with: python test-e2e-setup.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and print status."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (missing)")
        return False


def check_package_json() -> bool:
    """Check if package.json has the required scripts."""
    try:
        with open("web/package.json", "r") as f:
            data = json.load(f)
        
        scripts = data.get("scripts", {})
        required_scripts = [
            "test:e2e",
            "test:e2e:ui", 
            "test:e2e:headed",
            "test:e2e:debug"
        ]
        
        missing_scripts = [script for script in required_scripts if script not in scripts]
        
        if missing_scripts:
            print(f"❌ Missing scripts in package.json: {missing_scripts}")
            return False
        else:
            print("✅ All required scripts found in package.json")
            return True
            
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
        return False


def check_playwright_config() -> bool:
    """Check if Playwright config is valid."""
    try:
        # Try to import the config to check for syntax errors
        import subprocess
        result = subprocess.run(
            ["npx", "playwright", "test", "--list"],
            cwd="web",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Playwright configuration is valid")
            return True
        else:
            print(f"❌ Playwright configuration error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Playwright config: {e}")
        return False


def check_mock_system() -> bool:
    """Check if mock system is properly configured."""
    try:
        # Check if mock file exists and is importable
        sys.path.insert(0, "app")
        from api.mocks import MockProvider
        
        mock_provider = MockProvider()
        
        # Test mock data
        oauth_mock = mock_provider.get_oauth_mock("meta")
        if "auth_url" in oauth_mock:
            print("✅ Mock system is working")
            return True
        else:
            print("❌ Mock system not returning expected data")
            return False
            
    except Exception as e:
        print(f"❌ Error checking mock system: {e}")
        return False


def check_github_workflow() -> bool:
    """Check if GitHub workflow file exists."""
    return check_file_exists(
        ".github/workflows/e2e.yml",
        "GitHub Actions E2E workflow"
    )


def check_test_files() -> bool:
    """Check if all test files exist."""
    test_files = [
        "web/tests/e2e/smoke.spec.ts",
        "web/tests/e2e/fixtures/mocks.ts",
        "web/tests/e2e/global-setup.ts",
        "web/tests/e2e/global-teardown.ts",
        "web/playwright.config.ts"
    ]
    
    all_exist = True
    for file_path in test_files:
        if not check_file_exists(file_path, f"Test file"):
            all_exist = False
    
    return all_exist


def check_scripts() -> bool:
    """Check if helper scripts exist and are executable."""
    script_path = "scripts/run-e2e.sh"
    if not check_file_exists(script_path, "E2E runner script"):
        return False
    
    # Check if script is executable
    if not os.access(script_path, os.X_OK):
        print(f"❌ Script not executable: {script_path}")
        return False
    else:
        print(f"✅ Script is executable: {script_path}")
        return True


def main():
    """Run all checks."""
    print("🧪 E2E Testing Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Test Files", check_test_files),
        ("Package.json Scripts", check_package_json),
        ("Playwright Config", check_playwright_config),
        ("Mock System", check_mock_system),
        ("GitHub Workflow", check_github_workflow),
        ("Helper Scripts", check_scripts)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! E2E testing setup is ready.")
        print("\n📝 Next steps:")
        print("  1. Start API server: uvicorn app.main:app --reload --port 8000")
        print("  2. Start web server: cd web && npm run dev")
        print("  3. Run tests: ./scripts/run-e2e.sh")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
