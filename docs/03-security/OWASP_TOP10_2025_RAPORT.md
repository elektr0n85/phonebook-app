# 🛡️ Raport Bezpieczeństwa OWASP Top 10:2025
## Aplikacja Phonebook

**Data:** Luty 2025  
**Wersja aplikacji:** 5.0  
**Autor audytu:** Claude AI

---

## 📋 Podsumowanie

| Pozycja | Zagrożenie | Status | Ocena |
|---------|-----------|--------|-------|
| A01 | Broken Access Control | ✅ Chronione | 🟢 Dobry |
| A02 | Security Misconfiguration | ✅ Chronione | 🟢 Dobry |
| A03 | Software Supply Chain Failures | ⚠️ Częściowo | 🟡 Wymaga uwagi |
| A04 | Cryptographic Failures | ✅ Chronione | 🟢 Dobry |
| A05 | Injection | ✅ Chronione | 🟢 Dobry |
| A06 | Insecure Design | ✅ Chronione | 🟢 Dobry |
| A07 | Authentication Failures | ✅ Chronione | 🟢 Dobry |
| A08 | Software/Data Integrity Failures | ✅ Chronione | 🟢 Dobry |
| A09 | Logging & Alerting Failures | ✅ Chronione | 🟢 Dobry |
| A10 | Mishandling of Exceptional Conditions | ✅ Chronione | 🟢 Dobry |

---

## A01:2025 - Broken Access Control (Złamana Kontrola Dostępu)

### 🎯 Opis zagrożenia
Broken Access Control pozostaje na 1. miejscu listy OWASP 2025. Obejmuje sytuacje, gdy użytkownicy mogą działać poza przydzielonymi im uprawnieniami - np. uzyskać dostęp do danych innych użytkowników.

### ✅ Jak aplikacja się chroni

**1. Weryfikacja własności zasobów (Ownership Check)**

Każdy kontakt jest powiązany z `user_id`. Przy pobieraniu danych sprawdzamy własność:

```python
# backend/app/crud/contact.py
async def get_multi_by_owner(
    self,
    db: AsyncSession,
    *,
    user_id: int,  # ← tylko kontakty tego użytkownika
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False
) -> list[Contact]:
    stmt = select(Contact).where(Contact.user_id == user_id)
    
    if not include_deleted:
        stmt = stmt.where(Contact.is_deleted == False)
    # ...
```

**2. Dependency Injection dla uwierzytelniania**

Każdy chroniony endpoint używa `CurrentUser` dependency:

```python
# backend/app/api/deps.py
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    if current_user.is_account_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked"
        )
    
    return current_user

# Alias używany w endpointach
CurrentUser = Annotated[User, Depends(get_current_active_user)]
```

**3. Oddzielne uprawnienia administratora**

```python
# backend/app/api/deps.py
async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user

AdminUser = Annotated[User, Depends(get_current_admin_user)]
```

**4. Weryfikacja własności przy operacjach**

```python
# backend/app/api/v1/contacts.py
@router.get("/{contact_id}", response_model=ContactWithPhones)
async def get_contact(
    *,
    db: DatabaseSession,
    current_user: CurrentUser,
    contact_id: int
) -> ContactWithPhones:
    contact = await crud.contact.get_with_phones(db, id=contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # ← KLUCZOWE: sprawdzenie własności
    if contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    # ...
```

### 📊 Ocena: 🟢 DOBRY

---

## A02:2025 - Security Misconfiguration (Błędna Konfiguracja)

### 🎯 Opis zagrożenia
Awansowało z pozycji #5 na #2. Obejmuje nieprawidłowe ustawienia bezpieczeństwa: domyślne hasła, zbędne funkcje, verbose error messages.

### ✅ Jak aplikacja się chroni

**1. Wyłączona dokumentacja API w produkcji**

```python
# backend/app/main.py
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs" if settings.DEBUG else None,     # ← wyłączone w produkcji
    redoc_url="/redoc" if settings.DEBUG else None,   # ← wyłączone w produkcji
)
```

**2. Nagłówki bezpieczeństwa HTTP**

```python
# backend/app/main.py
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Zapobieganie MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Zapobieganie clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Ochrona XSS
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # HSTS (tylko produkcja)
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "frame-ancestors 'none';"
    )
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Wyłączenie niebezpiecznych funkcji
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), payment=()"
    )
    
    return response
```

