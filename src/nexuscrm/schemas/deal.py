"""Pydantic schemas for Deal."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from nexuscrm.models.deal import DealStage


class DealBase(BaseModel):
    title: str
    value: float = 0.0
    stage: DealStage = DealStage.PROSPECTING
    win_probability: float = 0.2
    expected_close_date: Optional[datetime] = None
    contact_id: Optional[str] = None
    company_id: Optional[str] = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: Optional[str] = None
    value: Optional[float] = None
    stage: Optional[DealStage] = None
    win_probability: Optional[float] = None
    expected_close_date: Optional[datetime] = None
    contact_id: Optional[str] = None
    company_id: Optional[str] = None


class DealResponse(DealBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

