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
  
- [ ] **⚠️ CORS in main.py**: Update hardcoded localhost origins to use `settings.ALLOWED_ORIGINS`
  ```python
  # Change from hardcoded localhost to:
  allow_origins=settings.ALLOWED_ORIGINS,
  ```

- [ ] **DEBUG**: Set to `false` in production
  ```
  DEBUG=false
  ENVIRONMENT=production
  ```

- [ ] **DATABASE_URL**: Uses production database credentials

- [ ] **FRONTEND_URL**: Set to production frontend URL (for password reset links)
  ```
  FRONTEND_URL=https://yourdomain.com
  ```

---

### **2. Email/SMTP Configuration** 📧

- [ ] **SMTP Credentials**: Configured for production email service
  ```
  SMTP_HOST=smtp.sendgrid.net
  SMTP_PORT=587
  SMTP_USER=apikey
  SMTP_PASSWORD=your_production_api_key
  ```

- [ ] **MAIL_FROM**: Set to verified sender address
  ```
  MAIL_FROM=noreply@yourdomain.com
  MAIL_FROM_NAME=Phonebook App
  ```

- [ ] **Email Delivery**: Test password reset flow end-to-end
  - [ ] Forgot password email sends correctly
  - [ ] Reset link works and contains correct URL
  - [ ] Password change notification sends

- [ ] **RESET_TOKEN_EXPIRE_HOURS**: Appropriate value (default: 1 hour)

---

### **3. Security Headers** 🔒

- [ ] **HTTPS/SSL**: Certificate installed and configured
- [ ] **HSTS**: Strict-Transport-Security header enabled (auto in production mode)
- [ ] **CSP**: Content-Security-Policy configured
- [ ] **X-Frame-Options**: Set to DENY ✅ (configured in main.py)
- [ ] **X-Content-Type-Options**: Set to nosniff ✅ (configured in main.py)
- [ ] **Permissions-Policy**: Dangerous features disabled ✅ (configured in main.py)

**Verify:**
```bash
curl -I https://yourdomain.com | grep -E "Strict-Transport|X-Frame|X-Content|Permissions-Policy"
```

---

### **4. Database** 💾

- [ ] **Backups**: Automated backup schedule configured
- [ ] **Migrations**: All Alembic migrations applied
  ```bash
  alembic upgrade head
  ```
  - [ ] Includes `add_reset_token_fields` migration

- [ ] **Indexes**: Created on foreign keys and frequently queried fields
  - [ ] `users.reset_token` index (for password reset lookups)
  
- [ ] **Connection Pooling**: Properly configured (size=10, max_overflow=20)
- [ ] **SSL Connection**: Database connection uses SSL

---

### **5. Authentication & Authorization** 🔐

- [ ] **Token Expiry**: Appropriate values set
  ```
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS=7
  RESET_TOKEN_EXPIRE_HOURS=1
  ```

- [ ] **Password Policy**: Strong passwords enforced (8+, complexity)
- [ ] **Account Lockout**: Enabled (5 failed attempts = 15 min lock)
- [ ] **Rate Limiting**: Configured and tested
  ```
  RATE_LIMIT_PER_MINUTE=100
  LOGIN_RATE_LIMIT_PER_15MIN=5
  ```

- [ ] **Password Reset Security**:
  - [ ] Reset tokens are hashed (bcrypt) before storage ✅
  - [ ] Tokens are single-use (cleared after reset) ✅
  - [ ] Generic responses prevent user enumeration ✅
  - [ ] Notification email sent after password change ✅

---

### **6. API Security** 🛡️

- [ ] **CORS**: Restricted to known origins only (no wildcards)
  - ⚠️ **Action Required**: Update `main.py` to use `settings.ALLOWED_ORIGINS`
  
- [ ] **Input Validation**: All endpoints validate input (Pydantic)
- [ ] **SQL Injection**: Using ORM (not raw SQL)
- [ ] **XSS Prevention**: Output escaped (React auto-escapes)
- [ ] **API Docs**: Disabled in production ✅ (auto via DEBUG=false)

---

### **7. Logging & Monitoring** 📊