**3. Restrykcyjna konfiguracja CORS**

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # ← whitelist, nie "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # ← jawna lista
    allow_headers=["Authorization", "Content-Type"],  # ← jawna lista
    max_age=3600,
)
```

**4. Konfiguracja przez zmienne środowiskowe**

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION"  # ← wymusza zmianę
    DEBUG: bool = False  # ← domyślnie wyłączony
    
    model_config = SettingsConfigDict(
        env_file=".env",  # ← z pliku .env
    )
```

### 📊 Ocena: 🟢 DOBRY

---

## A03:2025 - Software Supply Chain Failures (Błędy Łańcucha Dostaw) 🆕

### 🎯 Opis zagrożenia
**NOWA kategoria w 2025!** Rozszerza poprzednie "Vulnerable and Outdated Components" na cały łańcuch dostaw oprogramowania: zależności, systemy budowania, dystrybucję.

### ⚠️ Obecny stan

**Co jest zrobione:**

```text
# backend/requirements.txt - wersje są pinowane
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.2
```

**Narzędzia bezpieczeństwa w projekcie:**

```text
# backend/requirements.txt
bandit==1.7.6  # ← analiza statyczna kodu Python
```

### ⚠️ Rekomendacje do wdrożenia

1. **Regularne skanowanie zależności:**
   ```bash
   pip install pip-audit
   pip-audit  # skanuje podatności w zależnościach
   ```

2. **Automatyczne aktualizacje (Dependabot/Renovate)**

3. **Weryfikacja integralności:**
   ```bash
   pip install --require-hashes -r requirements.txt
   ```

4. **SBOM (Software Bill of Materials):**
   ```bash
   pip install cyclonedx-bom
   cyclonedx-py -r requirements.txt -o sbom.json
   ```

### 📊 Ocena: 🟡 WYMAGA UWAGI

---

## A04:2025 - Cryptographic Failures (Błędy Kryptograficzne)

### 🎯 Opis zagrożenia
Spadek z #2 na #4. Obejmuje brak szyfrowania, słabe algorytmy, wyciek kluczy.

### ✅ Jak aplikacja się chroni

**1. Bezpieczne hashowanie haseł (bcrypt)**

```python
# backend/app/core/security.py
from passlib.context import CryptContext

# bcrypt z cost factor 12 (domyślnie)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Security: bcrypt automatycznie dodaje sól i używa cost factor 12
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Security: Constant-time comparison (odporność na timing attack)
    """
    return pwd_context.verify(plain_password, hashed_password)
```

**2. Bezpieczne tokeny JWT**

```python
# backend/app/core/security.py
def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Security:
        - Krótki czas życia (30 minut domyślnie)
        - Algorytm HS256
        - Secret key z zmiennej środowiskowej
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY,       # ← klucz z .env
        algorithm=settings.ALGORITHM  # ← HS256
    )
    return encoded_jwt
```

**3. Bezpieczne tokeny resetowania hasła**

```python
# backend/app/api/v1/auth.py
import secrets

# 256-bit entropy (praktycznie niemożliwe do zgadnięcia)
token = secrets.token_urlsafe(32)

# Token jest hashowany przed zapisem do bazy
await crud.user.set_reset_token(db, user=user, token=token)
```

**4. HTTPS wymuszony w produkcji**

```python
# Nagłówek HSTS
response.headers["Strict-Transport-Security"] = (
    "max-age=31536000; includeSubDomains; preload"
)
```

### 📊 Ocena: 🟢 DOBRY

---

## A05:2025 - Injection (Wstrzykiwanie)

### 🎯 Opis zagrożenia
Spadek z #3 na #5, ale nadal jedno z najniebezpieczniejszych zagrożeń. Obejmuje SQL Injection, XSS, Command Injection.

### ✅ Jak aplikacja się chroni

**1. SQLAlchemy ORM - parametryzowane zapytania**

```python
# backend/app/crud/contact.py
async def search(
    self,
    db: AsyncSession,
    *,
    user_id: int,
    query: str,
    skip: int = 0,
    limit: int = 50
) -> list[Contact]:
    """
    Security:
        - SQL injection prevented by ORM
        - Case-insensitive search używa ilike() nie raw SQL
    """
    search_pattern = f"%{query}%"
    
    stmt = (
        select(Contact)
        .where(
            Contact.user_id == user_id,
            Contact.is_deleted == False,
            or_(
                Contact.name.ilike(search_pattern),   # ← ORM escape
                Contact.email.ilike(search_pattern),
                Contact.company.ilike(search_pattern),
            )
        )
    )
```

