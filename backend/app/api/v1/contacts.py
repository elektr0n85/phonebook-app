"""
Contacts API endpoints with phone number management.

Endpoints:
    GET /contacts - List user's contacts (with search)
    POST /contacts - Create new contact with phones
    GET /contacts/{id} - Get contact details with phones
    PUT /contacts/{id} - Update contact
    DELETE /contacts/{id} - Soft delete contact
    POST /contacts/{id}/phones - Add phone to contact
    DELETE /contacts/{id}/phones/{phone_id} - Remove phone from contact
    PUT /contacts/{id}/phones/{phone_id}/primary - Set phone as primary
"""
from fastapi import APIRouter, HTTPException, Query, Request, status

from app import crud
from app.api.deps import CurrentUser, DatabaseSession, get_client_ip, get_user_agent
from app.models.audit_log import AuditAction
from app.schemas.auth import MessageResponse
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.schemas.phone import (
    ContactCreateWithPhones,
    ContactPhoneCreate,
    ContactPhoneResponse,
    ContactWithPhones,
    PhoneCreate,
)

router = APIRouter()


# Maximum contacts per user (security limit)
MAX_CONTACTS_PER_USER = 1000


@router.get("/", response_model=list[ContactResponse])
async def list_contacts(
    *,
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=100)
) -> list[ContactResponse]:
    """
    List current user's contacts with optional search.
    
    Args:
        skip: Number of contacts to skip (pagination)
        limit: Maximum number of contacts to return (max 100)
        search: Optional search query (name, email, company, position)
        
    Returns:
        List of contacts (without phone details)
        
    Security:
        - Only returns user's own contacts
        - SQL injection prevented (ORM)
        - Rate limited to 100 requests per minute (TODO)
    """
    if search:
        # Search contacts
        contacts = await crud.contact.search(
            db, user_id=current_user.id, query=search, skip=skip, limit=limit
        )
    else:
        # List all contacts
        contacts = await crud.contact.get_multi_by_owner(
            db, user_id=current_user.id, skip=skip, limit=limit
        )
    
    return contacts


@router.post("/", response_model=ContactWithPhones, status_code=status.HTTP_201_CREATED)
async def create_contact(
    *,
    db: DatabaseSession,
    request: Request,
    contact_in: ContactCreateWithPhones,
    current_user: CurrentUser
) -> ContactWithPhones:
    """
    Create a new contact with phones.
    
    Args:
        contact_in: Contact data with phones array
        
    Returns:
        Created contact with phone details
        
    Security:
        - Max 1000 contacts per user
        - Input validation (Pydantic)
        - Phone number uniqueness enforced
        - Ownership (contact belongs to current user)
        - Audit log created
        
    Example request:
        {
            "name": "Jan Kowalski",
            "email": "jan@example.com",
            "company": "ACME Corp",
            "phones": [
                {
                    "phone_data": {
                        "phone_number": "+48123456789",
                        "phone_type": "mobile"
                    },
                    "is_primary": true,
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
    """    
    # Check max contacts limit
    contact_count = await crud.contact.count_by_owner(db, user_id=current_user.id)
    if contact_count >= MAX_CONTACTS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum number of contacts ({MAX_CONTACTS_PER_USER}) reached"
        )
    
    # Create contact (without phones first)
    contact_data = ContactCreate(
        name=contact_in.name,
        email=contact_in.email,
        address=contact_in.address,
        notes=contact_in.notes,
        company=contact_in.company,
        position=contact_in.position
    )
    
    contact = await crud.contact.create_with_user(
        db, obj_in=contact_data, user_id=current_user.id
    )
    
    # Add phones
    for phone_in in contact_in.phones:
        if phone_in.phone_data:
            # Create new phone (or get existing)
            phone, created = await crud.phone.get_or_create(
                db, obj_in=phone_in.phone_data
            )
            
            # Link phone to contact
            await crud.contact_phone.add_phone_to_contact(
                db,
                contact_id=contact.id,
                phone_id=phone.id,
                is_primary=phone_in.is_primary,
                label=phone_in.label,
                notes=phone_in.notes
            )
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action=AuditAction.CONTACT_CREATE,
        resource_type="contact",
        resource_id=contact.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"name": contact.name, "phones_count": len(contact_in.phones)}
    )
    
    # Reload contact with phones
    contact_with_phones = await crud.contact.get_with_phones(db, id=contact.id)
    if contact_with_phones:
        await db.refresh(contact_with_phones, ["phones"])
        # Eager load nested phone relationships
        for contact_phone in contact_with_phones.phones:
            await db.refresh(contact_phone, ["phone"])
        return contact_with_phones
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created contact"
        )


