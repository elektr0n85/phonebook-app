"""
Unit tests for Phone model.

Tests:
- Phone number normalization
- Display formatting
- Type validation
"""
import pytest

from app.models.phone import Phone, PhoneType


@pytest.mark.unit
class TestPhoneModel:
    """Test suite for Phone model."""
    
    def test_normalize_mobile_with_spaces(self):
        """Test normalizing mobile number with spaces."""
        normalized = Phone.normalize_phone_number(
            PhoneType.MOBILE,
            "+48 123 456 789"
        )
        assert normalized == "+48123456789"
    
    def test_normalize_mobile_with_dashes(self):
        """Test normalizing mobile number with dashes."""
        normalized = Phone.normalize_phone_number(
            PhoneType.MOBILE,
            "+48-123-456-789"
        )
        assert normalized == "+48123456789"
    
    def test_normalize_mobile_adds_plus(self):
        """Test normalizing mobile number adds + if missing."""
        normalized = Phone.normalize_phone_number(
            PhoneType.MOBILE,
            "48123456789"
        )
        assert normalized == "+48123456789"
    
    def test_normalize_landline_removes_spaces(self):
        """Test normalizing landline removes spaces."""
        normalized = Phone.normalize_phone_number(
            PhoneType.LANDLINE,
            "17 123 45 67"
        )
        assert normalized == "171234567"
    
    def test_normalize_landline_no_plus(self):
        """Test landline normalization doesn't add +."""
        normalized = Phone.normalize_phone_number(
            PhoneType.LANDLINE,
            "171234567"
        )
        assert normalized == "171234567"
        assert not normalized.startswith("+")
    
    def test_normalize_internal_preserves_digits(self):
        """Test internal number normalization."""
        normalized = Phone.normalize_phone_number(
            PhoneType.INTERNAL,
            "1234"
        )
        assert normalized == "1234"
    
    def test_format_display_mobile(self):
        """Test display formatting for mobile phone."""
        phone = Phone(
            phone_number="+48123456789",
            phone_type=PhoneType.MOBILE,
            country_code="+48",
            local_number="123 456 789"
        )
        
        display = phone.format_display()
        assert display == "+48 123 456 789"
    
    def test_format_display_landline(self):
        """Test display formatting for landline phone."""
        phone = Phone(
            phone_number="171234567",
            phone_type=PhoneType.LANDLINE,
            area_code="17",
            local_number="123 45 67"
        )
        
        display = phone.format_display()
        assert display == "(17) 123 45 67"
    
    def test_format_display_internal(self):
        """Test display formatting for internal phone."""
        phone = Phone(
            phone_number="1234",
            phone_type=PhoneType.INTERNAL,
            extension="1234"
        )
        
        display = phone.format_display()
        assert display == "ext. 1234"
    
    def test_format_display_fallback(self):
        """Test display formatting falls back to phone_number."""
        phone = Phone(
            phone_number="+48123456789",
            phone_type=PhoneType.MOBILE
            # No country_code or local_number
        )
        
        display = phone.format_display()
        assert display == "+48123456789"


@pytest.mark.unit
class TestPhoneNormalization:
    """Test phone number normalization edge cases."""
    
    def test_normalize_removes_parentheses(self):
        """Test normalization removes parentheses."""
        normalized = Phone.normalize_phone_number(
            PhoneType.LANDLINE,
            "(17) 123 45 67"
        )
        assert normalized == "171234567"
        assert "(" not in normalized
        assert ")" not in normalized
    
    def test_normalize_handles_empty_spaces(self):
        """Test normalization handles multiple spaces."""
        normalized = Phone.normalize_phone_number(
            PhoneType.MOBILE,
            "+48   123   456   789"
        )
        assert normalized == "+48123456789"
    
    def test_normalize_mobile_preserves_plus(self):
        """Test mobile normalization preserves + sign."""
        normalized = Phone.normalize_phone_number(
            PhoneType.MOBILE,
            "+48123456789"
        )
        assert normalized.startswith("+")
