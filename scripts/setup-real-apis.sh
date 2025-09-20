#!/bin/bash

# =============================================================================
# VANTAGE AI - Real API Setup Script
# =============================================================================
# This script helps you set up real API integrations

set -e

echo "🚀 VANTAGE AI - Real API Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp env.example .env
    print_status "Created .env file from template"
fi

echo ""
echo "📋 SETUP CHECKLIST"
echo "=================="
echo ""
echo "Before proceeding, make sure you have:"
echo "1. ✅ Facebook Developer Account (https://developers.facebook.com)"
echo "2. ✅ Facebook Page (for publishing content)"
echo "3. ✅ Instagram Business Account (optional, for Instagram publishing)"
echo "4. ✅ LinkedIn Developer Account (https://www.linkedin.com/developers/apps)"
echo "5. ✅ OpenAI API Key (https://platform.openai.com/api-keys)"
echo ""

read -p "Do you have all the required accounts? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Please set up the required accounts first. See docs/META_SETUP_GUIDE.md for details."
    exit 1
fi

echo ""
echo "🔧 CONFIGURING REAL API INTEGRATIONS"
echo "===================================="

# Meta/Facebook Configuration
echo ""
print_info "Meta/Facebook API Configuration"
echo "-----------------------------------"
read -p "Enter your Meta App ID: " META_APP_ID
read -p "Enter your Meta App Secret: " META_APP_SECRET
read -p "Enter your Facebook Page ID: " META_PAGE_ID
read -p "Enter your Instagram Business Account ID (optional): " META_IG_BUSINESS_ID

# LinkedIn Configuration
echo ""
print_info "LinkedIn API Configuration"
echo "-----------------------------"
read -p "Enter your LinkedIn Client ID: " LINKEDIN_CLIENT_ID
read -p "Enter your LinkedIn Client Secret: " LINKEDIN_CLIENT_SECRET
read -p "Enter your LinkedIn Organization URN: " LINKEDIN_PAGE_URN

# AI Configuration
echo ""
print_info "AI API Configuration"
echo "----------------------"
read -p "Enter your OpenAI API Key: " OPENAI_API_KEY
read -p "Enter your Anthropic API Key (optional): " ANTHROPIC_API_KEY

# Update .env file
echo ""
print_info "Updating .env file with real API credentials..."

# Create backup
cp .env .env.backup
print_status "Created backup of .env file"

# Update Meta configuration
sed -i.bak "s/META_APP_ID=.*/META_APP_ID=$META_APP_ID/" .env
sed -i.bak "s/META_APP_SECRET=.*/META_APP_SECRET=$META_APP_SECRET/" .env
sed -i.bak "s/META_PAGE_ID=.*/META_PAGE_ID=$META_PAGE_ID/" .env
sed -i.bak "s/META_IG_BUSINESS_ID=.*/META_IG_BUSINESS_ID=$META_IG_BUSINESS_ID/" .env

# Update LinkedIn configuration
sed -i.bak "s/LINKEDIN_CLIENT_ID=.*/LINKEDIN_CLIENT_ID=$LINKEDIN_CLIENT_ID/" .env
sed -i.bak "s/LINKEDIN_CLIENT_SECRET=.*/LINKEDIN_CLIENT_SECRET=$LINKEDIN_CLIENT_SECRET/" .env
sed -i.bak "s/LINKEDIN_PAGE_URN=.*/LINKEDIN_PAGE_URN=$LINKEDIN_PAGE_URN/" .env

# Update AI configuration
sed -i.bak "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$OPENAI_API_KEY/" .env
sed -i.bak "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY/" .env

# Enable real API calls
sed -i.bak "s/DRY_RUN=.*/DRY_RUN=false/" .env
sed -i.bak "s/NEXT_PUBLIC_MOCK_MODE=.*/NEXT_PUBLIC_MOCK_MODE=false/" .env

# Clean up backup files
rm .env.bak

print_status "Updated .env file with real API credentials"

echo ""
echo "🧪 TESTING CONFIGURATION"
echo "========================"

# Test if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Test if services are running
if ! docker compose ps | grep -q "vantage-db"; then
    print_warning "Database not running. Starting services..."
    docker compose up -d db redis
    sleep 10
fi

print_status "Database and Redis are running"

echo ""
echo "🚀 STARTING APPLICATION"
echo "======================"

# Start the application
print_info "Starting VANTAGE AI with real API integrations..."
docker compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 15

# Test API health
print_info "Testing API health..."
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    print_status "API is healthy"
else
    print_warning "API health check failed. Check logs with: docker compose logs api"
fi

# Test web health
print_info "Testing web health..."
if curl -f http://localhost:3000/healthz > /dev/null 2>&1; then
    print_status "Web application is healthy"
else
    print_warning "Web health check failed. Check logs with: docker compose logs web"
fi

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "Your VANTAGE AI application is now running with real API integrations:"
echo ""
echo "🌐 Web Application: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 API Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to http://localhost:3000/integrations"
echo "2. Click 'Connect Facebook' to test OAuth flow"
echo "3. Create a test post in the composer"
echo "4. Publish to Facebook to verify real integration"
echo ""
echo "📖 For detailed setup instructions, see:"
echo "   - docs/META_SETUP_GUIDE.md"
echo "   - docs/social_media_integration.md"
echo ""
echo "🔧 To view logs:"
echo "   docker compose logs -f api    # API logs"
echo "   docker compose logs -f web    # Web logs"
echo "   docker compose logs -f worker # Worker logs"
echo ""
print_status "Real API integration setup complete!"
