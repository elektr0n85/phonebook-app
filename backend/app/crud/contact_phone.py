"""
CRUD operations for ContactPhone model (N:M relationship).
"""
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.contact_phone import ContactPhone
from app.schemas.phone import ContactPhoneCreate, ContactPhoneUpdate


class CRUDContactPhone(CRUDBase[ContactPhone, ContactPhoneCreate, ContactPhoneUpdate]):
    """
    CRUD operations for ContactPhone model.
    
    Manages the N:M relationship between Contacts and Phones.
    
    Additional methods:
        - add_phone_to_contact: Link a phone to a contact
        - remove_phone_from_contact: Unlink a phone from a contact
        - get_contact_phones: Get all phones for a contact
        - update_primary_phone: Set a phone as primary
    """
    
    async def add_phone_to_contact(
        self,
        db: AsyncSession,
        *,
        contact_id: int,
        phone_id: int,
        is_primary: bool = False,
        label: str | None = None,
        notes: str | None = None
    ) -> ContactPhone:
        """
        Add a phone to a contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
            phone_id: Phone ID
            is_primary: Mark as primary phone
            label: Label (e.g., "Work", "Personal")
            notes: Additional notes
            
        Returns:
            Created ContactPhone instance
            
        Security: Assumes contact ownership was verified before calling
        """
        # If setting as primary, unset other primary phones for this contact
        if is_primary:
            await self._unset_primary_phones(db, contact_id=contact_id)
        
        db_obj = ContactPhone(
            contact_id=contact_id,
            phone_id=phone_id,
            is_primary=is_primary,
            label=label,
            notes=notes
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove_phone_from_contact(
        self,
        db: AsyncSession,
        *,
        contact_id: int,
        phone_id: int
    ) -> bool:
        """
        Remove a phone from a contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
            phone_id: Phone ID
            
        Returns:
            True if removed, False if not found
            
        Security: Does not delete the phone itself, only the relationship
        """
        stmt = select(ContactPhone).where(
            and_(
                ContactPhone.contact_id == contact_id,
                ContactPhone.phone_id == phone_id
            )
        )
        
        result = await db.execute(stmt)
        contact_phone = result.scalar_one_or_none()
        
        if contact_phone:
            await db.delete(contact_phone)
            await db.commit()
            return True
        
        return False
    
    async def get_contact_phones(
        self,
        db: AsyncSession,
        *,
        contact_id: int
    ) -> list[ContactPhone]:
        """
        Get all phones for a contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
            
        Returns:
            List of ContactPhone instances with phones loaded
        """
        stmt = (
            select(ContactPhone)
            .options(selectinload(ContactPhone.phone))
            .where(ContactPhone.contact_id == contact_id)
            .order_by(ContactPhone.is_primary.desc(), ContactPhone.created_at)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_phone_contacts(
        self,
        db: AsyncSession,
        *,
        phone_id: int
    ) -> list[ContactPhone]:
        """
        Get all contacts that have this phone number.
        
        Args:
            db: Database session
            phone_id: Phone ID
            
        Returns:
            List of ContactPhone instances with contacts loaded
            
        Use case: Find who shares a landline number
        """
        stmt = (
            select(ContactPhone)
            .options(selectinload(ContactPhone.contact))
            .where(ContactPhone.phone_id == phone_id)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def update_primary_phone(
        self,
        db: AsyncSession,
        *,
        contact_id: int,
        phone_id: int
    ) -> ContactPhone | None:
        """
        Set a phone as primary for a contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
            phone_id: Phone ID to set as primary
            
        Returns:
            Updated ContactPhone instance or None if not found
            
        Security: Unsets all other primary phones for this contact
        """
        # First, unset all primary phones for this contact
        await self._unset_primary_phones(db, contact_id=contact_id)
        
        # Then, set the specified phone as primary
        stmt = select(ContactPhone).where(
            and_(
                ContactPhone.contact_id == contact_id,
                ContactPhone.phone_id == phone_id
            )
        )
        
        result = await db.execute(stmt)
        contact_phone = result.scalar_one_or_none()
        
        if contact_phone:
            contact_phone.is_primary = True
            db.add(contact_phone)
            await db.commit()
            await db.refresh(contact_phone)
        
        return contact_phone
    
    async def _unset_primary_phones(
        self,
        db: AsyncSession,
        *,
        contact_id: int
    ) -> None:
        """
        Unset all primary phones for a contact (internal helper).
        
        Args:
            db: Database session
            contact_id: Contact ID
        """
        stmt = select(ContactPhone).where(
            and_(
                ContactPhone.contact_id == contact_id,
                ContactPhone.is_primary == True
            )
        )
        
        result = await db.execute(stmt)
        primary_phones = result.scalars().all()
        
        for cp in primary_phones:
            cp.is_primary = False
            db.add(cp)
        
        await db.flush()
    
    async def exists(
        self,
        db: AsyncSession,
        *,
        contact_id: int,
        phone_id: int
    ) -> bool:
        """
        Check if a phone is already linked to a contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
            phone_id: Phone ID
            
        Returns:
            True if link exists, False otherwise
            
        Security: Prevents duplicate phone links
        """
        stmt = select(ContactPhone).where(
            and_(
                ContactPhone.contact_id == contact_id,
                ContactPhone.phone_id == phone_id
            )
        )
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_primary_phone_display(
        self,
        db: AsyncSession,
        *,
        contact_id: int
    ) -> str | None:
        """
        Get formatted primary phone number for display.
        
        Args:
            db: Database session
            contact_id: Contact ID
            
        Returns:
            Formatted phone string or None if no primary phone
            
        Format: "+48 123 456 789" or "123 456 789 ext. 42"
        """
        stmt = (
            select(ContactPhone)
            .options(selectinload(ContactPhone.phone))
            .where(
                and_(
                    ContactPhone.contact_id == contact_id,
                    ContactPhone.is_primary == True
                )
            )
        )
        
        result = await db.execute(stmt)
        contact_phone = result.scalar_one_or_none()
        
        if not contact_phone or not contact_phone.phone:
            # No primary phone - try to get first phone
            stmt = (
                select(ContactPhone)
                .options(selectinload(ContactPhone.phone))
                .where(ContactPhone.contact_id == contact_id)
                .order_by(ContactPhone.created_at)
                .limit(1)
            )
            result = await db.execute(stmt)
            contact_phone = result.scalar_one_or_none()
            
            if not contact_phone or not contact_phone.phone:
                return None
        
        phone = contact_phone.phone
        
        # Format phone number for display
        parts = []
        if phone.country_code:
            parts.append(f"+{phone.country_code}")
        parts.append(phone.phone_number)
        
        display = " ".join(parts)
        
        if phone.extension:
            display += f" ext. {phone.extension}"
        
        return display


# Create singleton instance
contact_phone = CRUDContactPhone(ContactPhone)
