# 📞 Phonebook Application - Full Stack

Production-ready, OWASP-compliant phonebook application with comprehensive testing and deployment automation.

[![CI/CD](https://github.com/yourusername/phonebook-app/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/yourusername/phonebook-app/actions)
[![Coverage](https://codecov.io/gh/yourusername/phonebook-app/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/phonebook-app)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🚀 **Quick Start**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/phonebook-app.git
cd phonebook-app

# 2. Setup environment
cp .env.example .env
# Edit .env with your configuration

# 3. Start with Docker
docker-compose up -d

# 4. Access application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Or use Make:**
```bash
make start        # Start all services
make test         # Run tests
make security-scan # Security scan
make logs         # View logs
```

---

## 📊 **Project Overview**

### **Tech Stack**

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL 15
- SQLAlchemy 2.0 (async)
- Pydantic 2.0
- JWT Authentication
- Pytest (50+ tests)

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios

**Infrastructure:**
- Docker & Docker Compose
- Nginx
- GitHub Actions (CI/CD)
- Prometheus & Grafana (monitoring)

### **Features**

✅ **User Management**
- Registration with password strength validation
- JWT-based authentication
- Account lockout (brute force protection)
- Role-based access control (User/Admin)

✅ **Contact Management**
- Full CRUD operations
- Multiple phone numbers per contact (N:M relationship)
- 3 phone types: Mobile, Landline, Internal
- Search by name/email/company
- Soft delete (data recovery)

✅ **Security**
- OWASP Top 10 compliance
- bcrypt password hashing (cost=12)
- SQL injection prevention (ORM)
- XSS prevention
- CSRF protection
- Security headers (CSP, HSTS, etc.)
- Comprehensive audit logging
- 50+ security tests

✅ **Testing**
- 50+ automated tests
- 90%+ code coverage
- Unit, integration, security tests
- CI/CD integration

✅ **Deployment**
- Docker containerization
- Production-ready configuration
- Monitoring & logging
- Automated backups
- Health checks

---

## 📁 **Project Structure**

```
phonebook-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── crud/           # Database operations
│   │   ├── api/v1/         # API endpoints
│   │   └── core/           # Security, config
│   ├── tests/              # 50+ tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── security/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API integration
│   │   ├── context/        # State management
│   │   └── utils/          # Utilities
│   ├── Dockerfile
│   └── package.json
│
├── docs/                   # Documentation
│   ├── 01_PHASE1_BEFORE_DEVELOPMENT.md
│   ├── 02_PHASE2_DEFINITION_AND_DESIGN.md
│   └── 03_PHASE3_DURING_DEVELOPMENT.md
│
├── .github/workflows/      # CI/CD
│   └── ci-cd.yml
│
├── docker-compose.yml      # Docker orchestration
├── DEPLOYMENT.md           # Deployment guide
├── SECURITY_CHECKLIST.md   # Security checklist
├── MONITORING.md           # Monitoring guide
├── Makefile                # Convenient commands
└── README.md               # This file
```

---

## 🔧 **Development**

### **Prerequisites**

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (recommended)

### **Local Development (Without Docker)**

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup database
createdb phonebook_db

# Configure .env
cp .env.example .env
# Edit DATABASE_URL, SECRET_KEY

# Initialize database
python init_db.py

# Start server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install

# Configure .env
cp .env.example .env

# Start dev server
npm run dev
```

### **With Docker (Recommended)**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run tests in container
docker-compose exec backend pytest
```

---

## 🧪 **Testing**

### **Backend Tests** (50+ tests)

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# By category
pytest -m unit        # Unit tests
pytest -m integration # Integration tests
pytest -m security    # Security tests

# Specific test
pytest tests/unit/test_user_model.py::TestUserModel::test_set_password_hashes_password
```

**Coverage Report:**
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### **Security Tests**

Based on **OWASP Top 10 2021**:
- ✅ A01: Broken Access Control
- ✅ A02: Cryptographic Failures
- ✅ A03: Injection
- ✅ A07: Authentication Failures
- ✅ CSRF, XSS, SQL Injection

```bash
# Run security tests
pytest -m security -v

# Security scanning
bandit -r app/
safety check
```

See [backend/tests/README.md](backend/tests/README.md) for detailed testing guide.

---

## 🚀 **Deployment**

### **Docker (Production)**

```bash
# 1. Setup environment
cp .env.example .env
# Generate secrets:
#   SECRET_KEY: openssl rand -hex 32
#   POSTGRES_PASSWORD: openssl rand -base64 32

# 2. Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Verify
make prod-status
```

### **Cloud Platforms**

**AWS:**
- EC2 + Docker
- ECS Fargate
- Elastic Beanstalk

**Heroku:**
```bash
heroku create phonebook-app
heroku addons:create heroku-postgresql:mini
git push heroku main
```

**Railway:**
```bash
railway init
railway add postgresql
railway up
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide.

---

## 📊 **Monitoring**

### **Metrics**

- Application performance (response time, error rate)
- Infrastructure (CPU, memory, disk)
- Business metrics (users, API usage)

### **Tools**

- **Prometheus + Grafana** (metrics)
- **Sentry** (error tracking)
- **ELK Stack** (log aggregation)
- **UptimeRobot** (uptime monitoring)

See [MONITORING.md](MONITORING.md) for monitoring setup.

---

## 🔒 **Security**

### **Features**

- JWT authentication (30 min access, 7 day refresh)
- bcrypt password hashing (cost=12)
- Account lockout (5 attempts = 15 min)
- SQL injection prevention (ORM)
- XSS prevention (React auto-escape + CSP)
- CSRF protection (SameSite cookies)
- Security headers (HSTS, CSP, etc.)
- Comprehensive audit logging

### **Pre-Deployment Checklist**

See [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) for complete checklist.

**Critical:**
- [ ] Change SECRET_KEY
- [ ] Use strong DB password
- [ ] Enable HTTPS
- [ ] Configure CORS
- [ ] Set DEBUG=False
- [ ] Run security tests

---

## 📚 **Documentation**

- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide (AWS, Heroku, Railway, Docker)
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Security checklist (OWASP compliance)
- [MONITORING.md](MONITORING.md) - Monitoring & maintenance guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Project summary
- [backend/README.md](backend/README.md) - Backend documentation
- [frontend/README.md](frontend/README.md) - Frontend documentation
- [backend/tests/README.md](backend/tests/README.md) - Testing guide

**OWASP Documentation:**
- [docs/01_PHASE1_BEFORE_DEVELOPMENT.md](docs/01_PHASE1_BEFORE_DEVELOPMENT.md)
- [docs/02_PHASE2_DEFINITION_AND_DESIGN.md](docs/02_PHASE2_DEFINITION_AND_DESIGN.md)
- [docs/03_PHASE3_DURING_DEVELOPMENT.md](docs/03_PHASE3_DURING_DEVELOPMENT.md)

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Before submitting:**
```bash
make ci  # Runs tests, lint, security scan
```

---

## 📄 **License**

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👥 **Authors**

- **Your Name** - *Initial work* - [yourusername](https://github.com/yourusername)

---

## 🙏 **Acknowledgments**

- OWASP Testing Guide
- FastAPI documentation
- React documentation
- Claude (Anthropic) for assistance

---

## 📊 **Project Stats**

- **Total Files**: 70+ files
- **Total Lines**: ~7,500 lines
- **Tests**: 50+ tests
- **Coverage**: 90%+
- **API Endpoints**: 18 endpoints
- **Database Tables**: 6 tables
- **Security Features**: 15+ features
- **Status**: ✅ Production Ready

---

## 🔗 **Links**

- **Live Demo**: https://phonebook-app-demo.example.com
- **API Docs**: https://phonebook-app-demo.example.com/docs
- **GitHub**: https://github.com/yourusername/phonebook-app
- **Issues**: https://github.com/yourusername/phonebook-app/issues

---

**Built with ❤️ using FastAPI + React**

**Version**: 1.0.0  
**Last Updated**: 2026-01-20  
**Status**: Production Ready ✅
