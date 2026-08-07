"""Deals API router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from nexuscrm.core.db import get_db
from nexuscrm.api.auth import get_current_user
from nexuscrm.models.user import User
from nexuscrm.models.deal import Deal, DealStage
from nexuscrm.schemas.deal import DealCreate, DealUpdate, DealResponse

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("", response_model=List[DealResponse])
async def list_deals(
    skip: int = 0,
    limit: int = 50,
    stage: Optional[DealStage] = None,
    contact_id: Optional[str] = None,
    company_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve deals pipeline."""
    query = select(Deal).where(Deal.is_deleted == False)

    if stage:
        query = query.where(Deal.stage == stage)
    if contact_id:
        query = query.where(Deal.contact_id == contact_id)
    if company_id:
        query = query.where(Deal.company_id == company_id)

    query = query.offset(skip).limit(limit).order_by(Deal.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_in: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new deal."""
    deal = Deal(**deal_in.model_dump())
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


@router.get("/pipeline-summary")
async def get_pipeline_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Summarize deals pipeline by stage and total revenue value."""
    result = await db.execute(
        select(Deal.stage, func.count(Deal.id), func.sum(Deal.value))
        .where(Deal.is_deleted == False)
        .group_by(Deal.stage)
    )
    summary = {}
    total_value = 0.0
    for stage, count, val in result.all():
        value_sum = float(val or 0.0)
        summary[stage.value if hasattr(stage, "value") else str(stage)] = {
            "count": count,
            "total_value": value_sum,
        }
        total_value += value_sum

    return {"by_stage": summary, "total_pipeline_value": total_value}


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get deal details by ID."""
    result = await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False)
    )
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: str,
    deal_in: DealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update deal details or stage."""
    result = await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False)
    )
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    update_data = deal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)

    await db.commit()
    await db.refresh(deal)
    return deal
