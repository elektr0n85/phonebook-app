"""
Integration tests for contacts endpoints.

Tests:
- CRUD operations
- Search functionality
- Authorization (ownership checks)
- Phone management
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestContactCRUD:
    """Test contact CRUD operations."""
    
    async def test_list_contacts_empty(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test listing contacts when user has none."""
        response = await client.get(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_list_contacts_with_data(
        self,
        client: AsyncClient,
        user_token: str,
        test_contact
    ):
        """Test listing contacts returns user's contacts."""
        response = await client.get(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == test_contact.name
        assert data[0]["email"] == test_contact.email
    
    async def test_create_contact_basic(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test creating a basic contact."""
        response = await client.post(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Jane Smith",
                "email": "jane@example.com",
                "company": "Tech Corp"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jane Smith"
        assert data["email"] == "jane@example.com"
        assert data["company"] == "Tech Corp"
        assert "id" in data
    
    async def test_create_contact_with_phones(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test creating contact with multiple phones."""
        response = await client.post(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phones": [
                    {
                        "phone_data": {
                            "phone_number": "+48123456789",
                            "phone_type": "mobile"
                        },
                        "is_primary": True,
                        "label": "Personal"
                    },
                    {
                        "phone_data": {
                            "phone_number": "171234567",
                            "phone_type": "landline"
                        },
                        "label": "Office"
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert len(data["phones"]) == 2
        
        # Check primary phone
        primary_phone = next(p for p in data["phones"] if p["is_primary"])
        assert primary_phone["phone"]["phone_type"] == "mobile"
        assert primary_phone["label"] == "Personal"
    
    async def test_create_contact_without_auth(self, client: AsyncClient):
        """Test creating contact without authentication fails."""
        response = await client.post(
            "/api/v1/contacts/",
            json={"name": "Test User"}
        )
        
        assert response.status_code == 401
    
    async def test_get_contact_details(
        self,
        client: AsyncClient,
        user_token: str,
        test_contact
    ):
        """Test getting contact details."""
        response = await client.get(
            f"/api/v1/contacts/{test_contact.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_contact.id
        assert data["name"] == test_contact.name
        assert "phones" in data
    
    async def test_get_nonexistent_contact(
        self,
        client: AsyncClient,
        user_token: str
    ):
        """Test getting non-existent contact returns 404."""
        response = await client.get(
            "/api/v1/contacts/99999",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 404
    
    async def test_update_contact(
        self,
        client: AsyncClient,
        user_token: str,
        test_contact
    ):
        """Test updating contact information."""
        response = await client.put(
            f"/api/v1/contacts/{test_contact.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Updated Name",
                "email": "updated@example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.com"
    
    async def test_delete_contact(
        self,
        client: AsyncClient,
        user_token: str,
        test_contact
    ):
        """Test soft deleting a contact."""
        response = await client.delete(
            f"/api/v1/contacts/{test_contact.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify contact is no longer in list
        list_response = await client.get(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert len(list_response.json()) == 0


@pytest.mark.integration
class TestContactSearch:
    """Test contact search functionality."""
    
    async def test_search_by_name(
        self,
        client: AsyncClient,
        user_token: str,
        contact_factory
    ):
        """Test searching contacts by name."""
        await contact_factory("Alice Johnson")
        await contact_factory("Bob Smith")
        await contact_factory("Charlie Brown")
        
        response = await client.get(
            "/api/v1/contacts/?search=Alice",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Johnson"
    
    async def test_search_by_email(
        self,
        client: AsyncClient,
        user_token: str,
        contact_factory
    ):
        """Test searching contacts by email."""
        await contact_factory("Alice", email="alice@example.com")
        await contact_factory("Bob", email="bob@different.com")
        
        response = await client.get(
            "/api/v1/contacts/?search=alice@",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "alice@example.com"
    
    async def test_search_case_insensitive(
        self,
        client: AsyncClient,
        user_token: str,
        contact_factory
    ):
        """Test search is case-insensitive."""
        await contact_factory("Alice Johnson")
        
        # Search with different cases
        for query in ["alice", "ALICE", "Alice"]:
            response = await client.get(
                f"/api/v1/contacts/?search={query}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 200
            assert len(response.json()) == 1


@pytest.mark.integration
@pytest.mark.security
class TestContactAuthorization:
    """Test contact authorization and ownership."""
    
    async def test_user_cannot_see_other_users_contacts(
        self,
        client: AsyncClient,
        user_token: str,
        user_factory,
        contact_factory,
        db_session
    ):
        """Test users can only see their own contacts."""
        # Create another user with a contact
        other_user = await user_factory("other@example.com")
        
        # Create contact for other user (bypass contact_factory)
        from app.crud import contact as contact_crud
        from app.schemas.contact import ContactCreate
        
        other_contact = await contact_crud.create_with_user(
            db_session,
            obj_in=ContactCreate(name="Other User Contact"),
            user_id=other_user.id
        )
        await db_session.commit()
        
        # Try to list contacts as first user
        response = await client.get(
            "/api/v1/contacts/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Should not see other user's contact
        data = response.json()
        assert len(data) == 0
    
    async def test_user_cannot_access_other_users_contact_details(
        self,
        client: AsyncClient,
        user_token: str,
        user_factory,
        db_session
    ):
        """Test user cannot access another user's contact details."""
        # Create another user with a contact
        other_user = await user_factory("other@example.com")
        
        from app.crud import contact as contact_crud
        from app.schemas.contact import ContactCreate
        
        other_contact = await contact_crud.create_with_user(
            db_session,
            obj_in=ContactCreate(name="Other User Contact"),
            user_id=other_user.id
        )
        await db_session.commit()
        
        # Try to access other user's contact
        response = await client.get(
            f"/api/v1/contacts/{other_contact.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Should return 404 (not 403 to prevent enumeration)
        assert response.status_code == 404
    
    async def test_user_cannot_update_other_users_contact(
        self,
        client: AsyncClient,
        user_token: str,
        user_factory,
        db_session
    ):
        """Test user cannot update another user's contact."""
        other_user = await user_factory("other@example.com")
        
        from app.crud import contact as contact_crud
        from app.schemas.contact import ContactCreate
        
        other_contact = await contact_crud.create_with_user(
            db_session,
            obj_in=ContactCreate(name="Other User Contact"),
            user_id=other_user.id
        )
        await db_session.commit()
        
        response = await client.put(
            f"/api/v1/contacts/{other_contact.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Hacked Name"}
        )
        
        assert response.status_code == 404
