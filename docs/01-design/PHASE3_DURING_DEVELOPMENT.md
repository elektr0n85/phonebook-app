# FAZA 3: DURING DEVELOPMENT
## Projekt: Książka Telefoniczna (Phonebook Application)

---

## 3.1 CODE WALKTHROUGH

### 3.1.1 Purpose
Code walkthrough to wysokopoziomowy przegląd kodu, podczas którego deweloperzy:
- Wyjaśniają logikę i flow kodu
- Pokazują strukturę aplikacji
- Tłumaczą decyzje architektoniczne
- Identyfikują potencjalne security hotspots

### 3.1.2 Project Structure

```
phonebook-app/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── config.py          # Configuration & environment variables
│   │   ├── database.py        # Database connection & session
│   │   │
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── contact.py
│   │   │   ├── audit_log.py
│   │   │   └── password_reset.py
│   │   │
│   │   ├── schemas/           # Pydantic schemas (validation)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── contact.py
│   │   │   ├── auth.py
│   │   │   └── common.py
│   │   │
│   │   ├── api/               # API routes
│   │   │   ├── __init__.py
│   │   │   ├── deps.py        # Dependencies (auth, db session)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py    # /api/v1/auth/*
│   │   │       ├── users.py   # /api/v1/users/*
│   │   │       ├── contacts.py # /api/v1/contacts/*
│   │   │       └── admin.py   # /api/v1/admin/*
│   │   │
│   │   ├── core/              # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── security.py    # JWT, password hashing
│   │   │   ├── config.py      # Settings management
│   │   │   └── rate_limit.py  # Rate limiting
│   │   │
│   │   ├── crud/              # Database operations
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # Base CRUD class
│   │   │   ├── user.py
│   │   │   ├── contact.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── middleware/        # Custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── security_headers.py
│   │   │   ├── audit_logging.py
│   │   │   └── rate_limiting.py
│   │   │
│   │   └── tests/             # Tests
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_auth.py
│   │       ├── test_contacts.py
│   │       └── test_security.py
│   │
│   ├── alembic/               # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── pytest.ini            # Pytest configuration
│   └── README.md
│
├── frontend/                  # React Frontend
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Auth/
│   │   │   │   ├── Login.jsx
│   │   │   │   ├── Register.jsx
│   │   │   │   └── PasswordReset.jsx
│   │   │   │
│   │   │   ├── Contacts/
│   │   │   │   ├── ContactList.jsx
│   │   │   │   ├── ContactForm.jsx
│   │   │   │   ├── ContactCard.jsx
│   │   │   │   └── ContactSearch.jsx
│   │   │   │
│   │   │   ├── Layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   └── Navigation.jsx
│   │   │   │
│   │   │   └── Common/
│   │   │       ├── Button.jsx
│   │   │       ├── Input.jsx
│   │   │       └── Modal.jsx
│   │   │
│   │   ├── pages/            # Page components
│   │   │   ├── HomePage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── ContactsPage.jsx
│   │   │   └── AdminPage.jsx
│   │   │
│   │   ├── services/         # API services
│   │   │   ├── api.js        # Axios configuration
│   │   │   ├── authService.js
│   │   │   └── contactService.js
│   │   │
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useAuth.js
│   │   │   └── useContacts.js
│   │   │
│   │   ├── context/          # React Context
│   │   │   └── AuthContext.jsx
│   │   │
│   │   ├── utils/            # Utilities
│   │   │   ├── validation.js
│   │   │   └── helpers.js
│   │   │
│   │   ├── App.jsx
│   │   ├── index.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── .env.example
│   └── README.md
│
├── database/                  # Database scripts
│   ├── init.sql              # Initial schema
│   └── seed.sql              # Sample data
│
└── docs/                      # Documentation
    ├── 01_PHASE1_BEFORE_DEVELOPMENT.md
    ├── 02_PHASE2_DEFINITION_AND_DESIGN.md
    ├── 03_PHASE3_DURING_DEVELOPMENT.md
    ├── API_DOCUMENTATION.md
    └── DEPLOYMENT_GUIDE.md
```

### 3.1.3 Key Security Design Decisions

