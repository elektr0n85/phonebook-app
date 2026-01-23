"""
Contact model for storing phone book entries.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Contact(Base):
    """
    Contact model for phone book entries.
    
    Security features:
        - User ownership (each contact belongs to one user)
        - Soft delete (data recovery possible)
        - Audit trail (created_at, updated_at)
    """
    
    __tablename__ = "contacts"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign key - ownership
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Contact information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="contacts")
    phones: Mapped[list["ContactPhone"]] = relationship(
        "ContactPhone", back_populates="contact", cascade="all, delete-orphan"
    )
    
    def soft_delete(self) -> None:
        """
        Soft delete the contact (mark as deleted, don't remove from DB).
        
        Security: Allows data recovery, maintains audit trail
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """
        Restore a soft-deleted contact.
        """
        self.is_deleted = False
        self.deleted_at = None
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.name}', user_id={self.user_id})>"
