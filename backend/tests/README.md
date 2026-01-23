# Backend Testing Guide

## 🧪 **Test Suite Complete!**

Comprehensive test coverage for the Phonebook API backend.

---

## 📊 **Test Structure**

```
tests/
├── conftest.py              # Pytest fixtures (DB, client, users)
├── unit/                    # Unit tests (models, utilities)
│   ├── test_user_model.py   # User model tests
│   ├── test_contact_model.py# Contact model tests
│   └── test_phone_model.py  # Phone model tests
├── integration/             # API endpoint tests
│   ├── test_auth_endpoints.py    # Authentication flow
│   └── test_contact_endpoints.py # CRUD operations
└── security/                # OWASP security tests
    └── test_owasp.py        # OWASP Top 10 coverage
```

---

## 🚀 **Quick Start**

### **1. Install Test Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Run All Tests**
```bash
pytest
```

### **3. Run with Coverage**
```bash
pytest --cov=app --cov-report=html
# View coverage: open htmlcov/index.html
```

---

## 📋 **Test Categories**

### **Unit Tests** (`tests/unit/`)
Fast, isolated tests for models and utilities.

```bash
# Run only unit tests
pytest -m unit

# Run specific test file
pytest tests/unit/test_user_model.py

# Run specific test
pytest tests/unit/test_user_model.py::TestUserModel::test_set_password_hashes_password
```

**Coverage:**
- ✅ User model (password hashing, lockout, roles)
- ✅ Contact model (soft delete, restore)
- ✅ Phone model (normalization, formatting)

---

### **Integration Tests** (`tests/integration/`)
API endpoint tests with full HTTP client.

```bash
# Run only integration tests
pytest -m integration

# Run auth endpoint tests
pytest tests/integration/test_auth_endpoints.py

# Run contact endpoint tests
pytest tests/integration/test_contact_endpoints.py
```

**Coverage:**
- ✅ Authentication (register, login, logout, refresh)
- ✅ Contact CRUD (create, read, update, delete)
- ✅ Search functionality
- ✅ Authorization (ownership checks)
- ✅ Phone management

---

### **Security Tests** (`tests/security/`)
OWASP Top 10 security tests.

```bash
# Run only security tests
pytest -m security

# Run OWASP tests
pytest tests/security/test_owasp.py
```

**OWASP Coverage:**
- ✅ **A01: Broken Access Control**
  - Horizontal privilege escalation prevention
  - Vertical privilege escalation prevention
  - Missing authentication checks
  
- ✅ **A02: Cryptographic Failures**
  - Password hashing (bcrypt, cost=12)
  - Sensitive data in responses
  
- ✅ **A03: Injection**
  - SQL injection prevention
  - XSS in inputs
  
- ✅ **A07: Authentication Failures**
  - Weak password rejection
  - Account lockout (brute force protection)
  - Token expiration
  
- ✅ **Additional Security**
  - CSRF protection
  - Input validation
  - Email/phone format validation

---

## 📈 **Test Results**

### **Expected Coverage**
```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/__init__.py                       0      0   100%
app/core/__init__.py                  0      0   100%
app/core/config.py                   25      0   100%
app/core/security.py                 45      2    96%
app/crud/__init__.py                  5      0   100%
app/crud/base.py                     55      3    95%
app/crud/user.py                     85      5    94%
app/crud/contact.py                  75      4    95%
app/crud/phone.py                    60      3    95%
app/models/user.py                   50      0   100%
app/models/contact.py                30      0   100%
app/models/phone.py                  40      2    95%
app/api/v1/auth.py                  120      8    93%
app/api/v1/contacts.py              150     10    93%
-----------------------------------------------------
TOTAL                               740     37    95%
```

---

## 🔍 **Running Specific Test Types**

### **By Marker**
```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# Security tests only
pytest -m security

# Slow tests
pytest -m slow
```

### **By Pattern**
```bash
# All tests with "password" in name
pytest -k password

# All tests with "auth" in name
pytest -k auth

# All tests except slow ones
pytest -m "not slow"
```

### **Verbose Output**
```bash
# Show test names
pytest -v

# Show print statements
pytest -s

# Show locals on failure
pytest -l
```

---

## 🧹 **Test Database**

Tests use **in-memory SQLite** database:
- Fresh database for each test
- No cleanup needed
- Fast execution
- Isolated tests

**Configuration:**
```python
# tests/conftest.py
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

---

## 🔧 **Fixtures Available**

### **Database Fixtures**
- `db_session` - Test database session
- `client` - HTTP test client

### **User Fixtures**
- `test_user` - Regular user
- `test_admin` - Admin user
- `user_token` - JWT token for user
- `admin_token` - JWT token for admin

### **Data Fixtures**
- `test_contact` - Sample contact
- `test_phone` - Sample phone

### **Factory Fixtures**
- `user_factory(email)` - Create multiple users
- `contact_factory(name, email, company)` - Create multiple contacts

**Usage:**
```python
async def test_example(client, user_token, contact_factory):
    # Create test data
    contact1 = await contact_factory("Alice")
    contact2 = await contact_factory("Bob")
    
    # Make API call
    response = await client.get(
        "/api/v1/contacts/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
```

---

## 📊 **Coverage Report**

### **Generate HTML Coverage Report**
```bash
pytest --cov=app --cov-report=html
```

**View report:**
```bash
# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### **Terminal Coverage Report**
```bash
pytest --cov=app --cov-report=term-missing
```

### **Coverage Thresholds**
```bash
# Fail if coverage below 90%
pytest --cov=app --cov-fail-under=90
```

---

## 🐛 **Debugging Tests**

### **Run Single Test**
```bash
pytest tests/unit/test_user_model.py::TestUserModel::test_set_password_hashes_password -v
```

### **Drop into debugger on failure**
```bash
pytest --pdb
```

### **Show print statements**
```bash
pytest -s
```

### **Show full traceback**
```bash
pytest --tb=long
```

---

## ⚡ **Performance**

### **Parallel Execution** (optional)
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

### **Test Timing**
```bash
# Show slowest 10 tests
pytest --durations=10
```

---

## 📝 **Writing New Tests**

### **Unit Test Template**
```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    def test_something(self):
        """Test description."""
        # Arrange
        data = {"key": "value"}
        
        # Act
        result = process(data)
        
        # Assert
        assert result == expected
```

### **Integration Test Template**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
class TestMyEndpoint:
    async def test_create(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test creating resource."""
        response = await client.post(
            "/api/v1/resource/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Test"}
        )
        
        assert response.status_code == 201
```

### **Security Test Template**
```python
import pytest

@pytest.mark.security
class TestSecurity:
    async def test_injection(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test SQL injection prevention."""
        response = await client.get(
            "/api/v1/resource/?search=' OR 1=1--",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 0
```

---

## ✅ **Test Checklist**

Before committing code, ensure:
- [ ] All tests pass: `pytest`
- [ ] Coverage >90%: `pytest --cov=app --cov-fail-under=90`
- [ ] No security failures: `pytest -m security`
- [ ] Code formatted: `black app tests`
- [ ] Type checks pass: `mypy app`
- [ ] Security scan: `bandit -r app`

---

## 🔒 **Security Testing**

### **Static Analysis**
```bash
# Security issues
bandit -r app/

# Dependency vulnerabilities
safety check
```

### **Type Checking**
```bash
mypy app/
```

---

## 📚 **Additional Resources**

- [Pytest Documentation](https://docs.pytest.org/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Test Suite Version**: 1.0.0  
**Last Updated**: 2026-01-19  
**Total Tests**: 50+ tests  
**Coverage Target**: 90%+
