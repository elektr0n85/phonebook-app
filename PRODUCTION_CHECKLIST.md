# 🚀 Production Deployment Checklist

## ✅ **Pre-Deployment Security Checklist**

### **1. Environment Configuration** 🔧

- [ ] **SECRET_KEY**: Changed from default (min 32 characters, cryptographically random)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- [ ] **Database Password**: Strong password (16+ characters, mixed case, numbers, special chars)
  
- [ ] **ALLOWED_ORIGINS**: Set to actual domain(s) only
  ```
  ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  ```

- [ ] **DEBUG**: Set to `false` in production
  ```
  DEBUG=false
  ENVIRONMENT=production
  ```

- [ ] **DATABASE_URL**: Uses production database credentials

---

### **2. Security Headers** 🔒

- [ ] **HTTPS/SSL**: Certificate installed and configured
- [ ] **HSTS**: Strict-Transport-Security header enabled
- [ ] **CSP**: Content-Security-Policy configured
- [ ] **X-Frame-Options**: Set to DENY
- [ ] **X-Content-Type-Options**: Set to nosniff

**Verify:**
```bash
curl -I https://yourdomain.com | grep -E "Strict-Transport|X-Frame|X-Content"
```

---

### **3. Database** 💾

- [ ] **Backups**: Automated backup schedule configured
- [ ] **Migrations**: All Alembic migrations applied
  ```bash
  alembic upgrade head
  ```

- [ ] **Indexes**: Created on foreign keys and frequently queried fields
- [ ] **Connection Pooling**: Properly configured (size=10, max_overflow=20)
- [ ] **SSL Connection**: Database connection uses SSL

---

### **4. Authentication & Authorization** 🔐

- [ ] **Token Expiry**: Appropriate values set
  ```
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS=7
  ```

- [ ] **Password Policy**: Strong passwords enforced (8+, complexity)
- [ ] **Account Lockout**: Enabled (5 failed attempts = 15 min lock)
- [ ] **Rate Limiting**: Configured and tested
  ```
  RATE_LIMIT_PER_MINUTE=100
  LOGIN_RATE_LIMIT_PER_15MIN=5
  ```

---

### **5. API Security** 🛡️

- [ ] **CORS**: Restricted to known origins only (no wildcards)
- [ ] **Input Validation**: All endpoints validate input (Pydantic)
- [ ] **SQL Injection**: Using ORM (not raw SQL)
- [ ] **XSS Prevention**: Output escaped (React auto-escapes)
- [ ] **CSRF Protection**: Tokens implemented

---

### **6. Logging & Monitoring** 📊

- [ ] **Application Logs**: Configured and rotating
- [ ] **Audit Logs**: All security events logged (login, logout, changes)
- [ ] **Error Tracking**: Sentry or similar service configured
- [ ] **Uptime Monitoring**: Health check endpoints monitored
- [ ] **Performance Monitoring**: APM tool configured (optional)

---

### **7. Infrastructure** ☁️

- [ ] **Firewall**: Only necessary ports open (80, 443)
- [ ] **Reverse Proxy**: Nginx or similar configured
- [ ] **Load Balancer**: Configured if using multiple instances
- [ ] **CDN**: Static assets served via CDN (optional)
- [ ] **DDoS Protection**: Cloudflare or similar (optional)

---

### **8. Docker Security** 🐳

- [ ] **Images**: Using official base images (python:3.11-slim, postgres:15-alpine)
- [ ] **Non-Root User**: Containers run as non-root user
- [ ] **Secrets**: Not hardcoded in Dockerfile (use environment variables)
- [ ] **Scanning**: Docker images scanned for vulnerabilities
  ```bash
  docker scan phonebook-backend:latest
  ```

- [ ] **Resource Limits**: Memory and CPU limits set in docker-compose.yml

---

### **9. Testing** 🧪

- [ ] **All Tests Pass**: `pytest` runs successfully
  ```bash
  pytest --cov=app --cov-fail-under=90
  ```

- [ ] **Security Tests**: OWASP tests pass
  ```bash
  pytest -m security
  ```

- [ ] **Load Testing**: API can handle expected load (optional)
- [ ] **Penetration Testing**: Security audit completed (recommended)

---

### **10. Compliance & Legal** 📋

- [ ] **Privacy Policy**: Published and accessible
- [ ] **Terms of Service**: Published and accessible
- [ ] **GDPR Compliance**: User data handling compliant (if applicable)
- [ ] **Data Retention**: Policy defined and implemented
- [ ] **User Consent**: Cookie consent implemented (if applicable)

---

### **11. Backup & Recovery** 💿

- [ ] **Database Backups**: Daily automated backups
- [ ] **Backup Testing**: Restore tested successfully
- [ ] **Disaster Recovery Plan**: Documented and tested
- [ ] **Data Export**: Users can export their data

---

### **12. Documentation** 📚

- [ ] **API Documentation**: Swagger/ReDoc accessible at `/docs`
- [ ] **README**: Updated with production URLs
- [ ] **Deployment Guide**: Step-by-step deployment documented
- [ ] **Incident Response**: Runbook for common issues
- [ ] **Changelog**: Version history maintained

---

## 🔍 **Security Scan Commands**

### **Backend**
```bash
# Dependency vulnerabilities
safety check

# Code security issues
bandit -r app/

# Type checking
mypy app/
```

### **Frontend**
```bash
# Dependency vulnerabilities
npm audit

# Fix auto-fixable vulnerabilities
npm audit fix
```

### **Docker**
```bash
# Scan backend image
docker scan phonebook-backend:latest

# Scan frontend image
docker scan phonebook-frontend:latest
```

---

## 🚨 **Pre-Launch Verification**

### **1. Health Checks**
```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend loads
curl https://yourdomain.com
```

### **2. Authentication Flow**
- [ ] Register new user works
- [ ] Login works
- [ ] Token refresh works
- [ ] Logout works
- [ ] Account lockout works after 5 failed attempts

### **3. API Endpoints**
- [ ] Create contact works
- [ ] List contacts works
- [ ] Search works
- [ ] Update contact works
- [ ] Delete contact works
- [ ] Add phone works
- [ ] Remove phone works

### **4. Authorization**
- [ ] Users can only see their own contacts
- [ ] Regular users cannot access /admin endpoints
- [ ] CORS allows only configured origins

### **5. Performance**
- [ ] API response time < 200ms (average)
- [ ] Database queries optimized (no N+1)
- [ ] Static assets cached properly

---

## 📝 **Post-Deployment**

- [ ] **Monitor Logs**: Check for errors in first 24 hours
- [ ] **User Feedback**: Monitor user reports
- [ ] **Performance**: Check response times and database load
- [ ] **Security**: Monitor for unusual activity
- [ ] **Backups**: Verify first backup completed successfully

---

## 🔴 **Red Flags - DO NOT DEPLOY IF:**

- ❌ SECRET_KEY is still default value
- ❌ DEBUG=true in production
- ❌ No HTTPS/SSL certificate
- ❌ Tests failing
- ❌ Database not backed up
- ❌ ALLOWED_ORIGINS includes "*"
- ❌ Default passwords still in use
- ❌ Critical security vulnerabilities in dependencies

---

## ✅ **Sign-Off**

- [ ] **Developer**: Code reviewed and tested
- [ ] **Security**: Security checklist completed
- [ ] **DevOps**: Infrastructure ready
- [ ] **Manager**: Approved for production

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Version**: _______________  

---

**Last Updated**: 2026-01-19  
**Template Version**: 1.0
