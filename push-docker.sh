#!/bin/bash

# =============================================================================
# VANTAGE AI - Docker Registry Push Script
# =============================================================================

set -e  # Exit on any error

echo "📦 Pushing VANTAGE AI Docker Images to Registry..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
REGISTRY_URL=${REGISTRY_URL:-"your-registry.com"}
PROJECT_NAME=${PROJECT_NAME:-"vantage-ai"}
VERSION=${VERSION:-"latest"}

# Images to push
IMAGES=(
    "vantage-ai/api:latest"
    "vantage-ai/web:latest"
    "vantage-ai/worker:latest"
)

print_status "Registry URL: $REGISTRY_URL"
print_status "Project Name: $PROJECT_NAME"
print_status "Version: $VERSION"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build images first
print_status "Building images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Tag and push each image
for image in "${IMAGES[@]}"; do
    # Extract image name without tag
    image_name=$(echo $image | cut -d':' -f1)
    
    # Create registry tag
    registry_tag="$REGISTRY_URL/$PROJECT_NAME/$image_name:$VERSION"
    
    print_status "Tagging $image as $registry_tag"
    docker tag $image $registry_tag
    
    print_status "Pushing $registry_tag"
    docker push $registry_tag
    
    print_success "✅ Pushed $registry_tag"
done

print_success "🎉 All images pushed successfully!"
echo ""
print_status "Images pushed:"
for image in "${IMAGES[@]}"; do
    image_name=$(echo $image | cut -d':' -f1)
    registry_tag="$REGISTRY_URL/$PROJECT_NAME/$image_name:$VERSION"
    print_status "  📦 $registry_tag"
done
echo ""
print_status "To pull these images on another server:"
for image in "${IMAGES[@]}"; do
    image_name=$(echo $image | cut -d':' -f1)
    registry_tag="$REGISTRY_URL/$PROJECT_NAME/$image_name:$VERSION"
    print_status "  docker pull $registry_tag"
done
