#!/bin/bash

# VANTAGE AI Docker Deployment Script
# This script builds and pushes Docker images to Docker Hub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME=${DOCKER_USERNAME:-"vantage-ai"}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"docker.io"}
VERSION=${VERSION:-"latest"}

# Images to build
IMAGES=("api" "web" "worker")

echo -e "${BLUE}🚀 VANTAGE AI Docker Deployment${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if user is logged in to Docker Hub
if ! docker info | grep -q "Username:"; then
    echo -e "${YELLOW}⚠️  You're not logged in to Docker Hub.${NC}"
    echo "Please run: docker login"
    read -p "Press Enter to continue after logging in..."
fi

# Function to build and push image
build_and_push() {
    local service=$1
    local image_name="${DOCKER_USERNAME}/${service}"
    local full_image_name="${DOCKER_REGISTRY}/${image_name}:${VERSION}"
    
    echo -e "${BLUE}📦 Building ${service} image...${NC}"
    
    # Build the image
    docker build -f "infra/Dockerfile.${service}" -t "${image_name}:${VERSION}" .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully built ${service} image${NC}"
    else
        echo -e "${RED}❌ Failed to build ${service} image${NC}"
        exit 1
    fi
    
    # Tag for latest
    docker tag "${image_name}:${VERSION}" "${image_name}:latest"
    
    echo -e "${BLUE}📤 Pushing ${service} image to Docker Hub...${NC}"
    
    # Push the image
    docker push "${image_name}:${VERSION}"
    docker push "${image_name}:latest"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully pushed ${service} image${NC}"
        echo -e "   Image: ${full_image_name}"
    else
        echo -e "${RED}❌ Failed to push ${service} image${NC}"
        exit 1
    fi
}

# Build and push all images
for service in "${IMAGES[@]}"; do
    build_and_push "$service"
    echo ""
done

echo -e "${GREEN}🎉 All images successfully built and pushed!${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo "========================"
for service in "${IMAGES[@]}"; do
    echo -e "✅ ${DOCKER_USERNAME}/${service}:${VERSION}"
    echo -e "✅ ${DOCKER_USERNAME}/${service}:latest"
done

echo ""
echo -e "${BLUE}🚀 Quick Deploy Commands:${NC}"
echo "=========================="
echo ""
echo "# Pull and run with Docker Compose:"
echo "docker-compose -f docker-compose.prod.yml pull"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "# Or run individual containers:"
echo "docker run -d --name vantage-ai-api -p 8000:8000 ${DOCKER_USERNAME}/api:latest"
echo "docker run -d --name vantage-ai-web -p 3000:3000 ${DOCKER_USERNAME}/web:latest"
echo "docker run -d --name vantage-ai-worker ${DOCKER_USERNAME}/worker:latest"
echo ""
echo -e "${GREEN}🎯 Your VANTAGE AI platform is ready for deployment!${NC}"