#### **1. Authentication Flow**
```python
# JWT token with short expiry (30 minutes)
# Refresh token with longer expiry (7 days)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

**Rationale**: Short-lived access tokens minimize damage from token theft. Refresh tokens allow seamless UX while maintaining security.

#### **2. Password Hashing**
```python
# bcrypt with cost factor 12
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # bcrypt rounds=12 by default
```

**Rationale**: bcrypt is slow by design (prevents brute force), automatically salts passwords, and has configurable cost factor for future-proofing.

#### **3. SQL Injection Prevention**
```python
# SQLAlchemy ORM - automatic parameterization
from sqlalchemy import select

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# NEVER concatenate SQL strings!
# BAD: f"SELECT * FROM users WHERE email = '{email}'"
```

**Rationale**: ORM prevents SQL injection by using parameterized queries. Even if attacker sends `' OR '1'='1`, it's treated as literal string.

#### **4. Authorization Pattern**
```python
# Dependency injection for user authentication
from fastapi import Depends

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify JWT token
    # Return user object or raise 401
    ...

async def get_current_active_user(user: User = Depends(get_current_user)):
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

# Use in routes
@router.get("/contacts")
async def get_contacts(current_user: User = Depends(get_current_active_user)):
    # Only returns contacts owned by current_user
    ...
```

**Rationale**: Dependency injection ensures every protected route validates authentication. Separation of concerns (auth vs business logic).

#### **5. Input Validation Pattern**
```python
# Pydantic automatic validation
from pydantic import BaseModel, EmailStr, Field, validator

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r'^\+?[0-9]{9,15}$')
    email: EmailStr | None = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

# FastAPI automatically validates against schema
@router.post("/contacts")
async def create_contact(contact: ContactCreate, ...):
    # If we get here, contact is valid!
    ...
```

**Rationale**: Validation happens before business logic. Fail fast. Type safety. Automatic API documentation.

---

## 3.2 CODE REVIEWS

### 3.2.1 Security Code Review Checklist

#### **A. Authentication & Session Management**
- [ ] Passwords hashed with bcrypt (cost ≥ 12)
- [ ] JWT tokens have expiration (≤ 30 min)
- [ ] No hardcoded credentials in code
- [ ] Session timeout implemented (30 min inactivity)
- [ ] Account lockout after failed attempts (5 tries)
- [ ] Logout invalidates tokens
- [ ] Password reset tokens single-use & time-limited

#### **B. Authorization & Access Control**
- [ ] All protected routes require authentication
- [ ] Authorization checks on every resource access
- [ ] Users can only access own data
- [ ] Admin role checked server-side (not client-side)
- [ ] No insecure direct object references (IDOR)
- [ ] 404 instead of 403 for unauthorized access (prevents enumeration)

#### **C. Input Validation**
- [ ] All inputs validated server-side (Pydantic schemas)
- [ ] Whitelist validation (not blacklist)
- [ ] Length limits enforced
- [ ] Email format validated
- [ ] Phone number format validated
- [ ] No special characters allowed where not needed
- [ ] Sanitization before database insert

#### **D. SQL Injection Prevention**
- [ ] SQLAlchemy ORM used (no raw SQL)
- [ ] All queries use parameterized statements
- [ ] No string concatenation in queries
- [ ] No user input directly in SQL
- [ ] Database user has minimum privileges

#### **E. XSS Prevention**
- [ ] React auto-escaping used
- [ ] No dangerouslySetInnerHTML without sanitization
- [ ] CSP headers configured
- [ ] User-generated content sanitized
- [ ] JSON responses (not HTML from API)

#### **F. CSRF Protection**
- [ ] SameSite=Strict on cookies
- [ ] CSRF tokens for state-changing operations
- [ ] Origin validation
- [ ] No GET for state changes

#### **G. Cryptography**
- [ ] HTTPS enforced in production
- [ ] TLS 1.3 preferred
- [ ] No weak ciphers
- [ ] Secrets stored in environment variables
- [ ] No encryption keys in code

#### **H. Error Handling & Logging**
- [ ] Generic error messages to users
- [ ] No stack traces in production
- [ ] Sensitive data not logged (passwords, tokens)
- [ ] All security events logged (audit log)
- [ ] Logs include timestamp, user ID, action, IP

#### **I. Rate Limiting**
- [ ] Login endpoint rate limited (5/15min)
- [ ] API endpoints rate limited (100/min)
- [ ] Registration rate limited (3/hour)
- [ ] Password reset rate limited (3/hour)

#### **J. Dependencies**
- [ ] All dependencies up-to-date
- [ ] No known vulnerabilities (pip-audit)
- [ ] Minimal dependencies (reduce attack surface)
- [ ] Dependencies from trusted sources

### 3.2.2 OWASP Top 10 (2021) Coverage

| OWASP Top 10 | Mitigation in Code | Verification |
|--------------|-------------------|--------------|
| **A01:2021 – Broken Access Control** | - JWT authentication<br>- Ownership checks in CRUD<br>- RBAC implementation | ✅ Unit tests<br>✅ Integration tests |
| **A02:2021 – Cryptographic Failures** | - bcrypt for passwords<br>- HTTPS enforcement<br>- Secure session management | ✅ Config review<br>✅ Penetration test |
| **A03:2021 – Injection** | - SQLAlchemy ORM<br>- Pydantic validation<br>- No raw SQL | ✅ Code review<br>✅ SQLi tests |
| **A04:2021 – Insecure Design** | - Threat modeling done<br>- Security requirements<br>- Defense in depth | ✅ Architecture review |
| **A05:2021 – Security Misconfiguration** | - Security headers<br>- CORS whitelist<br>- Default deny | ✅ Config audit<br>✅ ZAP scan |
| **A06:2021 – Vulnerable Components** | - pip-audit<br>- Regular updates<br>- Minimal dependencies | ✅ Dependency scan |
| **A07:2021 – Authentication Failures** | - Strong password policy<br>- Account lockout<br>- MFA ready | ✅ Auth tests |
| **A08:2021 – Software & Data Integrity** | - Input validation<br>- Audit logging<br>- Database constraints | ✅ Integrity tests |
| **A09:2021 – Logging Failures** | - Comprehensive audit log<br>- No sensitive data logged<br>- Tamper-proof logs | ✅ Log review |
| **A10:2021 – SSRF** | - No user-controlled URLs<br>- Whitelist external services | ✅ SSRF tests |

### 3.2.3 Specific Code Review Focus Areas

#### **1. Password Handling**
```python
# ✅ CORRECT
class User(Base):
    password_hash: Mapped[str] = mapped_column(String(255))
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

