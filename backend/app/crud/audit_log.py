"""
CRUD operations for AuditLog model.
"""
from datetime import datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction, AuditLog


class CRUDAuditLog:
    """
    CRUD operations for AuditLog model.
    
    Note: AuditLog is append-only (no updates or deletes).
    
    Methods:
        - create_log: Create a new audit log entry
        - get_user_logs: Get logs for a specific user
        - get_action_logs: Get logs for a specific action
        - get_recent_logs: Get recent audit logs
    """
    
    async def create_log(
        self,
        db: AsyncSession,
        *,
        user_id: int | None,
        action: str,
        resource_type: str | None = None,
        resource_id: int | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None
    ) -> AuditLog:
        """
        Create a new audit log entry.
        
        Args:
            db: Database session
            user_id: User ID (can be None for anonymous actions)
            action: Action name (use AuditAction constants)
            resource_type: Resource type (e.g., 'contact', 'user')
            resource_id: Resource ID
            ip_address: Client IP address
            user_agent: Client user agent string
            details: Additional JSON details
            
        Returns:
            Created AuditLog instance
            
        Security:
            - Immutable (cannot be updated or deleted)
            - No sensitive data in details (passwords, tokens)
            - IP and user agent tracking
            
        Example:
            await audit_log.create_log(
                db,
                user_id=1,
                action=AuditAction.LOGIN_SUCCESS,
                ip_address="192.168.1.1",
                details={"method": "password"}
            )
        """
        db_obj = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_user_logs(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        action: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[AuditLog]:
        """
        Get audit logs for a specific user.
        
        Args:
            db: Database session
            user_id: User ID
            action: Optional action filter
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of AuditLog instances
        """
        limit = min(limit, 100)
        
        stmt = select(AuditLog).where(AuditLog.user_id == user_id)
        
        if action:
            stmt = stmt.where(AuditLog.action == action)
        
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_action_logs(
        self,
        db: AsyncSession,
        *,
        action: str,
        since: datetime | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[AuditLog]:
        """
        Get audit logs for a specific action.
        
        Args:
            db: Database session
            action: Action name (e.g., AuditAction.LOGIN_FAILED)
            since: Optional datetime to filter logs after
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of AuditLog instances
            
        Use case: Find all failed login attempts in last hour
        """
        limit = min(limit, 100)
        
        stmt = select(AuditLog).where(AuditLog.action == action)
        
        if since:
            stmt = stmt.where(AuditLog.created_at >= since)
        
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_recent_logs(
        self,
        db: AsyncSession,
        *,
        hours: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> list[AuditLog]:
        """
        Get recent audit logs.
        
        Args:
            db: Database session
            hours: Number of hours to look back
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of AuditLog instances
            
        Security: Admin-only feature (check permissions before calling)
        """
        limit = min(limit, 100)
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        stmt = (
            select(AuditLog)
            .where(AuditLog.created_at >= since)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def count_user_action(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        action: str,
        since: datetime
    ) -> int:
        """
        Count how many times a user performed an action since a specific time.
        
        Args:
            db: Database session
            user_id: User ID
            action: Action name
            since: Start datetime
            
        Returns:
            Count of matching logs
            
        Use case: Rate limiting (e.g., count failed logins in last 15 min)
        """
        from sqlalchemy import func
        
        stmt = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.user_id == user_id,
                AuditLog.action == action,
                AuditLog.created_at >= since
            )
        )
        
        result = await db.execute(stmt)
        return result.scalar_one()
    
    async def get_resource_logs(
        self,
        db: AsyncSession,
        *,
        resource_type: str,
        resource_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> list[AuditLog]:
        """
        Get audit logs for a specific resource.
        
        Args:
            db: Database session
            resource_type: Resource type (e.g., 'contact')
            resource_id: Resource ID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of AuditLog instances
            
        Use case: View history of a specific contact
        """
        limit = min(limit, 50)
        
        stmt = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.resource_type == resource_type,
                    AuditLog.resource_id == resource_id
                )
            )
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())


# Create singleton instance
audit_log = CRUDAuditLog()
