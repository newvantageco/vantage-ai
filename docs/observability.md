# Observability and Monitoring

This document describes the observability and monitoring setup for the VANTAGE AI platform.

## Overview

The platform uses OpenTelemetry for metrics collection and Grafana for visualization. We track key metrics across API, workers, and web components.

## Metrics Collection

### API Metrics

- **Request Count**: Total number of API requests
- **Request Duration**: API response times (histogram)
- **Error Rate**: Percentage of failed requests
- **Active Connections**: Number of concurrent connections

### Worker Metrics

- **Job Count**: Total number of jobs processed
- **Job Duration**: Time taken to process jobs
- **Queue Depth**: Number of pending jobs
- **Worker Heartbeat**: Last seen timestamp for each worker

### Scheduler Metrics

- **Scheduled Jobs**: Number of jobs scheduled
- **Execution Lag**: Delay between scheduled and actual execution
- **Success Rate**: Percentage of successfully executed jobs

### Database Metrics

- **Connection Pool**: Active database connections
- **Query Duration**: Database query execution times
- **Transaction Count**: Number of database transactions

## Grafana Dashboards

### 1. API Performance Dashboard

**Location**: `/grafana/dashboards/api-performance`

**Panels**:
- Request rate (requests/second)
- Response time percentiles (p50, p90, p95, p99)
- Error rate percentage
- Active connections
- Memory usage
- CPU usage

**Alerts**:
- High error rate (>5%)
- High response time (p95 > 2s)
- High memory usage (>80%)

### 2. Worker Health Dashboard

**Location**: `/grafana/dashboards/worker-health`

**Panels**:
- Job processing rate
- Queue depth over time
- Worker heartbeat status
- Job success/failure rate
- Worker memory usage

**Alerts**:
- Worker offline (no heartbeat for 5 minutes)
- High queue depth (>1000 jobs)
- High job failure rate (>10%)

### 3. Scheduler Performance Dashboard

**Location**: `/grafana/dashboards/scheduler-performance`

**Panels**:
- Scheduled jobs count
- Execution lag distribution
- Success rate over time
- Failed job reasons
- Scheduler memory usage

**Alerts**:
- High execution lag (>5 minutes)
- Low success rate (<90%)
- Scheduler offline

### 4. Database Performance Dashboard

**Location**: `/grafana/dashboards/database-performance`

**Panels**:
- Connection pool utilization
- Query duration percentiles
- Transaction rate
- Database size growth
- Index usage statistics

**Alerts**:
- High connection pool usage (>80%)
- Slow queries (>1s)
- Database size growth rate

### 5. Business Metrics Dashboard

**Location**: `/grafana/dashboards/business-metrics`

**Panels**:
- Active organizations
- Posts published per day
- AI generations per day
- Revenue metrics
- User engagement

**Alerts**:
- Unusual drop in posts
- High AI usage spike
- Revenue anomaly

## SLO Configuration

### API SLOs

```json
{
  "api": {
    "availability": {
      "target": 99.9,
      "window": "30d",
      "description": "API availability over 30 days"
    },
    "latency": {
      "target": 95,
      "threshold": 2000,
      "window": "30d",
      "description": "95% of requests under 2s over 30 days"
    },
    "error_rate": {
      "target": 99.5,
      "threshold": 0.5,
      "window": "30d",
      "description": "Error rate under 0.5% over 30 days"
    }
  }
}
```

### Worker SLOs

```json
{
  "workers": {
    "availability": {
      "target": 99.5,
      "window": "30d",
      "description": "Worker availability over 30 days"
    },
    "processing_time": {
      "target": 95,
      "threshold": 300,
      "window": "30d",
      "description": "95% of jobs processed under 5 minutes"
    },
    "queue_lag": {
      "target": 99,
      "threshold": 300,
      "window": "30d",
      "description": "99% of jobs processed within 5 minutes of schedule"
    }
  }
}
```

## Error Budget Tracking

Error budgets are calculated as:
- **Budget = (100 - SLO Target) / 100 * Time Window**
- **Burn Rate = Current Error Rate / SLO Threshold**

### Burn Rate Alerts

- **Warning**: Burn rate > 2x (50% of budget consumed in half the time)
- **Critical**: Burn rate > 10x (90% of budget consumed in 10% of the time)

## Health Endpoints

### API Health

- **GET /api/v1/health**: Basic health check
- **GET /api/v1/health/detailed**: Detailed health with dependencies
- **GET /api/v1/health/ready**: Readiness probe for Kubernetes

### Worker Health

- **GET /api/v1/workers/health**: Worker status and metrics
- **GET /api/v1/workers/{worker_id}/heartbeat**: Individual worker heartbeat

### Web Health

- **GET /status**: Public status page
- **GET /status/incidents**: Current incidents
- **GET /status/history**: Incident history

## Monitoring Setup

### 1. OpenTelemetry Configuration

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:14250")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
```

### 2. Metrics Configuration

```python
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider

# Configure metrics
metric_reader = PrometheusMetricReader()
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
```

### 3. Grafana Data Sources

- **Prometheus**: For metrics storage and querying
- **Jaeger**: For distributed tracing
- **Loki**: For log aggregation
- **PostgreSQL**: For business metrics

## Alerting Rules

### Critical Alerts

- API down (5xx errors > 10%)
- Database connection failure
- Worker offline for > 5 minutes
- High memory usage (>90%)
- Disk space low (<10%)

### Warning Alerts

- High error rate (>2%)
- Slow response times (p95 > 1s)
- Queue depth high (>500 jobs)
- CPU usage high (>80%)
- Memory usage high (>80%)

## Runbooks

### Incident Response

1. **Detection**: Monitor alerts and dashboards
2. **Assessment**: Check error budgets and impact
3. **Response**: Follow runbook procedures
4. **Resolution**: Fix root cause
5. **Post-mortem**: Document lessons learned

### Common Issues

- **High Error Rate**: Check logs, database connections, external APIs
- **Slow Performance**: Check database queries, memory usage, CPU
- **Worker Issues**: Check queue depth, worker logs, resource usage
- **Database Issues**: Check connection pool, query performance, disk space

## Dashboard Links

- [API Performance Dashboard](http://grafana:3000/d/api-performance)
- [Worker Health Dashboard](http://grafana:3000/d/worker-health)
- [Scheduler Performance Dashboard](http://grafana:3000/d/scheduler-performance)
- [Database Performance Dashboard](http://grafana:3000/d/database-performance)
- [Business Metrics Dashboard](http://grafana:3000/d/business-metrics)

## Maintenance

### Daily

- Check error budgets
- Review alert history
- Monitor key metrics

### Weekly

- Review SLO performance
- Analyze trends
- Update dashboards

### Monthly

- Review and update SLOs
- Analyze error budget consumption
- Plan capacity improvements
