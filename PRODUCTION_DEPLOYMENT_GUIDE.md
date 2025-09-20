# 🚀 VANTAGE AI - Production Deployment Guide

## Overview

This guide will walk you through deploying VANTAGE AI to production with enterprise-grade security, monitoring, and reliability.

## Prerequisites

- Docker and Docker Compose installed
- Domain name configured
- SSL certificates (Let's Encrypt or custom)
- Production API keys for all integrations

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd vantage-ai

# Run the production setup script
./scripts/setup-production.sh
```

This will:
- ✅ Create production environment configuration
- ✅ Set up SSL certificates
- ✅ Configure monitoring and alerting
- ✅ Create startup and backup scripts

### 2. Configure API Keys

Edit `.env.production` and update all placeholder values:

```bash
# Required API Keys
CLERK_SECRET_KEY=sk_live_your_actual_key
STRIPE_SECRET_KEY=sk_live_your_actual_key
OPENAI_API_KEY=sk-your_actual_key

# Optional Integrations
META_APP_ID=your_meta_app_id
LINKEDIN_CLIENT_ID=your_linkedin_client_id
# ... etc
```

### 3. Deploy to Production

```bash
# Start the production environment
./start-production.sh

# Start monitoring (optional)
./start-monitoring.sh
```

## Detailed Setup

### SSL Certificate Setup

#### Option 1: Let's Encrypt (Recommended)

```bash
# Run the SSL setup script
./scripts/setup-ssl.sh your-domain.com api.your-domain.com admin@your-domain.com

# Choose option 1 for Let's Encrypt
```

#### Option 2: Custom Certificates

```bash
# Place your certificates in infra/ssl/
# - cert.pem (main certificate)
# - key.pem (private key)
# - api-cert.pem (API certificate)

# Run the SSL setup script
./scripts/setup-ssl.sh your-domain.com api.your-domain.com admin@your-domain.com

# Choose option 3 for custom certificates
```

### Environment Configuration

#### Production Environment Variables

Key variables to configure in `.env.production`:

```bash
# Database
POSTGRES_USER=vantage_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=vantage

# Security
SECRET_KEY=your_32_character_secret_key
CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com

# API Configuration
NEXT_PUBLIC_API_URL=https://api.your-domain.com

# AI Services
OPENAI_API_KEY=sk-your_openai_key
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key

# Payment Processing
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key

# Authentication
CLERK_SECRET_KEY=sk_live_your_clerk_key
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_your_clerk_key
```

### Monitoring Setup

#### 1. Start Monitoring Stack

```bash
# Start monitoring services
./start-monitoring.sh
```

#### 2. Configure Slack Alerts

1. Create a Slack app at https://api.slack.com/apps
2. Set up incoming webhooks
3. Update `monitoring/alertmanager.yml` with your webhook URL

#### 3. Access Monitoring Dashboards

- **Grafana**: http://your-domain.com:3001 (admin/admin123)
- **Prometheus**: http://your-domain.com:9090
- **Jaeger**: http://your-domain.com:16686

### Database Setup

#### 1. Run Migrations

```bash
# Run database migrations
docker compose -f docker-compose.production.yml exec api alembic upgrade head
```

#### 2. Create Initial Admin User

```bash
# Create admin user (if needed)
docker compose -f docker-compose.production.yml exec api python -c "
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_password_hash

db = next(get_db())
admin_user = User(
    email='admin@your-domain.com',
    hashed_password=get_password_hash('admin_password'),
    is_active=True,
    is_superuser=True
)
db.add(admin_user)
db.commit()
"
```

## Security Configuration

### 1. SSL/TLS Setup

- ✅ SSL certificates configured
- ✅ HTTPS redirect enabled
- ✅ HSTS headers configured
- ✅ Security headers enabled

### 2. Authentication

- ✅ Clerk integration configured
- ✅ JWT token validation
- ✅ Role-based access control

### 3. Rate Limiting

- ✅ API rate limiting (10 req/s)
- ✅ Web rate limiting (30 req/s)
- ✅ Redis-backed rate limiting

### 4. Security Headers

- ✅ X-Frame-Options
- ✅ X-Content-Type-Options
- ✅ X-XSS-Protection
- ✅ Strict-Transport-Security
- ✅ Content-Security-Policy

## Monitoring & Alerting

### 1. Health Checks

```bash
# Check all services
./scripts/health-check.sh

# Individual service checks
curl https://your-domain.com/healthz
curl https://api.your-domain.com/api/v1/health
```

### 2. Metrics Collection

- **Prometheus**: Collects metrics from all services
- **Grafana**: Visualizes metrics and creates dashboards
- **Jaeger**: Distributed tracing for request flows

### 3. Alerting Rules

Pre-configured alerts for:
- Service downtime
- High error rates
- High response times
- Resource usage (CPU, memory, disk)
- Database performance issues

### 4. Log Management

- Structured logging with correlation IDs
- Centralized log collection
- Error tracking and alerting

## Backup & Recovery

### 1. Automated Backups

```bash
# Run backup script
./scripts/backup-production.sh

# Set up cron job for daily backups
0 2 * * * /path/to/vantage-ai/scripts/backup-production.sh
```

### 2. Database Backups

- Daily automated backups
- Point-in-time recovery support
- Backup verification

### 3. Disaster Recovery

- Multi-region deployment capability
- Automated failover procedures
- Data replication strategies

## Performance Optimization

### 1. Database Optimization

- Connection pooling configured
- Query optimization
- Index optimization
- Read replica support

### 2. Caching Strategy

- Redis caching for sessions
- Application-level caching
- CDN integration ready

### 3. Load Balancing

- Nginx reverse proxy
- Health check endpoints
- Graceful shutdown support

## Scaling

### 1. Horizontal Scaling

```bash
# Scale API workers
docker compose -f docker-compose.production.yml up -d --scale worker=3

# Scale web instances
docker compose -f docker-compose.production.yml up -d --scale web=2
```

### 2. Database Scaling

- Read replicas for read-heavy workloads
- Connection pooling optimization
- Query performance monitoring

### 3. Monitoring Scaling

- Prometheus federation for multi-instance monitoring
- Grafana dashboard sharing
- Centralized log aggregation

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check service status
docker compose -f docker-compose.production.yml ps

# Check logs
docker compose -f docker-compose.production.yml logs [service-name]

# Restart services
docker compose -f docker-compose.production.yml restart
```

#### 2. SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in infra/ssl/cert.pem -text -noout

# Renew Let's Encrypt certificates
sudo certbot renew
docker compose -f docker-compose.production.yml restart nginx
```

#### 3. Database Connection Issues

```bash
# Check database connectivity
docker compose -f docker-compose.production.yml exec api python -c "
from app.db.session import get_db
db = next(get_db())
print('Database connected successfully')
"

# Check database logs
docker compose -f docker-compose.production.yml logs db
```

#### 4. Performance Issues

```bash
# Check resource usage
docker stats

# Check Prometheus metrics
curl http://localhost:9090/api/v1/query?query=up

# Check Grafana dashboards
# Access http://your-domain.com:3001
```

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
docker compose -f docker-compose.production.yml up
```

## Maintenance

### 1. Regular Updates

```bash
# Update application
git pull origin main
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d

# Update dependencies
docker compose -f docker-compose.production.yml exec api pip install --upgrade -r requirements.txt
```

### 2. Security Updates

- Regular security patches
- Dependency updates
- SSL certificate renewal

### 3. Performance Monitoring

- Regular performance reviews
- Capacity planning
- Optimization recommendations

## Support

### 1. Health Monitoring

- Automated health checks
- Alert notifications
- Performance metrics

### 2. Log Analysis

- Centralized logging
- Error tracking
- Performance analysis

### 3. Backup Verification

- Regular backup testing
- Recovery procedure validation
- Data integrity checks

## Cost Optimization

### 1. Resource Right-sizing

- Monitor resource usage
- Adjust container limits
- Optimize database configuration

### 2. Caching Strategy

- Implement effective caching
- Reduce database load
- Optimize API responses

### 3. Monitoring Costs

- Track resource usage
- Optimize monitoring frequency
- Use cost-effective storage

---

## Quick Reference

### Essential Commands

```bash
# Start production
./start-production.sh

# Start monitoring
./start-monitoring.sh

# Health check
./scripts/health-check.sh

# Backup
./scripts/backup-production.sh

# View logs
docker compose -f docker-compose.production.yml logs -f

# Restart services
docker compose -f docker-compose.production.yml restart
```

### Important URLs

- **Application**: https://your-domain.com
- **API**: https://api.your-domain.com
- **API Docs**: https://api.your-domain.com/docs
- **Grafana**: http://your-domain.com:3001
- **Prometheus**: http://your-domain.com:9090
- **Jaeger**: http://your-domain.com:16686

### Configuration Files

- **Environment**: `.env.production`
- **Docker Compose**: `docker-compose.production.yml`
- **Nginx**: `infra/nginx-ssl.conf`
- **Monitoring**: `docker-compose.monitoring.yml`
- **Prometheus**: `monitoring/prometheus.yml`
- **AlertManager**: `monitoring/alertmanager.yml`

---

**🎉 Congratulations! Your VANTAGE AI platform is now production-ready!**

For additional support or questions, please refer to the troubleshooting section or check the monitoring dashboards for system status.
