# 📞 Database Model Update - VARIANT B Implementation

## 🎯 **Problem Addressed**

**Original Requirement**: 3 tables for application functionality

**Previous Model**: 
- ❌ Only 1 functional table (`contacts` with embedded phone field)
- User, audit_logs, password_reset_tokens are security tables

**Solution**: Implement N:M relationship for contacts and phones

---

## ✅ **NEW Database Model (VARIANT B)**

### **FUNCTIONAL TABLES** (3 tables = meets requirement!)

#### 1️⃣ **`contacts`** - Contact Information
```sql
contacts (
    id, user_id, name, email, address, notes, 
    company, position, is_deleted, deleted_at,
    created_at, updated_at
)
```
**Purpose**: Store people's basic information

---

#### 2️⃣ **`phones`** - Phone Numbers (Unique)
```sql
phones (
    id, phone_number UNIQUE, phone_type,
    country_code, area_code, local_number, extension,
    created_at, updated_at
)
```
**Purpose**: Store unique phone numbers (no duplicates)

**Types**:
- 📱 `mobile`: `+48123456789` (country code + number)
- ☎️ `landline`: `171234567` (area code + local)
- 📞 `internal`: `1234` (extension)

---

#### 3️⃣ **`contact_phones`** - N:M Relationship
```sql
contact_phones (
    id, contact_id, phone_id, 
    is_primary, label, notes,
    created_at,
    UNIQUE(contact_id, phone_id)
)
```
**Purpose**: Link contacts to phones (many-to-many)

**Features**:
- `is_primary`: Mark one phone as primary per contact
- `label`: "Work", "Personal", "Home", etc.
- `notes`: Additional context

---

### **SECURITY TABLES** (don't count)
- `users` - Authentication + owns contacts
- `audit_logs` - Security events
- `password_reset_tokens` - Password recovery

---

## 📊 **Real-World Example**

```
Jan Kowalski (Contact 1):
  ├─ +48 123 456 789 (mobile, PRIMARY, "Personal")
  ├─ 17 123 45 67 (landline, "Office main line")
  └─ 1234 (internal, "My extension")

Anna Nowak (Contact 2):
  ├─ +48 987 654 321 (mobile, PRIMARY, "Personal")
  └─ 17 123 45 67 (landline, "Office main line")  <- SHARED with Jan!

Piotr Wiśniewski (Contact 3):
  ├─ +48 555 666 777 (mobile, PRIMARY)
  ├─ 17 123 45 67 (landline, "Office")  <- SHARED!
  └─ 1235 (internal, "My extension")
```

**Phone `17 123 45 67` is shared by 3 contacts!** ✅

---

## 🔧 **Implementation Changes**

### **Models Updated**
✅ `app/models/contact.py` - Removed `phone` field, added `phones` relationship  
✅ `app/models/phone.py` - NEW model (PhoneType enum, normalize methods)  
✅ `app/models/contact_phone.py` - NEW model (N:M junction table)  
✅ `app/models/__init__.py` - Export new models  

### **Schemas Updated**
✅ `app/schemas/contact.py` - Removed phone validation  
✅ `app/schemas/phone.py` - NEW schemas with type-specific validation  
✅ `app/schemas/__init__.py` - Export new schemas  

### **Documentation Created**
✅ `docs/DATABASE_SCHEMA.md` - Complete ER diagram + examples  
✅ `backend/README.md` - Updated with new structure  

---

## 🎓 **Benefits of VARIANT B**

### ✅ **Meets Requirements**
- 3 functional tables: contacts, phones, contact_phones ✅
- Plus 3 security tables (users, audit_logs, password_reset_tokens)

### ✅ **Real-World Scenarios**
- Multiple people sharing office landline ✅
- One person with mobile + landline + extension ✅
- No duplicate phone numbers in database ✅

### ✅ **Data Integrity**
- Phone uniqueness enforced ✅
- Can't link same phone to same contact twice ✅
- Cascading deletes properly configured ✅

