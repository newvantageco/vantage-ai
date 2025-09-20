# VANTAGE AI Deployment Guide

This guide covers the complete deployment process for VANTAGE AI, including SSL setup, database encryption, performance optimization, and CI/CD pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [SSL/HTTPS Setup](#sslhttps-setup)
3. [Database Encryption](#database-encryption)
4. [Performance Optimization](#performance-optimization)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Deployment Options](#deployment-options)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### System Requirements

- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended for production)
- **Storage**: 100GB+ SSD
- **OS**: Ubuntu 20.04+ or CentOS 8+

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl
- openssl

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=vantage
POSTGRES_PORT=5432

# Security
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Authentication
CLERK_SECRET_KEY=your_clerk_secret_key
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key

# Payment
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Environment
ENVIRONMENT=production
DEBUG=false
```

## SSL/HTTPS Setup

### 1. Automated SSL Setup

Run the SSL setup script:

```bash
# For development (self-signed certificates)
ENVIRONMENT=development ./scripts/setup-ssl.sh

# For production (Let's Encrypt certificates)
ENVIRONMENT=production DOMAIN=vantage-ai.com EMAIL=admin@vantage-ai.com ./scripts/setup-ssl.sh
```

### 2. Manual SSL Setup

#### Development (Self-signed certificates)

```bash
# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Generate private key
sudo openssl genrsa -out /etc/nginx/ssl/key.pem 2048

# Generate certificate
sudo openssl req -new -x509 -key /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/cert.pem -days 365

# Set permissions
sudo chmod 600 /etc/nginx/ssl/key.pem
sudo chmod 644 /etc/nginx/ssl/cert.pem
```

#### Production (Let's Encrypt)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificates
sudo certbot certonly --standalone -d vantage-ai.com -d www.vantage-ai.com -d api.vantage-ai.com

# Set up auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'" | sudo crontab -
```

### 3. Deploy with SSL

```bash
# Use SSL-enabled docker-compose
docker-compose -f docker-compose.ssl.yml up -d
```

## Database Encryption

### 1. Setup Database Encryption

```bash
# Run the database encryption setup script
./scripts/setup-db-encryption.sh
```

### 2. Use Encrypted Database

```bash
# Deploy with encrypted database
docker-compose -f docker-compose.encrypted.yml up -d
```

### 3. Verify Encryption

```bash
# Check encrypted tables
docker-compose exec api python -c "
from app.utils.encryption import get_encryption
enc = get_encryption()
print('Encryption test:', enc.encrypt('test data'))
"
```

## Performance Optimization

### 1. Run Performance Optimization

```bash
# Apply all performance optimizations
./scripts/performance-optimization.sh
```

### 2. Deploy Optimized Configuration

```bash
# Deploy with performance optimizations
docker-compose -f docker-compose.production.yml up -d

# Start monitoring stack
docker-compose -f infra/docker-compose.monitoring.yml up -d
```

### 3. Monitor Performance

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Node Exporter**: http://localhost:9100
- **cAdvisor**: http://localhost:8080

## CI/CD Pipeline

### 1. GitHub Actions Setup

The CI/CD pipeline is configured in `.github/workflows/ci-cd.yml` and includes:

- Code quality checks
- Security scanning
- Automated testing
- Docker image building
- Deployment to staging/production

### 2. Required Secrets

Add the following secrets to your GitHub repository:

- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password
- `PRODUCTION_HOST`: Production server hostname
- `PRODUCTION_USER`: Production server username
- `PRODUCTION_SSH_KEY`: SSH private key for production server

### 3. Pipeline Triggers

- **Push to main**: Deploy to production
- **Push to develop**: Deploy to staging
- **Pull Request**: Run tests and security scans
- **Release**: Create and deploy release

## Deployment Options

### 1. Docker Compose (Recommended for small to medium deployments)

```bash
# Development
docker-compose up -d

# Production with SSL
docker-compose -f docker-compose.ssl.yml up -d

# Production with optimizations
docker-compose -f docker-compose.production.yml up -d
```

### 2. Kubernetes (Recommended for large deployments)

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy services
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/web-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### 3. Manual Deployment

```bash
# Use the deployment script
./scripts/deploy.sh production latest

# Or with specific options
./scripts/deploy.sh staging v1.2.3
./scripts/deploy.sh rollback
./scripts/deploy.sh health-check
```

## Monitoring and Maintenance

### 1. Health Checks

```bash
# Check service health
curl -f https://api.vantage-ai.com/api/v1/health
curl -f https://vantage-ai.com/healthz

# Check database
docker-compose exec db pg_isready -U postgres

# Check Redis
docker-compose exec redis redis-cli ping
```

### 2. Log Monitoring

```bash
# View application logs
docker-compose logs -f api
docker-compose logs -f web
docker-compose logs -f worker

# View nginx logs
docker-compose logs -f nginx
```

### 3. Performance Monitoring

- Monitor CPU and memory usage
- Check database query performance
- Monitor API response times
- Track error rates

### 4. Backup and Recovery

```bash
# Create backup
./scripts/deploy.sh backup

# Restore from backup
docker-compose exec db psql -U postgres -d vantage < backup.sql
```

### 5. Security Maintenance

- Regularly update dependencies
- Monitor security advisories
- Rotate encryption keys
- Review access logs

## Troubleshooting

### Common Issues

1. **SSL Certificate Issues**
   ```bash
   # Check certificate validity
   openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout
   
   # Renew Let's Encrypt certificate
   sudo certbot renew
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose exec db pg_isready -U postgres
   
   # Check connection logs
   docker-compose logs db
   ```

3. **Performance Issues**
   ```bash
   # Check resource usage
   docker stats
   
   # Check slow queries
   docker-compose exec db psql -U postgres -d vantage -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   ```

### Support

For additional support:

1. Check the logs for error messages
2. Review the monitoring dashboards
3. Consult the troubleshooting section
4. Contact the development team

## Security Considerations

### Production Security Checklist

- [ ] SSL certificates installed and auto-renewing
- [ ] Database encryption enabled
- [ ] Strong passwords and secrets
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] Monitoring and alerting enabled
- [ ] Backup strategy implemented
- [ ] Access controls configured

### Security Best Practices

1. **Never commit secrets to version control**
2. **Use environment variables for sensitive data**
3. **Regularly rotate encryption keys**
4. **Monitor for security vulnerabilities**
5. **Implement proper access controls**
6. **Keep all software updated**
7. **Use HTTPS everywhere**
8. **Implement proper logging and monitoring**

## Conclusion

This deployment guide provides comprehensive instructions for deploying VANTAGE AI with security, performance, and reliability in mind. Follow the steps carefully and always test in a staging environment before deploying to production.

For questions or issues, please refer to the troubleshooting section or contact the development team.
