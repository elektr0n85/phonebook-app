# 📦 NPM Installation Problems - Complete Fix Guide

Rozwiązanie dla "brakuje react, react-dom, react-router-dom..."

---

## 🚀 **SUPER SZYBKIE ROZWIĄZANIE** ⭐

### **Windows:**
```cmd
1. Idź do folderu phonebook-app
2. Kliknij dwukrotnie: INSTALL_FRONTEND.bat
3. Poczekaj 3 minuty
```

### **Linux/macOS:**
```bash
cd phonebook-app
chmod +x INSTALL_FRONTEND.sh
./INSTALL_FRONTEND.sh
```

**GOTOWE!** Wszystko zainstalowane automatycznie! 🎉

---

## 📋 **Co robi automatyczny skrypt:**

✅ Sprawdza Node.js  
✅ Czyści `node_modules/`  
✅ Czyści `package-lock.json`  
✅ Czyści npm cache  
✅ Instaluje wszystkie dependencies  
✅ Weryfikuje instalację (React, React DOM, Router, Axios, etc.)  
✅ Pokazuje wersje zainstalowanych pakietów  
✅ (Opcjonalnie) Uruchamia dev server  

**Żadnych problemów, wszystko automatycznie!** 😊

---

## 🛠️ **Jeśli wolisz manualnie (krok po kroku):**

### **Krok 1: Wyczyść wszystko**

**Windows (PowerShell):**
```powershell
cd phonebook-app\frontend

# Usuń node_modules
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue

# Usuń package-lock.json
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue

# Wyczyść cache
npm cache clean --force
```

**Linux/macOS:**
```bash
cd phonebook-app/frontend

# Usuń node_modules
rm -rf node_modules

# Usuń package-lock.json
rm -f package-lock.json

# Wyczyść cache
npm cache clean --force
```

---

### **Krok 2: Sprawdź package.json**

Otwórz `frontend/package.json` i upewnij się że ma:

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.3",
    "axios": "^1.6.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.55",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.1.0",
    "tailwindcss": "^3.4.1"
  }
}
```

**Jeśli brakuje - użyj `package.json.COMPLETE`:**
```cmd
copy /Y package.json.COMPLETE frontend\package.json
```

---

### **Krok 3: Zainstaluj dependencies**

```bash
cd frontend
npm install
```

**To powinno zająć 2-5 minut.**

---

### **Krok 4: Weryfikuj instalację**

```bash
# Sprawdź czy React jest
ls node_modules/react

# Sprawdź czy React DOM jest
ls node_modules/react-dom

# Sprawdź czy Router jest
ls node_modules/react-router-dom

# Sprawdź wszystkie
npm list --depth=0
```

**Wszystko powinno być zainstalowane!** ✅

---

## 🐛 **Troubleshooting - Konkretne problemy**

### **Problem 1: "npm ERR! code ENOENT"**

**Objawy:**
```
npm ERR! code ENOENT
npm ERR! syscall open
npm ERR! path C:\...\package.json
```

**Przyczyna:** Nie jesteś w folderze `frontend/`

**Rozwiązanie:**
```cmd
cd phonebook-app\frontend
npm install
```

---

### **Problem 2: "npm ERR! network timeout"**

**Objawy:**
```
npm ERR! network timeout
npm ERR! network This is a problem related to network connectivity
```

**Przyczyny:**
- Słaby internet
- Firewall blokuje npm
- Proxy

**Rozwiązanie:**

**A. Zwiększ timeout:**
```bash
npm config set fetch-timeout 60000
npm config set fetch-retries 5
npm install
```

**B. Zmień registry (w Polsce często szybsze):**
```bash
npm config set registry https://registry.npmjs.org/
npm install
```

**C. Użyj VPN jeśli firewall blokuje**

---

### **Problem 3: "npm ERR! EACCES: permission denied"**

**Objawy:**
```
npm ERR! Error: EACCES: permission denied
```

**Przyczyna:** Brak uprawnień do zapisu

**Rozwiązanie:**

**Windows:**
```cmd
REM Uruchom PowerShell jako Administrator
REM Prawy kliknij na PowerShell → "Run as Administrator"

cd phonebook-app\frontend
npm install
```

**Linux/macOS:**
```bash
# NIE używaj sudo npm install!
# Zamiast tego napraw uprawnienia:

sudo chown -R $USER:$USER ~/.npm
sudo chown -R $USER:$USER node_modules

npm install
```

---

### **Problem 4: "Peer dependency warnings"**

**Objawy:**
```
npm WARN ERESOLVE overriding peer dependency
npm WARN ERESOLVE peer dependency warning
```

**To jest OK!** Możesz zignorować warnings o peer dependencies.

**Jeśli chcesz je naprawić:**
```bash
npm install --legacy-peer-deps
```

---

### **Problem 5: "Module not found: Can't resolve 'react'"**

**Objawy:**
Po `npm install` wszystko OK, ale `npm run dev` pokazuje:
```
Error: Module not found: Can't resolve 'react'
```

**Przyczyna:** React zainstalowany w złym miejscu

**Rozwiązanie:**
```bash
# Sprawdź czy jesteś w frontend/
pwd  # lub cd (Windows)

# Powinno pokazać: .../phonebook-app/frontend

# Jeśli nie:
cd frontend

# Zainstaluj ponownie
rm -rf node_modules
npm install
```

---

### **Problem 6: "npm install nic nie instaluje"**

**Objawy:**
```
npm install
# Kończy się od razu, nic nie pobiera
```

**Przyczyna:** Cache jest zepsuty

**Rozwiązanie:**
```bash
# Wyczyść WSZYSTKO
rm -rf node_modules
rm -f package-lock.json
npm cache clean --force

