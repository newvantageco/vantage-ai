#!/usr/bin/env python3
"""
Check documentation completeness
"""
import os
import re
import sys
from pathlib import Path

def check_docs():
    """Check documentation files for completeness"""
    errors = []
    
    # Check README.md
    readme_path = Path("README.md")
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            content = f.read()
            
        required_sections = [
            "## Quick Start",
            "## Architecture", 
            "## API Endpoints",
            "## Environment Variables",
            "## Deployment",
            "## Contributing"
        ]
        
        for section in required_sections:
            if section not in content:
                errors.append(f"❌ README.md missing section: {section}")
    else:
        errors.append("❌ README.md not found")
    
    # Check API documentation
    api_docs = Path("docs/api.md")
    if not api_docs.exists():
        errors.append("❌ docs/api.md not found")
    
    # Check environment documentation
    env_docs = Path("docs/ENV.md")
    if not env_docs.exists():
        errors.append("❌ docs/ENV.md not found")
    
    if errors:
        print("Documentation issues found:")
        for error in errors:
            print(error)
        return 1
    
    print("✅ Documentation looks complete")
    return 0

if __name__ == "__main__":
    sys.exit(check_docs())
