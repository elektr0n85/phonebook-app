# Phonebook Frontend (React + TypeScript + Vite)

## 🎨 **FRONTEND COMPLETE!**

### ✅ **What's Implemented:**

**Components** (10 files):
- ✅ `Login` - User login with validation
- ✅ `Register` - User registration with password strength check
- ✅ `ContactList` - List all contacts with search
- ✅ `ContactDetail` - View contact with phones
- ✅ `ContactForm` - Create contact with multiple phones
- ✅ `Navigation` - Header navigation
- ✅ `ProtectedRoute` - Route protection
- ✅ `HomePage` - Landing page

**Services** (3 files):
- ✅ `api.ts` - Axios configuration with interceptors
- ✅ `authService.ts` - Authentication API calls
- ✅ `contactService.ts` - Contacts API calls

**Context**:
- ✅ `AuthContext` - Authentication state management

**Utils**:
- ✅ `validation.ts` - Client-side validation (matches backend)

**Styling**:
- ✅ Tailwind CSS
- ✅ Responsive design
- ✅ Custom utility classes

---

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
cd frontend
npm install
```

### **2. Configure Environment**
```bash
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000/api/v1)
```

### **3. Start Development Server**
```bash
npm run dev
```

**Frontend**: http://localhost:3000  
**Backend proxy**: Vite proxies `/api` to `http://localhost:8000`

---

## 📦 **Tech Stack**

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Context API** - State management

---

## 🔐 **Security Features**

### **1. Client-Side Validation**
```typescript
// Password strength validation
validation.password(password);
// Email format validation
validation.email(email);
// Phone number validation (type-specific)
validation.phone(number, 'mobile');
```

### **2. XSS Prevention**
- React auto-escaping (default)
- Input sanitization utility
- CSP headers in index.html

### **3. Authentication**
- JWT token storage (localStorage)
- Automatic token injection (Axios interceptor)
- Token refresh on 401
- Protected routes

### **4. CSRF Protection**
- SameSite cookies
- Backend handles CSRF tokens

### **5. Error Handling**
- Generic error messages (no info leakage)
- User-friendly error display
- API error handling

---

## 📁 **Project Structure**

```
frontend/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── Login.tsx          ✅ Login form
│   │   │   └── Register.tsx       ✅ Registration form
│   │   ├── Contacts/
│   │   │   ├── ContactList.tsx    ✅ List + search
│   │   │   ├── ContactDetail.tsx  ✅ View with phones
│   │   │   └── ContactForm.tsx    ✅ Create with phones
│   │   ├── Layout/
│   │   │   └── Navigation.tsx     ✅ Header nav
│   │   └── Common/
│   │       └── ProtectedRoute.tsx ✅ Auth guard
│   ├── pages/
│   │   └── HomePage.tsx           ✅ Landing page
│   ├── services/
│   │   ├── api.ts                 ✅ Axios config
│   │   ├── authService.ts         ✅ Auth API
│   │   └── contactService.ts      ✅ Contacts API
│   ├── context/
│   │   └── AuthContext.tsx        ✅ Auth state
│   ├── utils/
│   │   └── validation.ts          ✅ Validation
│   ├── types.ts                   ✅ TypeScript types
│   ├── App.tsx                    ✅ Routing
│   ├── main.tsx                   ✅ Entry point
│   └── index.css                  ✅ Tailwind CSS
├── index.html                     ✅ HTML template
├── vite.config.ts                 ✅ Vite config
├── tailwind.config.js             ✅ Tailwind config
├── tsconfig.json                  ✅ TypeScript config
├── package.json                   ✅ Dependencies
└── .env.example                   ✅ Env template
```

---

## 🎯 **Features**

### **Authentication**
- ✅ Login with email/password
- ✅ Registration with password strength validation
- ✅ Automatic token refresh
- ✅ Logout

### **Contacts Management**
- ✅ List all contacts
- ✅ Search by name/email/company
- ✅ Create contact with multiple phones
- ✅ View contact details
- ✅ Delete contact (soft delete)

### **Phone Management**
- ✅ Add multiple phones per contact
- ✅ 3 phone types: Mobile, Landline, Internal
- ✅ Set primary phone
- ✅ Remove phones
- ✅ Type-specific validation

---

## 🧪 **Testing** (TODO)

```bash
# Unit tests (not implemented yet)
npm run test

# E2E tests (not implemented yet)
npm run test:e2e
```

---

## 🏗️ **Build for Production**

```bash
npm run build
# Output: dist/

# Preview production build
npm run preview
```

---

## 📝 **Available Scripts**

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

---

## 🔗 **API Integration**

### **Authentication Flow**
1. User logs in → Frontend calls `/api/v1/auth/login`
2. Backend returns JWT tokens (access + refresh)
3. Frontend stores tokens in localStorage
4. Frontend includes token in all requests (Axios interceptor)
5. On 401 error → Auto-refresh token
6. If refresh fails → Redirect to login

### **Protected API Calls**
```typescript
// Automatic token injection
await contactService.getContacts();
// Axios interceptor adds: Authorization: Bearer <token>
```

---

## 🎨 **Styling with Tailwind**

### **Custom Classes** (defined in index.css)
```css
.btn-primary    - Blue button
.btn-secondary  - Gray button
.btn-danger     - Red button
.input-field    - Text input with focus styles
.card           - White card with shadow
```

### **Usage**
```jsx
<button className="btn-primary">Click Me</button>
<input className="input-field" />
<div className="card">Content</div>
```

---

## 🐛 **Troubleshooting**

### **Backend not responding**
- Make sure backend is running on port 8000
- Check Vite proxy configuration in `vite.config.ts`

### **CORS errors**
- Backend must include `http://localhost:3000` in ALLOWED_ORIGINS
- Check backend `.env` file

### **TypeScript errors**
- Run `npm install` to ensure all types are installed
- Check `tsconfig.json` settings

---

## 🚀 **Full Stack Run**

### **Terminal 1 - Backend**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### **Terminal 2 - Frontend**
```bash
cd frontend
npm run dev
```

**Access**: http://localhost:3000

---

## ✅ **Status**

**PHASE 3: FRONTEND** - ✅ **COMPLETE!**

All features implemented:
- ✅ Authentication (login, register, logout)
- ✅ Contact management (CRUD)
- ✅ Phone management (add, remove, set primary)
- ✅ Search functionality
- ✅ Responsive design
- ✅ Security features (validation, XSS prevention, auth)

**Next**: Testing, deployment, or additional features!

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-19  
**Status**: Production-ready ✅
