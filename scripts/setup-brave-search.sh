#!/bin/bash

# =============================================================================
# Brave Search Integration Setup Script for VANTAGE AI
# =============================================================================

set -e

echo "🚀 Setting up Brave Search Integration for VANTAGE AI"
echo "=================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Add Brave Search API key to .env file
echo "🔑 Adding Brave Search API key to .env file..."

# Check if BRAVE_API_KEY already exists in .env
if grep -q "BRAVE_API_KEY=" .env; then
    echo "⚠️  BRAVE_API_KEY already exists in .env file"
    echo "   Current value: $(grep 'BRAVE_API_KEY=' .env)"
    echo "   To update it, manually edit the .env file"
else
    # Add the API key
    echo "BRAVE_API_KEY=BSAso6On09fy4xKCg9FDG58TkRSqMWd" >> .env
    echo "✅ Brave Search API key added to .env file"
fi

# Install dependencies (if needed)
echo "📦 Checking dependencies..."
if ! python -c "import aiohttp" 2>/dev/null; then
    echo "📦 Installing aiohttp..."
    pip install aiohttp==3.9.1
    echo "✅ aiohttp installed"
else
    echo "✅ aiohttp already installed"
fi

# Test the integration
echo "🧪 Testing Brave Search integration..."
if python test_brave_search.py; then
    echo "✅ Brave Search integration test passed!"
else
    echo "❌ Brave Search integration test failed!"
    echo "   Please check your API key and internet connection"
    exit 1
fi

echo ""
echo "🎉 Brave Search Integration Setup Complete!"
echo "=========================================="
echo ""
echo "📋 What was set up:"
echo "   ✅ Brave Search API integration"
echo "   ✅ REST API endpoints at /api/v1/brave-search/"
echo "   ✅ High-level service functions"
echo "   ✅ Test scripts"
echo ""
echo "🔗 Available API Endpoints:"
echo "   • POST /api/v1/brave-search/web - Web search"
echo "   • POST /api/v1/brave-search/news - News search"
echo "   • POST /api/v1/brave-search/images - Image search"
echo "   • POST /api/v1/brave-search/videos - Video search"
echo "   • POST /api/v1/brave-search/local - Local business search"
echo "   • POST /api/v1/brave-search/summary - AI summary generation"
echo "   • GET  /api/v1/brave-search/health - Health check"
echo ""
echo "🚀 To start using:"
echo "   1. Start your VANTAGE AI server: python -m uvicorn app.main:app --reload"
echo "   2. Visit http://localhost:8000/docs to see the API documentation"
echo "   3. Use the Brave Search endpoints in your applications"
echo ""
echo "📚 Example usage in Python:"
echo "   from app.services.brave_search_service import research_topic"
echo "   result = await research_topic('AI marketing trends')"
echo ""
echo "✨ Happy searching!"
