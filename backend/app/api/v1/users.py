"""
User profile API endpoints.

Endpoints:
    GET /users/me - Get current user profile
    PUT /users/me - Update current user profile
    PUT /users/me/password - Change password
"""
from fastapi import APIRouter, HTTPException, Request, status

from app import crud
from app.api.deps import CurrentUser, DatabaseSession, get_client_ip, get_user_agent
from app.models.audit_log import AuditAction
from app.schemas.auth import MessageResponse
from app.schemas.user import UserPasswordChange, UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUser
) -> UserResponse:
    """
    Get current user profile.
    
    Returns:
        User profile (without password hash)
        
    Security: JWT required (current_user dependency)
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    *,
    db: DatabaseSession,
    request: Request,
    current_user: CurrentUser,
    user_in: UserUpdate
) -> UserResponse:
    """
    Update current user profile.
    
    Args:
        user_in: Updated user data (only email for now)
        
    Returns:
        Updated user profile
        
    Security:
        - Can only update own profile
        - Email uniqueness checked
        - Audit log created
    """
    # Check if new email is already taken by another user
    if user_in.email:
        existing_user = await crud.user.get_by_email(db, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user"
            )
    
    # Update user
    updated_user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action="user_profile_update",
        resource_type="user",
        resource_id=current_user.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"updated_fields": list(user_in.model_dump(exclude_unset=True).keys())}
    )
    
    return updated_user


@router.put("/me/password", response_model=MessageResponse)
async def change_password(
    *,
    db: DatabaseSession,
    request: Request,
    current_user: CurrentUser,
    password_in: UserPasswordChange
) -> MessageResponse:
    """
    Change current user password.
    
    Args:
        password_in: Old password and new password
        
    Returns:
        Success message
        
    Security:
        - Requires old password verification
        - New password strength validation (Pydantic schema)
        - Password hashing (bcrypt)
        - Audit log created
        - User should re-login after password change
    """
    # Verify old password
    if not current_user.verify_password(password_in.old_password):
        # Audit log - failed attempt
        await crud.audit_log.create_log(
            db,
            user_id=current_user.id,
            action="password_change_failed",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"reason": "invalid_old_password"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Check new password is different from old
    if password_in.old_password == password_in.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.set_password(password_in.new_password)
    db.add(current_user)
    await db.commit()
    
    # Audit log - successful change
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action=AuditAction.PASSWORD_CHANGE,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return MessageResponse(
        message="Password changed successfully. Please login again with your new password."
    )
