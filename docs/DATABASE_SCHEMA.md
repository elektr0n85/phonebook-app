# Database Schema - Phonebook Application

## 📊 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SECURITY TABLES                               │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────┐
│       users           │  (Authentication & Authorization)
├───────────────────────┤
│ PK  id                │
│ UQ  email             │
│     password_hash     │
│     role              │  ('user' or 'admin')
│     is_active         │
│     is_locked         │
│     failed_attempts   │
│     locked_until      │
│     last_login        │
│     created_at        │
│     updated_at        │
└───────┬───────────────┘
        │
        │ 1:N (owns)
        ▼
┌───────────────────────┐
│    audit_logs         │  (Security Event Tracking)
├───────────────────────┤
│ PK  id                │
│ FK  user_id           │  → users.id (SET NULL)
│     action            │  ('login_success', 'contact_create', etc.)
│     resource_type     │
│     resource_id       │
│     ip_address        │
│     user_agent        │
│     details (JSON)    │
│     created_at        │
└───────────────────────┘

┌───────────────────────┐
│ password_reset_tokens │  (Password Recovery)
├───────────────────────┤
│ PK  id                │
│ FK  user_id           │  → users.id (CASCADE)
│ UQ  token             │
│     expires_at        │
│     is_used           │
│     created_at        │
└───────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                     FUNCTIONAL TABLES (3 tables)                     │
└─────────────────────────────────────────────────────────────────────┘

        ┌─────────────────┐
        │    users        │  (Also functional - ownership)
        │                 │
        └────────┬────────┘
                 │
                 │ 1:N (owns contacts)
                 ▼
        ┌─────────────────┐
        │    contacts     │  ✅ TABLE 1: Contact Information
        ├─────────────────┤
        │ PK  id          │
        │ FK  user_id     │  → users.id (CASCADE)
        │     name        │
        │     email       │
        │     address     │
        │     notes       │
        │     company     │
        │     position    │
        │     is_deleted  │
        │     deleted_at  │
        │     created_at  │
        │     updated_at  │
        └────────┬────────┘
                 │
                 │ N:M (has phones)
                 ▼
        ┌─────────────────┐
        │ contact_phones  │  ✅ TABLE 2: Contact-Phone Relationship
        ├─────────────────┤
        │ PK  id          │
        │ FK  contact_id  │  → contacts.id (CASCADE)
        │ FK  phone_id    │  → phones.id (CASCADE)
        │     is_primary  │
        │     label       │  ('Work', 'Personal', 'Home')
        │     notes       │
        │     created_at  │
        └────────┬────────┘
                 │
                 │ N:1 (references phone)
                 ▼
        ┌─────────────────┐
        │     phones      │  ✅ TABLE 3: Phone Numbers
        ├─────────────────┤
        │ PK  id          │
        │ UQ  phone_number│  (normalized: "+48123456789", "171234567", "1234")
        │     phone_type  │  ('mobile', 'landline', 'internal')
        │     country_code│  (e.g., "+48")
        │     area_code   │  (e.g., "17")
        │     local_number│  (e.g., "123 45 67")
        │     extension   │  (for internal)
        │     created_at  │
        │     updated_at  │
        └─────────────────┘
```

---

## 📋 Table Details

### **SECURITY TABLES** (Don't count towards requirement)

#### 1. `users` (Hybrid - Security + Functional)
- **Purpose**: Authentication, authorization, AND contact ownership
- **Security Features**: 
  - Password hashing (bcrypt)
  - Account lockout (5 failed attempts)
  - Role-based access control (user/admin)
- **Functional Role**: Owns contacts

#### 2. `audit_logs` (Security)
- **Purpose**: Security event tracking
- **Features**:
  - Immutable records
  - IP address tracking
  - JSON metadata

#### 3. `password_reset_tokens` (Security)
- **Purpose**: Secure password recovery
- **Features**:
  - Single-use tokens
  - Expiration (1 hour)
  - SHA-256 hashed

---

### **FUNCTIONAL TABLES** ✅ (3 tables - meets requirement!)

#### 1. `contacts` ✅
**Purpose**: Store contact information (people in phonebook)

**Fields**:
- `name`: Full name (required)
- `email`: Email address (optional)
- `company`: Company name
- `position`: Job title
- `address`: Physical address
- `notes`: Free-text notes
- `is_deleted`: Soft delete flag
- `user_id`: FK to users (who owns this contact)

**Example**:
```sql
INSERT INTO contacts (user_id, name, email, company, position)
VALUES (1, 'Jan Kowalski', 'jan@example.com', 'ACME Corp', 'CEO');
```

---

#### 2. `contact_phones` ✅ (N:M Relationship Table)
**Purpose**: Link contacts to phone numbers (many-to-many)

**Why N:M?**
- **Many contacts can share a phone** (e.g., office landline)
- **One contact can have multiple phones** (mobile, landline, internal)

**Fields**:
- `contact_id`: FK to contacts
- `phone_id`: FK to phones
- `is_primary`: Is this the primary phone for this contact?
- `label`: "Work", "Personal", "Home", etc.
- `notes`: Additional context

**Example**:
```sql
-- Jan Kowalski has 3 phones:
INSERT INTO contact_phones (contact_id, phone_id, is_primary, label)
VALUES 
  (1, 1, true, 'Personal'),   -- +48 123 456 789 (mobile)
  (1, 2, false, 'Office'),    -- 17 123 45 67 (landline)
  (1, 3, false, 'Extension'); -- 1234 (internal)