- [ ] **Application Logs**: Configured and rotating
- [ ] **Audit Logs**: All security events logged
  - [ ] Login success/failure ✅
  - [ ] Registration ✅
  - [ ] Password reset request ✅
  - [ ] Password reset complete ✅
  - [ ] Password change ✅
  - [ ] Logout ✅
  - [ ] Contact CRUD operations ✅

- [ ] **Error Tracking**: Sentry or similar service configured
- [ ] **Uptime Monitoring**: Health check endpoints monitored
- [ ] **Email Delivery Monitoring**: Track failed email sends

---

### **8. Infrastructure** ☁️

- [ ] **Firewall**: Only necessary ports open (80, 443)
- [ ] **Reverse Proxy**: Nginx or similar configured
- [ ] **Load Balancer**: Configured if using multiple instances
- [ ] **CDN**: Static assets served via CDN (optional)
- [ ] **DDoS Protection**: Cloudflare or similar (optional)

---

### **9. Docker Security** 🐳

- [ ] **Images**: Using official base images (python:3.11-slim, postgres:15-alpine)
- [ ] **Non-Root User**: Containers run as non-root user
- [ ] **Secrets**: Not hardcoded in Dockerfile (use environment variables)
- [ ] **Scanning**: Docker images scanned for vulnerabilities
  ```bash
  docker scout cves phonebook-backend:latest
  ```

- [ ] **Resource Limits**: Memory and CPU limits set in docker-compose.yml

---

### **10. Testing** 🧪

- [ ] **All Tests Pass**: `pytest` runs successfully
  ```bash
  pytest --cov=app --cov-fail-under=80
  ```

- [ ] **Security Tests**: OWASP tests pass
  ```bash
  pytest -m security -v
  ```

- [ ] **Password Reset Flow**: Manual test
  - [ ] Request reset email
  - [ ] Verify email received
  - [ ] Reset password via link
  - [ ] Verify login with new password
  - [ ] Verify old password no longer works

- [ ] **Load Testing**: API can handle expected load (optional)
- [ ] **Penetration Testing**: Security audit completed (recommended)

---

### **11. Compliance & Legal** 📋

- [ ] **Privacy Policy**: Published and accessible
- [ ] **Terms of Service**: Published and accessible
- [ ] **GDPR Compliance**: User data handling compliant (if applicable)
- [ ] **Data Retention**: Policy defined and implemented
- [ ] **User Consent**: Cookie consent implemented (if applicable)

---

### **12. Backup & Recovery** 💿

- [ ] **Database Backups**: Daily automated backups
- [ ] **Backup Testing**: Restore tested successfully
- [ ] **Disaster Recovery Plan**: Documented and tested
- [ ] **Data Export**: Users can export their data

---

### **13. Documentation** 📚

- [ ] **API Documentation**: Swagger/ReDoc accessible at `/docs` (dev only)
- [ ] **README**: Updated with production URLs
- [ ] **Deployment Guide**: Step-by-step deployment documented
- [ ] **Incident Response**: Runbook for common issues
- [ ] **Changelog**: Version history maintained

---

## 🔍 **Security Scan Commands**

### **Backend**
```bash
# Dependency vulnerabilities
pip-audit
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
docker scout cves phonebook-backend:latest

# Scan frontend image
docker scout cves phonebook-frontend:latest
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
- [ ] **Forgot password sends email**
- [ ] **Reset password with token works**
- [ ] **Password change (logged in) works**
- [ ] **Password change notification email sends**

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
- [ ] Reset tokens work only once

### **5. Performance**
- [ ] API response time < 200ms (average)
- [ ] Database queries optimized (no N+1)
- [ ] Static assets cached properly
- [ ] Email sending doesn't block requests (async)

---

## 📝 **Post-Deployment**

- [ ] **Monitor Logs**: Check for errors in first 24 hours
- [ ] **User Feedback**: Monitor user reports
- [ ] **Performance**: Check response times and database load
- [ ] **Security**: Monitor for unusual activity
- [ ] **Backups**: Verify first backup completed successfully
- [ ] **Email Delivery**: Monitor bounce rates and delivery success

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
- ❌ **CORS still using hardcoded localhost in main.py**
- ❌ **SMTP not configured (password reset won't work)**
- ❌ **FRONTEND_URL still pointing to localhost**

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

**Last Updated**: 2026-02-05  
**Template Version**: 2.0 (Added Password Reset, Email, Updated CORS notes)
