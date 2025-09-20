#!/bin/bash

# =============================================================================
# VANTAGE AI - Monitoring & Alerting Setup Script
# =============================================================================
# This script sets up comprehensive monitoring, alerting, and observability

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITORING_DIR="$PROJECT_DIR/monitoring"
GRAFANA_DIR="$PROJECT_DIR/grafana"

echo -e "${BLUE}📊 Setting up VANTAGE AI Monitoring & Alerting${NC}"
echo -e "${BLUE}=============================================${NC}"

# Function to create monitoring directory structure
create_directories() {
    echo -e "${YELLOW}📁 Creating monitoring directory structure...${NC}"
    
    mkdir -p "$MONITORING_DIR"/{rules,dashboards,alerts}
    mkdir -p "$GRAFANA_DIR"/{dashboards,datasources}
    
    echo -e "${GREEN}✅ Monitoring directories created${NC}"
}

# Function to create Prometheus rules
create_prometheus_rules() {
    echo -e "${YELLOW}📋 Creating Prometheus alerting rules...${NC}"
    
    # API Health Rules
    cat > "$MONITORING_DIR/rules/api-health.yml" << 'EOF'
groups:
- name: vantage-api-health
  rules:
  - alert: APIHealthCheckFailed
    expr: up{job="vantage-api"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "VANTAGE API is down"
      description: "API health check has been failing for more than 1 minute"

  - alert: APIHighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High API error rate"
      description: "API error rate is above 10% for more than 2 minutes"

  - alert: APIHighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High API response time"
      description: "95th percentile response time is above 2 seconds"

  - alert: APIMemoryUsage
    expr: container_memory_usage_bytes{name="vantage-api-prod"} / container_spec_memory_limit_bytes{name="vantage-api-prod"} > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High API memory usage"
      description: "API memory usage is above 80%"

  - alert: APICPUUsage
    expr: rate(container_cpu_usage_seconds_total{name="vantage-api-prod"}[5m]) > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High API CPU usage"
      description: "API CPU usage is above 80%"
EOF

    # Database Rules
    cat > "$MONITORING_DIR/rules/database.yml" << 'EOF'
groups:
- name: vantage-database
  rules:
  - alert: DatabaseDown
    expr: up{job="postgres"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "PostgreSQL database is down"
      description: "Database health check has been failing for more than 1 minute"

  - alert: DatabaseHighConnections
    expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database connection usage"
      description: "Database connections are above 80% of maximum"

  - alert: DatabaseSlowQueries
    expr: rate(pg_stat_database_tup_returned[5m]) / rate(pg_stat_database_tup_fetched[5m]) < 0.1
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Slow database queries detected"
      description: "Database query efficiency is below 10%"

  - alert: DatabaseDiskSpace
    expr: (pg_database_size_bytes / 1024 / 1024 / 1024) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Database disk space warning"
      description: "Database size is above 80GB"
EOF

    # Redis Rules
    cat > "$MONITORING_DIR/rules/redis.yml" << 'EOF'
groups:
- name: vantage-redis
  rules:
  - alert: RedisDown
    expr: up{job="redis"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Redis is down"
      description: "Redis health check has been failing for more than 1 minute"

  - alert: RedisHighMemoryUsage
    expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High Redis memory usage"
      description: "Redis memory usage is above 80%"

  - alert: RedisHighKeyCount
    expr: redis_db_keys > 1000000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High Redis key count"
      description: "Redis has more than 1 million keys"
EOF

    # Worker Rules
    cat > "$MONITORING_DIR/rules/workers.yml" << 'EOF'
groups:
- name: vantage-workers
  rules:
  - alert: WorkerDown
    expr: up{job="vantage-worker"} == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Celery worker is down"
      description: "Worker health check has been failing for more than 2 minutes"

  - alert: WorkerHighQueueLength
    expr: celery_queue_length > 1000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High worker queue length"
      description: "Worker queue has more than 1000 pending tasks"

  - alert: WorkerHighFailureRate
    expr: rate(celery_task_failures_total[5m]) / rate(celery_task_total[5m]) > 0.1
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High worker failure rate"
      description: "Worker failure rate is above 10%"
EOF

    echo -e "${GREEN}✅ Prometheus alerting rules created${NC}"
}

# Function to create Grafana dashboards
create_grafana_dashboards() {
    echo -e "${YELLOW}📊 Creating Grafana dashboards...${NC}"
    
    # API Performance Dashboard
    cat > "$GRAFANA_DIR/dashboards/api-performance.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "VANTAGE AI - API Performance",
    "tags": ["vantage", "api", "performance"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Response Time (s)"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %"
          }
        ],
        "yAxes": [
          {
            "label": "Error Rate %"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

    # System Overview Dashboard
    cat > "$GRAFANA_DIR/dashboards/system-overview.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "VANTAGE AI - System Overview",
    "tags": ["vantage", "system", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Service Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"vantage-api\"}",
            "legendFormat": "API"
          },
          {
            "expr": "up{job=\"vantage-web\"}",
            "legendFormat": "Web"
          },
          {
            "expr": "up{job=\"postgres\"}",
            "legendFormat": "Database"
          },
          {
            "expr": "up{job=\"redis\"}",
            "legendFormat": "Redis"
          }
        ]
      },
      {
        "id": 2,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m]) * 100",
            "legendFormat": "{{name}}"
          }
        ],
        "yAxes": [
          {
            "label": "CPU %"
          }
        ]
      },
      {
        "id": 3,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes / 1024 / 1024 / 1024",
            "legendFormat": "{{name}}"
          }
        ],
        "yAxes": [
          {
            "label": "Memory (GB)"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

    echo -e "${GREEN}✅ Grafana dashboards created${NC}"
}

# Function to create Slack integration
create_slack_integration() {
    echo -e "${YELLOW}💬 Creating Slack integration...${NC}"
    
    cat > "$MONITORING_DIR/slack-setup.md" << 'EOF'
# Slack Integration Setup

## 1. Create Slack App
1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name: "VANTAGE AI Alerts"
5. Select your workspace

## 2. Configure Webhook
1. Go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to On
3. Click "Add New Webhook to Workspace"
4. Select the channel for alerts
5. Copy the webhook URL

## 3. Update AlertManager
Replace `YOUR_SLACK_WEBHOOK_URL` in `monitoring/alertmanager.yml` with your webhook URL.

## 4. Test Integration
Run: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test alert from VANTAGE AI"}' YOUR_SLACK_WEBHOOK_URL`
EOF

    echo -e "${GREEN}✅ Slack integration guide created${NC}"
}

# Function to create monitoring startup script
create_monitoring_script() {
    echo -e "${YELLOW}🚀 Creating monitoring startup script...${NC}"
    
    cat > "$PROJECT_DIR/start-monitoring.sh" << 'EOF'
#!/bin/bash

# =============================================================================
# VANTAGE AI - Monitoring Startup Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 Starting VANTAGE AI Monitoring Stack${NC}"
echo -e "${BLUE}======================================${NC}"

# Check if main services are running
if ! docker compose ps | grep -q "vantage-api-prod"; then
    echo -e "${RED}❌ Main VANTAGE AI services not running!${NC}"
    echo -e "${YELLOW}Please start main services first: ./start-production.sh${NC}"
    exit 1
fi

# Start monitoring services
echo -e "${YELLOW}🐳 Starting monitoring services...${NC}"
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for monitoring services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${YELLOW}🔍 Checking monitoring service health...${NC}"

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus is healthy${NC}"
else
    echo -e "${RED}❌ Prometheus health check failed${NC}"
fi

# Check Grafana
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana is healthy${NC}"
else
    echo -e "${RED}❌ Grafana health check failed${NC}"
fi

# Check Jaeger
if curl -f http://localhost:16686 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Jaeger is healthy${NC}"
else
    echo -e "${RED}❌ Jaeger health check failed${NC}"
fi

echo -e "${GREEN}🎉 VANTAGE AI Monitoring Stack Started!${NC}"
echo -e "${BLUE}Prometheus: http://localhost:9090${NC}"
echo -e "${BLUE}Grafana: http://localhost:3001 (admin/admin123)${NC}"
echo -e "${BLUE}Jaeger: http://localhost:16686${NC}"
echo -e "${BLUE}AlertManager: http://localhost:9093${NC}"
EOF
    
    chmod +x "$PROJECT_DIR/start-monitoring.sh"
    echo -e "${GREEN}✅ Monitoring startup script created${NC}"
}

# Function to create health check script
create_health_check_script() {
    echo -e "${YELLOW}🏥 Creating health check script...${NC}"
    
    cat > "$PROJECT_DIR/scripts/health-check.sh" << 'EOF'
#!/bin/bash

# =============================================================================
# VANTAGE AI - Health Check Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏥 VANTAGE AI Health Check${NC}"
echo -e "${BLUE}=========================${NC}"

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ $name: Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Unhealthy${NC}"
        return 1
    fi
}

# Check main services
echo -e "${YELLOW}🔍 Checking main services...${NC}"
check_service "API" "http://localhost/api/v1/health"
check_service "Web" "http://localhost/healthz"

# Check monitoring services
echo -e "${YELLOW}📊 Checking monitoring services...${NC}"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3001/api/health"
check_service "Jaeger" "http://localhost:16686"

# Check database
echo -e "${YELLOW}🗄️ Checking database...${NC}"
if docker exec vantage-db-prod pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database: Healthy${NC}"
else
    echo -e "${RED}❌ Database: Unhealthy${NC}"
fi

# Check Redis
echo -e "${YELLOW}🔴 Checking Redis...${NC}"
if docker exec vantage-redis-prod redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis: Healthy${NC}"
else
    echo -e "${RED}❌ Redis: Unhealthy${NC}"
fi

echo -e "${BLUE}🏥 Health check completed${NC}"
EOF
    
    chmod +x "$PROJECT_DIR/scripts/health-check.sh"
    echo -e "${GREEN}✅ Health check script created${NC}"
}

# Main setup function
main() {
    echo -e "${BLUE}📊 VANTAGE AI Monitoring Setup${NC}"
    echo -e "${BLUE}==============================${NC}"
    echo ""
    
    # Create directory structure
    create_directories
    
    # Create Prometheus rules
    create_prometheus_rules
    
    # Create Grafana dashboards
    create_grafana_dashboards
    
    # Create Slack integration
    create_slack_integration
    
    # Create monitoring startup script
    create_monitoring_script
    
    # Create health check script
    create_health_check_script
    
    echo -e "${GREEN}🎉 Monitoring setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo -e "${BLUE}1. Configure Slack webhook URL in monitoring/alertmanager.yml${NC}"
    echo -e "${BLUE}2. Run: ./start-monitoring.sh${NC}"
    echo -e "${BLUE}3. Access Grafana at http://localhost:3001${NC}"
    echo -e "${BLUE}4. Set up custom dashboards and alerts${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Default Grafana credentials: admin/admin123${NC}"
    echo -e "${YELLOW}⚠️  Remember to change default passwords in production${NC}"
}

# Run main function
main "$@"
