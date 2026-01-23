"""
CRUD operations for User model.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.
    
    Additional methods:
        - get_by_email: Find user by email
        - authenticate: Verify credentials
        - create: Override to hash password
    """
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User email (case-insensitive)
            
        Returns:
            User instance or None if not found
            
        Security: Email comparison is case-insensitive
        """
        stmt = select(User).where(User.email == email.lower())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db: Database session
            obj_in: UserCreate schema with email and plain password
            
        Returns:
            Created user instance
            
        Security:
            - Password is hashed using bcrypt before storage
            - Email is converted to lowercase
            - Never stores plain password
        """
        db_obj = User(
            email=obj_in.email.lower(),
            role="user",  # Default role
            is_active=True,
        )
        db_obj.set_password(obj_in.password)  # Hash password
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def authenticate(
        self, 
        db: AsyncSession, 
        *, 
        email: str, 
        password: str
    ) -> User | None:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User instance if credentials are valid, None otherwise
            
        Security:
            - Constant-time password comparison (timing attack resistant)
            - Does not reveal whether email exists (prevents user enumeration)
            - Returns None for both "user not found" and "wrong password"
        """
        user = await self.get_by_email(db, email=email)
        
        if not user:
            # User doesn't exist
            # Still call verify_password to prevent timing attacks
            from app.core.security import verify_password
            verify_password("dummy", "dummy_hash")
            return None
        
        if not user.verify_password(password):
            # Wrong password
            return None
        
        return user
    
    async def is_active(self, user: User) -> bool:
        """
        Check if user account is active.
        
        Args:
            user: User instance
            
        Returns:
            True if user is active and not locked
        """
        return user.is_active and not user.is_account_locked()
    
    async def is_admin(self, user: User) -> bool:
        """
        Check if user has admin role.
        
        Args:
            user: User instance
            
        Returns:
            True if user is admin
        """
        return user.is_admin()
    
    async def update_last_login(self, db: AsyncSession, *, user: User) -> User:
        """
        Update user's last login timestamp.
        
        Args:
            db: Database session
            user: User instance
            
        Returns:
            Updated user instance
        """
        user.last_login = datetime.utcnow()
        user.reset_failed_login()  # Reset failed attempts on successful login
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def record_failed_login(
        self, 
        db: AsyncSession, 
        *, 
        user: User,
        lock_threshold: int = 5
    ) -> User:
        """
        Record a failed login attempt and lock account if threshold reached.
        
        Args:
            db: Database session
            user: User instance
            lock_threshold: Number of failed attempts before account lock
            
        Returns:
            Updated user instance
            
        Security: Auto-lock account after X failed attempts (brute force protection)
        """
        user.increment_failed_login()
        
        if user.failed_login_attempts >= lock_threshold:
            user.lock_account(duration_minutes=15)
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def unlock_account(self, db: AsyncSession, *, user: User) -> User:
        """
        Manually unlock a locked user account.
        
        Args:
            db: Database session
            user: User instance
            
        Returns:
            Updated user instance
        """
        user.reset_failed_login()
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


# Create singleton instance
user = CRUDUser(User)
