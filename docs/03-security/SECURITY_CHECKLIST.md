# 🔒 Production Security Checklist

Comprehensive security checklist for deploying Phonebook application to production.

---

## ✅ **Pre-Deployment Security**

### **1. Environment & Secrets** 🔑

- [ ] **Generate strong SECRET_KEY**
  ```bash
  openssl rand -hex 32
  ```
  - Minimum 32 characters
  - Never reuse across environments
  - Rotate every 90 days

- [ ] **Database credentials**
  - [ ] Strong password (16+ chars, mixed case, numbers, symbols)
  - [ ] Unique password (not used elsewhere)
  - [ ] Stored in environment variables only

- [ ] **SMTP credentials**
  - [ ] API key or password secured
  - [ ] Not hardcoded in code
  - [ ] Sender address verified with email provider

- [ ] **Remove hardcoded secrets**
  ```bash
  # Scan for potential secrets
  grep -r "password" --include="*.py" backend/
  grep -r "secret" --include="*.py" backend/
  grep -r "token" --include="*.py" backend/
  grep -r "smtp" --include="*.py" backend/
  ```

- [ ] **.env file security**
  - [ ] Added to .gitignore
  - [ ] Never committed to version control
  - [ ] Restricted file permissions: `chmod 600 .env`

### **2. Application Configuration** ⚙️

- [ ] **DEBUG mode disabled**
  ```python
  DEBUG = False
  ENVIRONMENT = "production"
  ```

- [ ] **CORS configuration**
  ```python
  ALLOWED_ORIGINS = [
      "https://yourdomain.com",
      "https://www.yourdomain.com"
  ]
  # No wildcards (*)
  # No localhost in production
  ```
  
- [ ] **⚠️ Update main.py CORS**
  - Current: hardcoded localhost URLs
  - Required: `allow_origins=settings.ALLOWED_ORIGINS`

- [ ] **Rate limiting enabled**
  - [ ] Login endpoint: 5 attempts per 15 minutes
  - [ ] API endpoints: 100 requests per minute
  - [ ] Password reset: 3 attempts per hour (TODO: implement)
  - [ ] Registration: 3 per hour per IP (TODO: implement)

- [ ] **Session security**
  - [ ] JWT access token expiration: 30 minutes
  - [ ] Refresh token: 7 days max
  - [ ] Reset token: 1 hour expiration
  - [ ] Secure cookie flags (HttpOnly, Secure, SameSite)

### **3. Database Security** 🗄️

- [ ] **Connection security**
  - [ ] SSL/TLS enabled for connections
  - [ ] Database not exposed to internet
  - [ ] Firewall rules: only app server can connect
  - [ ] Non-default port (optional)

- [ ] **User permissions**
  ```sql
  -- Application user has minimal privileges
  GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO phonebook_user;
  -- No DROP, CREATE, or ALTER permissions
  ```

- [ ] **Backups configured**
  - [ ] Automated daily backups
  - [ ] Backup retention: 30 days
  - [ ] Encrypted backups
  - [ ] Test restoration procedure
  - [ ] Off-site backup storage

### **4. HTTPS/SSL** 🔐

