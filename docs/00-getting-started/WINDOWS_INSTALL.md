# 🪟 Windows Installation Guide - Krok po kroku

Najprostsza możliwa instrukcja instalacji dla Windows.

---

## ⚡ **SUPER SZYBKI START (3 komendy)**

```cmd
1. Otwórz folder phonebook-app w Eksploratorze
2. Kliknij dwukrotnie: FIX_PROBLEMS.bat
3. Poczekaj 2 minuty
```

**GOTOWE!** Otwórz http://localhost 🎉

---

## 📋 **Krok po kroku (jeśli coś nie działa)**

### **KROK 1: Zainstaluj Docker Desktop**

1. Idź na: https://www.docker.com/products/docker-desktop
2. Kliknij **"Download for Windows"**
3. Uruchom pobrany plik `Docker Desktop Installer.exe`
4. Zaznacz **"Use WSL 2 instead of Hyper-V"** (jeśli widzisz opcję)
5. Kliknij **"Install"**
6. **RESTART komputera** (obowiązkowy!)
7. Po restarcie uruchom **Docker Desktop** (ikona na pulpicie)
8. Poczekaj aż Docker Desktop się w pełni uruchomi (ikona w zasobniku)

**Jak sprawdzić czy działa?**
```cmd
1. Otwórz PowerShell
2. Wpisz: docker --version
3. Powinno pokazać: Docker version 24.x.x
```

---

### **KROK 2: Zatrzymaj lokalnego PostgreSQL (jeśli zainstalowałeś)**

**Dlaczego?** Bo zajmuje port 5432, którego potrzebuje Docker.

**Jak zatrzymać?**

**Opcja A - Services:**
1. Wciśnij `Win + R`
2. Wpisz: `services.msc`
3. Kliknij OK
4. Znajdź na liście: `postgresql-x64-15` (lub podobny)
5. Kliknij prawym przyciskiem → **Stop**
6. (Opcjonalnie) Kliknij prawym → Properties → Startup type: **Manual**

**Opcja B - PowerShell (jako Administrator):**
```powershell
net stop postgresql-x64-15
```

---

### **KROK 3: Przygotuj projekt**

