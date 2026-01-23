"""
Schemas package - exports all Pydantic schemas.
"""
from app.schemas.auth import ErrorResponse, MessageResponse, Token, TokenData, TokenPair
from app.schemas.contact import ContactCreate, ContactInDB, ContactResponse, ContactUpdate
from app.schemas.phone import (
    ContactCreateWithPhones,
    ContactPhoneCreate,
    ContactPhoneResponse,
    ContactPhoneUpdate,
    ContactWithPhones,
    PhoneCreate,
    PhoneResponse,
)
from app.schemas.user import (
    UserCreate,
    UserInDB,
    UserLogin,
    UserPasswordChange,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserPasswordChange",
    "UserResponse",
    "UserInDB",
    # Contact schemas
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    "ContactInDB",
    "ContactWithPhones",
    "ContactCreateWithPhones",
    # Phone schemas
    "PhoneCreate",
    "PhoneResponse",
    "ContactPhoneCreate",
    "ContactPhoneUpdate",
    "ContactPhoneResponse",
    # Auth schemas
    "Token",
    "TokenData",
    "TokenPair",
    "MessageResponse",
    "ErrorResponse",
]
