# FAZA 1: PRZED ROZPOCZĘCIEM DEVELOPMENT
## Projekt: Książka Telefoniczna (Phonebook Application)

---

## 1.1 DEFINCJA SDLC

### 1.1.1 Wybrany Model SDLC
**Model**: Waterfall z elementami Agile  
**Uzasadnienie**: Projekt edukacyjny z jasno określonymi wymaganiami, ale z iteracyjnym podejściem do implementacji zabezpieczeń.

### 1.1.2 Fazy Projektu
1. **Planowanie i Wymagania** (Phase 1) - 1 tydzień
2. **Design i Architektura** (Phase 2) - 1 tydzień  
3. **Development** (Phase 3) - 2 tygodnie
4. **Deployment** (Phase 4) - 2 dni
5. **Maintenance** (Phase 5) - ciągły proces

### 1.1.3 Bezpieczeństwo w SDLC
Bezpieczeństwo jest zintegrowane na każdym etapie:
- **Planowanie**: Definicja wymagań bezpieczeństwa
- **Design**: Threat modeling, security architecture review
- **Development**: Secure coding practices, code reviews
- **Testing**: Security testing, penetration testing
- **Deployment**: Security configuration, hardening
- **Maintenance**: Security monitoring, patch management

---

## 1.2 PRZEGLĄD POLITYK I STANDARDÓW

### 1.2.1 Polityki Bezpieczeństwa

#### A. **Polityka Haseł**
- Minimalna długość: 8 znaków
- Wymagania:
  - Co najmniej 1 wielka litera
  - Co najmniej 1 mała litera  
  - Co najmniej 1 cyfra
  - Co najmniej 1 znak specjalny
- Hashowanie: bcrypt z salt (cost factor: 12)
- Historia haseł: Ostatnie 3 hasła nie mogą być ponownie użyte
- Wygasanie: Brak automatycznego wygasania (dla aplikacji edukacyjnej)
- Blokada konta: 5 nieudanych prób logowania = 15 minut blokady

#### B. **Polityka Sesji**
- Timeout sesji: 30 minut nieaktywności
- Absolute timeout: 8 godzin
- Session ID: Kryptograficznie bezpieczny, losowy (256-bit)
- Session fixation protection: Regeneracja ID po logowaniu
- Cookie security:
  - HttpOnly: true
  - Secure: true (production)
  - SameSite: Strict

#### C. **Polityka Dostępu do Danych**
- **Principle of Least Privilege**: Użytkownicy widzą tylko swoje kontakty
- **Role-Based Access Control (RBAC)**:
  - `USER`: Standardowy użytkownik (CRUD na własnych kontaktach)
  - `ADMIN`: Administrator (zarządzanie użytkownikami, przegląd logów)

#### D. **Polityka Walidacji Danych**
- **Wszystkie dane wejściowe są traktowane jako niebezpieczne**
- Walidacja po stronie klienta (UX) + serwera (bezpieczeństwo)
- Whitelist validation preferowana nad blacklist
- Sanityzacja przed zapisem do bazy danych
- Prepared statements dla wszystkich zapytań SQL

#### E. **Polityka Logowania i Audytu**
- Logowanie wszystkich zdarzeń bezpieczeństwa:
  - Logowania (udane i nieudane)
  - Zmiany haseł
  - Tworzenie/usuwanie kont
  - Modyfikacje danych
- Logi przechowywane przez 90 dni
- Logi nie zawierają wrażliwych danych (hasła, tokeny)

### 1.2.2 Standardy Kodowania

#### A. **FastAPI Security Standards**
```python
# 1. ENVIRONMENT VARIABLES
# Nigdy nie hardcode credentials
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

# 2. INPUT VALIDATION
# Pydantic automatic validation
from pydantic import BaseModel, Field, EmailStr, constr

class ContactCreate(BaseModel):
    name: constr(min_length=1, max_length=100)
    phone: constr(pattern=r'^\+?[0-9]{9,15}$')
    email: EmailStr

# 3. SQL INJECTION PREVENTION  
# SQLAlchemy ORM - automatic parameterization
from sqlalchemy import select
stmt = select(User).where(User.email == email)
result = await session.execute(stmt)

# 4. XSS PREVENTION
# FastAPI automatic JSON encoding (safe by default)
# For HTML: use bleach for sanitization
import bleach
clean_text = bleach.clean(user_input)

# 5. SECURITY HEADERS
# Use fastapi-security or middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# 6. RATE LIMITING
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/contacts")
@limiter.limit("5/minute")
async def get_contacts(request: Request):
    pass
```

#### B. **React Security Standards**
```javascript
// 1. XSS PREVENTION
// React automatycznie escapuje, ale:
dangerouslySetInnerHTML // NIGDY nie używaj bez sanityzacji

// 2. SECURE STATE MANAGEMENT  
// Nie przechowuj wrażliwych danych w localStorage
// Używaj httpOnly cookies dla tokenów

// 3. API CALLS
// Zawsze używaj HTTPS
// Zawsze dołączaj CSRF token

// 4. DEPENDENCY MANAGEMENT
// Regularnie aktualizuj zależności
npm audit fix
```

