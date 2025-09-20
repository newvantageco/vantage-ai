#!/usr/bin/env python3
"""
Check environment files for security issues
"""
import os
import re
import sys
from pathlib import Path

def check_env_files():
    """Check environment files for security issues"""
    env_files = [".env", ".env.local", ".env.production", "web/.env.local"]
    errors = []
    
    for env_file in env_files:
        if not Path(env_file).exists():
            continue
            
        with open(env_file, 'r') as f:
            content = f.read()
            
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\']?[^"\'\s]+["\']?',
            r'secret\s*=\s*["\']?[^"\'\s]+["\']?',
            r'key\s*=\s*["\']?[^"\'\s]+["\']?',
            r'token\s*=\s*["\']?[^"\'\s]+["\']?',
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if not any(placeholder in match.lower() for placeholder in ['your_', 'placeholder', 'example', 'xxx', '***']):
                    errors.append(f"❌ {env_file}: Potential hardcoded secret found: {match}")
    
    if errors:
        print("Environment file security issues found:")
        for error in errors:
            print(error)
        return 1
    
    print("✅ Environment files look secure")
    return 0

if __name__ == "__main__":
    sys.exit(check_env_files())