# ❌ WRONG - Never store plain passwords
class User(Base):
    password: Mapped[str]  # NEVER!
```

#### **2. JWT Secret Management**
```python
# ✅ CORRECT
from app.core.config import settings

SECRET_KEY = settings.secret_key  # From environment variable

# ❌ WRONG - Hardcoded secret
SECRET_KEY = "my-secret-key-12345"  # NEVER!
```

#### **3. SQL Queries**
```python
# ✅ CORRECT - ORM
stmt = select(Contact).where(Contact.user_id == user_id)
result = await db.execute(stmt)

# ❌ WRONG - String concatenation
query = f"SELECT * FROM contacts WHERE user_id = {user_id}"  # SQL INJECTION!
```

#### **4. Authorization Checks**
```python
# ✅ CORRECT - Ownership verification
async def get_contact(contact_id: int, current_user: User, db: AsyncSession):
    contact = await crud.contact.get(db, id=contact_id)
    if not contact:
        raise HTTPException(status_code=404)
    if contact.user_id != current_user.id:
        raise HTTPException(status_code=404)  # Not 403!
    return contact

# ❌ WRONG - No ownership check
async def get_contact(contact_id: int, db: AsyncSession):
    return await crud.contact.get(db, id=contact_id)  # Anyone can access!
```

#### **5. Error Messages**
```python
# ✅ CORRECT - Generic message
raise HTTPException(status_code=401, detail="Invalid credentials")

# ❌ WRONG - Information disclosure
raise HTTPException(status_code=401, detail="User not found")  # User enumeration!
raise HTTPException(status_code=401, detail="Wrong password")  # User enumeration!
```

### 3.2.4 Static Analysis Tools

#### **A. Bandit (Python Security Linter)**
```bash
# Run Bandit security checks
bandit -r app/ -ll

# Expected output: No issues
# Any findings should be reviewed and fixed
```

#### **B. mypy (Type Checking)**
```bash
# Run type checking
mypy app/

# Catches type-related bugs that could lead to security issues
```

#### **C. pylint (Code Quality)**
```bash
# Run linting
pylint app/

# Enforces coding standards, catches potential bugs
```

#### **D. pip-audit (Dependency Scanning)**
```bash
# Check for vulnerable dependencies
pip-audit

