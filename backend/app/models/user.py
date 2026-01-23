"""
User model with authentication and security features.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import hash_password, verify_password
from app.database import Base


class User(Base):
    """
    User model for authentication and authorization.
    
    Security features:
        - Password hashing (never store plain passwords)
        - Account locking (prevent brute force)
        - Failed login tracking
        - Role-based access control (RBAC)
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Authentication
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Authorization
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="user"
    )  # 'user' or 'admin'
    
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Security tracking
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationships
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact", back_populates="owner", cascade="all, delete-orphan"
    )
    
    def set_password(self, password: str) -> None:
        """
        Hash and set user password.
        
        Args:
            password: Plain text password
            
        Security: Uses bcrypt with cost factor 12
        """
        self.password_hash = hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
            
        Security: Constant-time comparison (timing attack resistant)
        """
        return verify_password(password, self.password_hash)
    
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"
    
    def increment_failed_login(self) -> None:
        """
        Increment failed login counter.
        
        Security: Part of brute force protection
        """
        self.failed_login_attempts += 1
    
    def reset_failed_login(self) -> None:
        """
        Reset failed login counter after successful login.
        
        Security: Allow user to login again after successful attempt
        """
        self.failed_login_attempts = 0
        self.is_locked = False
        self.locked_until = None
    
    def lock_account(self, duration_minutes: int = 15) -> None:
        """
        Lock account temporarily.
        
        Args:
            duration_minutes: How long to lock account
            
        Security: Prevents brute force attacks
        """
        from datetime import timedelta
        
        self.is_locked = True
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def is_account_locked(self) -> bool:
        """
        Check if account is currently locked.
        
        Returns:
            True if account is locked and lock hasn't expired
        """
        if not self.is_locked:
            return False
        
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        
        # Lock has expired, unlock account
        self.is_locked = False
        self.locked_until = None
        return False
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
