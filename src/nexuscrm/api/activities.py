"""Activities API router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexuscrm.core.db import get_db
from nexuscrm.api.auth import get_current_user
from nexuscrm.models.user import User
from nexuscrm.models.activity import Activity, ActivityType
from nexuscrm.schemas.activity import ActivityCreate, ActivityResponse

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("", response_model=List[ActivityResponse])
async def list_activities(
    skip: int = 0,
    limit: int = 50,
    contact_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    activity_type: Optional[ActivityType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve activity log feed."""
    query = select(Activity).where(Activity.is_deleted == False)

    if contact_id:
        query = query.where(Activity.contact_id == contact_id)
    if deal_id:
        query = query.where(Activity.deal_id == deal_id)
    if activity_type:
        query = query.where(Activity.type == activity_type)

    query = query.offset(skip).limit(limit).order_by(Activity.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_in: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a new activity record."""
    activity = Activity(**activity_in.model_dump())
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity
