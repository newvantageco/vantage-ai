#!/bin/bash

# E2E Test Runner Script
# Usage: ./scripts/run-e2e.sh [options]
# Options:
#   --mocks    Enable mock mode (default: true)
#   --headed   Run tests in headed mode
#   --debug    Run tests in debug mode
#   --ui       Run tests with UI mode

set -e

# Default values
MOCKS=true
HEADED=false
DEBUG=false
UI=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --mocks)
      MOCKS=true
      shift
      ;;
    --no-mocks)
      MOCKS=false
      shift
      ;;
    --headed)
      HEADED=true
      shift
      ;;
    --debug)
      DEBUG=true
      shift
      ;;
    --ui)
      UI=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --mocks      Enable mock mode (default: true)"
      echo "  --no-mocks   Disable mock mode"
      echo "  --headed     Run tests in headed mode"
      echo "  --debug      Run tests in debug mode"
      echo "  --ui         Run tests with UI mode"
      echo "  --help       Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo "🚀 Starting E2E test run..."
echo "📡 Mock mode: $MOCKS"
echo "🖥️  Headed mode: $HEADED"
echo "🐛 Debug mode: $DEBUG"
echo "🎨 UI mode: $UI"

# Check if we're in the right directory
if [ ! -f "web/package.json" ]; then
  echo "❌ Error: Please run this script from the project root directory"
  exit 1
fi

# Set environment variables
export E2E_MOCKS=$MOCKS
export BASE_URL=http://localhost:3000
export API_BASE=http://localhost:8000/api/v1

# Check if services are running
echo "🔍 Checking if services are running..."

# Check API server
if ! curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
  echo "❌ API server is not running. Please start it with:"
  echo "   uvicorn app.main:app --reload --port 8000"
  exit 1
fi

# Check web server
if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
  echo "❌ Web server is not running. Please start it with:"
  echo "   cd web && npm run dev"
  exit 1
fi

echo "✅ Services are running"

# Install Playwright browsers if not already installed
echo "📦 Installing Playwright browsers..."
cd web
npx playwright install --with-deps

# Build the test command
TEST_CMD="npx playwright test"

if [ "$UI" = true ]; then
  TEST_CMD="npx playwright test --ui"
elif [ "$DEBUG" = true ]; then
  TEST_CMD="npx playwright test --debug"
elif [ "$HEADED" = true ]; then
  TEST_CMD="npx playwright test --headed"
fi

# Run the tests
echo "🧪 Running E2E tests..."
echo "Command: $TEST_CMD"

if eval $TEST_CMD; then
  echo "✅ E2E tests passed!"
  exit 0
else
  echo "❌ E2E tests failed!"
  echo "📊 Check the test results in web/playwright-report/"
  echo "🔍 Check traces in web/test-results/ for debugging"
  exit 1
fi
