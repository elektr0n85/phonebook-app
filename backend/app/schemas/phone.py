"""
Pydantic schemas for Phone and ContactPhone - phone number validation and serialization.
"""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.phone import PhoneType


class PhoneBase(BaseModel):
    """Base phone schema."""
    
    phone_number: str = Field(..., min_length=3, max_length=20)
    phone_type: PhoneType


class PhoneCreate(PhoneBase):
    """
    Schema for creating a new phone number.
    
    Security:
        - Type-specific validation
        - Whitelist validation (digits only, + for mobile)
        - Length limits
    """
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str, info) -> str:
        """
        Validate phone number based on type.
        
        Rules:
            - Mobile: +XX XXX XXX XXX (10-15 digits with country code)
            - Landline: XX XX XXX (9-12 digits with area code)
            - Internal: XXXX (3-5 digits)
            
        Security: Whitelist validation (only allowed characters)
        """
        import re
        
        # Get phone_type from context
        phone_type = info.data.get("phone_type")
        
        # Remove spaces and dashes for validation
        cleaned = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if phone_type == PhoneType.MOBILE:
            # Mobile: must start with +, then 10-15 digits
            if not re.match(r'^\+[0-9]{10,15}$', cleaned):
                raise ValueError(
                    "Mobile number must start with + and contain 10-15 digits "
                    "(e.g., +48123456789)"
                )
        
        elif phone_type == PhoneType.LANDLINE:
            # Landline: 9-12 digits (area code + local number)
            if not re.match(r'^[0-9]{9,12}$', cleaned):
                raise ValueError(
                    "Landline number must contain 9-12 digits "
                    "(e.g., 171234567 for area code 17)"
                )
        
        elif phone_type == PhoneType.INTERNAL:
            # Internal: 3-5 digits
            if not re.match(r'^[0-9]{3,5}$', cleaned):
                raise ValueError(
                    "Internal extension must contain 3-5 digits "
                    "(e.g., 1234)"
                )
        
        return cleaned  # Store normalized version


class PhoneResponse(PhoneBase):
    """
    Schema for phone response.
    
    Includes:
        - Normalized phone_number (stored in DB)
        - Optional display format
        - Creation timestamp
    """
    
    id: int
    country_code: str | None
    area_code: str | None
    local_number: str | None
    extension: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PhoneInDB(PhoneResponse):
    """Schema for phone in database (internal use)."""
    
    updated_at: datetime


# ============================================================================
# ContactPhone Schemas (N:M relationship)
# ============================================================================

class ContactPhoneBase(BaseModel):
    """Base contact-phone relationship schema."""
    
    is_primary: bool = False
    label: str | None = Field(None, max_length=50)
    notes: str | None = Field(None, max_length=200)


class ContactPhoneCreate(ContactPhoneBase):
    """
    Schema for adding a phone to a contact.
    
    Two options:
        1. Reference existing phone_id
        2. Create new phone (phone_data)
    """
    
    phone_id: int | None = None  # Use existing phone
    phone_data: PhoneCreate | None = None  # Or create new phone
    
    @field_validator("phone_id")
    @classmethod
    def validate_phone_reference(cls, v, info):
        """Ensure either phone_id or phone_data is provided, not both."""
        phone_data = info.data.get("phone_data")
        
        if v is None and phone_data is None:
            raise ValueError("Either phone_id or phone_data must be provided")
        
        if v is not None and phone_data is not None:
            raise ValueError("Cannot specify both phone_id and phone_data")
        
        return v


class ContactPhoneUpdate(ContactPhoneBase):
    """Schema for updating contact-phone relationship metadata."""
    
    is_primary: bool | None = None
    label: str | None = None
    notes: str | None = None


class ContactPhoneResponse(ContactPhoneBase):
    """
    Schema for contact-phone relationship response.
    
    Includes the full phone details.
    """
    
    id: int
    phone: PhoneResponse  # Nested phone data
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Combined Schemas for Contact with Phones
# ============================================================================

class ContactWithPhones(BaseModel):
    """
    Extended contact schema with associated phones.
    
    Use this for GET /contacts/{id} to include phone numbers.
    """
    
    id: int
    name: str
    email: str | None
    address: str | None
    notes: str | None
    company: str | None
    position: str | None
    phones: list[ContactPhoneResponse]  # List of phones
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContactCreateWithPhones(BaseModel):
    """
    Schema for creating contact with phones in one request.
    
    Example:
        {
            "name": "Jan Kowalski",
            "email": "jan@example.com",
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
                }
            ]
        }
    """
    
    name: str = Field(..., min_length=1, max_length=100)
    email: str | None = None
    address: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)
    company: str | None = Field(None, max_length=200)
    position: str | None = Field(None, max_length=100)
    phones: list[ContactPhoneCreate] = Field(default_factory=list)
    
    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate name is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()