@router.get("/{contact_id}", response_model=ContactWithPhones)
async def get_contact(
    *,
    db: DatabaseSession,
    current_user: CurrentUser,
    contact_id: int
) -> ContactWithPhones:
    """
    Get contact details with phones.
    
    Args:
        contact_id: Contact ID
        
    Returns:
        Contact with phone details
        
    Security:
        - Ownership check (404 if not owned by user)
        - Returns 404 instead of 403 (prevents contact enumeration)
    """
    contact = await crud.contact.get_with_phones(db, id=contact_id)
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Ownership check
    if contact.user_id != current_user.id:
        # Return 404 instead of 403 to prevent contact enumeration
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Don't return deleted contacts
    if contact.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
        
    # Eager load nested phone relationships
    for contact_phone in contact.phones:
        await db.refresh(contact_phone, ["phone"])
    
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    *,
    db: DatabaseSession,
    request: Request,
    current_user: CurrentUser,
    contact_id: int,
    contact_in: ContactUpdate
) -> ContactResponse:
    """
    Update contact information.
    
    Args:
        contact_id: Contact ID
        contact_in: Updated contact data (partial update)
        
    Returns:
        Updated contact
        
    Security:
        - Ownership check
        - Audit log created
        
    Note: Use separate endpoints to manage phones
    """
    contact = await crud.contact.get(db, id=contact_id)
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Ownership check
    if contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Don't update deleted contacts
    if contact.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Update contact
    updated_contact = await crud.contact.update(db, db_obj=contact, obj_in=contact_in)
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action=AuditAction.CONTACT_UPDATE,
        resource_type="contact",
        resource_id=contact.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"updated_fields": list(contact_in.model_dump(exclude_unset=True).keys())}
    )
    
    return updated_contact


@router.delete("/{contact_id}", response_model=MessageResponse)
async def delete_contact(
    *,
    db: DatabaseSession,
    request: Request,
    current_user: CurrentUser,
    contact_id: int
) -> MessageResponse:
    """
    Soft delete a contact.
    
    Args:
        contact_id: Contact ID
        
    Returns:
        Success message
        
    Security:
        - Ownership check
        - Soft delete (data recovery possible)
        - Audit log created
        
    Note: Phone numbers are not deleted (may be shared with other contacts)
    """
    contact = await crud.contact.get(db, id=contact_id)
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Ownership check
    if contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Already deleted?
    if contact.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Soft delete
    await crud.contact.soft_delete(db, id=contact.id)
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action=AuditAction.CONTACT_DELETE,
        resource_type="contact",
        resource_id=contact.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"name": contact.name}
    )
    
    return MessageResponse(message="Contact deleted successfully")


# ============================================================================
# Phone Management Endpoints
# ============================================================================