**NIGDY nie robimy:**
```python
# ❌ ZŁE - podatne na SQL Injection
query = f"SELECT * FROM contacts WHERE name LIKE '%{user_input}%'"
```

**2. Walidacja danych wejściowych (Pydantic)**

```python
# backend/app/schemas/contact.py
class ContactCreate(ContactBase):
    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @field_validator("address", "notes")
    @classmethod
    def validate_text_fields(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        
        # Podstawowa ochrona XSS
        if "<script" in v.lower() or "</script" in v.lower():
            raise ValueError("Text contains potentially dangerous content")
        
        return v
```

**3. Limity długości pól**

```python
# backend/app/schemas/contact.py
class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)
```

**4. Content Security Policy (ochrona XSS)**

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self'; "  # ← blokuje inline scripts
)
```

### 📊 Ocena: 🟢 DOBRY

---

## A06:2025 - Insecure Design (Niebezpieczny Projekt)

### 🎯 Opis zagrożenia
Spadek z #4 na #6. Obejmuje błędy architektoniczne, słabe przepływy (np. reset hasła), brak threat modeling.

### ✅ Jak aplikacja się chroni

**1. Bezpieczny przepływ resetowania hasła**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Użytkownik podaje email                                   │
│    ↓                                                         │
│ 2. Serwer generuje token (secrets.token_urlsafe(32))        │
│    ↓                                                         │
│ 3. Token hashowany przed zapisem (bcrypt)                   │
│    ↓                                                         │
│ 4. Email z linkiem (token w URL, nie w bazie plain)         │
│    ↓                                                         │
│ 5. Link wygasa po 1 godzinie                                │
│    ↓                                                         │
│ 6. Token jednorazowy (kasowany po użyciu)                   │
│    ↓                                                         │
│ 7. Powiadomienie email o zmianie hasła                      │
└─────────────────────────────────────────────────────────────┘
```

**2. Zapobieganie enumeracji użytkowników**

```python
# backend/app/api/v1/auth.py
@router.post("/forgot-password")
async def forgot_password(...):
    # ZAWSZE ta sama odpowiedź - nie ujawnia czy email istnieje
    response_message = "If an account with this email exists, a password reset link has been sent."
    
    user = await crud.user.get_by_email(db, email=body.email)
    
    if not user:
        return MessageResponse(message=response_message)  # ← ta sama odpowiedź
    
    # ... wysłanie emaila ...
    
    return MessageResponse(message=response_message)  # ← ta sama odpowiedź
```

**3. Limity zasobów**

```python
# backend/app/api/v1/contacts.py
MAX_CONTACTS_PER_USER = 1000

# backend/app/crud/contact.py
async def get_multi_by_owner(...):
    limit = min(limit, 100)  # ← cap na limit
```

**4. Soft delete (możliwość odzyskania danych)**

```python
# backend/app/models/contact.py
class Contact(Base):
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    
    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
```

### 📊 Ocena: 🟢 DOBRY

---

## A07:2025 - Identification and Authentication Failures

### 🎯 Opis zagrożenia
Bez zmian na pozycji #7. Obejmuje słabe hasła, brak ochrony przed brute force, błędną implementację sesji.

### ✅ Jak aplikacja się chroni

**1. Silna polityka haseł**

```python
# backend/app/schemas/user.py
def validate_password_strength(password: str) -> str:
    """
    Wymagania:
        - Minimum 8 znaków
        - Minimum 1 wielka litera
        - Minimum 1 mała litera
        - Minimum 1 cyfra
        - Minimum 1 znak specjalny
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")
    
    special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_characters for c in password):
        raise ValueError("Password must contain at least one special character")
    
    return password
```

**2. Blokada konta po nieudanych próbach**

```python
# backend/app/models/user.py
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

def is_account_locked(self) -> bool:
    if self.locked_until and self.locked_until > datetime.utcnow():
        return True
    return False

def record_failed_login(self) -> None:
    self.failed_login_attempts += 1
    if self.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
        self.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
```

**3. Generyczna odpowiedź przy błędnym logowaniu**

