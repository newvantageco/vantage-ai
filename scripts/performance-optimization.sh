#!/bin/bash

# VANTAGE AI - Performance Optimization Script
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PERFORMANCE_DIR="$PROJECT_DIR/performance"

echo "⚡ VANTAGE AI Performance Optimization"

# Create performance directory
mkdir -p "$PERFORMANCE_DIR"/{reports,scripts,configs}

# Create Locust load testing configuration
cat > "$PERFORMANCE_DIR/locustfile.py" << 'EOF'
from locust import HttpUser, task, between
import random

class VantageAIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/v1/dashboard")
    
    @task(2)
    def list_content(self):
        self.client.get("/api/v1/cms/content")
    
    @task(1)
    def create_content(self):
        content_data = {
            "title": f"Test Content {random.randint(1, 1000)}",
            "content": "This is a test content for performance testing",
            "platform": random.choice(["facebook", "twitter", "linkedin"])
        }
        self.client.post("/api/v1/cms/content", json=content_data)
EOF

# Create performance monitoring script
cat > "$PERFORMANCE_DIR/scripts/monitor-performance.sh" << 'EOF'
#!/bin/bash
echo "📊 VANTAGE AI Performance Monitoring"

# Get container stats
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" vantage-api-prod vantage-web-prod vantage-db-prod vantage-redis-prod

# Test API response times
echo "🔍 Testing API response times..."
time curl -s -o /dev/null -w "Health: %{time_total}s\n" http://localhost:8000/api/v1/health
time curl -s -o /dev/null -w "Dashboard: %{time_total}s\n" http://localhost:8000/api/v1/dashboard
EOF

chmod +x "$PERFORMANCE_DIR/scripts/monitor-performance.sh"

echo "✅ Performance optimization setup completed!"
echo "Run: ./performance/scripts/monitor-performance.sh"
