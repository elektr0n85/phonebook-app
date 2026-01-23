"""
API dependencies for FastAPI endpoints.

Provides:
    - Database session dependency
    - Current user authentication
    - Admin role verification
    - Request context (IP, user agent)
"""
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

# OAuth2 scheme for JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        Current user instance
        
    Raises:
        HTTPException 401: If token is invalid or user not found
        
    Security:
        - Validates JWT signature
        - Checks token expiration
        - Verifies user exists in database
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await crud.user.get_by_email(db, email=email)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current active user (not locked, account active).
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Current active user instance
        
    Raises:
        HTTPException 400: If user account is inactive
        HTTPException 403: If user account is locked
        
    Security:
        - Checks is_active flag
        - Checks account lock status
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    if current_user.is_account_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to failed login attempts"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Get current admin user.
    
    Args:
        current_user: User from get_current_active_user dependency
        
    Returns:
        Current admin user instance
        
    Raises:
        HTTPException 403: If user is not admin
        
    Security: Admin-only endpoints use this dependency
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    
    return current_user


def get_client_ip(request: Request) -> str | None:
    """
    Extract client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address or None
        
    Security:
        - Checks X-Forwarded-For header (if behind proxy)
        - Falls back to direct connection IP
    """
    # Check if behind proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()
    
    # Direct connection
    if request.client:
        return request.client.host
    
    return None


def get_user_agent(request: Request) -> str | None:
    """
    Extract User-Agent from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User-Agent string or None
    """
    return request.headers.get("User-Agent")


# Type aliases for common dependencies
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(get_current_admin_user)]