```python
# backend/app/api/v1/auth.py
if not user:
    # Nie ujawniamy czy użytkownik istnieje
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",  # ← ogólny komunikat
    )
```

**4. Krótki czas życia tokenów**

```python
# backend/app/core/config.py
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30   # ← 30 minut
REFRESH_TOKEN_EXPIRE_DAYS: int = 7      # ← 7 dni
```

**5. Rozdzielenie tokenów dostępu i odświeżania**

```python
# backend/app/core/security.py
def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    to_encode.update({
        "exp": expire, 
        "type": "refresh"  # ← oznaczenie typu
    })
    return jwt.encode(to_encode, settings.SECRET_KEY)

def verify_token_type(payload: dict, expected_type: str = "access") -> bool:
    token_type = payload.get("type", "access")
    return token_type == expected_type  # ← walidacja typu
```

### 📊 Ocena: 🟢 DOBRY

---

## A08:2025 - Software and Data Integrity Failures

### 🎯 Opis zagrożenia
Bez zmian na pozycji #8. Obejmuje brak weryfikacji integralności kodu, niezaufane źródła aktualizacji.

### ✅ Jak aplikacja się chroni

**1. Pinowane wersje zależności**

```text
# backend/requirements.txt
fastapi==0.109.0       # ← dokładna wersja
sqlalchemy==2.0.25
python-jose[cryptography]==3.3.0
```

**2. Walidacja tokenów JWT**

```python
# backend/app/core/security.py
def decode_token(token: str) -> dict[str, Any]:
    """
    Security:
        - Validates signature (sprawdza podpis)
        - Checks expiration (sprawdza wygaśnięcie)
        - Prevents tampering (zapobiega modyfikacji)
    """
    payload = jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    return payload
```

**3. Docker z oficjalnych obrazów**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim  # ← oficjalny obraz Python
```

### 📊 Ocena: 🟢 DOBRY

---

## A09:2025 - Security Logging and Monitoring Failures

### 🎯 Opis zagrożenia
Bez zmian na pozycji #9. Bez logowania ataki nie mogą być wykryte ani śledzone.

### ✅ Jak aplikacja się chroni

**1. Kompleksowy system audit logów**

```python
# backend/app/models/audit_log.py
class AuditAction:
    # Authentication
    REGISTER = "register"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    
    # Contacts
    CONTACT_CREATE = "contact_create"
    CONTACT_UPDATE = "contact_update"
    CONTACT_DELETE = "contact_delete"
    CONTACT_VIEW = "contact_view"
    
    # Admin
    USER_DEACTIVATE = "user_deactivate"
    USER_ACTIVATE = "user_activate"
```

**2. Struktura logu audytowego**

```python
# backend/app/models/audit_log.py
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(50))
    resource_type: Mapped[str | None] = mapped_column(String(50))
    resource_id: Mapped[int | None]
    ip_address: Mapped[str | None] = mapped_column(String(45))  # ← IPv6
    user_agent: Mapped[str | None] = mapped_column(String(500))
    details: Mapped[dict | None] = mapped_column(JSON)  # ← dodatkowe dane
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

**3. Logowanie wszystkich prób logowania**

```python
# backend/app/api/v1/auth.py
if existing_user:
    # Użytkownik istnieje ale złe hasło
    await crud.audit_log.create_log(
        db,
        user_id=existing_user.id,
        action=AuditAction.LOGIN_FAILED,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"reason": "invalid_password"}
    )
else:
    # Użytkownik nie istnieje
    await crud.audit_log.create_log(
        db,
        user_id=None,
        action=AuditAction.LOGIN_FAILED,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"reason": "user_not_found", "email": email}
    )
```

**4. Ekstrakcja adresu IP (obsługa proxy)**

```python
# backend/app/api/deps.py
def get_client_ip(request: Request) -> str | None:
    # Sprawdź X-Forwarded-For (za proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Bezpośrednie połączenie
    if request.client:
        return request.client.host
    
    return None
```

**5. Zapytania do logów dla analizy bezpieczeństwa**

```python
# backend/app/crud/audit_log.py
async def count_user_action(
    self,
    db: AsyncSession,
    *,
    user_id: int,
    action: str,
    since: datetime
) -> int:
    """
    Use case: Rate limiting - policz nieudane logowania w ostatnich 15 min
    """
    stmt = select(func.count(AuditLog.id)).where(
        and_(
            AuditLog.user_id == user_id,
            AuditLog.action == action,
            AuditLog.created_at >= since
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()
```

