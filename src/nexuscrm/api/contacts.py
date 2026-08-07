"""Contacts API router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from nexuscrm.core.db import get_db
from nexuscrm.api.auth import get_current_user
from nexuscrm.models.user import User
from nexuscrm.models.contact import Contact, LeadStatus
from nexuscrm.schemas.contact import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=List[ContactResponse])
async def list_contacts(
    skip: int = 0,
    limit: int = 50,
    lead_status: Optional[LeadStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve contacts with optional filtering and search."""
    query = select(Contact).where(Contact.is_deleted == False)

    if lead_status:
        query = query.where(Contact.lead_status == lead_status)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (Contact.first_name.ilike(pattern))
            | (Contact.last_name.ilike(pattern))
            | (Contact.email.ilike(pattern))
        )

    query = query.offset(skip).limit(limit).order_by(Contact.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new contact."""
    existing = await db.execute(
        select(Contact).where(Contact.email == contact_in.email, Contact.is_deleted == False)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Contact with this email already exists")

    contact = Contact(**contact_in.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get contact by ID."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    contact_in: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update contact by ID."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = contact_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete contact by ID."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.is_deleted = True
    await db.commit()