#### C. **PostgreSQL Security Standards**
```sql
-- 1. PRINCIPLE OF LEAST PRIVILEGE
-- Dedykowany user dla aplikacji, nie superuser
CREATE USER phonebook_app WITH PASSWORD 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO phonebook_app;

-- 2. ROW LEVEL SECURITY (RLS)
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
CREATE POLICY contacts_isolation ON contacts
    USING (user_id = current_setting('app.current_user_id')::int);

-- 3. ENCRYPTION
-- Szyfrowanie na poziomie kolumny dla wrażliwych danych
```

### 1.2.3 Compliance Requirements

Aplikacja musi być zgodna z:
- **OWASP Top 10** (2021)
- **OWASP ASVS** (Application Security Verification Standard) - Level 2
- **GDPR** (dla danych osobowych):
  - Prawo do usunięcia danych
  - Prawo do eksportu danych  
  - Szyfrowanie danych w transit i at rest

---

## 1.3 METRYKI I KRYTERIA POMIARU

### 1.3.1 Metryki Bezpieczeństwa

#### A. **Code Security Metrics**
| Metryka | Target | Pomiar |
|---------|--------|--------|
| Code coverage (testy) | >80% | Jest/Coverage |
| Security test coverage | >90% | Manual review |
| Critical vulnerabilities | 0 | npm audit, Snyk |
| High vulnerabilities | 0 | npm audit, Snyk |
| Medium vulnerabilities | <5 | npm audit, Snyk |
| SAST findings (critical) | 0 | SonarQube |

#### B. **Runtime Security Metrics**
| Metryka | Target | Monitoring |
|---------|--------|------------|
| Failed login attempts | <100/day | Application logs |
| Account lockouts | <10/day | Application logs |
| 5xx errors | <1% | Server logs |
| Average response time | <200ms | APM tools |

#### C. **Compliance Metrics**
| Wymaganie | Status | Weryfikacja |
|-----------|--------|-------------|
| OWASP Top 10 compliance | 100% | Penetration test |
| Input validation coverage | 100% | Code review |
| Authentication enforcement | 100% | Automated tests |
| Authorization checks | 100% | Automated tests |

### 1.3.2 Kryteria Akceptacji

#### Security Gates (muszą być spełnione przed deployment):
✅ 0 critical/high vulnerabilities  
✅ Code review completed  
✅ All security tests passing  
✅ Penetration testing completed  
✅ No secrets in code repository  
✅ HTTPS enforced  
✅ Security headers configured  
✅ Input validation implemented  
✅ SQL injection prevention verified  
✅ XSS prevention verified  

### 1.3.3 Traceability Matrix

| Wymaganie Bezpieczeństwa | Test Case | Status |
|--------------------------|-----------|--------|
| REQ-SEC-001: Silne hasła | TC-AUTH-001 | ⏳ |
| REQ-SEC-002: Session management | TC-AUTH-002 | ⏳ |
| REQ-SEC-003: Input validation | TC-VAL-001 | ⏳ |
| REQ-SEC-004: SQL injection protection | TC-SQL-001 | ⏳ |
| REQ-SEC-005: XSS protection | TC-XSS-001 | ⏳ |
| REQ-SEC-006: CSRF protection | TC-CSRF-001 | ⏳ |
| REQ-SEC-007: Authentication | TC-AUTH-003 | ⏳ |
| REQ-SEC-008: Authorization | TC-AUTHZ-001 | ⏳ |
| REQ-SEC-009: Secure communication | TC-TLS-001 | ⏳ |
| REQ-SEC-010: Error handling | TC-ERR-001 | ⏳ |

---

## 1.4 DOKUMENTACJA

### 1.4.1 Wymagane Dokumenty
- [x] Security Policy Document (ten dokument)
- [ ] System Architecture Document
- [ ] Threat Model Document  
- [ ] API Security Specification
- [ ] Database Security Specification
- [ ] Deployment Security Checklist
- [ ] Incident Response Plan

### 1.4.2 Code Documentation Standards
- JSDoc dla funkcji JavaScript
- README.md dla każdego modułu
- Inline comments dla złożonej logiki
- Security annotations dla krytycznych sekcji

---

## 1.5 TOOLING

### 1.5.1 Development Tools
- **IDE**: VS Code / PyCharm
- **Version Control**: Git + GitHub
- **Package Manager**: pip + poetry (dependency management)
- **Python Version**: 3.11+ (for best FastAPI performance)

### 1.5.2 Security Tools
- **SAST**: Bandit (Python security linter)
- **Dependency Scanning**: pip-audit, Safety
- **Secrets Detection**: detect-secrets, git-secrets
- **Code Quality**: pylint, mypy (type checking)
- **Linting**: ruff (fast Python linter)

### 1.5.3 Testing Tools
- **Unit Tests**: Jest
- **Integration Tests**: Supertest
- **E2E Tests**: Playwright
- **Security Tests**: OWASP ZAP, Burp Suite

---

## ✅ PHASE 1 COMPLETION CHECKLIST

- [x] SDLC model defined
- [x] Security policies documented
- [x] Coding standards established
- [x] Compliance requirements identified
- [x] Metrics and criteria defined
- [x] Traceability matrix created
- [x] Documentation structure defined
- [x] Tooling identified

**Status**: ✅ PHASE 1 COMPLETE - Ready to proceed to Phase 2 (Design)

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-19  
**Next Review**: Before Phase 2 kickoff
