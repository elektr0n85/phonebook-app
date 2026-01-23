# 🔧 Frontend TypeScript Fixes

Poprawki dla błędów TypeScript w frontend.

---

## 🐛 **Znalezione błędy:**

1. **api.ts linia 11** - Property 'env' does not exist on type 'ImportMeta'
2. **tsconfig.json linia 24** - File 'tsconfig.node.json' not found

---

## ✅ **Szybkie naprawienie (3 pliki do podmiany)**

### **Metoda 1: Skopiuj gotowe pliki (najłatwiej)**

W folderze projektu znajdziesz pliki z końcówką `.FIXED`:
- `api.ts.FIXED`
- `tsconfig.json.FIXED`
- `tsconfig.node.json.FIXED`
- `vite-env.d.ts.FIXED`

**Skopiuj je:**
```bash
# W folderze phonebook-app:
copy api.ts.FIXED frontend\src\services\api.ts
copy tsconfig.json.FIXED frontend\tsconfig.json
copy tsconfig.node.json.FIXED frontend\tsconfig.node.json
copy vite-env.d.ts.FIXED frontend\src\vite-env.d.ts
```

---

### **Metoda 2: Ręczna naprawa**

#### **1. Napraw api.ts**

Otwórz: `frontend\src\services\api.ts`

**Znajdź (linijki 9-12):**
```typescript
import axios, { AxiosError, AxiosInstance } from 'axios';
import ViteEnv from 'vite';

const env: ViteEnv = import.meta.env;

const API_BASE_URL = env.VITE_API_URL || 'http://localhost:8000/api/v1';
```

**Zamień na:**
```typescript
import axios, { AxiosError, AxiosInstance } from 'axios';

// Get API URL from environment variables (Vite)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
```

**Zapisz** (Ctrl+S)

---

#### **2. Utwórz tsconfig.node.json**

Stwórz nowy plik: `frontend\tsconfig.node.json`

**Zawartość:**
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

**Zapisz**

---

#### **3. Utwórz vite-env.d.ts (bonus - TypeScript types)**

Stwórz nowy plik: `frontend\src\vite-env.d.ts`

**Zawartość:**
```typescript
/// <reference types="vite/client" />

/**
 * Vite environment variables type definitions.
 * Add your custom env variables here for TypeScript autocomplete.
 */
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  // Add more env variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

**Zapisz**

---

#### **4. Sprawdź tsconfig.json**

Otwórz: `frontend\tsconfig.json`

**Powinno być tak:**
```json
{
  "compilerOptions": {    
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Zapisz**

---

## ✅ **Weryfikacja**

Po naprawie, sprawdź czy błędy zniknęły:

### **W VS Code:**
1. Zamknij i otwórz ponownie VS Code
2. Otwórz `frontend\src\services\api.ts`
3. Sprawdź czy nie ma czerwonych podkreśleń

### **W terminalu:**
```bash
cd frontend
npm run build
```

**Powinno się zbudować bez błędów!** ✅

---

## 📝 **Co naprawiłem:**

### **api.ts:**
**Przed (błąd):**
```typescript
import ViteEnv from 'vite';  // ❌ Niepoprawny import
const env: ViteEnv = import.meta.env;  // ❌ Niepoprawny typ
const API_BASE_URL = env.VITE_API_URL || '...';
```

**Po (poprawnie):**
```typescript
// Vite automatycznie udostępnia import.meta.env
const API_BASE_URL = import.meta.env.VITE_API_URL || '...';  // ✅
```

### **tsconfig.node.json:**
**Przed:**
```
❌ Plik nie istnieje
```

**Po:**
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

**Co to robi?**
- Konfiguracja TypeScript dla pliku `vite.config.ts`
- Vite wymaga tego pliku dla poprawnego typowania

### **vite-env.d.ts (nowy bonus!):**
```typescript
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}
```

**Co to robi?**
- Daje TypeScript autocomplete dla `import.meta.env.VITE_API_URL`
- Teraz VS Code podpowie Ci dostępne zmienne środowiskowe!

---

## 🎯 **Dlaczego te błędy wystąpiły:**

1. **api.ts:** Próba zaimportowania `ViteEnv` z pakietu `vite` - ten typ nie istnieje
   - Vite używa własnego `ImportMetaEnv` interface
   - Nie trzeba importować, `import.meta.env` działa out-of-the-box

2. **tsconfig.node.json:** Standardowy plik dla projektów Vite
   - Potrzebny do konfiguracji `vite.config.ts`
   - Był w szablonie Vite, ale jakoś się zgubił

3. **vite-env.d.ts:** TypeScript type definitions dla Vite
   - Opcjonalny, ale bardzo pomocny
   - Daje autocomplete i type safety

---

## 🚀 **Po naprawie możesz:**

```bash
# Build frontend bez błędów
cd frontend
npm run build

# Lub uruchom dev server
npm run dev

# Lub w Docker
cd ..
docker-compose up -d --build
```

**Wszystko powinno działać!** 🎉

---

## 🆘 **Jeśli nadal są błędy:**

```bash
# Wyczyść cache i node_modules
cd frontend
rm -rf node_modules
rm -rf dist
npm cache clean --force
npm install
npm run build
```

---

**Fixes Version**: 1.0.0  
**Date**: 2026-01-21  
**Status**: Tested ✅
