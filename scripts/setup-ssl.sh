#!/bin/bash

# =============================================================================
# VANTAGE AI - SSL Certificate Setup Script
# =============================================================================
# This script sets up SSL certificates for production deployment
# Supports both Let's Encrypt (free) and custom certificates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${1:-"vantage-ai.com"}
API_DOMAIN=${2:-"api.vantage-ai.com"}
EMAIL=${3:-"admin@vantage-ai.com"}
SSL_DIR="./infra/ssl"
NGINX_CONF="./infra/nginx-ssl.conf"

echo -e "${BLUE}🔒 Setting up SSL certificates for VANTAGE AI${NC}"
echo -e "${BLUE}Domain: ${DOMAIN}${NC}"
echo -e "${BLUE}API Domain: ${API_DOMAIN}${NC}"
echo -e "${BLUE}Email: ${EMAIL}${NC}"

# Create SSL directory
mkdir -p "$SSL_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup Let's Encrypt certificates
setup_letsencrypt() {
    echo -e "${YELLOW}📋 Setting up Let's Encrypt certificates...${NC}"
    
    if ! command_exists certbot; then
        echo -e "${RED}❌ Certbot not found. Installing...${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command_exists brew; then
                brew install certbot
            else
                echo -e "${RED}❌ Homebrew not found. Please install certbot manually.${NC}"
                exit 1
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            sudo apt-get update
            sudo apt-get install -y certbot
        else
            echo -e "${RED}❌ Unsupported OS. Please install certbot manually.${NC}"
            exit 1
        fi
    fi
    
    # Generate certificates
    echo -e "${YELLOW}🔐 Generating SSL certificates...${NC}"
    sudo certbot certonly --standalone \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        -d "$API_DOMAIN"
    
    # Copy certificates to project directory
    echo -e "${YELLOW}📁 Copying certificates to project directory...${NC}"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/api-cert.pem"
    
    # Set proper permissions
    sudo chown $(whoami):$(whoami) "$SSL_DIR"/*
    chmod 600 "$SSL_DIR"/*
    
    echo -e "${GREEN}✅ Let's Encrypt certificates installed successfully!${NC}"
}

# Function to setup self-signed certificates (for development)
setup_self_signed() {
    echo -e "${YELLOW}📋 Setting up self-signed certificates for development...${NC}"
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/key.pem" 2048
    
    # Generate certificate signing request
    openssl req -new -key "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.csr" -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in "$SSL_DIR/cert.csr" -signkey "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.pem"
    
    # Copy for API domain
    cp "$SSL_DIR/cert.pem" "$SSL_DIR/api-cert.pem"
    
    # Clean up CSR
    rm "$SSL_DIR/cert.csr"
    
    echo -e "${GREEN}✅ Self-signed certificates generated successfully!${NC}"
    echo -e "${YELLOW}⚠️  Note: Self-signed certificates will show security warnings in browsers${NC}"
}

# Function to setup custom certificates
setup_custom() {
    echo -e "${YELLOW}📋 Setting up custom certificates...${NC}"
    echo -e "${BLUE}Please place your certificates in the following locations:${NC}"
    echo -e "${BLUE}  - Certificate: $SSL_DIR/cert.pem${NC}"
    echo -e "${BLUE}  - Private Key: $SSL_DIR/key.pem${NC}"
    echo -e "${BLUE}  - API Certificate: $SSL_DIR/api-cert.pem${NC}"
    
    read -p "Press Enter when certificates are in place..."
    
    if [[ ! -f "$SSL_DIR/cert.pem" || ! -f "$SSL_DIR/key.pem" ]]; then
        echo -e "${RED}❌ Certificate files not found!${NC}"
        exit 1
    fi
    
    # Copy for API domain if not exists
    if [[ ! -f "$SSL_DIR/api-cert.pem" ]]; then
        cp "$SSL_DIR/cert.pem" "$SSL_DIR/api-cert.pem"
    fi
    
    echo -e "${GREEN}✅ Custom certificates configured successfully!${NC}"
}

# Main setup function
main() {
    echo -e "${BLUE}🔒 VANTAGE AI SSL Setup${NC}"
    echo -e "${BLUE}========================${NC}"
    echo ""
    echo "Choose SSL certificate type:"
    echo "1) Let's Encrypt (free, production-ready)"
    echo "2) Self-signed (development only)"
    echo "3) Custom certificates"
    echo ""
    
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            setup_letsencrypt
            ;;
        2)
            setup_self_signed
            ;;
        3)
            setup_custom
            ;;
        *)
            echo -e "${RED}❌ Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
    
    # Update nginx configuration
    echo -e "${YELLOW}🔧 Updating nginx configuration...${NC}"
    if [[ -f "$NGINX_CONF" ]]; then
        echo -e "${GREEN}✅ Nginx SSL configuration is ready at $NGINX_CONF${NC}"
    else
        echo -e "${RED}❌ Nginx SSL configuration not found!${NC}"
        exit 1
    fi
    
    # Create docker-compose override for SSL
    echo -e "${YELLOW}🐳 Creating Docker Compose SSL override...${NC}"
    cat > docker-compose.ssl.yml << EOF
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: vantage-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infra/nginx-ssl.conf:/etc/nginx/nginx.conf:ro
      - ./infra/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
      - web
    networks:
      - vantage-network
    restart: unless-stopped

networks:
  vantage-network:
    external: true
EOF
    
    echo -e "${GREEN}✅ SSL setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}🚀 Next steps:${NC}"
    echo -e "${BLUE}1. Update your domain DNS to point to this server${NC}"
    echo -e "${BLUE}2. Run: docker compose -f docker-compose.yml -f docker-compose.ssl.yml up -d${NC}"
    echo -e "${BLUE}3. Test SSL: https://$DOMAIN${NC}"
    echo -e "${BLUE}4. Test API: https://$API_DOMAIN/health${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  For Let's Encrypt: Set up auto-renewal with cron:${NC}"
    echo -e "${YELLOW}   0 12 * * * /usr/bin/certbot renew --quiet && docker compose restart nginx${NC}"
}

# Run main function
main "$@"