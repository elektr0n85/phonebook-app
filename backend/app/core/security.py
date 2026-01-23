"""
Security utilities for authentication and authorization.
Includes JWT token management and password hashing.
"""
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context (bcrypt with default cost=12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
        
    Security: bcrypt automatically adds salt and uses cost factor 12
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
        
    Security: Constant-time comparison (timing attack resistant)
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in token (e.g., {"sub": user_email})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
        
    Security:
        - Short expiration (30 minutes by default)
        - HS256 algorithm (symmetric)
        - Secret key from environment variable
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid, expired, or tampered with
        
    Security:
        - Validates signature
        - Checks expiration
        - Prevents tampering
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        # Re-raise to let caller handle (don't log sensitive data)
        raise e


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a JWT refresh token (longer expiration).
    
    Args:
        data: Payload data to encode in token
        
    Returns:
        Encoded JWT refresh token
        
    Security:
        - Longer expiration (7 days by default)
        - Used only to obtain new access tokens
        - Should be stored securely (httpOnly cookie)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token_type(payload: dict[str, Any], expected_type: str = "access") -> bool:
    """
    Verify token type (access vs refresh).
    
    Args:
        payload: Decoded JWT payload
        expected_type: Expected token type ("access" or "refresh")
        
    Returns:
        True if token type matches expected type
        
    Security: Prevents using refresh tokens as access tokens and vice versa
    """
    token_type = payload.get("type", "access")  # Default to access if not specified
    return token_type == expected_type
