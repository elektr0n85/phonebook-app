"""
ContactPhone model - many-to-many relationship between Contacts and Phones.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContactPhone(Base):
    """
    Contact-Phone relationship table (N:M).
    
    Features:
        - Many contacts can have the same phone number
        - One contact can have multiple phone numbers
        - Additional metadata (is_primary, label, notes)
        
    Example:
        Jan Kowalski:
          - +48 123 456 789 (mobile, primary, "Personal")
          - 17 123 45 67 (landline, "Office main line")
          - 1234 (internal, "Office extension")
          
        Anna Nowak:
          - +48 987 654 321 (mobile, primary)
          - 17 123 45 67 (landline, "Office main line")  <- SAME as Jan!
    """
    
    __tablename__ = "contact_phones"
    
    # Composite primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    contact_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    phone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("phones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Additional metadata
    is_primary: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # One contact should have one primary phone
    
    label: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g., "Work", "Personal", "Office", "Home"
    
    notes: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )  # Additional notes for this phone
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    
    # Relationships
    contact: Mapped["Contact"] = relationship("Contact", back_populates="phones")
    phone: Mapped["Phone"] = relationship("Phone", back_populates="contact_phones")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("contact_id", "phone_id", name="uq_contact_phone"),
    )  # One contact cannot have the same phone twice
    
    def __repr__(self) -> str:
        return (
            f"<ContactPhone(contact_id={self.contact_id}, phone_id={self.phone_id}, "
            f"label='{self.label}', primary={self.is_primary})>"
        )