-- Anna Nowak shares the same office landline:
INSERT INTO contact_phones (contact_id, phone_id, label)
VALUES (2, 2, 'Office');  -- Same phone_id=2!
```

---

#### 3. `phones` ✅
**Purpose**: Store unique phone numbers (no duplicates)

**Phone Types**:
1. **Mobile** (`mobile`): International format with country code
   - Format: `+XX XXX XXX XXX`
   - Example: `+48123456789`
   
2. **Landline** (`landline`): National format with area code
   - Format: `XX XX XXX`
   - Example: `171234567` (Rzeszów)
   
3. **Internal** (`internal`): Company extension
   - Format: `XXXX`
   - Example: `1234`

**Fields**:
- `phone_number`: Normalized number (UNIQUE!)
- `phone_type`: Enum (mobile/landline/internal)
- `country_code`: For display formatting ("+48")
- `area_code`: For display formatting ("17")
- `local_number`: For display formatting ("123 45 67")
- `extension`: For internal phones

**Example**:
```sql
-- Mobile phone
INSERT INTO phones (phone_number, phone_type, country_code, local_number)
VALUES ('+48123456789', 'mobile', '+48', '123 456 789');

-- Landline (shared by multiple contacts)
INSERT INTO phones (phone_number, phone_type, area_code, local_number)
VALUES ('171234567', 'landline', '17', '123 45 67');

-- Internal extension
INSERT INTO phones (phone_number, phone_type, extension)
VALUES ('1234', 'internal', '1234');
```

---

## 🔍 Example Queries

### Get contact with all phones:
```sql
SELECT 
    c.name,
    c.email,
    p.phone_number,
    p.phone_type,
    cp.is_primary,
    cp.label
FROM contacts c
JOIN contact_phones cp ON c.id = cp.contact_id
JOIN phones p ON cp.phone_id = p.id
WHERE c.id = 1
ORDER BY cp.is_primary DESC;
```

### Find all contacts with a specific phone number:
```sql
SELECT c.name, c.email, cp.label
FROM contacts c
JOIN contact_phones cp ON c.id = cp.contact_id
JOIN phones p ON cp.phone_id = p.id
WHERE p.phone_number = '171234567';
```

### Get user's contacts with their primary phone:
```sql
SELECT 
    c.name,
    p.phone_number,
    p.phone_type
FROM contacts c
LEFT JOIN contact_phones cp ON c.id = cp.contact_id AND cp.is_primary = true
LEFT JOIN phones p ON cp.phone_id = p.id
WHERE c.user_id = 1 AND c.is_deleted = false;
```

---

## ✅ REQUIREMENT VERIFICATION

### **Original Requirement**: 3 tables for application functionality

**Our solution**:
1. ✅ **`contacts`** - Contact information
2. ✅ **`contact_phones`** - Contact-Phone relationships
3. ✅ **`phones`** - Phone numbers

**Plus security tables** (don't count):
- `users` (hybrid - also functional for ownership)
- `audit_logs` (pure security)
- `password_reset_tokens` (pure security)

**Total**: 3 functional tables + 3 security tables = **6 tables** 🎉

---

## 🔒 Security Features

### Row Level Security (RLS) - PostgreSQL
```sql
-- Users can only see their own contacts
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY contacts_isolation ON contacts
    FOR ALL
    USING (user_id = current_setting('app.current_user_id', true)::int);
```

### Constraints
- `users.email`: UNIQUE (no duplicate accounts)
- `phones.phone_number`: UNIQUE (no duplicate phones)
- `contact_phones(contact_id, phone_id)`: UNIQUE (can't link same phone twice)

### Cascading Deletes
- Delete user → Delete all their contacts → Delete contact_phones
- Delete phone → Delete all contact_phones referencing it
- **Contacts**: Soft delete (is_deleted flag, data recovery possible)

---

## 📝 Migration Notes

When creating Alembic migrations, ensure:
1. Create tables in order: `users` → `contacts` → `phones` → `contact_phones`
2. Add indexes on foreign keys
3. Enable RLS policies
4. Add check constraints for enum values

---

**Version**: 2.0 (N:M relationship model)  
**Last Updated**: 2026-01-19  
**Status**: ✅ Ready for implementation
