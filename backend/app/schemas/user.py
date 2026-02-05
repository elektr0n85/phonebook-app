"""
Pydantic schemas for User model - input validation and serialization.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_password_strength(password: str) -> str:
    """
    Validate password meets security requirements.
    
    Requirements:
        - At least 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character
        
    Args:
        password: Password to validate
        
    Returns:
        Password if valid
        
    Raises:
        ValueError: If password doesn't meet requirements
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


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for user registration.
    
    Security:
        - Password strength enforced
        - Email validation
    """
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password must be at least 8 characters long"
    )
    
    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v: str) -> str:
        """Validate password strength using shared function."""
        return validate_password_strength(v)


class UserLogin(BaseModel):
    """
    Schema for user login.
    
    Security: Email validation only (password validated during authentication)
    """
    
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    
    Security: Email must be unique (checked in service layer)
    """
    
    email: EmailStr | None = None


class UserPasswordChange(BaseModel):
    """
    Schema for changing password.
    
    Security: Requires old password verification
    """
    
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("new_password")
    @classmethod
    def check_new_password_strength(cls, v: str) -> str:
        """Validate new password strength using shared function."""
        return validate_password_strength(v)


class UserResponse(UserBase):
    """
    Schema for user response (what API returns).
    
    Security:
        - Never return password_hash
        - Expose only safe fields
    """
    
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode (was orm_mode in Pydantic v1)


class UserInDB(UserResponse):
    """
    Schema for user in database (internal use only).
    
    Security: Includes password_hash (never exposed via API)
    """
    
    password_hash: str
    is_locked: bool
    failed_login_attempts: int
    locked_until: datetime | None
    updated_at: datetime