### ✅ **Flexibility**
- Easy to add phone metadata (label, notes) ✅
- Primary phone marking per contact ✅
- Can find all contacts for a phone number ✅

---

## 📋 **Next Steps**

### ⏳ **TODO in Phase 3.2**
1. **CRUD Operations**
   - `crud/phone.py` - Get/create phone, find by number
   - `crud/contact_phone.py` - Link phones to contacts
   - Update `crud/contact.py` - Handle phones in contact CRUD

2. **API Endpoints**
   - `POST /api/v1/contacts` - Accept phones array
   - `GET /api/v1/contacts/{id}` - Return with phones
   - `POST /api/v1/contacts/{id}/phones` - Add phone to contact
   - `DELETE /api/v1/contacts/{id}/phones/{phone_id}` - Remove phone

3. **Database Migration**
   - Alembic migration script to create tables
   - Indexes on foreign keys
   - Check constraints for phone types

4. **Tests**
   - Test phone validation (mobile/landline/internal)
   - Test N:M relationship
   - Test shared phones scenario

---

## 💡 **Validation Examples**

### ✅ **Valid Phone Numbers**

**Mobile**:
```python
phone = PhoneCreate(
    phone_number="+48123456789",
    phone_type=PhoneType.MOBILE
)
# Stored as: "+48123456789"
# Displayed as: "+48 123 456 789"
```

**Landline**:
```python
phone = PhoneCreate(
    phone_number="17 123 45 67",  # Accepts spaces
    phone_type=PhoneType.LANDLINE
)
# Stored as: "171234567" (normalized)
# Displayed as: "(17) 123 45 67"
```

**Internal**:
```python
phone = PhoneCreate(
    phone_number="1234",
    phone_type=PhoneType.INTERNAL
)
# Stored as: "1234"
# Displayed as: "ext. 1234"
```

### ❌ **Invalid Phone Numbers**

```python
# Mobile without country code
PhoneCreate(phone_number="123456789", phone_type=PhoneType.MOBILE)
# Error: "Mobile number must start with +"

# Landline too short
PhoneCreate(phone_number="12345", phone_type=PhoneType.LANDLINE)
# Error: "Landline number must contain 9-12 digits"

# Internal too long
PhoneCreate(phone_number="123456", phone_type=PhoneType.INTERNAL)
# Error: "Internal extension must contain 3-5 digits"
```

---

## 🚀 **Quick API Usage Example** (once implemented)

### Create contact with multiple phones:
```bash
POST /api/v1/contacts
{
  "name": "Jan Kowalski",
  "email": "jan@example.com",
  "company": "ACME Corp",
  "phones": [
    {
      "phone_data": {
        "phone_number": "+48123456789",
        "phone_type": "mobile"
      },
      "is_primary": true,
      "label": "Personal"
    },
    {
      "phone_data": {
        "phone_number": "171234567",
        "phone_type": "landline"
      },
      "label": "Office"
    },
    {
      "phone_data": {
        "phone_number": "1234",
        "phone_type": "internal"
      },
      "label": "Extension"
    }
  ]
}
```

### Get contact with phones:
```bash
GET /api/v1/contacts/1

Response:
{
  "id": 1,
  "name": "Jan Kowalski",
  "email": "jan@example.com",
  "company": "ACME Corp",
  "phones": [
    {
      "id": 1,
      "phone": {
        "id": 1,
        "phone_number": "+48123456789",
        "phone_type": "mobile"
      },
      "is_primary": true,
      "label": "Personal"
    },
    {
      "id": 2,
      "phone": {
        "id": 2,
        "phone_number": "171234567",
        "phone_type": "landline"
      },
      "is_primary": false,
      "label": "Office"
    }
  ]
}
```

---

**Status**: ✅ **Models & Schemas Complete**  
**Next**: Implement CRUD operations and API endpoints  
**Version**: 2.0 (N:M Model)  
**Date**: 2026-01-19