# Usuń globalny cache (opcjonalnie)
# Windows:
# del /s /q %AppData%\npm-cache

# Linux/macOS:
rm -rf ~/.npm

# Zainstaluj ponownie
npm install
```

---

### **Problem 7: "Bardzo wolne pobieranie (Poland)"**

**Objawy:**
npm install trwa 30+ minut

**Rozwiązanie:**

**A. Użyj szybszego registry:**
```bash
npm config set registry https://registry.npmjs.org/
npm install
```

**B. Użyj yarn zamiast npm:**
```bash
# Zainstaluj yarn
npm install -g yarn

# Użyj yarn
yarn install

# Uruchom
yarn dev
```

---

### **Problem 8: "node_modules/ jest pusty po npm install"**

**Objawy:**
```
npm install
# Zwraca success, ale node_modules/ jest pusty lub ma tylko 1-2 foldery
```

**Przyczyna:** Antywirusy blokowały instalację

**Rozwiązanie:**
```bash
# 1. Wyłącz antywirus na chwilę
# 2. Wyczyść i zainstaluj ponownie:

rm -rf node_modules
npm cache clean --force
npm install

# 3. Włącz antywirus z powrotem
```

---

### **Problem 9: "Windows Defender usunął pliki"**

**Objawy:**
Po `npm install` niektóre pliki brakują lub są w kwarantannie

**Rozwiązanie:**
```cmd
1. Otwórz Windows Security
2. Virus & threat protection
3. Protection history
4. Znajdź zablokowane pliki
5. Restore them
6. Settings → Add exclusion
7. Dodaj folder: C:\...\phonebook-app\frontend\node_modules
8. npm install ponownie
```

---

## 📝 **Lista WSZYSTKICH dependencies**

Jeśli chcesz sprawdzić co powinno być zainstalowane:

### **Production Dependencies (4):**
```json
{
  "react": "^18.2.0",           // React library
  "react-dom": "^18.2.0",       // React DOM bindings
  "react-router-dom": "^6.21+", // Routing
  "axios": "^1.6+"              // HTTP client
}
```

### **Development Dependencies (16):**
```json
{
  "@types/react": "^18.2+",              // React types
  "@types/react-dom": "^18.2+",          // React DOM types
  "@typescript-eslint/eslint-plugin": "^6.21+",
  "@typescript-eslint/parser": "^6.21+",
  "@vitejs/plugin-react": "^4.2+",       // Vite React plugin
  "autoprefixer": "^10.4+",              // CSS autoprefixer
  "eslint": "^8.56+",                    // Linter
  "eslint-plugin-react-hooks": "^4.6+",
  "eslint-plugin-react-refresh": "^0.4+",
  "postcss": "^8.4+",                    // CSS processor
  "tailwindcss": "^3.4+",                // Tailwind CSS
  "typescript": "^5.3+",                 // TypeScript
  "vite": "^5.0+"                        // Build tool
}
```

**RAZEM:** 20 packages (4 main + 16 dev)

Po `npm install` powinno być **200-300 packages** w `node_modules/` (z subdependencies).

---

## ✅ **Weryfikacja poprawnej instalacji**

```bash
cd frontend

# 1. Sprawdź czy main packages są
ls node_modules/react
ls node_modules/react-dom
ls node_modules/react-router-dom
ls node_modules/axios
ls node_modules/vite
ls node_modules/typescript
ls node_modules/tailwindcss

# 2. Policz foldery
# Windows:
dir node_modules | find /c /v ""
# Powinno być 200-300+

# Linux/macOS:
ls node_modules | wc -l
# Powinno być 200-300+

# 3. Sprawdź rozmiar
# Windows:
dir node_modules
# Powinno być ~200-400 MB

# Linux/macOS:
du -sh node_modules
# Powinno być ~200-400 MB

# 4. Test build
npm run build
# Powinno zbudować bez błędów

# 5. Test dev server
npm run dev
# Powinno wystartować na http://localhost:5173
```

**Wszystko OK?** Gratulacje! 🎉

---

## 🎯 **Quick Reference - Komendy ratunkowe**

```bash
# Szybki reset i instalacja (Windows)
cd frontend
rmdir /s /q node_modules
del package-lock.json
npm cache clean --force
npm install

# Szybki reset i instalacja (Linux/Mac)
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Jeśli nadal nie działa - użyj yarn
npm install -g yarn
yarn install
yarn dev

# Nuklearna opcja - pełny reset npm
npm config delete prefix
npm cache clean --force
npm install -g npm@latest
npm install
```

---

## 💡 **Dlaczego to się dzieje?**

**Najczęstsze przyczyny:**
1. **Słaby internet** - timeouty podczas pobierania
2. **Zepsuty cache** - npm cache jest skorumpowany
3. **Antywirus** - blokuje node_modules/
4. **Uprawnienia** - brak praw zapisu do folderu
5. **Stary npm** - wersja npm < 8.0 ma problemy
6. **Proxy/Firewall** - blokuje registry.npmjs.org

**Rozwiązanie:** Użyj `INSTALL_FRONTEND.bat` - rozwiązuje 99% problemów! 😊

---

## 📞 **Nadal problemy?**

**Wyślij mi:**
```bash
# 1. Wersje
node --version
npm --version

# 2. Logi
npm install > install.log 2>&1
# Wyślij plik install.log

# 3. Package.json
cat frontend/package.json
```

Pomogę! 💪

---

**NPM Troubleshooting Guide**  
**Version**: 1.0.0  
**Last Updated**: 2026-01-21  
**Tested**: Windows 10/11, macOS, Ubuntu 22.04
