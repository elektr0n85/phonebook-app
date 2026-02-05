# 📞 Phonebook Application

Bezpieczna aplikacja książki telefonicznej z uwierzytelnianiem JWT.  
Zgodna z OWASP Top 10:2025.

---

## 🚀 Szybki start

```bash
# 1. Sklonuj i skonfiguruj
git clone https://github.com/yourusername/phonebook-app.git
cd phonebook-app
cp .env.example .env

# 2. Uruchom (Docker)
docker-compose up -d

# 3. Otwórz
# Frontend: http://localhost
# API Docs: http://localhost:8000/docs
```

**Lub użyj skryptów:**
```bash
./scripts/quick-start.sh      # Linux/Mac
scripts\quick-start.bat       # Windows
```

**Lub Make:**
```bash
make start    # Uruchom
make test     # Testy
make logs     # Logi
```

---

## 🛠️ Stack technologiczny

| Warstwa | Technologie |
|---------|-------------|
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.0, PostgreSQL 15 |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **Auth** | JWT (access + refresh tokens), bcrypt |
| **Infra** | Docker, Nginx, GitHub Actions |

---

## ✨ Funkcjonalności

- ✅ Rejestracja i logowanie (JWT)
- ✅ Blokada konta po nieudanych próbach
- ✅ Zarządzanie kontaktami (CRUD)
- ✅ Wiele telefonów na kontakt (N:M)
- ✅ Wyszukiwanie po nazwie/email/telefonie
- ✅ Reset hasła przez email
- ✅ Role użytkowników (User/Admin)
- ✅ Audit log wszystkich operacji

---

## 📁 Struktura projektu

```
phonebook-app/
├── backend/          # FastAPI API
├── frontend/         # React SPA
├── scripts/          # Skrypty instalacyjne
├── docs/             # 📚 Dokumentacja (szczegóły poniżej)
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 📚 Dokumentacja

Pełna dokumentacja znajduje się w folderze [`docs/`](./docs/README.md):

| Sekcja | Opis |
|--------|------|
| [00. Jak zacząć](./docs/00-getting-started/) | Instalacja, konfiguracja, Windows |
| [01. Projektowanie](./docs/01-design/) | Fazy SSDLC, wymagania, architektura |
| [02. Architektura](./docs/02-architecture/) | Struktura, baza danych, implementacja |
| [03. Bezpieczeństwo](./docs/03-security/) | OWASP, checklisty, audyty |
| [04. Wdrożenie](./docs/04-deployment/) | Docker, Railway, monitoring |
| [05. Troubleshooting](./docs/05-troubleshooting/) | Rozwiązywanie problemów |

**Dokumentacja komponentów:**
- [Backend README](./backend/README.md) - API, endpointy, modele
- [Frontend README](./frontend/README.md) - Komponenty, routing
- [Testy](./backend/tests/README.md) - 50+ testów

---

## 🔐 Bezpieczeństwo

Aplikacja implementuje zabezpieczenia zgodne z **OWASP Top 10:2025**:

- ✅ Kontrola dostępu (ownership check)
- ✅ Hashowanie haseł (bcrypt, cost=12)
- ✅ Ochrona przed SQL Injection (ORM)
- ✅ Ochrona przed XSS (CSP, React escape)
- ✅ Nagłówki bezpieczeństwa (HSTS, X-Frame-Options)
- ✅ Audit logging

📋 [Pełny raport OWASP](./docs/03-security/OWASP_TOP10_2025_RAPORT.md)

---

## 🧪 Testy

```bash
# Backend (50+ testów)
cd backend
pytest                        # Wszystkie
pytest -m security            # Tylko security
pytest --cov=app              # Z coverage

# Security scan
bandit -r app/
```

---

## 🚢 Deployment

```bash
# Produkcja z Docker
docker-compose -f docker-compose.yml up -d

# Railway
railway init && railway up
```

📋 [Instrukcja wdrożenia](./docs/04-deployment/DEPLOYMENT.md)

---

## 📊 Statystyki

| Metryka | Wartość |
|---------|---------|
| Pliki | 70+ |
| Linie kodu | ~7,500 |
| Testy | 50+ |
| Pokrycie | 90%+ |
| Endpointy API | 18 |
| Tabele DB | 5 |

---

## 📄 Licencja

MIT License - zobacz [LICENSE](LICENSE)

---

**Wersja:** 5.0  
**Status:** ✅ Production Ready  
**Ostatnia aktualizacja:** Luty 2025

---

*Built with ❤️ using FastAPI + React*
