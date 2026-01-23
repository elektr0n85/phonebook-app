# 👋 START HERE - First Time Setup

## Witaj w Phonebook Application! 🚀

To jest **kompletna aplikacja full-stack** do zarządzania kontaktami z funkcjami:
- 📱 Wiele numerów telefonu per kontakt
- 🔐 Bezpieczna autentykacja (JWT + bcrypt)
- 🎨 Nowoczesny interfejs (React + Tailwind)
- ✅ 50+ testów bezpieczeństwa
- 🐳 Gotowy do deploy (Docker)

---

## 📁 Struktura projektu po rozpakowaniu:

```
phonebook-app/
├── 📄 START_HERE.md          ← TEN PLIK (czytasz go teraz!)
├── 📄 INSTALL.md             ← Szczegółowa instrukcja instalacji
├── 📄 README.md              ← Pełna dokumentacja projektu
├── 📄 QUICK_START.sh         ← Skrypt instalacyjny (Linux/Mac)
├── 📄 QUICK_START.bat        ← Skrypt instalacyjny (Windows)
├── 📄 docker-compose.yml     ← Docker konfiguracja
├── 📄 .env.example           ← Szablon zmiennych środowiskowych
│
├── 📂 backend/               ← Backend (FastAPI + Python)
│   ├── app/                  ← Kod aplikacji
│   ├── tests/                ← 50+ testów
│   ├── requirements.txt      ← Python dependencies
│   └── Dockerfile            ← Docker image backend
│
├── 📂 frontend/              ← Frontend (React + TypeScript)
│   ├── src/                  ← Kod aplikacji
│   ├── package.json          ← Node dependencies
│   └── Dockerfile            ← Docker image frontend
│
└── 📂 docs/                  ← Dokumentacja OWASP
```

---

## 🚀 Szybki Start (3 kroki)

### **Metoda 1: Automatyczny skrypt (NAJŁATWIEJ!)**

**Linux/macOS:**
```bash
chmod +x QUICK_START.sh
./QUICK_START.sh
```

**Windows:**
```cmd
QUICK_START.bat
```

Skrypt automatycznie:
- ✅ Sprawdzi Docker
- ✅ Wygeneruje bezpieczne hasła
- ✅ Zbuduje i uruchomi aplikację
- ✅ Wyświetli adresy URL

---

### **Metoda 2: Docker Compose (szybko, manualnie)**

```bash
# 1. Skopiuj plik środowiskowy
cp .env.example .env

# 2. Wygeneruj SECRET_KEY (WAŻNE!)
openssl rand -hex 32
# Skopiuj wynik i wklej do .env jako SECRET_KEY

# 3. Uruchom
docker-compose up -d --build

# 4. Sprawdź status
docker-compose ps
```

---

### **Metoda 3: Manualna instalacja (bez Docker)**

Zobacz szczegóły w [INSTALL.md](INSTALL.md)

Wymagania:
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

---

## 🌐 Dostęp do aplikacji

Po uruchomieniu:

| Serwis | URL | Opis |
|--------|-----|------|
| **Frontend** | http://localhost | Interfejs użytkownika |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger/OpenAPI docs |

---

## 🎯 Pierwsze kroki w aplikacji

1. **Otwórz przeglądarkę**: http://localhost

2. **Zarejestruj się**:
   - Kliknij "Register"
   - Email: `twoj@email.com`
   - Hasło: `SecurePass123!` (min. 8 znaków, wielka litera, cyfra, znak specjalny)

3. **Zaloguj się**:
   - Podaj email i hasło
   - Zostaniesz przekierowany do dashboardu

4. **Dodaj pierwszy kontakt**:
   - Kliknij "Add Contact"
   - Wypełnij: Imię, Email, Firma
   - Dodaj telefon: +48 123 456 789
   - Zapisz

5. **Eksploruj**:
   - Wyszukaj kontakt
   - Edytuj dane
   - Dodaj więcej numerów
   - Usuń kontakt

---

## 🔧 Komendy Docker

```bash
# Zobacz logi
docker-compose logs -f

# Restart aplikacji
docker-compose restart

# Zatrzymaj aplikację
docker-compose down

# Usuń wszystko (baza danych również!)
docker-compose down -v
```

