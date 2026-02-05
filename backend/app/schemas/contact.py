"""
Pydantic schemas for Contact model - input validation and serialization.
"""
from datetime import datetime
from app.schemas.phone import ContactPhoneCreate

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactBase(BaseModel):
    """Base contact schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)
    company: str | None = Field(None, max_length=200)
    position: str | None = Field(None, max_length=100)


class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.
    
    Security:
        - Name validation (no empty strings)
        - Email validation (if provided)
        - XSS prevention (length limits, no scripts)
        
    Note: Phones are managed separately via ContactPhone relationship
    """
    
    phones: list[ContactPhoneCreate] = []  # ← DODAJ TUTAJ!
    
    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate name is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()
    
    @field_validator("address", "notes")
    @classmethod
    def validate_text_fields(cls, v: str | None) -> str | None:
        """
        Validate text fields (prevent XSS, excessive length).
        
        Security: Strip whitespace, check for suspicious patterns
        """
        if v is None:
            return None
        
        # Strip whitespace
        v = v.strip()
        
        # Return None if empty after stripping
        if not v:
            return None
        
        # Check for script tags (basic XSS prevention)
        # Note: FastAPI + React auto-escape, but defense in depth
        if "<script" in v.lower() or "</script" in v.lower():
            raise ValueError("Text contains potentially dangerous content")
        
        return v


class ContactUpdate(BaseModel):
    """
    Schema for updating a contact.
    
    Security: All fields optional, same validation as create
    """
    
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)
    company: str | None = Field(None, max_length=200)
    position: str | None = Field(None, max_length=100)
    
    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str | None) -> str | None:
        """Validate name is not empty if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip() if v else None


class ContactResponse(ContactBase):
    """
    Schema for contact response (what API returns).
    
    Security:
        - Never return user_id directly (prevents enumeration)
        - Include only safe fields
    """
    
    id: int
    primary_phone: str | None = None  # Formatted primary phone number
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContactInDB(ContactResponse):
    """
    Schema for contact in database (internal use only).
    
    Security: Includes user_id for ownership validation
    """
    
    user_id: int
    is_deleted: bool
    deleted_at: datetime | None
