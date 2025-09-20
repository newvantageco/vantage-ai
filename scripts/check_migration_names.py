#!/usr/bin/env python3
"""
Check migration file naming conventions
"""
import os
import re
import sys
from pathlib import Path

def check_migration_names():
    """Check that migration files follow naming conventions"""
    versions_dir = Path("alembic/versions")
    if not versions_dir.exists():
        print("❌ alembic/versions directory not found")
        return 1
    
    errors = []
    pattern = re.compile(r'^\d{4}_[a-z0-9_]+\.py$')
    
    for file_path in versions_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
            
        if not pattern.match(file_path.name):
            errors.append(f"❌ {file_path.name} doesn't follow naming convention (YYYY_description.py)")
    
    if errors:
        print("Migration naming errors found:")
        for error in errors:
            print(error)
        return 1
    
    print("✅ All migration files follow naming conventions")
    return 0

if __name__ == "__main__":
    sys.exit(check_migration_names())