- [ ] **SSL certificate installed**
  - [ ] Valid certificate (not self-signed)
  - [ ] Auto-renewal configured (Let's Encrypt)
  - [ ] TLS 1.2+ only (disable TLS 1.0, 1.1)
  - [ ] Strong cipher suites

- [ ] **HTTPS enforced**
  - [ ] HTTP → HTTPS redirect
  - [ ] HSTS header enabled
  ```
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  ```

- [ ] **Security headers configured** (✅ in main.py)
  ```
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Content-Security-Policy: default-src 'self'; script-src 'self'; ...
  Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=()
  ```

---

## 🛡️ **OWASP Top 10 (2021) Compliance**

### **A01: Broken Access Control** ✅

- [ ] **Authorization checks implemented**
  - [ ] Users can only access own data
  - [ ] Admin routes protected by role check
  - [ ] Ownership validation on all CRUD operations
  - [ ] Password reset tokens bound to specific user

- [ ] **Tested scenarios:**
  - [ ] User cannot view other users' contacts
  - [ ] User cannot update other users' contacts
  - [ ] Regular user cannot access /api/v1/admin/*
  - [ ] Unauthenticated users redirected to login
  - [ ] Cannot use another user's reset token

### **A02: Cryptographic Failures** ✅

- [ ] **Password storage**
  - [ ] bcrypt hashing (cost factor 12+) ✅
  - [ ] Passwords never stored in plaintext ✅
  - [ ] Password never returned in API responses ✅
  - [ ] Reset tokens hashed before storage ✅

- [ ] **Data in transit**
  - [ ] HTTPS enforced
  - [ ] Database connections encrypted (SSL)
  - [ ] Email sent via TLS (STARTTLS)
  - [ ] No sensitive data in URLs or logs

### **A03: Injection** ✅

- [ ] **SQL injection prevention**
  - [ ] ORM used (SQLAlchemy) ✅
  - [ ] Parameterized queries only ✅
  - [ ] No raw SQL or string concatenation ✅
  - [ ] Input validation with Pydantic ✅

- [ ] **XSS prevention**
  - [ ] React auto-escaping enabled ✅
  - [ ] CSP headers configured ✅
  - [ ] No dangerouslySetInnerHTML usage

- [ ] **Command injection prevention**
  - [ ] No os.system() or subprocess with user input
  - [ ] Input validation on all user inputs

- [ ] **Email header injection prevention**
  - [ ] Using fastapi-mail library (handles safely) ✅

### **A04: Insecure Design** ✅

- [ ] **Secure architecture**
  - [ ] Principle of least privilege
  - [ ] Defense in depth
  - [ ] Threat modeling completed (STRIDE)

- [ ] **Password reset design**
  - [ ] Cryptographically secure tokens (secrets.token_urlsafe) ✅
  - [ ] Token expiration (1 hour default) ✅
  - [ ] Single-use tokens ✅
  - [ ] Generic responses (no user enumeration) ✅
  - [ ] Notification on password change ✅

### **A05: Security Misconfiguration** ✅

- [ ] **Server hardening**
  - [ ] Unnecessary services disabled
  - [ ] Default passwords changed
  - [ ] Error messages don't leak information ✅
  - [ ] Verbose errors disabled in production ✅
  - [ ] API docs disabled in production ✅

- [ ] **Dependency management**
  ```bash
  # Check for vulnerabilities
  safety check
  pip-audit
  ```

### **A06: Vulnerable Components** ✅

- [ ] **Dependencies up to date**
  ```bash
  # Backend
  pip list --outdated
  safety check
  pip-audit
  
  # Frontend
  npm audit
  npm audit fix
  ```

- [ ] **Key dependencies (verified secure versions)**
  - [ ] fastapi==0.109.0
  - [ ] sqlalchemy==2.0.25
  - [ ] python-jose[cryptography]==3.3.0
  - [ ] passlib[bcrypt]==1.7.4
  - [ ] fastapi-mail==1.4.1

- [ ] **Automated scanning**
  - [ ] Dependabot enabled (GitHub)
  - [ ] Regular security updates

### **A07: Authentication Failures** ✅

- [ ] **Strong password policy**
  - [ ] Minimum 8 characters ✅
  - [ ] Requires: uppercase, lowercase, digit, special char ✅
  - [ ] Password complexity validation (Pydantic) ✅

- [ ] **Account lockout**
  - [ ] 5 failed attempts = 15 minute lockout ✅
  - [ ] Lockout prevents brute force attacks ✅
  - [ ] Lockout logged in audit_logs ✅

- [ ] **Session management**
  - [ ] JWT tokens with expiration ✅
  - [ ] Access/refresh token separation ✅
  - [ ] Token type verification ✅
  - [ ] Logout audit logging ✅

- [ ] **Password reset security**
  - [ ] Secure token generation (secrets.token_urlsafe(32)) ✅
  - [ ] Token hashed with bcrypt ✅
  - [ ] Single-use (cleared after reset) ✅
  - [ ] Expiration enforced ✅
  - [ ] Email notification after change ✅

### **A08: Software and Data Integrity** ✅

- [ ] **Code integrity**
  - [ ] Code signing (optional)
  - [ ] Integrity checks in CI/CD
  - [ ] Dependencies from trusted sources only

### **A09: Logging Failures** ✅

- [ ] **Comprehensive logging**
  - [ ] All authentication events logged ✅
  - [ ] All authorization failures logged ✅
  - [ ] All data modifications logged (audit_logs) ✅
  - [ ] Logs include: timestamp, user, IP, action ✅
  - [ ] Password reset events logged ✅

- [ ] **Audit log actions tracked:**
  - [ ] `login_success` ✅
  - [ ] `login_failed` ✅
  - [ ] `logout` ✅
  - [ ] `register` ✅
  - [ ] `password_change` ✅
  - [ ] `password_reset_request` ✅
  - [ ] `password_reset_complete` ✅
  - [ ] `account_locked` ✅
  - [ ] Contact CRUD operations ✅

- [ ] **Log security**
  - [ ] Logs don't contain passwords/secrets
  - [ ] Logs stored securely
  - [ ] Log retention policy: 90 days

- [ ] **Monitoring & Alerts**
  - [ ] Failed login alerts (>10 in 5 min)
  - [ ] Error rate alerts
  - [ ] Disk space alerts
  - [ ] Database connection alerts
  - [ ] Email delivery failure alerts

### **A10: Server-Side Request Forgery** ✅

- [ ] **SSRF prevention**
  - [ ] No user-controlled URLs in backend
  - [ ] Input validation on any external requests
  - [ ] Whitelist allowed domains
  - [ ] Email URLs constructed server-side ✅

---

## 🧪 **Security Testing**

### **Automated Tests**

```bash
# Run all security tests
pytest -m security

# OWASP tests specifically
pytest tests/security/test_owasp.py -v

# Code coverage
pytest --cov=app --cov-report=html
```

### **Security Scanning**

```bash
# Python security linter
bandit -r app/

# Dependency vulnerabilities
safety check
pip-audit

# Type checking
mypy app/

# Code quality
pylint app/
```

### **Manual Testing**

- [ ] **SQL Injection attempts**
  ```
  GET /api/v1/contacts/?search=' OR '1'='1
  GET /api/v1/contacts/?search='; DROP TABLE contacts--
  ```
  Expected: No error, empty results

- [ ] **XSS attempts**
  ```json
  POST /api/v1/contacts/
  {
    "name": "<script>alert('XSS')</script>",
    "email": "test@example.com"
  }
  ```
  Expected: Accepted but safely escaped on render

- [ ] **Authentication bypass**
  ```
  GET /api/v1/contacts/ (without Authorization header)
  ```
  Expected: 401 Unauthorized

- [ ] **Privilege escalation**
  ```
  GET /api/v1/admin/users (as regular user)
  ```
  Expected: 403 Forbidden

- [ ] **Password reset abuse**
  ```
  POST /api/v1/auth/forgot-password
  {"email": "nonexistent@example.com"}
  ```
  Expected: Same response as valid email (no enumeration)

- [ ] **Token reuse**
  ```
  Use reset token twice
  ```
  Expected: Second attempt fails

---

## 🔍 **Penetration Testing**

### **Tools to Use**

- [ ] **OWASP ZAP** - Automated security scanner
  ```bash
  docker run -t owasp/zap2docker-stable zap-baseline.py -t http://your-app
  ```

- [ ] **Burp Suite** - Manual penetration testing

- [ ] **sqlmap** - SQL injection testing
  ```bash
  sqlmap -u "http://your-app/api/v1/contacts?search=test" --headers="Authorization: Bearer TOKEN"
  ```

- [ ] **Nikto** - Web server scanner
  ```bash
  nikto -h your-app.com
  ```

### **Professional Audit**

For production systems handling sensitive data:
- [ ] Schedule professional penetration test
- [ ] Address all findings before launch
- [ ] Annual security audits

---

## 📊 **Compliance & Standards**

### **GDPR (if applicable)**

- [ ] Privacy policy published
- [ ] User consent for data collection
- [ ] Right to access data (export feature)
- [ ] Right to deletion (hard delete option)
- [ ] Data breach notification plan
- [ ] Data retention policy

### **SOC 2 (if applicable)**

- [ ] Security policies documented
- [ ] Access controls implemented
- [ ] Audit logging enabled
- [ ] Incident response plan
- [ ] Regular security training

---

## 🚨 **Incident Response Plan**

### **Preparation**

- [ ] Incident response team identified
- [ ] Contact list maintained
- [ ] Escalation procedures documented
- [ ] Communication templates prepared

### **Detection & Analysis**

- [ ] Monitoring alerts configured
- [ ] Log analysis procedures
- [ ] Severity classification defined

### **Containment & Recovery**

- [ ] Isolation procedures
- [ ] Backup restoration tested
- [ ] Rollback procedures documented
- [ ] Password reset mass-invalidation plan

### **Post-Incident**

- [ ] Root cause analysis template
- [ ] Lessons learned process
- [ ] Security improvements implemented

---

## 📝 **Documentation**

- [ ] **Security policies documented**
- [ ] **Deployment runbook created**
- [ ] **Disaster recovery plan**
- [ ] **Contact information for security team**
- [ ] **Change management process**
- [ ] **Password reset process documented**

---

## ✅ **Final Verification**

Before going live:

```bash
# 1. Run all tests
pytest

# 2. Security scan
bandit -r app/
safety check
pip-audit

# 3. Check secrets
git secrets --scan

# 4. Verify environment
printenv | grep -i "secret\|password\|key\|smtp"

# 5. Test backup restoration
# (Restore to staging and verify)

# 6. Test password reset flow
# Request reset → check email → reset password → verify login

# 7. Load testing
# Use tools like Apache Bench, Locust, or K6

# 8. Verify monitoring
# Check dashboards, test alerts
```

---

## 📞 **Security Contacts**

- **Security Team**: security@yourdomain.com
- **Responsible Disclosure**: security-report@yourdomain.com
- **Emergency Contact**: +1-xxx-xxx-xxxx

---

**Security Checklist Version**: 2.0.0  
**Last Updated**: 2026-02-05  
**Next Review**: 2026-05-05 (quarterly)  
**Status**: Production Ready ✅

**Changelog v2.0:**
- Added Password Reset security section
- Added SMTP/Email configuration
- Updated audit log actions
- Added email-related security checks
- Updated OWASP A07 with reset token security
- Added CORS hardcoding warning