@router.post("/{contact_id}/phones", response_model=ContactPhoneResponse, status_code=status.HTTP_201_CREATED)
async def add_phone_to_contact(
    *,
    db: DatabaseSession,
    request: Request,
    current_user: CurrentUser,
    contact_id: int,
    phone_in: ContactPhoneCreate
) -> ContactPhoneResponse:
    """
    Add a phone number to a contact.
    
    Args:
        contact_id: Contact ID
        phone_in: Phone data (either phone_id or phone_data)
        
    Returns:
        Created ContactPhone relationship
        
    Security:
        - Ownership check
        - Phone uniqueness enforced
        - Duplicate link prevention
        
    Example request (new phone):
        {
            "phone_data": {
                "phone_number": "+48555666777",
                "phone_type": "mobile"
            },
            "is_primary": false,
            "label": "Work mobile"
        }
        
    Example request (existing phone):
        {
            "phone_id": 5,
            "label": "Office"
        }
    """
    # Get contact and verify ownership
    contact = await crud.contact.get(db, id=contact_id)
    
    if not contact or contact.user_id != current_user.id or contact.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Get or create phone
    if phone_in.phone_id:
        # Use existing phone
        phone = await crud.phone.get(db, id=phone_in.phone_id)
        if not phone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone not found"
            )
    elif phone_in.phone_data:
        # Create new phone or get existing
        phone, created = await crud.phone.get_or_create(db, obj_in=phone_in.phone_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either phone_id or phone_data must be provided"
        )
    
    # Check if phone is already linked to this contact
    exists = await crud.contact_phone.exists(
        db, contact_id=contact.id, phone_id=phone.id
    )
    
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This phone is already linked to this contact"
        )
    
    # Add phone to contact
    contact_phone = await crud.contact_phone.add_phone_to_contact(
        db,
        contact_id=contact.id,
        phone_id=phone.id,
        is_primary=phone_in.is_primary,
        label=phone_in.label,
        notes=phone_in.notes
    )
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action="contact_phone_add",
        resource_type="contact",
        resource_id=contact.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"phone_id": phone.id, "phone_number": phone.phone_number}
    )
    
    # Reload with phone details
    await db.refresh(contact_phone, ["phone"])
    
    return contact_phone


@router.delete("/{contact_id}/phones/{phone_id}", response_model=MessageResponse)
async def remove_phone_from_contact(
    *,
    db: DatabaseSession,
    request: Request,
    current_user: CurrentUser,
    contact_id: int,
    phone_id: int
) -> MessageResponse:
    """
    Remove a phone number from a contact.
    
    Args:
        contact_id: Contact ID
        phone_id: Phone ID
        
    Returns:
        Success message
        
    Security:
        - Ownership check
        - Does not delete the phone itself (may be shared)
        - Audit log created
    """
    # Get contact and verify ownership
    contact = await crud.contact.get(db, id=contact_id)
    
    if not contact or contact.user_id != current_user.id or contact.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Remove phone from contact
    removed = await crud.contact_phone.remove_phone_from_contact(
        db, contact_id=contact.id, phone_id=phone_id
    )
    
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone not found for this contact"
        )
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action="contact_phone_remove",
        resource_type="contact",
        resource_id=contact.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"phone_id": phone_id}
    )
    
    return MessageResponse(message="Phone removed from contact successfully")


@router.put("/{contact_id}/phones/{phone_id}/primary", response_model=ContactPhoneResponse)
async def set_primary_phone(
    *,
    db: DatabaseSession,
    request: Request,
    current_user: CurrentUser,
    contact_id: int,
    phone_id: int
) -> ContactPhoneResponse:
    """
    Set a phone as primary for a contact.
    
    Args:
        contact_id: Contact ID
        phone_id: Phone ID to set as primary
        
    Returns:
        Updated ContactPhone relationship
        
    Security:
        - Ownership check
        - Auto-unsets other primary phones for this contact
        - Audit log created
    """
    # Get contact and verify ownership
    contact = await crud.contact.get(db, id=contact_id)
    
    if not contact or contact.user_id != current_user.id or contact.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Set phone as primary
    contact_phone = await crud.contact_phone.update_primary_phone(
        db, contact_id=contact.id, phone_id=phone_id
    )
    
    if not contact_phone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone not found for this contact"
        )
    
    # Audit log
    await crud.audit_log.create_log(
        db,
        user_id=current_user.id,
        action="contact_phone_set_primary",
        resource_type="contact",
        resource_id=contact.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"phone_id": phone_id}
    )
    
    # Reload with phone details
    await db.refresh(contact_phone, ["phone"])
    
    return contact_phone
