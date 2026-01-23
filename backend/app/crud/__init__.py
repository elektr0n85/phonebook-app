"""
CRUD package - exports all CRUD operations.
"""
from app.crud.audit_log import audit_log
from app.crud.contact import contact
from app.crud.contact_phone import contact_phone
from app.crud.phone import phone
from app.crud.user import user

__all__ = ["user", "contact", "phone", "contact_phone", "audit_log"]
