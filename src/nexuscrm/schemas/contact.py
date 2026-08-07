"""Pydantic schemas for Contact."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from nexuscrm.models.contact import LeadStatus


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: Optional[str] = None
    lead_status: LeadStatus = LeadStatus.NEW
    company_id: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    lead_status: Optional[LeadStatus] = None
    lead_score: Optional[float] = None
    churn_risk: Optional[float] = None
    company_id: Optional[str] = None


class ContactResponse(ContactBase):
    id: str
    lead_score: float
    churn_risk: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

