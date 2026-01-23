"""
CRUD operations for Phone model.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.phone import Phone, PhoneType
from app.schemas.phone import PhoneCreate, PhoneResponse


class CRUDPhone(CRUDBase[Phone, PhoneCreate, PhoneResponse]):
    """
    CRUD operations for Phone model.
    
    Additional methods:
        - get_by_number: Find phone by normalized number
        - get_or_create: Get existing or create new phone
    """
    
    async def get_by_number(
        self, 
        db: AsyncSession, 
        *, 
        phone_number: str,
        phone_type: PhoneType
    ) -> Phone | None:
        """
        Get phone by normalized number.
        
        Args:
            db: Database session
            phone_number: Normalized phone number
            phone_type: Phone type (for normalization)
            
        Returns:
            Phone instance or None if not found
            
        Security: Searches by normalized number (prevents duplicates)
        """
        # Normalize the search number
        normalized = Phone.normalize_phone_number(phone_type, phone_number)
        
        stmt = select(Phone).where(Phone.phone_number == normalized)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, *, obj_in: PhoneCreate) -> Phone:
        """
        Create a new phone number.
        
        Args:
            db: Database session
            obj_in: PhoneCreate schema
            
        Returns:
            Created phone instance
            
        Security: Normalizes phone number before storage
        """
        # Normalize phone number
        normalized = Phone.normalize_phone_number(
            obj_in.phone_type, 
            obj_in.phone_number
        )
        
        # Parse components for display formatting
        country_code = None
        area_code = None
        local_number = None
        extension = None
        
        if obj_in.phone_type == PhoneType.MOBILE:
            # Mobile: +CC XXXXXXXXX
            # Extract country code (e.g., "+48")
            if normalized.startswith("+"):
                # Find where digits start after +
                for i in range(1, min(6, len(normalized))):
                    if i < len(normalized):
                        country_code = normalized[:i+2]
                        local_number = normalized[i+2:]
                        # Format local number with spaces (XXX XXX XXX)
                        if len(local_number) >= 9:
                            local_number = f"{local_number[:3]} {local_number[3:6]} {local_number[6:]}"
                        break
        
        elif obj_in.phone_type == PhoneType.LANDLINE:
            # Landline: ACXXXXXXX (area code + local)
            # Assume first 2 digits are area code
            if len(normalized) >= 2:
                area_code = normalized[:2]
                rest = normalized[2:]
                # Format: XX XX XXX
                if len(rest) >= 5:
                    local_number = f"{rest[:2]} {rest[2:4]} {rest[4:]}"
                else:
                    local_number = rest
        
        elif obj_in.phone_type == PhoneType.INTERNAL:
            # Internal: just the extension
            extension = normalized
        
        # Create phone object
        db_obj = Phone(
            phone_number=normalized,
            phone_type=obj_in.phone_type,
            country_code=country_code,
            area_code=area_code,
            local_number=local_number,
            extension=extension,
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_or_create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: PhoneCreate
    ) -> tuple[Phone, bool]:
        """
        Get existing phone or create new one.
        
        Args:
            db: Database session
            obj_in: PhoneCreate schema
            
        Returns:
            Tuple of (Phone instance, created: bool)
            - created=True if phone was created
            - created=False if phone already existed
            
        Security: Prevents duplicate phone numbers in database
        """
        # Try to find existing phone
        existing = await self.get_by_number(
            db, 
            phone_number=obj_in.phone_number,
            phone_type=obj_in.phone_type
        )
        
        if existing:
            return (existing, False)
        
        # Create new phone
        new_phone = await self.create(db, obj_in=obj_in)
        return (new_phone, True)


# Create singleton instance
phone = CRUDPhone(Phone)