### 📊 Ocena: 🟢 DOBRY

---

## A10:2025 - Mishandling of Exceptional Conditions 🆕

### 🎯 Opis zagrożenia
**NOWA kategoria w 2025!** Obejmuje nieprawidłową obsługę błędów: wyciek stack trace, fail-open logic, crash przy nieoczekiwanych danych.

### ✅ Jak aplikacja się chroni

**1. Generyczne komunikaty błędów dla użytkownika**

```python
# backend/app/api/v1/auth.py
# ❌ ZŁE - ujawnia szczegóły
# raise HTTPException(detail="User admin@example.com not found in database")

# ✅ DOBRE - ogólny komunikat
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials"  # ← nie ujawnia czy user istnieje
)
```

**2. Fail-secure przy weryfikacji tokena**

```python
# backend/app/api/deps.py
async def get_current_user(...) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception  # ← fail secure
            
    except JWTError:
        raise credentials_exception  # ← fail secure
    
    user = await crud.user.get_by_email(db, email=email)
    
    if user is None:
        raise credentials_exception  # ← fail secure
    
    return user
```

**3. Graceful degradation dla email**

```python
# backend/app/core/email.py
def _get_fast_mail():
    """
    Lazy-load FastMail - aplikacja działa nawet bez SMTP.
    """
    # Sprawdź czy SMTP skonfigurowany
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("⚠️  SMTP not configured - email sending disabled")
        return None  # ← graceful degradation
    
    # Sprawdź czy domena jest prawidłowa
    mail_domain = settings.MAIL_FROM.split('@')[1].lower()
    invalid_tlds = ['.local', '.localhost', '.test']
    if any(mail_domain.endswith(tld) for tld in invalid_tlds):
        print(f"⚠️  MAIL_FROM domain '{mail_domain}' is invalid")
        return None  # ← graceful degradation
    
    try:
        # ... konfiguracja ...
        return FastMail(email_config)
    except Exception as e:
        print(f"⚠️  Failed to configure email: {e}")
        return None  # ← aplikacja nadal działa
```

**4. Walidacja limitów w zapytaniach**

```python
# backend/app/crud/contact.py
async def get_multi_by_owner(..., limit: int = 100):
    limit = min(limit, 100)  # ← cap chroni przed DoS
```

**5. Try-catch z odpowiednim logowaniem**

```python
# backend/app/core/email.py
try:
    await fast_mail.send_message(message)
    return True
except Exception as e:
    print(f"❌ Failed to send email to {email}: {e}")  # ← log wewnętrznie
    return False  # ← nie crash, tylko False
```

### 📊 Ocena: 🟢 DOBRY

---

## 📈 Podsumowanie i Rekomendacje

### ✅ Mocne strony aplikacji

1. **Solidna kontrola dostępu** - każdy zasób powiązany z użytkownikiem
2. **Bezpieczna kryptografia** - bcrypt, JWT z krótkim czasem życia
3. **Kompleksowe logowanie** - audit log dla wszystkich operacji
4. **Ochrona przed injection** - ORM, walidacja Pydantic
5. **Bezpieczny reset hasła** - tokeny jednorazowe, hashowane
6. **Nagłówki bezpieczeństwa** - CSP, HSTS, X-Frame-Options

### ⚠️ Rekomendacje do wdrożenia

| Priorytet | Rekomendacja | Kategoria OWASP |
|-----------|--------------|-----------------|
| 🔴 Wysoki | Wdrożenie skanowania zależności (pip-audit) | A03 |
| 🔴 Wysoki | Automatyczne aktualizacje (Dependabot) | A03 |
| 🟡 Średni | Rate limiting na endpointach | A07 |
| 🟡 Średni | Token blacklist dla wylogowania | A07 |
| 🟢 Niski | SBOM dla audytu | A03 |
| 🟢 Niski | Alerting przy anomaliach w logach | A09 |

### 🏆 Ocena końcowa: **8.5/10**

Aplikacja implementuje większość najlepszych praktyk bezpieczeństwa OWASP Top 10:2025. Główny obszar do poprawy to **A03: Software Supply Chain** - wdrożenie automatycznego skanowania i aktualizacji zależności.

---

*Raport wygenerowany na podstawie analizy kodu źródłowego aplikacji Phonebook.*
