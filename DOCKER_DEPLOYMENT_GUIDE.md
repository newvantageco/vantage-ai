# 🐳 VANTAGE AI Docker Deployment Guide

## ✅ Docker Images Successfully Published

Your VANTAGE AI platform is now available on Docker Hub with the following images:

### 📦 Published Images
- **API Service**: `sabanali/vantage-ai-api:latest`
- **Web Frontend**: `sabanali/vantage-ai-web:latest`
- **Worker Service**: `sabanali/vantage-ai-worker:latest`

### 🔗 Docker Hub Links
- [API Image](https://hub.docker.com/r/sabanali/vantage-ai-api)
- [Web Image](https://hub.docker.com/r/sabanali/vantage-ai-web)
- [Worker Image](https://hub.docker.com/r/sabanali/vantage-ai-worker)

## 🚀 Quick Start Deployment

### Option 1: Docker Compose (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/newvantageco/vantage-ai.git
cd vantage-ai

# 2. Create environment file
cp env.production.example .env

# 3. Edit environment variables
nano .env

# 4. Start all services
docker-compose -f docker-compose.prod.yml up -d

# 5. Check status
docker-compose -f docker-compose.prod.yml ps
```

### Option 2: Individual Containers
```bash
# 1. Start PostgreSQL
docker run -d --name vantage-postgres \
  -e POSTGRES_DB=vantage_ai \
  -e POSTGRES_USER=vantage_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15-alpine

# 2. Start Redis
docker run -d --name vantage-redis \
  -p 6379:6379 \
  redis:7-alpine

# 3. Start API
docker run -d --name vantage-api \
  --link vantage-postgres:postgres \
  --link vantage-redis:redis \
  -e DATABASE_URL=postgresql://vantage_user:your_password@postgres:5432/vantage_ai \
  -e REDIS_URL=redis://redis:6379 \
  -e OPENAI_API_KEY=your_openai_key \
  -p 8000:8000 \
  sabanali/vantage-ai-api:latest

# 4. Start Web
docker run -d --name vantage-web \
  --link vantage-api:api \
  -e NEXT_PUBLIC_API_URL=http://api:8000 \
  -p 3000:3000 \
  sabanali/vantage-ai-web:latest

# 5. Start Worker
docker run -d --name vantage-worker \
  --link vantage-postgres:postgres \
  --link vantage-redis:redis \
  -e DATABASE_URL=postgresql://vantage_user:your_password@postgres:5432/vantage_ai \
  -e REDIS_URL=redis://redis:6379 \
  -e OPENAI_API_KEY=your_openai_key \
  sabanali/vantage-ai-worker:latest
```

## 🔧 Environment Configuration

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://vantage_user:password@postgres:5432/vantage_ai
REDIS_URL=redis://redis:6379

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# OAuth Providers
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# Stripe Billing
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Security
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret

# Web Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Service Health Checks

### API Health Endpoints
- `GET http://localhost:8000/api/v1/health` - Basic health check
- `GET http://localhost:8000/api/v1/health/detailed` - Detailed system status

### Web Frontend
- `GET http://localhost:3000` - Main application

### Database Health
```bash
# Check PostgreSQL
docker exec vantage-postgres pg_isready -U vantage_user -d vantage_ai

# Check Redis
docker exec vantage-redis redis-cli ping
```

## 🔄 Production Deployment

### 1. Cloud Provider Setup

#### AWS ECS
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name vantage-ai

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster vantage-ai \
  --service-name vantage-ai-service \
  --task-definition vantage-ai:1 \
  --desired-count 3
```

#### Google Cloud Run
```bash
# Deploy API
gcloud run deploy vantage-ai-api \
  --image sabanali/vantage-ai-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy Web
gcloud run deploy vantage-ai-web \
  --image sabanali/vantage-ai-web:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Create resource group
az group create --name vantage-ai-rg --location eastus

# Deploy API
az container create \
  --resource-group vantage-ai-rg \
  --name vantage-ai-api \
  --image sabanali/vantage-ai-api:latest \
  --ports 8000 \
  --environment-variables DATABASE_URL=your_db_url
```

### 2. Load Balancer Configuration

#### Nginx Configuration
```nginx
upstream api {
    server vantage-ai-api:8000;
}

upstream web {
    server vantage-ai-web:3000;
}

server {
    listen 80;
    server_name api.vantage-ai.com;
    
    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name vantage-ai.com;
    
    location / {
        proxy_pass http://web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📈 Monitoring & Scaling

### Health Monitoring
```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check resource usage
docker stats
```

### Auto-scaling
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  api:
    image: sabanali/vantage-ai-api:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Database Scaling
```bash
# Scale PostgreSQL with read replicas
docker run -d --name vantage-postgres-replica \
  -e POSTGRES_DB=vantage_ai \
  -e POSTGRES_USER=vantage_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_MASTER_SERVICE=postgres \
  postgres:15-alpine
```

## 🔒 Security Best Practices

### 1. Network Security
```bash
# Create isolated network
docker network create vantage-network

# Run containers in isolated network
docker run --network vantage-network sabanali/vantage-ai-api:latest
```

### 2. Secrets Management
```bash
# Use Docker secrets
echo "your_secret_key" | docker secret create secret_key -
echo "your_db_password" | docker secret create db_password -

# Reference in compose file
version: '3.8'
services:
  api:
    image: sabanali/vantage-ai-api:latest
    secrets:
      - secret_key
      - db_password
```

### 3. Image Security
```bash
# Scan images for vulnerabilities
docker scan sabanali/vantage-ai-api:latest
docker scan sabanali/vantage-ai-web:latest
docker scan sabanali/vantage-ai-worker:latest
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database connectivity
docker exec vantage-api python -c "
import psycopg2
conn = psycopg2.connect('postgresql://vantage_user:password@postgres:5432/vantage_ai')
print('Database connected successfully')
"
```

#### 2. Redis Connection Issues
```bash
# Check Redis connectivity
docker exec vantage-api python -c "
import redis
r = redis.Redis(host='redis', port=6379)
print('Redis connected:', r.ping())
"
```

#### 3. API Not Responding
```bash
# Check API logs
docker logs vantage-api

# Check API health
curl http://localhost:8000/api/v1/health
```

#### 4. Web Frontend Issues
```bash
# Check web logs
docker logs vantage-web

# Check web connectivity
curl http://localhost:3000
```

### Performance Optimization

#### 1. Resource Limits
```yaml
services:
  api:
    image: sabanali/vantage-ai-api:latest
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

#### 2. Caching
```bash
# Enable Redis caching
docker run -d --name vantage-redis \
  -e REDIS_MAXMEMORY=256mb \
  -e REDIS_MAXMEMORY_POLICY=allkeys-lru \
  redis:7-alpine
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup strategy implemented

### Post-Deployment
- [ ] Health checks passing
- [ ] All services running
- [ ] Database connectivity confirmed
- [ ] API endpoints responding
- [ ] Web frontend accessible
- [ ] Worker processes active

## 🎯 Success Metrics

### Performance Targets
- **API Response Time**: < 200ms average
- **Web Load Time**: < 2 seconds
- **Container Uptime**: > 99.9%
- **Memory Usage**: < 80% of allocated

### Business Metrics
- **User Registration**: Track daily signups
- **Content Generation**: Monitor AI usage
- **Revenue**: Track billing and subscriptions
- **Engagement**: Monitor user activity

---

## 🎉 Your VANTAGE AI Platform is Ready!

Your Docker images are now available on Docker Hub and ready for deployment anywhere:

- **GitHub Repository**: https://github.com/newvantageco/vantage-ai
- **Docker Hub**: https://hub.docker.com/u/sabanali
- **Documentation**: Complete deployment and testing guides included

**Next Steps:**
1. Choose your deployment platform (AWS/GCP/Azure)
2. Configure environment variables
3. Deploy using Docker Compose or individual containers
4. Set up monitoring and alerts
5. Scale as needed

Your VANTAGE AI platform is production-ready and systematically tested! 🚀