# Update any vulnerable packages
pip install --upgrade <package>
```

### 3.2.5 Manual Security Review Points

When reviewing code, look for:

1. **Authentication bypass opportunities**
   - Can JWT be missing/invalid but still work?
   - Can expired tokens still authenticate?
   
2. **Authorization flaws**
   - Can user A access user B's contacts?
   - Can regular user access admin endpoints?
   
3. **Input validation gaps**
   - What happens with empty strings?
   - What happens with very long strings?
   - What happens with special characters?
   
4. **Race conditions**
   - Can account lockout be bypassed with parallel requests?
   - Can same email be registered twice?
   
5. **Information leakage**
   - Do error messages reveal too much?
   - Are stack traces visible?
   - Do timing attacks reveal user existence?

---

## 3.3 SECURITY TESTING STRATEGY

### 3.3.1 Unit Tests (Security-focused)

```python
# Test password hashing
def test_password_hashing():
    password = "SecurePassword123!"
    hashed = hash_password(password)
    
    assert hashed != password  # Not stored plain
    assert verify_password(password, hashed)  # Can verify
    assert not verify_password("wrong", hashed)  # Wrong password fails

# Test JWT expiration
def test_jwt_expiration():
    token = create_access_token({"sub": "user@example.com"}, 
                                 expires_delta=timedelta(seconds=-1))
    with pytest.raises(JWTError):
        decode_token(token)  # Expired token raises error

# Test authorization
def test_cannot_access_other_user_contacts(client, normal_user_token):
    # Create contact as user A
    response = client.post("/api/v1/contacts", 
                          json={"name": "Test"},
                          headers={"Authorization": f"Bearer {normal_user_token}"})
    contact_id = response.json()["id"]
    
    # Try to access as user B
    other_user_token = create_user_and_login(client, "other@example.com")
    response = client.get(f"/api/v1/contacts/{contact_id}",
                         headers={"Authorization": f"Bearer {other_user_token}"})
    
    assert response.status_code == 404  # Not 403!
```

### 3.3.2 Integration Tests

```python
# Test rate limiting
def test_login_rate_limiting(client):
    for i in range(6):  # 6 attempts (limit is 5)
        response = client.post("/api/v1/auth/login",
                              json={"email": "test@example.com", 
                                   "password": "wrong"})
    
    assert response.status_code == 429  # Too many requests

# Test account lockout
def test_account_lockout(client):
    # Register user
    client.post("/api/v1/auth/register", 
                json={"email": "test@example.com", "password": "Pass123!"})
    
    # 5 failed login attempts
    for i in range(5):
        client.post("/api/v1/auth/login",
                   json={"email": "test@example.com", "password": "wrong"})
    
    # 6th attempt should fail even with correct password
    response = client.post("/api/v1/auth/login",
                          json={"email": "test@example.com", "password": "Pass123!"})
    
    assert response.status_code == 403
    assert "locked" in response.json()["detail"].lower()
```

### 3.3.3 Security Test Cases

| Test ID | Test Case | Expected Result | Status |
|---------|-----------|-----------------|--------|
| SEC-001 | SQL injection in login | No SQLi, query fails safely | ⏳ |
| SEC-002 | XSS in contact name | Input escaped, no script execution | ⏳ |
| SEC-003 | CSRF attack on create contact | Request rejected without token | ⏳ |
| SEC-004 | JWT token tampering | Token rejected, 401 error | ⏳ |
| SEC-005 | Expired JWT token | Token rejected, 401 error | ⏳ |
| SEC-006 | Access other user's contact | 404 error, no data returned | ⏳ |
| SEC-007 | Weak password registration | Registration rejected | ⏳ |
| SEC-008 | Brute force login | Account locked after 5 attempts | ⏳ |
| SEC-009 | API rate limiting | 429 error after limit exceeded | ⏳ |
| SEC-010 | Password in audit log | Logs contain no passwords | ⏳ |

---

## ✅ PHASE 3 COMPLETION CHECKLIST

### **Development**
- [ ] Backend structure created
- [ ] Models implemented (User, Contact, AuditLog, PasswordResetToken)
- [ ] Schemas implemented (Pydantic validation)
- [ ] CRUD operations implemented
- [ ] API routes implemented (auth, users, contacts, admin)
- [ ] Middleware implemented (security headers, rate limiting, audit logging)
- [ ] Database migrations created (Alembic)

### **Code Review**
- [ ] Authentication logic reviewed
- [ ] Authorization checks reviewed
- [ ] Input validation reviewed
- [ ] SQL injection prevention reviewed
- [ ] OWASP Top 10 compliance verified
- [ ] Security checklist completed
- [ ] Static analysis passed (Bandit, mypy)
- [ ] No hardcoded secrets

### **Testing**
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests written
- [ ] Security tests written
- [ ] All tests passing
- [ ] Manual testing completed

---

**Status**: ⏳ IN PROGRESS  
**Next**: Start implementation (Backend → Frontend → Integration)

**Document Version**: 1.0  
**Last Updated**: 2026-01-19  
**Next Review**: During code implementation
