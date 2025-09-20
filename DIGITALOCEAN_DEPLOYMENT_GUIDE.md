# 🚀 **DIGITALOCEAN DEPLOYMENT GUIDE - VANTAGE AI**

## 📋 **QUICK START (15 MINUTES)**

### **Step 1: Access DigitalOcean**
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Sign in or create account
3. Click **"Create App"**

### **Step 2: Connect GitHub**
1. Select **"GitHub"** as source
2. Choose repository: `newvantageco/vantage-ai`
3. Select branch: `master`
4. Click **"Next"**

### **Step 3: Configure Services**
DigitalOcean will auto-detect your services from the `.do/app.yaml` file:

#### **✅ Backend API Service:**
- **Type**: Web Service
- **Source**: Root directory
- **Dockerfile**: `infra/Dockerfile.api`
- **Port**: 8000
- **Routes**: `/api/*`

#### **✅ Frontend Service:**
- **Type**: Web Service
- **Source**: `/web`
- **Dockerfile**: `infra/Dockerfile.web`
- **Port**: 3000
- **Routes**: `/`

#### **✅ Worker Service:**
- **Type**: Worker
- **Source**: Root directory
- **Dockerfile**: `infra/Dockerfile.worker`

### **Step 4: Set Environment Variables**
Add these secrets in DigitalOcean dashboard:

```bash
# Database (will be auto-created)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Redis (use DigitalOcean Redis or external)
REDIS_URL=redis://host:port

# AI Services
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Social Media APIs
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Brave Search
BRAVE_SEARCH_API_KEY=your-brave-api-key

# Security
SECRET_KEY=your-32-char-secret-key
JWT_SECRET=your-jwt-secret-key

# App Settings
ENVIRONMENT=production
DEBUG=false
```

### **Step 5: Create Database**
1. In DigitalOcean dashboard, go to **"Databases"**
2. Create **PostgreSQL 14** database
3. Copy connection string to `DATABASE_URL`

### **Step 6: Deploy!**
1. Click **"Create Resources"**
2. Wait for build (10-15 minutes)
3. Your app will be live!

---

## 🔧 **DETAILED CONFIGURATION**

### **Service Configuration:**

#### **Backend API (`api` service):**
- **Instance Size**: Basic XXS (1 vCPU, 512MB RAM)
- **Instance Count**: 1
- **Health Check**: `/healthz`
- **Environment**: Production

#### **Frontend (`web` service):**
- **Instance Size**: Basic XXS (1 vCPU, 512MB RAM)
- **Instance Count**: 1
- **Build Command**: Auto-detected from Dockerfile
- **Environment**: Production

#### **Worker (`worker` service):**
- **Instance Size**: Basic XXS (1 vCPU, 512MB RAM)
- **Instance Count**: 1
- **Type**: Background worker
- **Environment**: Production

### **Database Configuration:**
- **Engine**: PostgreSQL 14
- **Size**: 1 vCPU, 1GB RAM
- **Storage**: 10GB SSD
- **Backups**: Enabled
- **High Availability**: Optional

---

## 📊 **COST ESTIMATION**

### **Monthly Costs:**
- **API Service**: $5/month
- **Frontend Service**: $5/month
- **Worker Service**: $5/month
- **Database**: $15/month
- **Total**: ~$30/month

### **Scaling Options:**
- **Basic S**: $12/month per service
- **Basic M**: $24/month per service
- **Professional S**: $48/month per service

---

## 🔍 **POST-DEPLOYMENT CHECKLIST**

### **1. Verify Services:**
- [ ] API health check: `https://your-app.ondigitalocean.app/healthz`
- [ ] Frontend loads: `https://your-app.ondigitalocean.app/`
- [ ] Database connection working
- [ ] Worker processing jobs

### **2. Test Integrations:**
- [ ] OpenAI API working
- [ ] Social media OAuth flows
- [ ] Brave Search integration
- [ ] File uploads working

### **3. Configure Domains:**
- [ ] Add custom domain (optional)
- [ ] Set up SSL certificate
- [ ] Configure DNS records

### **4. Monitor Performance:**
- [ ] Check DigitalOcean monitoring
- [ ] Set up alerts
- [ ] Monitor database performance

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues:**

#### **Build Failures:**
- Check Dockerfile paths
- Verify environment variables
- Check build logs in DigitalOcean

#### **Database Connection:**
- Verify `DATABASE_URL` format
- Check database is running
- Test connection string

#### **API Errors:**
- Check environment variables
- Verify service dependencies
- Check logs in DigitalOcean

#### **Frontend Issues:**
- Check `NEXT_PUBLIC_API_URL`
- Verify API endpoints
- Check browser console

---

## 📚 **USEFUL LINKS**

- **DigitalOcean App Platform**: [cloud.digitalocean.com/apps](https://cloud.digitalocean.com/apps)
- **Documentation**: [docs.digitalocean.com/products/app-platform](https://docs.digitalocean.com/products/app-platform)
- **Pricing**: [digitalocean.com/pricing/app-platform](https://digitalocean.com/pricing/app-platform)
- **Support**: [digitalocean.com/support](https://digitalocean.com/support)

---

## 🎉 **YOU'RE READY TO DEPLOY!**

Your VANTAGE AI platform is perfectly configured for DigitalOcean App Platform deployment. The `.do/app.yaml` file will automatically configure all services, and you just need to add your environment variables.

**Estimated deployment time: 15-30 minutes**
**Monthly cost: ~$30**
**Scaling: Easy with DigitalOcean's interface**

**Good luck with your launch! 🚀**
