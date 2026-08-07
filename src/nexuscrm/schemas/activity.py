"""Pydantic schemas for Activity."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from nexuscrm.models.activity import ActivityType


class ActivityBase(BaseModel):
    type: ActivityType
    subject: str
    content: str
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    id: str
    sentiment_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

