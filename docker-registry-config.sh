#!/bin/bash

# =============================================================================
# VANTAGE AI - Docker Registry Configuration
# =============================================================================

# Configuration for Docker registry
REGISTRY_URL="docker.io"
REGISTRY_USERNAME="sabanali"
PROJECT_NAME="vantage-ai"
VERSION="latest"

# Set these environment variables or modify the values above
export REGISTRY_URL=${REGISTRY_URL:-"docker.io"}
export REGISTRY_USERNAME=${REGISTRY_USERNAME:-"sabanali"}
export PROJECT_NAME=${PROJECT_NAME:-"vantage-ai"}
export VERSION=${VERSION:-"latest"}

echo "🐳 Docker Registry Configuration:"
echo "  Registry: $REGISTRY_URL"
echo "  Username: $REGISTRY_USERNAME"
echo "  Project: $PROJECT_NAME"
echo "  Version: $VERSION"
echo ""

# Login to Docker registry (uncomment and modify as needed)
# echo "Logging into Docker registry..."
# docker login $REGISTRY_URL

echo "Ready to push images to: $REGISTRY_USERNAME/$PROJECT_NAME"
