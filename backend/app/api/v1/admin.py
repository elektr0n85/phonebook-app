"""
Admin API endpoints.

Endpoints:
    GET /admin/users - List all users
    GET /admin/users/{user_id} - Get user details
    PUT /admin/users/{user_id}/block - Block/unblock user
    GET /admin/audit-logs - View audit logs
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, status

from app import crud
from app.api.deps import AdminUser, DatabaseSession
from app.models.audit_log import AuditAction
from app.schemas.auth import MessageResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    *,
    db: DatabaseSession,
    admin: AdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> list[UserResponse]:
    """
    List all users (admin only).
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        
    Returns:
        List of users (without password hashes)
        
    Security:
        - Admin role required
        - Never returns password hashes
        - Rate limited (TODO)
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=admin.id,
        action=AuditAction.ADMIN_USER_VIEW,
        details={"action": "list_users", "count": len(users)}
    )
    
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    *,
    db: DatabaseSession,
    admin: AdminUser,
    user_id: int
) -> UserResponse:
    """
    Get user details (admin only).
    
    Args:
        user_id: User ID
        
    Returns:
        User details (without password hash)
        
    Security:
        - Admin role required
        - Audit log created
    """
    user = await crud.user.get(db, id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=admin.id,
        action=AuditAction.ADMIN_USER_VIEW,
        resource_type="user",
        resource_id=user.id,
        details={"action": "view_user", "target_user_email": user.email}
    )
    
    return user


@router.put("/users/{user_id}/block", response_model=MessageResponse)
async def toggle_user_block(
    *,
    db: DatabaseSession,
    admin: AdminUser,
    user_id: int,
    block: bool = Query(..., description="True to block, False to unblock")
) -> MessageResponse:
    """
    Block or unblock a user account (admin only).
    
    Args:
        user_id: User ID to block/unblock
        block: True to block, False to unblock
        
    Returns:
        Success message
        
    Security:
        - Admin role required
        - Cannot block self
        - Audit log created
        
    Example:
        PUT /admin/users/5/block?block=true  # Block user 5
        PUT /admin/users/5/block?block=false # Unblock user 5
    """
    # Get target user
    user = await crud.user.get(db, id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from blocking themselves
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block yourself"
        )
    
    # Block or unblock
    if block:
        # Block user
        user.is_active = False
        action = AuditAction.ADMIN_USER_BLOCK
        message = f"User {user.email} has been blocked"
    else:
        # Unblock user
        user.is_active = True
        await crud.user.unlock_account(db, user=user)  # Also unlock if locked
        action = "admin_user_unblock"
        message = f"User {user.email} has been unblocked"
    
    db.add(user)
    await db.commit()
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=admin.id,
        action=action,
        resource_type="user",
        resource_id=user.id,
        details={"target_user_email": user.email, "blocked": block}
    )
    
    return MessageResponse(message=message)


@router.get("/audit-logs")
async def get_audit_logs(
    *,
    db: DatabaseSession,
    admin: AdminUser,
    user_id: int | None = Query(None, description="Filter by user ID"),
    action: str | None = Query(None, description="Filter by action"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back (max 7 days)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> dict:
    """
    View audit logs (admin only).
    
    Args:
        user_id: Optional user ID filter
        action: Optional action filter (e.g., "login_success", "contact_create")
        hours: Hours to look back (default 24, max 168 = 7 days)
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        
    Returns:
        Dictionary with logs and metadata
        
    Security:
        - Admin role required
        - Self-audit log created
        - Limited to 7 days history
        
    Example:
        GET /admin/audit-logs?user_id=5&action=login_failed&hours=48
    """
    # Get logs
    if user_id and action:
        # Filter by user and action
        since = datetime.utcnow() - timedelta(hours=hours)
        logs = await crud.audit_log.get_user_logs(
            db, user_id=user_id, action=action, skip=skip, limit=limit
        )
        # Manual date filter (crude but works)
        logs = [log for log in logs if log.created_at >= since]
    elif user_id:
        # Filter by user only
        logs = await crud.audit_log.get_user_logs(
            db, user_id=user_id, skip=skip, limit=limit
        )
    elif action:
        # Filter by action only
        since = datetime.utcnow() - timedelta(hours=hours)
        logs = await crud.audit_log.get_action_logs(
            db, action=action, since=since, skip=skip, limit=limit
        )
    else:
        # Recent logs (all)
        logs = await crud.audit_log.get_recent_logs(
            db, hours=hours, skip=skip, limit=limit
        )
    
    # Audit log (viewing audit logs)
    await crud.audit_log.create_log(
        db,
        user_id=admin.id,
        action=AuditAction.ADMIN_AUDIT_VIEW,
        details={
            "filters": {
                "user_id": user_id,
                "action": action,
                "hours": hours
            },
            "results_count": len(logs)
        }
    )
    
    # Convert logs to dict (SQLAlchemy models to JSON)
    logs_data = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "user_agent": log.user_agent,
            "details": log.details,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
    
    return {
        "logs": logs_data,
        "count": len(logs_data),
        "filters": {
            "user_id": user_id,
            "action": action,
            "hours": hours
        }
    }
