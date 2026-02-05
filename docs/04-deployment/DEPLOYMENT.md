# 🚀 Deployment Guide - Phonebook Application

Complete guide for deploying the Phonebook application to production.

---

## 📋 **Table of Contents**

1. [Prerequisites](#prerequisites)
2. [Docker Deployment (Recommended)](#docker-deployment)
3. [Cloud Platforms](#cloud-platforms)
   - [AWS](#aws-deployment)
   - [Heroku](#heroku-deployment)
   - [Railway](#railway-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Production Checklist](#production-checklist)

---

## ✅ **Prerequisites**

### **Required:**
- Docker & Docker Compose (20.10+)
- PostgreSQL (15+)
- Domain name (for HTTPS)
- SSL certificate (Let's Encrypt recommended)

### **Recommended:**
- Reverse proxy (Nginx/Traefik)
- CDN (Cloudflare)
- Monitoring (Sentry, Datadog)
- Backup solution

---

## 🐳 **Docker Deployment (Recommended)**

### **Quick Start** (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/phonebook-app.git
cd phonebook-app

# 2. Create environment file
cp .env.example .env

# 3. Edit .env with production values
nano .env  # or vim .env

# Required changes:
# - POSTGRES_PASSWORD: Strong password
# - SECRET_KEY: Generate with: openssl rand -hex 32
# - ALLOWED_ORIGINS: Your domain(s)
# - VITE_API_URL: Your API URL

# 4. Start application
docker-compose up -d

# 5. Verify deployment
docker-compose ps
docker-compose logs -f

# 6. Access application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### **Production Configuration**

#### **1. Generate Secure Secrets**

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate strong password
openssl rand -base64 32
```

#### **2. Configure .env**

```bash
# Database
POSTGRES_DB=phonebook_prod
POSTGRES_USER=phonebook_user
POSTGRES_PASSWORD=<your-secure-password>

# Backend
SECRET_KEY=<your-secret-key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVIRONMENT=production
DEBUG=False

# Frontend
VITE_API_URL=https://api.yourdomain.com/api/v1
```

#### **3. SSL/HTTPS Setup**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - certbot-data:/var/www/certbot
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  certbot:
    image: certbot/certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - certbot-data:/var/www/certbot
    command: certonly --webroot --webroot-path=/var/www/certbot --email your@email.com --agree-tos --no-eff-email -d yourdomain.com -d www.yourdomain.com

  # ... rest of services from docker-compose.yml

volumes:
  certbot-data:
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## ☁️ **Cloud Platforms**

### **AWS Deployment**

#### **Option 1: EC2 + Docker**

```bash
# 1. Launch EC2 instance (Ubuntu 22.04, t3.medium)

# 2. SSH to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
sudo systemctl enable docker

# 4. Clone and deploy
git clone your-repo
cd phonebook-app
cp .env.example .env
# Edit .env
docker-compose up -d

# 5. Configure security group
# Allow: 80 (HTTP), 443 (HTTPS), 22 (SSH)
```

#### **Option 2: ECS Fargate**

1. Create ECR repositories:
```bash
aws ecr create-repository --repository-name phonebook-backend
aws ecr create-repository --repository-name phonebook-frontend
```

2. Push images:
```bash
# Build and tag
docker build -t phonebook-backend ./backend
docker build -t phonebook-frontend ./frontend

# Tag for ECR
docker tag phonebook-backend:latest <account-id>.dkr.ecr.region.amazonaws.com/phonebook-backend:latest
docker tag phonebook-frontend:latest <account-id>.dkr.ecr.region.amazonaws.com/phonebook-frontend:latest

# Push
docker push <account-id>.dkr.ecr.region.amazonaws.com/phonebook-backend:latest
docker push <account-id>.dkr.ecr.region.amazonaws.com/phonebook-frontend:latest
```

3. Create ECS task definitions and service (use AWS Console)

#### **Option 3: Elastic Beanstalk**

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize
eb init -p docker phonebook-app

# 3. Create environment
eb create phonebook-prod

# 4. Deploy
eb deploy
```

---

### **Heroku Deployment**

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create phonebook-app

# 4. Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# 5. Set environment variables
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set ENVIRONMENT=production
heroku config:set DEBUG=False
heroku config:set ALLOWED_ORIGINS=https://phonebook-app.herokuapp.com

# 6. Deploy backend
cd backend
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
git init
git add .
git commit -m "Deploy backend"
heroku git:remote -a phonebook-app
git push heroku main

# 7. Run migrations
heroku run python init_db.py

# 8. Deploy frontend (separate app or static hosting)
# Option: Use Vercel/Netlify for frontend
```

---

### **Railway Deployment**

Railway is the easiest deployment option!

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add PostgreSQL
railway add postgresql

# 5. Deploy backend
cd backend
railway up

# 6. Set environment variables (in Railway dashboard)
# - SECRET_KEY
# - ALLOWED_ORIGINS
# - etc.

# 7. Deploy frontend
cd ../frontend
railway up

# Done! Railway provides URLs automatically
```

**Or use Railway's GitHub integration:**
1. Push code to GitHub
2. Connect Railway to GitHub repo
3. Railway auto-deploys on push!

---

## 🔧 **Manual Deployment**

### **Backend (FastAPI)**

```bash
# 1. Setup server (Ubuntu 22.04)
sudo apt update
sudo apt install -y python3.11 python3-pip python3-venv postgresql nginx

# 2. Create virtual environment
cd /opt/phonebook-backend
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure PostgreSQL
sudo -u postgres createdb phonebook_db
sudo -u postgres createuser phonebook_user
sudo -u postgres psql
# ALTER USER phonebook_user WITH PASSWORD 'your_password';
# GRANT ALL PRIVILEGES ON DATABASE phonebook_db TO phonebook_user;

# 5. Set environment variables
export DATABASE_URL="postgresql+asyncpg://phonebook_user:password@localhost/phonebook_db"
export SECRET_KEY="your-secret-key"

# 6. Run migrations
python init_db.py

# 7. Start with systemd
sudo nano /etc/systemd/system/phonebook-backend.service
```

Systemd service file:
```ini
[Unit]
Description=Phonebook Backend API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/phonebook-backend
Environment="PATH=/opt/phonebook-backend/venv/bin"
EnvironmentFile=/opt/phonebook-backend/.env
ExecStart=/opt/phonebook-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable phonebook-backend
sudo systemctl start phonebook-backend
```

### **Frontend (React)**

```bash
# 1. Build frontend
cd frontend
npm install
npm run build

# 2. Copy to nginx
sudo cp -r dist/* /var/www/phonebook-frontend/

# 3. Configure nginx
sudo nano /etc/nginx/sites-available/phonebook
```

Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/phonebook-frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/phonebook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ **Production Checklist**

Before deploying to production, ensure:

### **Security** 🔒
- [ ] Change default SECRET_KEY
- [ ] Use strong database password
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set DEBUG=False
- [ ] Remove .env from version control (.gitignore)
- [ ] Use environment variables for secrets
- [ ] Enable firewall (UFW/Security Groups)
- [ ] Disable unnecessary ports
- [ ] Set up fail2ban (SSH protection)

### **Database** 🗄️
- [ ] Configure automated backups
- [ ] Test backup restoration
- [ ] Set up connection pooling
- [ ] Configure max connections
- [ ] Enable SSL for database connections
- [ ] Monitor disk space

### **Application** 🚀
- [ ] Set appropriate ALLOWED_ORIGINS
- [ ] Configure rate limiting
- [ ] Set up logging (Sentry/CloudWatch)
- [ ] Configure health checks
- [ ] Test error handling
- [ ] Set up monitoring/alerts

### **Infrastructure** 🏗️
- [ ] Use CDN for static assets
- [ ] Configure reverse proxy (Nginx/Traefik)
- [ ] Set up load balancer (if needed)
- [ ] Configure auto-scaling (if needed)
- [ ] Set up container orchestration (if using Docker)

### **Testing** 🧪
- [ ] Run all tests: `pytest`
- [ ] Test with production-like data
- [ ] Load testing
- [ ] Security scanning: `bandit -r app/`
- [ ] Dependency audit: `safety check`

### **Monitoring** 📊
- [ ] Application metrics (response time, errors)
- [ ] Server metrics (CPU, memory, disk)
- [ ] Database metrics (connections, queries)
- [ ] Log aggregation
- [ ] Uptime monitoring
- [ ] Set up alerts

### **Documentation** 📝
- [ ] API documentation accessible
- [ ] Deployment runbook
- [ ] Incident response plan
- [ ] Contact information for on-call

---

## 🆘 **Troubleshooting**

### **Database Connection Issues**
```bash
# Check PostgreSQL is running
docker-compose ps db
docker-compose logs db

# Test connection
docker-compose exec backend python -c "from app.database import engine; print('OK')"
```

### **Container Issues**
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart backend

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### **Permission Issues**
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Fix Docker socket
sudo chmod 666 /var/run/docker.sock
```

---

## 📞 **Support**

For issues or questions:
- GitHub Issues: [your-repo/issues](https://github.com/yourusername/phonebook-app/issues)
- Documentation: [/docs](../docs/)
- Email: your-email@example.com

---

**Deployment Guide Version**: 1.0.0  
**Last Updated**: 2026-01-20  
**Status**: Production Ready ✅
