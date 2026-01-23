"""
Audit Log model for tracking security-relevant events.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    """
    Audit log for tracking security events and user actions.
    
    Security features:
        - Immutable records (no updates/deletes)
        - Comprehensive tracking (who, what, when, where)
        - IP and user agent logging
        - JSON metadata for additional context
    """
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Who (user can be null for anonymous actions like registration)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # What
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g., 'login', 'logout', 'create_contact'
    
    resource_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g., 'user', 'contact'
    
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # When
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )
    
    # Where (network information)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Additional context (JSON)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"


# Common audit actions (for consistency)
class AuditAction:
    """
    Standard audit action names.
    
    Usage: AuditAction.LOGIN instead of hardcoded "login"
    """
    
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    
    # Account management
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    ACCOUNT_DELETED = "account_deleted"
    
    # Contacts
    CONTACT_CREATE = "contact_create"
    CONTACT_READ = "contact_read"
    CONTACT_UPDATE = "contact_update"
    CONTACT_DELETE = "contact_delete"
    
    # Admin actions
    ADMIN_USER_VIEW = "admin_user_view"
    ADMIN_USER_BLOCK = "admin_user_block"
    ADMIN_AUDIT_VIEW = "admin_audit_view"
    
    # Security events
    UNAUTHORIZED_ACCESS_ATTEMPT = "unauthorized_access_attempt"
    INVALID_TOKEN = "invalid_token"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
