# Frontend Testing Guide

## 🧪 **Frontend Testing Setup** (Example)

This is a basic testing setup example for the React frontend.

---

## 📦 **Test Dependencies** (to install)

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom
```

---

## ⚙️ **Vitest Configuration**

Create `vitest.config.ts`:

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
```

---

## 🧪 **Example Tests**

### **1. Component Test - Login.test.tsx**

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Login } from '../components/Auth/Login';
import { AuthProvider } from '../context/AuthContext';

describe('Login Component', () => {
  it('renders login form', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );
    
    expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });
  
  it('shows validation error for invalid email', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );
    
    const emailInput = screen.getByPlaceholderText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
    });
  });
  
  it('shows validation error for empty password', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });
});
```

---

### **2. Validation Utils Test - validation.test.ts**

```typescript
import { describe, it, expect } from 'vitest';
import { validation } from '../utils/validation';

describe('Validation Utils', () => {
  describe('email validation', () => {
    it('accepts valid email', () => {
      expect(validation.email('test@example.com')).toBeNull();
    });
    
    it('rejects invalid email', () => {
      expect(validation.email('invalid')).not.toBeNull();
      expect(validation.email('test@')).not.toBeNull();
      expect(validation.email('@example.com')).not.toBeNull();
    });
    
    it('rejects empty email', () => {
      expect(validation.email('')).not.toBeNull();
    });
  });
  
  describe('password validation', () => {
    it('accepts strong password', () => {
      expect(validation.password('SecurePass123!')).toBeNull();
    });
    
    it('rejects short password', () => {
      expect(validation.password('Short1!')).not.toBeNull();
    });
    
    it('rejects password without uppercase', () => {
      expect(validation.password('lowercase123!')).not.toBeNull();
    });
    
    it('rejects password without lowercase', () => {
      expect(validation.password('UPPERCASE123!')).not.toBeNull();
    });
    
    it('rejects password without digit', () => {
      expect(validation.password('NoDigits!')).not.toBeNull();
    });
    
    it('rejects password without special char', () => {
      expect(validation.password('NoSpecial123')).not.toBeNull();
    });
  });
  
  describe('phone validation', () => {
    it('accepts valid mobile number', () => {
      expect(validation.phone('+48123456789', 'mobile')).toBeNull();
    });
    
    it('rejects mobile without plus', () => {
      expect(validation.phone('48123456789', 'mobile')).not.toBeNull();
    });
    
    it('accepts valid landline', () => {
      expect(validation.phone('171234567', 'landline')).toBeNull();
    });
    
    it('accepts valid internal', () => {
      expect(validation.phone('1234', 'internal')).toBeNull();
    });
    
    it('rejects invalid phone', () => {
      expect(validation.phone('invalid', 'mobile')).not.toBeNull();
    });
  });
});
```

---

### **3. Service Test - authService.test.ts**

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { authService } from '../services/authService';
import api from '../services/api';

vi.mock('../services/api');

describe('Auth Service', () => {
  beforeEach(() => {
    localStorage.clear();
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  describe('login', () => {
    it('stores tokens on successful login', async () => {
      const mockResponse = {
        data: {
          access_token: 'test_access_token',
          refresh_token: 'test_refresh_token',
          token_type: 'bearer'
        }
      };
      
      vi.mocked(api.post).mockResolvedValue(mockResponse);
      
      await authService.login('test@example.com', 'password');
      
      expect(localStorage.getItem('access_token')).toBe('test_access_token');
      expect(localStorage.getItem('refresh_token')).toBe('test_refresh_token');
    });
  });
  
  describe('logout', () => {
    it('removes tokens from localStorage', async () => {
      localStorage.setItem('access_token', 'test_token');
      localStorage.setItem('refresh_token', 'test_refresh');
      
      vi.mocked(api.post).mockResolvedValue({ data: { message: 'Logged out' } });
      
      await authService.logout();
      
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });
  });
  
  describe('isAuthenticated', () => {
    it('returns true when access token exists', () => {
      localStorage.setItem('access_token', 'test_token');
      expect(authService.isAuthenticated()).toBe(true);
    });
    
    it('returns false when no access token', () => {
      localStorage.clear();
      expect(authService.isAuthenticated()).toBe(false);
    });
  });
});
```

---

## 🚀 **Running Tests**

### **Add to package.json:**

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

### **Run tests:**

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Watch mode
npm test -- --watch
```

---

## 📊 **Coverage Goals**

- **Components**: 80%+
- **Utils/Services**: 90%+
- **Context**: 85%+

---

## 🔒 **Security Testing**

### **XSS Prevention Test**

```typescript
it('escapes user input to prevent XSS', () => {
  const xssPayload = '<script>alert("XSS")</script>';
  
  render(<ContactCard name={xssPayload} />);
  
  // React automatically escapes, so script should not execute
  expect(screen.getByText(xssPayload)).toBeInTheDocument();
  expect(document.querySelector('script')).toBeNull();
});
```

---

## ✅ **Test Checklist**

- [ ] All components have basic tests
- [ ] Utils have 90%+ coverage
- [ ] Services are mocked properly
- [ ] No console errors in tests
- [ ] Tests run in CI/CD

---

**Note**: These are example tests. Full implementation requires installing testing libraries and setting up test infrastructure.

**Status**: Example tests only (not implemented in codebase)  
**To implement**: Install dependencies and create test files
