"""
Integration tests for authentication endpoints.

Tests:
- User registration
- Login/logout
- Token refresh
- Password validation
- Failed login attempts and lockout
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user as user_crud


@pytest.mark.integration
class TestRegistration:
    """Test user registration endpoint."""
    
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data
    
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "weak"  # Too short, no uppercase, no special char
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        test_user
    ):
        """Test registration with existing email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,  # Already exists
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()


@pytest.mark.integration
class TestLogin:
    """Test login endpoint."""
    
    async def test_login_success(
        self,
        client: AsyncClient,
        test_user
    ):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,  # OAuth2 uses 'username'
                "password": "TestPass123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        test_user
    ):
        """Test login with wrong password fails."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "WrongPassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "AnyPassword123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        # Should not reveal if user exists (generic error)
        assert "Invalid credentials" in response.json()["detail"]
    
    async def test_login_account_lockout(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user
    ):
        """Test account lockout after failed attempts."""
        # Make 5 failed login attempts
        for _ in range(5):
            await client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user.email,
                    "password": "WrongPassword"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        # 6th attempt should fail with account locked
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPass123!"  # Correct password!
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()


@pytest.mark.integration
class TestLogout:
    """Test logout endpoint."""
    
    async def test_logout_success(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test successful logout."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()
    
    async def test_logout_without_token(self, client: AsyncClient):
        """Test logout without token fails."""
        response = await client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401


@pytest.mark.integration
class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    async def test_refresh_token_success(
        self,
        client: AsyncClient,
        test_user
    ):
        """Test successful token refresh."""
        # First login to get refresh token
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPass123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Now refresh the access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.security
class TestPasswordSecurity:
    """Security tests for password handling."""
    
    async def test_password_not_in_response(
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
        # Neither password nor password_hash should be in response
        assert "password" not in str(data).lower()
        assert "hash" not in str(data).lower()
    
    async def test_login_timing_attack_resistance(
        self,
        client: AsyncClient,
        test_user
    ):
        """Test login endpoint is resistant to timing attacks."""
        import time
        
        # Time with existing user, wrong password
        start = time.time()
        await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "WrongPassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        existing_user_time = time.time() - start
        
        # Time with non-existent user
        start = time.time()
        await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "WrongPassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        nonexistent_user_time = time.time() - start
        
        # Times should be similar (within 200ms)
        # This prevents user enumeration via timing
        time_diff = abs(existing_user_time - nonexistent_user_time)
        assert time_diff < 0.2
