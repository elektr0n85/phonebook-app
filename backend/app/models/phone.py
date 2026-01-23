"""
Phone model for storing unique phone numbers.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PhoneType(str, Enum):
    """
    Enum for phone number types.
    
    Types:
        - MOBILE: Mobile/cell phone with country code (+XX XXX XXX XXX)
        - LANDLINE: Landline phone with area code (XX XX XXX)
        - INTERNAL: Internal company extension (XXXX)
    """
    
    MOBILE = "mobile"
    LANDLINE = "landline"
    INTERNAL = "internal"


class Phone(Base):
    """
    Phone model for storing unique phone numbers.
    
    Features:
        - Unique phone numbers (no duplicates)
        - Multiple types (mobile, landline, internal)
        - Can be shared between multiple contacts (N:M relationship)
        - Structured storage (country code, area code, number, extension)
    """
    
    __tablename__ = "phones"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Phone number components
    phone_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )  # Full normalized number (e.g., "+48123456789", "171234567", "1234")
    
    phone_type: Mapped[PhoneType] = mapped_column(
        String(20), nullable=False, index=True
    )
    
    # Optional breakdown for display formatting
    country_code: Mapped[str | None] = mapped_column(
        String(5), nullable=True
    )  # e.g., "+48" for mobile
    
    area_code: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # e.g., "17" for Rzeszów landline
    
    local_number: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # e.g., "1234567" or "123 45 67"
    
    extension: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # For internal phones
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationships
    contact_phones: Mapped[list["ContactPhone"]] = relationship(
        "ContactPhone", back_populates="phone", cascade="all, delete-orphan"
    )
    
    @staticmethod
    def normalize_phone_number(phone_type: PhoneType, number: str) -> str:
        """
        Normalize phone number for storage.
        
        Args:
            phone_type: Type of phone number
            number: Raw phone number
            
        Returns:
            Normalized phone number (digits only, with + for mobile)
            
        Examples:
            Mobile: "+48 123 456 789" -> "+48123456789"
            Landline: "17 123 45 67" -> "171234567"
            Internal: "1234" -> "1234"
        """
        # Remove spaces, dashes, parentheses
        cleaned = number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if phone_type == PhoneType.MOBILE:
            # Ensure mobile starts with +
            if not cleaned.startswith("+"):
                cleaned = "+" + cleaned
        
        return cleaned
    
    def format_display(self) -> str:
        """
        Format phone number for display.
        
        Returns:
            Formatted phone number based on type
            
        Examples:
            Mobile: "+48 123 456 789"
            Landline: "(17) 123 45 67"
            Internal: "ext. 1234"
        """
        if self.phone_type == PhoneType.MOBILE:
            # Format: +CC XXX XXX XXX
            if self.country_code and self.local_number:
                return f"{self.country_code} {self.local_number}"
            return self.phone_number
        
        elif self.phone_type == PhoneType.LANDLINE:
            # Format: (AC) XX XX XXX
            if self.area_code and self.local_number:
                return f"({self.area_code}) {self.local_number}"
            return self.phone_number
        
        elif self.phone_type == PhoneType.INTERNAL:
            # Format: ext. XXXX
            return f"ext. {self.extension or self.phone_number}"
        
        return self.phone_number
    
    def __repr__(self) -> str:
        return f"<Phone(id={self.id}, type='{self.phone_type}', number='{self.phone_number}')>"
