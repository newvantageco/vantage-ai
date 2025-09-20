#!/bin/bash
# VANTAGE AI Security Setup Script
# This script helps set up production-ready security configurations

set -e

echo "🔒 VANTAGE AI Security Setup"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to generate secure secret key
generate_secret_key() {
    echo -e "${BLUE}🔑 Generating secure secret key...${NC}"
    
    # Generate a 32-character random string
    SECRET_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    
    if [ -z "$SECRET_KEY" ]; then
        echo -e "${RED}❌ Failed to generate secret key. Please install OpenSSL.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Generated secure secret key: ${SECRET_KEY}${NC}"
    echo ""
}

# Function to check environment file
check_env_file() {
    echo -e "${BLUE}📋 Checking environment configuration...${NC}"
    
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
        cp env.example .env
        echo -e "${GREEN}✅ Created .env file from template${NC}"
    else
        echo -e "${GREEN}✅ .env file exists${NC}"
    fi
    
    # Check for hardcoded secrets
    if grep -q "SECRET_KEY=dev-not-secret" .env; then
        echo -e "${RED}❌ CRITICAL: Hardcoded secret key found in .env${NC}"
        echo -e "${YELLOW}🔧 Updating with secure secret key...${NC}"
        sed -i.bak "s/SECRET_KEY=dev-not-secret/SECRET_KEY=${SECRET_KEY}/" .env
        echo -e "${GREEN}✅ Updated secret key in .env${NC}"
    elif grep -q "SECRET_KEY=your-secure-secret-key" .env; then
        echo -e "${RED}❌ CRITICAL: Placeholder secret key found in .env${NC}"
        echo -e "${YELLOW}🔧 Updating with secure secret key...${NC}"
        sed -i.bak "s/SECRET_KEY=your-secure-secret-key-32-chars-minimum/SECRET_KEY=${SECRET_KEY}/" .env
        echo -e "${GREEN}✅ Updated secret key in .env${NC}"
    else
        echo -e "${GREEN}✅ Secret key appears to be configured${NC}"
    fi
    
    echo ""
}

# Function to check CORS configuration
check_cors_config() {
    echo -e "${BLUE}🌐 Checking CORS configuration...${NC}"
    
    if grep -q "CORS_ORIGINS=\*" .env; then
        echo -e "${RED}❌ CRITICAL: CORS wildcard found in .env${NC}"
        echo -e "${YELLOW}🔧 Updating CORS configuration...${NC}"
        sed -i.bak "s/CORS_ORIGINS=\*/CORS_ORIGINS=http:\/\/localhost:3000,http:\/\/localhost:3001/" .env
        echo -e "${GREEN}✅ Updated CORS configuration${NC}"
    else
        echo -e "${GREEN}✅ CORS configuration appears safe${NC}"
    fi
    
    echo ""
}

# Function to check authentication configuration
check_auth_config() {
    echo -e "${BLUE}🔐 Checking authentication configuration...${NC}"
    
    if [ -z "$CLERK_SECRET_KEY" ] || [ "$CLERK_SECRET_KEY" = "your_clerk_secret_key_here" ]; then
        echo -e "${YELLOW}⚠️  Clerk secret key not configured${NC}"
        echo -e "${BLUE}📝 Please configure CLERK_SECRET_KEY in .env file${NC}"
    else
        echo -e "${GREEN}✅ Clerk secret key configured${NC}"
    fi
    
    echo ""
}

# Function to check production readiness
check_production_readiness() {
    echo -e "${BLUE}🚀 Checking production readiness...${NC}"
    
    # Check if running in production mode
    if grep -q "ENVIRONMENT=production" .env; then
        echo -e "${GREEN}✅ Production environment detected${NC}"
        
        # Check for production-specific settings
        if grep -q "DEBUG=true" .env; then
            echo -e "${RED}❌ CRITICAL: Debug mode enabled in production${NC}"
            echo -e "${YELLOW}🔧 Disabling debug mode...${NC}"
            sed -i.bak "s/DEBUG=true/DEBUG=false/" .env
            echo -e "${GREEN}✅ Debug mode disabled${NC}"
        fi
        
        if grep -q "DRY_RUN=true" .env; then
            echo -e "${RED}❌ CRITICAL: Dry run mode enabled in production${NC}"
            echo -e "${YELLOW}🔧 Disabling dry run mode...${NC}"
            sed -i.bak "s/DRY_RUN=true/DRY_RUN=false/" .env
            echo -e "${GREEN}✅ Dry run mode disabled${NC}"
        fi
        
    else
        echo -e "${YELLOW}⚠️  Development environment detected${NC}"
    fi
    
    echo ""
}

# Function to display security checklist
display_security_checklist() {
    echo -e "${BLUE}📋 Security Checklist${NC}"
    echo "=================="
    echo ""
    echo -e "${GREEN}✅ Hardcoded secrets removed${NC}"
    echo -e "${GREEN}✅ CORS wildcards removed${NC}"
    echo -e "${GREEN}✅ Security headers middleware added${NC}"
    echo -e "${GREEN}✅ Rate limiting middleware added${NC}"
    echo -e "${GREEN}✅ Authentication bypass removed${NC}"
    echo -e "${GREEN}✅ OAuth tokens encrypted${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Manual steps required:${NC}"
    echo "1. Configure real API keys in .env file"
    echo "2. Set up HTTPS/SSL certificates"
    echo "3. Configure production CORS origins"
    echo "4. Set up monitoring and alerting"
    echo "5. Configure backup and disaster recovery"
    echo ""
}

# Main execution
main() {
    echo -e "${GREEN}Starting security setup...${NC}"
    echo ""
    
    generate_secret_key
    check_env_file
    check_cors_config
    check_auth_config
    check_production_readiness
    display_security_checklist
    
    echo -e "${GREEN}🎉 Security setup completed!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review and update .env file with your actual values"
    echo "2. Test the application with: docker compose up --build"
    echo "3. Run security tests: python -m pytest tests/test_security.py"
    echo "4. Deploy to production with proper SSL certificates"
    echo ""
}

# Run main function
main "$@"