1. **Rozpakuj ZIP:**
   - Kliknij prawym na `phonebook-app.zip`
   - "Wyodrębnij wszystkie..." / "Extract All..."
   - Wybierz folder (np. `C:\Users\TwojeImie\Desktop\`)
   - Kliknij "Wyodrębnij" / "Extract"

2. **Przejdź do folderu:**
   ```
   C:\Users\TwojeImie\Desktop\phonebook-app\
   ```

   Powinny być tam pliki:
   - FIX_PROBLEMS.bat ⭐
   - QUICK_START.bat
   - docker-compose.yml
   - .env.example
   - .env.READY
   - backend\ (folder)
   - frontend\ (folder)

---

### **KROK 4: Przygotuj plik .env**

**NAJŁATWIEJ - użyj gotowego pliku:**

1. W folderze `phonebook-app\` znajdź plik `.env.READY`
2. Skopiuj go (Ctrl+C)
3. Wklej w tym samym folderze (Ctrl+V)
4. Zmień nazwę kopii z `.env.READY - Copy` na `.env`
   - **WAŻNE:** Nazwa to `.env` (kropka na początku!)

**Lub ręcznie:**

1. Skopiuj `.env.example` jako `.env`
2. Otwórz `.env` w Notatniku
3. Zmień te 2 linie:

**PRZED:**
```
SECRET_KEY=CHANGE_ME_TO_RANDOM_32_CHAR_HEX
POSTGRES_PASSWORD=CHANGE_ME_TO_SECURE_PASSWORD
```

**PO (wklej dokładnie to):**
```
SECRET_KEY=8a7b6c5d4e3f2a1b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b
POSTGRES_PASSWORD=MySecureDockerPass123!
```

4. Zapisz (Ctrl+S) i zamknij

---

### **KROK 5: Uruchom aplikację**

**Metoda 1 - Automatyczny skrypt (POLECANE!):**

1. Kliknij dwukrotnie: `FIX_PROBLEMS.bat`
2. Skrypt automatycznie:
   - Sprawdzi Docker ✅
   - Sprawdzi .env ✅
   - Wygeneruje hasła jeśli trzeba ✅
   - Zatrzyma stare kontenery ✅
   - Uruchomi aplikację ✅
3. Poczekaj 2 minuty
4. Gdy zobaczysz "SUKCES" - otwórz http://localhost

**Metoda 2 - Ręcznie (PowerShell):**

1. Otwórz PowerShell w folderze projektu:
   - W Eksploratorze: Shift + prawy kliknij w pustym miejscu
   - "Otwórz okno PowerShell tutaj" / "Open PowerShell window here"

2. Wpisz komendy:
```powershell
# Zatrzymaj stare kontenery
docker-compose down -v

# Uruchom nowe
docker-compose up -d --build

# Sprawdź status
docker-compose ps
```

3. Poczekaj 30 sekund

4. Otwórz: http://localhost

---

### **KROK 6: Sprawdź czy działa**

**W PowerShell:**
```powershell
docker-compose ps
```

Powinno pokazać **3 kontenery** ze statusem **"Up"**:
```
NAME                  STATUS
phonebook-db          Up
phonebook-backend     Up
phonebook-frontend    Up
```

**W przeglądarce:**
- Otwórz: http://localhost
- Powinno pokazać stronę z przyciskami "Login" i "Register"

**Jeśli widzisz stronę - SUKCES!** 🎉

---

## 🐛 **Problemy i rozwiązania**

### **Problem 1: "Docker command not found"**

**Przyczyna:** Docker Desktop nie jest uruchomiony

**Rozwiązanie:**
1. Uruchom Docker Desktop (ikona na pulpicie)
2. Poczekaj aż ikona w zasobniku przestanie się kręcić
3. Spróbuj ponownie

---

### **Problem 2: "Port 5432 already in use"**

**Przyczyna:** Lokalny PostgreSQL zajmuje port

**Rozwiązanie:**
1. Zobacz KROK 2 powyżej (zatrzymaj PostgreSQL)
2. Lub zmień port w `docker-compose.yml`:
   ```yaml
   db:
     ports:
       - "5433:5432"  # Zmień 5432 na 5433
   ```

---

### **Problem 3: "Cannot connect to database"**

**Przyczyna:** Baza danych nie zdążyła się uruchomić

**Rozwiązanie:**
```powershell
# Sprawdź logi bazy danych
docker-compose logs db

# Jeśli widzisz błędy, restart:
docker-compose restart db

# Poczekaj 10 sekund i sprawdź backend
docker-compose logs backend
```

---

### **Problem 4: "File not found: .env"**

**Przyczyna:** Brak pliku .env

**Rozwiązanie:**
1. Zobacz KROK 4 powyżej
2. Skopiuj `.env.READY` jako `.env`
3. Lub uruchom `FIX_PROBLEMS.bat` - zrobi to automatycznie

---

### **Problem 5: Docker Desktop "WSL 2 installation incomplete"**

**Przyczyna:** Brak WSL 2

**Rozwiązanie:**
1. Otwórz PowerShell **jako Administrator**
2. Wpisz:
   ```powershell
   wsl --install
   ```
3. **Restart komputera**
4. Uruchom Docker Desktop ponownie

---

### **Problem 6: Strona nie ładuje się (http://localhost)**

**Rozwiązanie:**

1. **Sprawdź czy frontend działa:**
   ```powershell
   docker-compose logs frontend
   ```

2. **Sprawdź czy port 80 jest wolny:**
   ```powershell
   netstat -ano | findstr ":80"
   ```
   
   Jeśli coś używa portu 80:
   - Znajdź PID (ostatnia kolumna)
   - W Task Manager znajdź proces o tym PID i zamknij

3. **Restart frontend:**
   ```powershell
   docker-compose restart frontend
   ```

---

### **Problem 7: "This site can't be reached"**

**Rozwiązanie - pełny reset:**

```powershell
# 1. Zatrzymaj wszystko
docker-compose down -v

# 2. Wyczyść Docker
docker system prune -f

# 3. Usuń obrazy
docker-compose down --rmi all

# 4. Zbuduj od nowa
docker-compose build --no-cache

# 5. Uruchom
docker-compose up -d

# 6. Poczekaj 1 minutę
timeout 60

# 7. Sprawdź status
docker-compose ps
```

---

## ✅ **Weryfikacja instalacji**

Sprawdź czy wszystko działa:

### **1. Backend health check:**
Otwórz: http://localhost:8000/health

Powinno pokazać:
```json
{"status":"healthy"}
```

### **2. API docs:**
Otwórz: http://localhost:8000/docs

Powinno pokazać Swagger UI z listą endpoints.

### **3. Frontend:**
Otwórz: http://localhost

Powinno pokazać stronę główną.

### **4. Pełny test:**

1. Kliknij **"Register"**
2. Email: `test@example.com`
3. Hasło: `TestPass123!`
4. Kliknij "Register"
5. Zaloguj się tym samym emailem i hasłem
6. Kliknij **"Add Contact"**
7. Wypełnij formularz i zapisz
8. Kontakt powinien się pojawić na liście

**Jeśli wszystko powyższe działa - instalacja zakończona sukcesem!** 🎉

---

## 📁 **Przydatne komendy**

### **Podstawowe:**
```powershell
# Zobacz logi (na żywo)
docker-compose logs -f

# Zobacz logi tylko backend
docker-compose logs -f backend

# Zobacz logi tylko frontend
docker-compose logs -f frontend

# Sprawdź status kontenerów
docker-compose ps

# Restart wszystkiego
docker-compose restart

# Zatrzymaj aplikację
docker-compose down
```

### **Czyszczenie:**
```powershell
# Usuń wszystko (kontenery + wolumeny + sieci)
docker-compose down -v

# Wyczyść cache Docker
docker system prune -f

# Usuń WSZYSTKO Docker (ostrożnie!)
docker system prune -a --volumes
```

### **Debugging:**
```powershell
# Wejdź do kontenera backend (shell)
docker-compose exec backend bash

# Wejdź do bazy danych
docker-compose exec db psql -U phonebook_user phonebook_db

# Sprawdź użycie zasobów
docker stats
```

---

## 🆘 **Nadal nie działa?**

Jeśli nadal masz problemy:

1. **Sprawdź logi:**
   ```powershell
   docker-compose logs -f > logi.txt
   ```
   
2. **Sprawdź .env:**
   ```powershell
   type .env
   ```
   
   Pokaże zawartość - upewnij się że nie ma "CHANGE_ME"

3. **Sprawdź czy Docker ma zasoby:**
   - Otwórz Docker Desktop
   - Settings → Resources
   - Memory: minimum 4GB
   - CPU: minimum 2 cores

4. **Spróbuj manualnej instalacji:**
   - Zobacz: `INSTALL.md` sekcja "Manual Installation"

---

## 📞 **Co dalej?**

Po pomyślnej instalacji:

1. ✅ Przeczytaj `README.md` - pełna dokumentacja
2. ✅ Zobacz `SECURITY_CHECKLIST.md` przed produkcją
3. ✅ Sprawdź `DEPLOYMENT.md` jak wdrożyć na cloud
4. ✅ Uruchom testy: `docker-compose exec backend pytest`

---

**Miłego korzystania z aplikacji!** 🚀

---

**Windows Installation Guide**  
**Version**: 1.0.0  
**Last Updated**: 2026-01-20  
**For**: Windows 10/11 users
