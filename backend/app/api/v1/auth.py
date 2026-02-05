"""
Authentication API endpoints.

Endpoints:
    POST /auth/register - Register new user
    POST /auth/login - Login with email/password
    POST /auth/logout - Logout (invalidate token)
    POST /auth/refresh - Refresh access token
    POST /auth/forgot-password - Request password reset
    POST /auth/reset-password - Reset password with token
"""
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import DatabaseSession, CurrentUser, get_client_ip, get_user_agent
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.core.email import send_password_reset_email, send_password_changed_notification
from app.models.audit_log import AuditAction
from app.schemas.auth import (
    MessageResponse, 
    Token, 
    TokenPair,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    *,
    db: DatabaseSession,
    request: Request,
    user_in: UserCreate
) -> UserResponse:
    """
    Register a new user.
    
    Security:
        - Password strength validation (Pydantic schema)
        - Email uniqueness check
        - Password hashing (bcrypt)
        - Audit log created
        
    Rate limit: 3 registrations per hour per IP (TODO: implement)
    """
    # Check if user already exists
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await crud.user.create(db, obj_in=user_in)
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=user.id,
        action=AuditAction.REGISTER,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return user


@router.post("/login", response_model=TokenPair)
async def login(
    *,
    db: DatabaseSession,
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenPair:
    """
    Login with email and password (OAuth2 compatible).
    
    Args:
        form_data: OAuth2 form with username (email) and password
        
    Returns:
        Access token and refresh token
        
    Security:
        - Rate limiting (5 attempts per 15 minutes) - TODO: implement
        - Account lockout after 5 failed attempts
        - Generic error message (prevents user enumeration)
        - Audit log for success and failure
        
    Note: OAuth2PasswordRequestForm uses 'username' field, but we treat it as email
    """
    email = form_data.username  # OAuth2 standard uses 'username'
    password = form_data.password
    
    # Authenticate user
    user = await crud.user.authenticate(db, email=email, password=password)
    
    if not user:
        # Failed login - try to find user for logging
        existing_user = await crud.user.get_by_email(db, email=email)
        
        if existing_user:
            # User exists but wrong password - record failed attempt
            await crud.user.record_failed_login(db, user=existing_user)
            
            # Audit log - failed login
            await crud.audit_log.create_log(
                db,
                user_id=existing_user.id,
                action=AuditAction.LOGIN_FAILED,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                details={"reason": "invalid_password"}
            )
        else:
            # User doesn't exist - still log for security monitoring
            await crud.audit_log.create_log(
                db,
                user_id=None,
                action=AuditAction.LOGIN_FAILED,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                details={"reason": "user_not_found", "email": email}
            )
        
        # Generic error message (don't reveal if user exists)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if user.is_account_locked():
        await crud.audit_log.create_log(
            db,
            user_id=user.id,
            action=AuditAction.LOGIN_FAILED,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"reason": "account_locked"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked until {user.locked_until}. Please try again later."
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account"
        )
    
    # Successful login - update last login time
    await crud.user.update_last_login(db, user=user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Audit log - successful login
    await crud.audit_log.create_log(
        db,
        user_id=user.id,
        action=AuditAction.LOGIN_SUCCESS,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    *,
    db: DatabaseSession,
    request: Request,
    current_user: CurrentUser
) -> MessageResponse:
    """
    Logout current user.
    
    Note: JWT tokens are stateless, so we can't truly "invalidate" them.
    This endpoint exists for:
        - Audit logging
        - Client-side token removal
        - Future token blacklist implementation
        
    Security:
        - Audit log created
        - Client should remove token from storage
    """
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action=AuditAction.LOGOUT,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return MessageResponse(message="Successfully logged out")


@router.post("/refresh", response_model=Token)
async def refresh_token(
    *,
    db: DatabaseSession,
    request: Request,
    refresh_token: str
) -> Token:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token (from login response)
        
    Returns:
        New access token
        
    Security:
        - Validates refresh token signature and expiration
        - Checks user still exists and is active
        - Does NOT issue new refresh token (use login for that)
        
    TODO: Implement refresh token rotation for better security
    """
    from app.core.security import decode_token, verify_token_type
    from jose import JWTError
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(refresh_token)
        
        # Verify it's a refresh token (not access token)
        if not verify_token_type(payload, expected_type="refresh"):
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise credentials_exception
    
    if not user.is_active or user.is_account_locked():
        raise credentials_exception
    
    # Create new access token
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    *,
    db: DatabaseSession,
    request: Request,
    body: ForgotPasswordRequest
) -> MessageResponse:
    """
    Request password reset email.
    
    Args:
        body: Email address to send reset link to
        
    Returns:
        Generic success message (doesn't reveal if email exists)
        
    Security:
        - Always returns success (prevents user enumeration)
        - Token is cryptographically secure
        - Token expires after configured time
        - Audit log created
    """
    # Generic message (always same response to prevent user enumeration)
    response_message = "If an account with this email exists, a password reset link has been sent."
    
    # Find user
    user = await crud.user.get_by_email(db, email=body.email)
    
    if not user:
        # User doesn't exist - return same message (security)
        return MessageResponse(message=response_message)
    
    if not user.is_active:
        # Inactive account - return same message
        return MessageResponse(message=response_message)
    
    # Generate secure random token
    token = secrets.token_urlsafe(32)
    
    # Save hashed token to user
    await crud.user.set_reset_token(
        db, 
        user=user, 
        token=token,
        expires_hours=settings.RESET_TOKEN_EXPIRE_HOURS
    )
    
    # Send reset email
    email_sent = await send_password_reset_email(
        email=user.email,
        token=token,
        username=None  # Could extract from email if needed
    )
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=user.id,
        action=AuditAction.PASSWORD_RESET_REQUEST,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"email_sent": email_sent}
    )
    
    return MessageResponse(message=response_message)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    *,
    db: DatabaseSession,
    request: Request,
    body: ResetPasswordRequest
) -> MessageResponse:
    """
    Reset password using token from email.
    
    Args:
        body: Token, email, and new password
        
    Returns:
        Success message
        
    Raises:
        HTTPException 400: If token is invalid or expired
        
    Security:
        - Validates token cryptographically
        - Token can only be used once
        - Password strength is validated
        - Notification email sent after reset
        - Audit log created
    """
    # Validate password strength
    from app.schemas.user import validate_password_strength
    try:
        validate_password_strength(body.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Find user and verify token
    user = await crud.user.get_by_reset_token(
        db, 
        email=body.email, 
        token=body.token
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Reset password
    await crud.user.reset_password(db, user=user, new_password=body.new_password)
    
    # Send notification email
    await send_password_changed_notification(email=user.email)
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=user.id,
        action=AuditAction.PASSWORD_RESET_COMPLETE,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return MessageResponse(message="Password has been reset successfully. You can now login with your new password.")
