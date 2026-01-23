"""
Pytest fixtures and configuration for tests.

Provides:
- Test database setup
- Test client
- Authenticated user fixtures
- Factory functions
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.security import create_access_token
from app.database import Base, get_db
from app.main import app
from app.models import User, Contact, Phone, ContactPhone

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

# Create test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create event loop for async tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session.
    
    Yields:
        AsyncSession: Test database session
        
    Note: Creates all tables before each test and drops them after.
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test client with test database.
    
    Args:
        db_session: Test database session
        
    Yields:
        AsyncClient: Test HTTP client
    """
    # Override database dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Create test user.
    
    Returns:
        User: Test user instance
    """
    from app.crud import user as user_crud
    from app.schemas.user import UserCreate
    
    user_in = UserCreate(
        email="test@example.com",
        password="TestPass123!"
    )
    
    user = await user_crud.create(db_session, obj_in=user_in)
    await db_session.commit()
    
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> User:
    """
    Create test admin user.
    
    Returns:
        User: Test admin user instance
    """
    from app.crud import user as user_crud
    from app.schemas.user import UserCreate
    
    user_in = UserCreate(
        email="admin@example.com",
        password="AdminPass123!"
    )
    
    user = await user_crud.create(db_session, obj_in=user_in)
    user.role = "admin"  # Promote to admin
    db_session.add(user)
    await db_session.commit()
    
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    """
    Create JWT access token for test user.
    
    Args:
        test_user: Test user instance
        
    Returns:
        str: JWT access token
    """
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def admin_token(test_admin: User) -> str:
    """
    Create JWT access token for test admin.
    
    Args:
        test_admin: Test admin instance
        
    Returns:
        str: JWT access token
    """
    return create_access_token(data={"sub": test_admin.email})


@pytest_asyncio.fixture
async def test_contact(db_session: AsyncSession, test_user: User) -> Contact:
    """
    Create test contact.
    
    Args:
        db_session: Database session
        test_user: Test user instance
        
    Returns:
        Contact: Test contact instance
    """
    from app.crud import contact as contact_crud
    from app.schemas.contact import ContactCreate
    
    contact_in = ContactCreate(
        name="John Doe",
        email="john@example.com",
        company="ACME Corp",
        position="CEO"
    )
    
    contact = await contact_crud.create_with_user(
        db_session, obj_in=contact_in, user_id=test_user.id
    )
    await db_session.commit()
    
    return contact


@pytest_asyncio.fixture
async def test_phone(db_session: AsyncSession) -> Phone:
    """
    Create test phone.
    
    Args:
        db_session: Database session
        
    Returns:
        Phone: Test phone instance
    """
    from app.crud import phone as phone_crud
    from app.schemas.phone import PhoneCreate
    
    phone_in = PhoneCreate(
        phone_number="+48123456789",
        phone_type="mobile"
    )
    
    phone = await phone_crud.create(db_session, obj_in=phone_in)
    await db_session.commit()
    
    return phone


# Factory fixtures for creating multiple test objects
@pytest.fixture
def user_factory(db_session: AsyncSession):
    """
    Factory for creating test users.
    
    Usage:
        user1 = await user_factory("user1@example.com")
        user2 = await user_factory("user2@example.com")
    """
    from app.crud import user as user_crud
    from app.schemas.user import UserCreate
    
    async def _create_user(email: str, password: str = "TestPass123!") -> User:
        user_in = UserCreate(email=email, password=password)
        user = await user_crud.create(db_session, obj_in=user_in)
        await db_session.commit()
        return user
    
    return _create_user


@pytest.fixture
def contact_factory(db_session: AsyncSession, test_user: User):
    """
    Factory for creating test contacts.
    
    Usage:
        contact1 = await contact_factory("John Doe")
        contact2 = await contact_factory("Jane Smith", email="jane@example.com")
    """
    from app.crud import contact as contact_crud
    from app.schemas.contact import ContactCreate
    
    async def _create_contact(
        name: str,
        email: str | None = None,
        company: str | None = None
    ) -> Contact:
        contact_in = ContactCreate(
            name=name,
            email=email,
            company=company
        )
        contact = await contact_crud.create_with_user(
            db_session, obj_in=contact_in, user_id=test_user.id
        )
        await db_session.commit()
        return contact
    
    return _create_contact
