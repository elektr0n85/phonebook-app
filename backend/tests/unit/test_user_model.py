"""
Unit tests for User model.

Tests:
- Password hashing and verification
- Account lockout functionality
- Role checks
- Failed login attempts tracking
"""
import pytest
from datetime import datetime, timedelta

from app.models.user import User


@pytest.mark.unit
class TestUserModel:
    """Test suite for User model."""
    
    def test_set_password_hashes_password(self):
        """Test that password is hashed correctly."""
        user = User(email="test@example.com")
        user.set_password("TestPassword123!")
        
        # Password should be hashed (not stored as plaintext)
        assert user.password_hash != "TestPassword123!"
        assert len(user.password_hash) > 0
        assert user.password_hash.startswith("$2b$")  # bcrypt hash
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        user = User(email="test@example.com")
        user.set_password("TestPassword123!")
        
        # Correct password should verify
        assert user.verify_password("TestPassword123!") is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        user = User(email="test@example.com")
        user.set_password("TestPassword123!")
        
        # Incorrect password should not verify
        assert user.verify_password("WrongPassword") is False
    
    def test_is_admin_user_role(self):
        """Test is_admin() returns True for admin users."""
        user = User(email="admin@example.com", role="admin")
        assert user.is_admin() is True
    
    def test_is_admin_regular_user(self):
        """Test is_admin() returns False for regular users."""
        user = User(email="user@example.com", role="user")
        assert user.is_admin() is False
    
    def test_increment_failed_login(self):
        """Test incrementing failed login attempts."""
        user = User(email="test@example.com")
        assert user.failed_login_attempts == 0
        
        user.increment_failed_login()
        assert user.failed_login_attempts == 1
        
        user.increment_failed_login()
        assert user.failed_login_attempts == 2
    
    def test_reset_failed_login(self):
        """Test resetting failed login attempts."""
        user = User(email="test@example.com")
        user.failed_login_attempts = 5
        
        user.reset_failed_login()
        assert user.failed_login_attempts == 0
    
    def test_lock_account(self):
        """Test account lockout functionality."""
        user = User(email="test@example.com")
        
        user.lock_account(duration_minutes=15)
        
        assert user.is_locked is True
        assert user.locked_until is not None
        # Should be locked for approximately 15 minutes
        time_diff = (user.locked_until - datetime.utcnow()).total_seconds()
        assert 14 * 60 < time_diff < 16 * 60  # Within 1 minute tolerance
    
    def test_is_account_locked_when_locked(self):
        """Test is_account_locked() returns True for locked account."""
        user = User(email="test@example.com")
        user.lock_account(duration_minutes=15)
        
        assert user.is_account_locked() is True
    
    def test_is_account_locked_when_not_locked(self):
        """Test is_account_locked() returns False for non-locked account."""
        user = User(email="test@example.com")
        
        assert user.is_account_locked() is False
    
    def test_is_account_locked_after_expiry(self):
        """Test account is unlocked after lockout period expires."""
        user = User(email="test@example.com")
        user.is_locked = True
        user.locked_until = datetime.utcnow() - timedelta(minutes=1)  # Expired
        
        assert user.is_account_locked() is False
    
    def test_password_not_stored_plaintext(self):
        """Test that plaintext password is never stored."""
        user = User(email="test@example.com")
        password = "SuperSecret123!"
        user.set_password(password)
        
        # Password hash should not contain original password
        assert password not in user.password_hash
        assert password.lower() not in user.password_hash.lower()


@pytest.mark.unit
class TestUserSecurity:
    """Security-focused tests for User model."""
    
    def test_bcrypt_cost_factor(self):
        """Test that bcrypt uses appropriate cost factor (12)."""
        user = User(email="test@example.com")
        user.set_password("TestPassword123!")
        
        # bcrypt hash format: $2b$[cost]$[salt][hash]
        # Cost should be 12
        parts = user.password_hash.split("$")
        cost = int(parts[2])
        assert cost == 12  # Secure cost factor
    
    def test_different_hashes_for_same_password(self):
        """Test that same password gets different hashes (salt)."""
        user1 = User(email="user1@example.com")
        user2 = User(email="user2@example.com")
        
        password = "SamePassword123!"
        user1.set_password(password)
        user2.set_password(password)
        
        # Hashes should be different due to random salt
        assert user1.password_hash != user2.password_hash
    
    def test_timing_attack_resistance(self):
        """Test password verification is timing-safe."""
        user = User(email="test@example.com")
        user.set_password("TestPassword123!")
        
        import time
        
        # Measure time for correct password
        start = time.time()
        user.verify_password("TestPassword123!")
        correct_time = time.time() - start
        
        # Measure time for incorrect password
        start = time.time()
        user.verify_password("WrongPassword")
        wrong_time = time.time() - start
        
        # Times should be similar (constant-time comparison)
        # Note: This is approximate, bcrypt handles timing internally
        assert abs(correct_time - wrong_time) < 0.1  # Within 100ms
