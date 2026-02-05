# 📦 Installation Guide - Phonebook Application

Szczegółowa instrukcja instalacji dla różnych systemów operacyjnych.

---

## 🚀 **Quick Start (Recommended)**

### **Option 1: Automatyczny skrypt (najszybszy!)**

**Linux/macOS:**
```bash
# 1. Rozpakuj archiwum
unzip phonebook-app.zip
cd phonebook-app

# 2. Uruchom skrypt instalacyjny
chmod +x QUICK_START.sh
./QUICK_START.sh
```

**Windows:**
```cmd
REM 1. Rozpakuj archiwum (kliknij prawym, "Extract All")
cd phonebook-app

REM 2. Uruchom skrypt instalacyjny
QUICK_START.bat
```

**That's it!** 🎉 Aplikacja będzie dostępna na:
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### **Option 2: Docker Compose (manualnie)**

```bash
# 1. Rozpakuj projekt
unzip phonebook-app.zip
cd phonebook-app

# 2. Skopiuj .env
cp .env.example .env

# 3. Wygeneruj sekretny klucz
# Linux/macOS:
openssl rand -hex 32

# Windows PowerShell:
[System.Convert]::ToBase64String((1..32 | %{Get-Random -Maximum 256}))

# 4. Edytuj .env i wstaw wygenerowany klucz do SECRET_KEY

# 5. Uruchom Docker
docker-compose up -d --build

# 6. Sprawdź status
docker-compose ps
```

**Dostęp:**
- Frontend: http://localhost
- Backend: http://localhost:8000/docs

---

## 📋 **Wymagania systemowe**

### **Minimalne:**
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Dysk**: 2 GB wolnego miejsca
- **System**: Linux, macOS, Windows 10/11

### **Software (Docker):**
- Docker 20.10+
- Docker Compose 2.0+

### **Software (Manual):**
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

---

## 🐳 **Instalacja Docker**

### **Windows:**
1. Pobierz Docker Desktop: https://www.docker.com/products/docker-desktop
2. Zainstaluj (wymaga restart)
3. Uruchom Docker Desktop
4. W ustawieniach: Resources → zwiększ pamięć do 4GB

### **macOS:**
1. Pobierz Docker Desktop: https://www.docker.com/products/docker-desktop
2. Przeciągnij do Applications
3. Uruchom Docker Desktop
4. Zezwól na dostęp w ustawieniach

### **Linux (Ubuntu/Debian):**
```bash
# Instalacja Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dodaj siebie do grupy docker
sudo usermod -aG docker $USER

# Zaloguj się ponownie lub:
newgrp docker

# Instalacja Docker Compose
sudo apt install docker-compose-plugin

# Weryfikacja
docker --version
docker compose version
```

---

## 💻 **Instalacja Manualna (bez Docker)**

### **1. Backend (Python/FastAPI)**

#### **Linux/macOS:**
```bash
# 1. Przejdź do folderu backend
cd backend

# 2. Utwórz virtual environment
python3 -m venv venv

# 3. Aktywuj venv
source venv/bin/activate

# 4. Zainstaluj dependencies
pip install -r requirements.txt

# 5. Skonfiguruj .env
cp .env.example .env
nano .env  # lub vim, lub inny edytor

# Edytuj:
DATABASE_URL=postgresql+asyncpg://phonebook_user:haslo@localhost/phonebook_db
SECRET_KEY=<wygeneruj: openssl rand -hex 32>

# 6. Zainstaluj PostgreSQL (jeśli nie masz)
# Ubuntu/Debian:
sudo apt install postgresql postgresql-contrib

# macOS (Homebrew):
brew install postgresql@15

# 7. Utwórz bazę danych
sudo -u postgres psql
CREATE DATABASE phonebook_db;
CREATE USER phonebook_user WITH PASSWORD 'haslo123';
GRANT ALL PRIVILEGES ON DATABASE phonebook_db TO phonebook_user;
\q

# 8. Inicjalizuj bazę
python init_db.py

# 9. Uruchom serwer
uvicorn app.main:app --reload --port 8000
```

#### **Windows:**
```cmd
REM 1. Przejdź do folderu backend
cd backend

REM 2. Utwórz virtual environment
python -m venv venv

REM 3. Aktywuj venv
venv\Scripts\activate

REM 4. Zainstaluj dependencies
pip install -r requirements.txt

REM 5. Skonfiguruj .env
copy .env.example .env
notepad .env

REM Edytuj DATABASE_URL i SECRET_KEY

REM 6. Zainstaluj PostgreSQL
REM Pobierz z: https://www.postgresql.org/download/windows/

REM 7. Utwórz bazę (w pgAdmin lub psql)
REM CREATE DATABASE phonebook_db;

REM 8. Inicjalizuj bazę
python init_db.py

REM 9. Uruchom serwer
uvicorn app.main:app --reload --port 8000
```

**Sprawdź:** http://localhost:8000/docs

---

### **2. Frontend (React/TypeScript)**

**Otwórz nowy terminal!**

#### **Linux/macOS/Windows:**
```bash
# 1. Przejdź do folderu frontend
cd frontend

# 2. Zainstaluj Node.js (jeśli nie masz)
# Linux (Ubuntu/Debian):
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# macOS (Homebrew):
brew install node@18

# Windows:
# Pobierz z: https://nodejs.org/

# 3. Zainstaluj dependencies
npm install

# 4. Skonfiguruj .env
cp .env.example .env

# Edytuj (powinno być domyślnie OK):
VITE_API_URL=http://localhost:8000/api/v1

# 5. Uruchom dev server
npm run dev
```

