# 🔧 QUICK FIX - 2 Błędy Dockera

## ❌ Błędy które masz:
1. `POSTGRES_PASSWORD is missing a value`
2. `npm ci --only=production failed`

---

## ✅ ROZWIĄZANIE (3 kroki):

### **KROK 1: Napraw .env**
```cmd
REM W folderze phonebook-app:
copy /Y .env.READY .env
```

### **KROK 2: Napraw Dockerfile frontend**
```cmd
REM W folderze phonebook-app:
copy /Y Dockerfile.frontend.FIXED frontend\Dockerfile
```

### **KROK 3: Uruchom ponownie**
```cmd
docker-compose down -v
docker-compose up -d --build
```

**Poczekaj 2 minuty** (build trwa dłużej przy pierwszym razie)

---

## 📊 Sprawdź status:
```cmd
docker-compose ps
```

Powinny być **3 kontenery "Up"**:
- phonebook-db
- phonebook-backend  
- phonebook-frontend

---

## 🌐 Otwórz:
**http://localhost**

**GOTOWE!** 🎉

---

## 🐛 Jeśli nadal błędy:

### Zobacz logi:
```cmd
docker-compose logs frontend
```

### Jeśli "npm install failed":
```cmd
REM W folderze frontend musisz mieć package-lock.json
REM Wygeneruj go:
cd frontend
npm install
cd ..
docker-compose up -d --build
```

---

## 📝 Co zostało naprawione:

**1. .env:**
- PRZED: brak pliku lub puste
- PO: skopiowany z .env.READY (ma hasła)

**2. Dockerfile:**
- PRZED: `npm ci --only=production` ❌
- PO: `npm install` ✅

**Dlaczego?** Bo Vite build potrzebuje devDependencies (TypeScript, Vite), a `--only=production` ich nie instaluje!
