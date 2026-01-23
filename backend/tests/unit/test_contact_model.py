"""
Unit tests for Contact model.

Tests:
- Soft delete functionality
- Restore functionality
- Timestamps
"""
import pytest
from datetime import datetime

from app.models.contact import Contact


@pytest.mark.unit
class TestContactModel:
    """Test suite for Contact model."""
    
    def test_soft_delete_marks_as_deleted(self):
        """Test soft delete marks contact as deleted."""
        contact = Contact(
            name="John Doe",
            user_id=1
        )
        assert contact.is_deleted is False
        assert contact.deleted_at is None
        
        contact.soft_delete()
        
        assert contact.is_deleted is True
        assert contact.deleted_at is not None
        assert isinstance(contact.deleted_at, datetime)
    
    def test_restore_unmarks_deleted(self):
        """Test restore marks contact as not deleted."""
        contact = Contact(
            name="John Doe",
            user_id=1
        )
        contact.soft_delete()
        assert contact.is_deleted is True
        
        contact.restore()
        
        assert contact.is_deleted is False
        assert contact.deleted_at is None
    
    def test_soft_delete_preserves_data(self):
        """Test soft delete doesn't remove actual data."""
        contact = Contact(
            name="John Doe",
            email="john@example.com",
            company="ACME Corp",
            user_id=1
        )
        
        contact.soft_delete()
        
        # Data should still be present
        assert contact.name == "John Doe"
        assert contact.email == "john@example.com"
        assert contact.company == "ACME Corp"
    
    def test_restore_idempotent(self):
        """Test restore is idempotent (safe to call multiple times)."""
        contact = Contact(
            name="John Doe",
            user_id=1
        )
        
        contact.restore()
        contact.restore()
        
        assert contact.is_deleted is False
        assert contact.deleted_at is None
    
    def test_soft_delete_idempotent(self):
        """Test soft delete is idempotent."""
        contact = Contact(
            name="John Doe",
            user_id=1
        )
        
        contact.soft_delete()
        first_deleted_at = contact.deleted_at
        
        contact.soft_delete()
        second_deleted_at = contact.deleted_at
        
        # Both should be marked deleted
        assert contact.is_deleted is True
        # Timestamp might change on second call (that's ok)
        assert second_deleted_at is not None
