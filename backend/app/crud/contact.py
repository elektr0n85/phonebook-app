"""
CRUD operations for Contact model.
"""
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.contact import Contact
from app.models.contact_phone import ContactPhone
from app.models.phone import Phone
from app.schemas.contact import ContactCreate, ContactUpdate


class CRUDContact(CRUDBase[Contact, ContactCreate, ContactUpdate]):
    """
    CRUD operations for Contact model.
    
    Additional methods:
        - get_multi_by_owner: Get all contacts for a user
        - search: Search contacts by name/email/company
        - get_with_phones: Get contact with phones loaded
    """
    
    async def create_with_user(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: ContactCreate, 
        user_id: int
    ) -> Contact:
        """
        Create a new contact for a specific user.
        
        Args:
            db: Database session
            obj_in: ContactCreate schema
            user_id: Owner's user ID
            
        Returns:
            Created contact instance
            
        Security: Associates contact with user (ownership)
        """
        obj_in_data = obj_in.model_dump()
        db_obj = Contact(**obj_in_data, user_id=user_id)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> list[Contact]:
        """
        Get all contacts for a specific user.
        
        Args:
            db: Database session
            user_id: Owner's user ID
            skip: Number of records to skip
            limit: Maximum number of records
            include_deleted: Include soft-deleted contacts
            
        Returns:
            List of contact instances
            
        Security: Only returns contacts owned by specified user
        """
        # Cap limit
        limit = min(limit, 100)
        
        stmt = select(Contact).where(Contact.user_id == user_id)
        
        if not include_deleted:
            stmt = stmt.where(Contact.is_deleted == False)
        
        stmt = stmt.offset(skip).limit(limit).order_by(Contact.created_at.desc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def search(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        query: str,
        skip: int = 0,
        limit: int = 50
    ) -> list[Contact]:
        """
        Search contacts by name, email, or company.
        
        Args:
            db: Database session
            user_id: Owner's user ID
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of matching contact instances
            
        Security:
            - Only searches within user's own contacts
            - Case-insensitive search
            - SQL injection prevented by ORM
        """
        # Cap limit
        limit = min(limit, 50)
        
        # Case-insensitive search
        search_pattern = f"%{query}%"
        
        stmt = (
            select(Contact)
            .outerjoin(ContactPhone, Contact.id == ContactPhone.contact_id)
            .outerjoin(Phone, ContactPhone.phone_id == Phone.id)
            .where(
                Contact.user_id == user_id,
                Contact.is_deleted == False,
                or_(
                    Contact.name.ilike(search_pattern),
                    Contact.email.ilike(search_pattern),
                    Contact.company.ilike(search_pattern),
                    Contact.position.ilike(search_pattern),
                    Phone.phone_number.ilike(search_pattern),
                    Phone.extension.ilike(search_pattern),
                    Phone.local_number.ilike(search_pattern),
                )
            )
            .distinct()  # Avoid duplicates when contact has multiple matching phones
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_phones(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Contact | None:
        """
        Get contact with phones eagerly loaded.
        
        Args:
            db: Database session
            id: Contact ID
            
        Returns:
            Contact instance with phones loaded, or None
            
        Security: Returns contact regardless of owner (check ownership separately!)
        """
        stmt = (
            select(Contact)
            .options(selectinload(Contact.phones))
            .where(Contact.id == id)
        )
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def soft_delete(self, db: AsyncSession, *, id: int) -> Contact | None:
        """
        Soft delete a contact (mark as deleted, don't remove).
        
        Args:
            db: Database session
            id: Contact ID
            
        Returns:
            Soft-deleted contact or None if not found
            
        Security: Allows data recovery, maintains audit trail
        """
        contact = await self.get(db, id=id)
        
        if contact:
            contact.soft_delete()
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
        
        return contact
    
    async def restore(self, db: AsyncSession, *, id: int) -> Contact | None:
        """
        Restore a soft-deleted contact.
        
        Args:
            db: Database session
            id: Contact ID
            
        Returns:
            Restored contact or None if not found
        """
        contact = await self.get(db, id=id)
        
        if contact and contact.is_deleted:
            contact.restore()
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
        
        return contact
    
    async def count_by_owner(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int
    ) -> int:
        """
        Count total contacts for a user.
        
        Args:
            db: Database session
            user_id: Owner's user ID
            
        Returns:
            Number of contacts (excluding deleted)
            
        Security: Used to enforce max contacts per user limit
        """
        from sqlalchemy import func
        
        stmt = select(func.count(Contact.id)).where(
            Contact.user_id == user_id,
            Contact.is_deleted == False
        )
        
        result = await db.execute(stmt)
        return result.scalar_one()


# Create singleton instance
contact = CRUDContact(Contact)