---

## 📚 Dokumentacja

Po instalacji przeczytaj:

1. **README.md** - Pełna dokumentacja projektu
2. **INSTALL.md** - Szczegółowa instrukcja instalacji + troubleshooting
3. **DEPLOYMENT.md** - Jak wdrożyć na produkcję (AWS, Heroku, Railway)
4. **SECURITY_CHECKLIST.md** - Checklist bezpieczeństwa

Audyty OWASP:
- **OWASP_SECTION4_AUDIT.md** - 45 stron audytu bezpieczeństwa
- **SECURE_DESIGN_LIFECYCLE_AUDIT.md** - 30 stron analizy SDLC

---

## ❓ Problemy?

### **Port zajęty (8000 lub 80)**
```bash
# Sprawdź co używa portu
lsof -i :8000    # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Zabij proces lub zmień port w docker-compose.yml
```

### **Docker nie działa**
```bash
# Linux
sudo systemctl start docker

# Windows/Mac: Uruchom Docker Desktop
```

### **"Cannot connect to database"**
```bash
# Sprawdź czy wszystkie kontenery działają
docker-compose ps

# Sprawdź logi bazy danych
docker-compose logs db
```

### **Inne problemy**
Zobacz sekcję Troubleshooting w [INSTALL.md](INSTALL.md)

---

## 📊 Testy

Aplikacja ma **50+ automatycznych testów**:

```bash
# Uruchom testy w Docker
docker-compose exec backend pytest

# Lub lokalnie (w venv)
cd backend
source venv/bin/activate  # Linux/Mac
pytest
```

---

## 🎓 Technologie

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL 15
- SQLAlchemy 2.0 (async)
- JWT authentication
- bcrypt password hashing

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios

**DevOps:**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Nginx (production)

---

## 🔒 Bezpieczeństwo

Aplikacja implementuje:
- ✅ OWASP Top 10 best practices
- ✅ bcrypt hashing (cost=12)
- ✅ JWT tokens (30 min expiry)
- ✅ SQL injection prevention (ORM)
- ✅ XSS prevention (React auto-escape)
- ✅ Input validation (Pydantic)
- ✅ Audit logging
- ✅ Account lockout (brute force protection)

**Znane ograniczenia** (przed produkcją napraw):
- 🔴 Brak rate limiting
- 🔴 JWT stateless (nie można revoke)
- 🔴 Brak email verification

Zobacz pełny audyt: [OWASP_SECTION4_AUDIT.md](OWASP_SECTION4_AUDIT.md)

---

## 🚀 Deploy na produkcję

Gotowy do uruchomienia na:
- **Docker** (localhost, VPS)
- **Railway** (najłatwiejszy!)
- **Heroku**
- **AWS** (EC2, ECS, Elastic Beanstalk)

Instrukcje: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📞 Potrzebujesz pomocy?

1. Sprawdź [INSTALL.md](INSTALL.md) - szczegółowe instrukcje
2. Zobacz logi: `docker-compose logs -f`
3. Sprawdź status: `docker-compose ps`

---

## ✅ Quick Verification

Czy wszystko działa? Sprawdź:

```bash
# 1. Backend health check
curl http://localhost:8000/health
# Powinno zwrócić: {"status":"healthy"}

# 2. Frontend
# Otwórz: http://localhost
# Powinieneś zobaczyć stronę główną

# 3. API docs
# Otwórz: http://localhost:8000/docs
# Powinieneś zobaczyć Swagger UI
```

**Wszystko działa?** 🎉 Gratulacje! Możesz zacząć korzystać z aplikacji!

---

**Next Steps:**
1. ✅ Przeczytaj [README.md](README.md)
2. ✅ Zapoznaj się z [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) przed produkcją
3. ✅ Zobacz [DEPLOYMENT.md](DEPLOYMENT.md) jak wdrożyć aplikację

---

**Project**: Phonebook Full Stack Application  
**Version**: 1.0.0  
**Status**: Production Ready (with security improvements needed)  
**Author**: Claude (Anthropic)  
**Date**: 2026-01-20
