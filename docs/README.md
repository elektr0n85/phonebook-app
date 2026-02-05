# 📚 Dokumentacja Phonebook App

Kompletna dokumentacja aplikacji książki telefonicznej z uwierzytelnianiem JWT.

---

## 📖 Spis treści

### 🚀 [00. Jak zacząć](./00-getting-started/)

Pierwsze kroki z aplikacją - instalacja i konfiguracja.

| Dokument | Opis |
|----------|------|
| [START_HERE.md](./00-getting-started/START_HERE.md) | Szybki start - od zera do działającej aplikacji |
| [INSTALL.md](./00-getting-started/INSTALL.md) | Szczegółowa instrukcja instalacji |
| [WINDOWS_INSTALL.md](./00-getting-started/WINDOWS_INSTALL.md) | Instalacja na Windows (bez Docker Desktop) |

---

### 🎨 [01. Projektowanie](./01-design/)

Fazy projektowe aplikacji zgodne z cyklem SSDLC.

| Dokument | Opis |
|----------|------|
| [PHASE1_BEFORE_DEVELOPMENT.md](./01-design/PHASE1_BEFORE_DEVELOPMENT.md) | Faza 1: Wymagania i planowanie |
| [PHASE2_DEFINITION_AND_DESIGN.md](./01-design/PHASE2_DEFINITION_AND_DESIGN.md) | Faza 2: Definicja i projekt architektury |
| [PHASE3_DURING_DEVELOPMENT.md](./01-design/PHASE3_DURING_DEVELOPMENT.md) | Faza 3: Implementacja i przeglądy kodu |

---

### 🏗️ [02. Architektura](./02-architecture/)

Struktura projektu, baza danych i szczegóły implementacji.

| Dokument | Opis |
|----------|------|
| [PROJECT_STRUCTURE.md](./02-architecture/PROJECT_STRUCTURE.md) | Struktura folderów i plików |
| [DATABASE_SCHEMA.md](./02-architecture/DATABASE_SCHEMA.md) | Schemat bazy danych |
| [DATABASE_MODEL_UPDATE.md](./02-architecture/DATABASE_MODEL_UPDATE.md) | Historia zmian modelu danych |
| [IMPLEMENTATION_SUMMARY.md](./02-architecture/IMPLEMENTATION_SUMMARY.md) | Podsumowanie implementacji |

---

### 🔐 [03. Bezpieczeństwo](./03-security/)

Audyty bezpieczeństwa, checklisty i raporty OWASP.

| Dokument | Opis |
|----------|------|
| [SECURITY_CHECKLIST.md](./03-security/SECURITY_CHECKLIST.md) | Checklista bezpieczeństwa |
| [PRODUCTION_CHECKLIST.md](./03-security/PRODUCTION_CHECKLIST.md) | Checklista przed wdrożeniem produkcyjnym |
| [OWASP_TOP10_2025_RAPORT.md](./03-security/OWASP_TOP10_2025_RAPORT.md) | 🆕 Raport OWASP Top 10:2025 |
| [OWASP_SECTION4_AUDIT.md](./03-security/OWASP_SECTION4_AUDIT.md) | Audyt sekcji 4 OWASP |
| [SECURE_DESIGN_LIFECYCLE_AUDIT.md](./03-security/SECURE_DESIGN_LIFECYCLE_AUDIT.md) | Audyt cyklu życia bezpiecznego projektowania |

---

### 🚢 [04. Wdrożenie](./04-deployment/)

Deployment, konfiguracja produkcyjna i monitoring.

| Dokument | Opis |
|----------|------|
| [DEPLOYMENT.md](./04-deployment/DEPLOYMENT.md) | Instrukcja wdrożenia |
| [MONITORING.md](./04-deployment/MONITORING.md) | Konfiguracja monitoringu |
| [RAILWAY.md](./04-deployment/RAILWAY.md) | Deployment na Railway.app |

---

### 🔧 [05. Rozwiązywanie problemów](./05-troubleshooting/)

Typowe problemy i ich rozwiązania.

| Dokument | Opis |
|----------|------|
| [DOCKER_FIX.md](./05-troubleshooting/DOCKER_FIX.md) | Problemy z Docker |
| [FRONTEND_FIXES.md](./05-troubleshooting/FRONTEND_FIXES.md) | Problemy z frontendem |
| [NPM_TROUBLESHOOTING.md](./05-troubleshooting/NPM_TROUBLESHOOTING.md) | Problemy z npm/Node.js |

---

## 📁 Dokumentacja komponentów

| Komponent | Lokalizacja | Opis |
|-----------|-------------|------|
| Backend | [../backend/README.md](../backend/README.md) | API FastAPI, endpointy, modele |
| Frontend | [../frontend/README.md](../frontend/README.md) | React, komponenty, routing |
| Testy Frontend | [../frontend/TESTING.md](../frontend/TESTING.md) | Testy jednostkowe i E2E |

---

## 🛠️ Skrypty pomocnicze

Skrypty instalacyjne znajdują się w folderze `scripts/`:

```bash
scripts/
├── quick-start.sh       # Szybki start (Linux/Mac)
├── quick-start.bat      # Szybki start (Windows)
├── install-frontend.sh  # Instalacja frontendu (Linux/Mac)
└── install-frontend.bat # Instalacja frontendu (Windows)
```

---

## 📊 Status dokumentacji

| Sekcja | Status | Ostatnia aktualizacja |
|--------|--------|----------------------|
| Getting Started | ✅ Aktualna | Luty 2025 |
| Design | ✅ Aktualna | Luty 2025 |
| Architecture | ✅ Aktualna | Luty 2025 |
| Security | 🔄 Do odświeżenia | Luty 2025 |
| Deployment | ✅ Aktualna | Luty 2025 |
| Troubleshooting | ✅ Aktualna | Luty 2025 |

---

*Dokumentacja projektu Phonebook App v5.0*