**Sprawdź:** http://localhost:3000

---

## 🧪 **Testowanie instalacji**

### **1. Sprawdź backend:**
```bash
# Health check
curl http://localhost:8000/health

# Powinno zwrócić: {"status":"healthy"}
```

### **2. Sprawdź API docs:**
Otwórz: http://localhost:8000/docs

Powinieneś zobaczyć Swagger UI z listą endpoints.

### **3. Sprawdź frontend:**
Otwórz: http://localhost (lub http://localhost:3000 dla dev)

Powinieneś zobaczyć stronę główną z przyciskami Login/Register.

### **4. Utwórz konto testowe:**
1. Kliknij "Register"
2. Email: `test@example.com`
3. Hasło: `TestPass123!`
4. Zaloguj się

### **5. Dodaj testowy kontakt:**
1. Po zalogowaniu kliknij "Add Contact"
2. Wypełnij formularz
3. Dodaj numer telefonu
4. Zapisz

**Jeśli wszystko działa - gratulacje!** ✅

---

## 🔧 **Troubleshooting**

### **Problem: Docker nie startuje**

**Objaw:** `Cannot connect to Docker daemon`

**Rozwiązanie:**
```bash
# Linux: Uruchom Docker daemon
sudo systemctl start docker

# Windows/Mac: Uruchom Docker Desktop (kliknij ikonę)
```

---

### **Problem: Port 8000 zajęty**

**Objaw:** `Address already in use`

**Rozwiązanie:**
```bash
# Sprawdź co używa portu
# Linux/macOS:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Zabij proces lub zmień port w docker-compose.yml
```

---

### **Problem: PostgreSQL connection failed**

**Objaw:** `could not connect to server`

**Rozwiązanie:**
```bash
# Sprawdź czy PostgreSQL działa
# Linux:
sudo systemctl status postgresql

# macOS:
brew services list

# Windows: Sprawdź w Task Manager

# Uruchom jeśli nie działa:
sudo systemctl start postgresql  # Linux
brew services start postgresql@15  # macOS
```

---

### **Problem: npm install fails**

**Objaw:** `EACCES: permission denied`

**Rozwiązanie:**
```bash
# Nie używaj sudo! Napraw permissions:
sudo chown -R $USER:$USER ~/.npm
sudo chown -R $USER:$USER node_modules
```

---

### **Problem: Python ModuleNotFoundError**

**Objaw:** `No module named 'fastapi'`

**Rozwiązanie:**
```bash
# Upewnij się że venv jest aktywowany:
# Powinno być (venv) w prompt

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Zainstaluj ponownie:
pip install -r requirements.txt
```

---

### **Problem: Database initialization fails**

**Objaw:** `relation "users" does not exist`

**Rozwiązanie:**
```bash
# Wyczyść bazę i zainicjalizuj ponownie:
cd backend

# Usuń bazę (PostgreSQL):
sudo -u postgres psql
DROP DATABASE phonebook_db;
CREATE DATABASE phonebook_db;
GRANT ALL PRIVILEGES ON DATABASE phonebook_db TO phonebook_user;
\q

# Zainicjalizuj ponownie:
python init_db.py
```

---

### **Problem: Frontend pokazuje błąd CORS**

**Objaw:** `blocked by CORS policy`

**Rozwiązanie:**
```bash
# Sprawdź ALLOWED_ORIGINS w backend/.env
# Powinno zawierać:
ALLOWED_ORIGINS=http://localhost:3000,http://localhost

# Restart backendu
```

---

### **Problem: Docker build fails**

**Objaw:** `failed to solve with frontend dockerfile`

**Rozwiązanie:**
```bash
# Wyczyść cache Dockera:
docker system prune -a

# Build ponownie:
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 **Weryfikacja instalacji**

### **Checklist:**
- [ ] Backend odpowiada na http://localhost:8000/health
- [ ] API docs dostępne na http://localhost:8000/docs
- [ ] Frontend dostępny na http://localhost
- [ ] Możesz się zarejestrować
- [ ] Możesz się zalogować
- [ ] Możesz dodać kontakt
- [ ] Możesz dodać telefon do kontaktu
- [ ] Możesz wyszukać kontakt
- [ ] Możesz usunąć kontakt

**Wszystko zaznaczone?** Gratulacje! 🎉

---

## 📝 **Konfiguracja produkcyjna**

Dla instalacji produkcyjnej zobacz:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment na cloud (AWS, Heroku, Railway)
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Security checklist przed deploy
- [MONITORING.md](MONITORING.md) - Monitoring i maintenance

---

## 🆘 **Pomoc**

### **Logi:**
```bash
# Docker:
docker-compose logs -f backend  # Backend logs
docker-compose logs -f frontend # Frontend logs

# Manual:
# Backend: w terminalu gdzie uruchomiłeś uvicorn
# Frontend: w terminalu gdzie uruchomiłeś npm run dev
```

### **Restart:**
```bash
# Docker:
docker-compose restart

# Manual:
# Ctrl+C w każdym terminalu, potem uruchom ponownie
```

### **Czyszczenie:**
```bash
# Docker (usuwa wszystko):
docker-compose down -v

# Manual:
# Backend: deaktywuj venv, usuń venv/
# Frontend: usuń node_modules/
```

---

## 📞 **Wsparcie**

- **Issues**: GitHub Issues (jeśli projekt na GitHub)
- **Documentation**: Zobacz README.md
- **Stack Overflow**: Tag `phonebook-app`

---

**Installation Guide Version**: 1.0.0  
**Last Updated**: 2026-01-20  
**Status**: Complete ✅
