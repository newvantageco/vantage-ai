#!/bin/bash

# Vantage AI - Comprehensive Cleanup Script
# This script removes temporary files, cache files, and build artifacts

set -e

echo "🧹 Starting Vantage AI cleanup process..."

# Function to safely remove files/directories
safe_remove() {
    local path="$1"
    local description="$2"
    
    if [ -e "$path" ]; then
        echo "  🗑️  Removing $description: $path"
        rm -rf "$path"
    else
        echo "  ✅ $description not found: $path"
    fi
}

# Function to count files before removal
count_files() {
    local pattern="$1"
    local count=$(find . -name "$pattern" -type f 2>/dev/null | wc -l)
    echo "$count"
}

echo ""
echo "📊 Analyzing cleanup targets..."

# Count files to be removed
pycache_count=$(count_files "__pycache__")
pyc_count=$(count_files "*.pyc")
pytest_count=$(count_files ".pytest_cache")
coverage_count=$(count_files ".coverage*")
tsbuild_count=$(count_files "*.tsbuildinfo")
next_count=$(count_files ".next")
node_modules_count=$(count_files "node_modules")
dist_count=$(count_files "dist")
build_count=$(count_files "build")
cache_count=$(count_files ".cache")
log_count=$(count_files "*.log")
tmp_count=$(count_files "*.tmp")
temp_count=$(count_files "*.temp")
bak_count=$(count_files "*.bak")
backup_count=$(count_files "*.backup")
old_count=$(count_files "*.old")
ds_store_count=$(count_files ".DS_Store")

echo "  📈 Found:"
echo "    - $pycache_count __pycache__ directories"
echo "    - $pyc_count .pyc files"
echo "    - $pytest_count .pytest_cache directories"
echo "    - $coverage_count coverage files"
echo "    - $tsbuild_count TypeScript build info files"
echo "    - $next_count .next directories"
echo "    - $node_modules_count node_modules directories"
echo "    - $dist_count dist directories"
echo "    - $build_count build directories"
echo "    - $cache_count .cache directories"
echo "    - $log_count log files"
echo "    - $tmp_count .tmp files"
echo "    - $temp_count .temp files"
echo "    - $bak_count .bak files"
echo "    - $backup_count .backup files"
echo "    - $old_count .old files"
echo "    - $ds_store_count .DS_Store files"

echo ""
echo "🗑️  Starting cleanup process..."

# Python cache files
echo ""
echo "🐍 Cleaning Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true
find . -name "*.pyd" -type f -delete 2>/dev/null || true

# Test and coverage files
echo ""
echo "🧪 Cleaning test and coverage files..."
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".coverage*" -type f -delete 2>/dev/null || true
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".tox" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".nox" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".hypothesis" -type d -exec rm -rf {} + 2>/dev/null || true

# Node.js and TypeScript files
echo ""
echo "📦 Cleaning Node.js and TypeScript files..."
find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".next" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.tsbuildinfo" -type f -delete 2>/dev/null || true
find . -name ".cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".parcel-cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Log files
echo ""
echo "📝 Cleaning log files..."
find . -name "*.log" -type f -delete 2>/dev/null || true
find . -name "logs" -type d -exec rm -rf {} + 2>/dev/null || true

# Temporary files
echo ""
echo "🗂️  Cleaning temporary files..."
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.temp" -type f -delete 2>/dev/null || true
find . -name "tmp" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "temp" -type d -exec rm -rf {} + 2>/dev/null || true

# Backup files
echo ""
echo "💾 Cleaning backup files..."
find . -name "*.bak" -type f -delete 2>/dev/null || true
find . -name "*.backup" -type f -delete 2>/dev/null || true
find . -name "*.old" -type f -delete 2>/dev/null || true

# OS files
echo ""
echo "🖥️  Cleaning OS files..."
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "Thumbs.db" -type f -delete 2>/dev/null || true
find . -name "ehthumbs.db" -type f -delete 2>/dev/null || true
find . -name "*.swp" -type f -delete 2>/dev/null || true
find . -name "*.swo" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true

# IDE files
echo ""
echo "💻 Cleaning IDE files..."
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".idea" -type d -exec rm -rf {} + 2>/dev/null || true

# Docker cleanup (optional - be careful with this)
echo ""
echo "🐳 Cleaning Docker artifacts (optional)..."
# Uncomment the following lines if you want to clean Docker artifacts
# docker system prune -f 2>/dev/null || true
# docker volume prune -f 2>/dev/null || true
echo "  ⚠️  Docker cleanup skipped (uncomment in script if needed)"

# Database files
echo ""
echo "🗄️  Cleaning database files..."
find . -name "*.db" -type f -delete 2>/dev/null || true
find . -name "*.sqlite" -type f -delete 2>/dev/null || true
find . -name "*.sqlite3" -type f -delete 2>/dev/null || true
find . -name "dump.rdb" -type f -delete 2>/dev/null || true

# Environment files (be careful!)
echo ""
echo "🔐 Checking for environment files..."
if [ -f ".env" ] && [ ! -f ".env.sample" ]; then
    echo "  ⚠️  Found .env file without .env.sample - skipping for safety"
else
    find . -name ".env" -not -name ".env.sample" -not -name ".env.example" -type f -delete 2>/dev/null || true
fi

echo ""
echo "📊 Cleanup summary:"
echo "  ✅ Python cache files removed"
echo "  ✅ Test and coverage files removed"
echo "  ✅ Node.js and TypeScript build files removed"
echo "  ✅ Log files removed"
echo "  ✅ Temporary files removed"
echo "  ✅ Backup files removed"
echo "  ✅ OS files removed"
echo "  ✅ IDE files removed"
echo "  ✅ Database files removed"
echo "  ✅ Environment files cleaned (safely)"

echo ""
echo "🎉 Cleanup completed successfully!"
echo ""
echo "💡 To reinstall dependencies:"
echo "  - Python: pip install -r requirements.txt"
echo "  - Node.js: cd web && npm install"
echo "  - Docker: docker-compose up --build"
echo ""
echo "💡 To start development:"
echo "  - ./scripts/dev_up.sh"
