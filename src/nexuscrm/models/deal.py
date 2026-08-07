"""Deal Model."""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nexuscrm.core.db import Base


class DealStage(str, Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Deal(Base):
    """Sales Opportunity/Deal entity model."""

    __tablename__ = "deals"

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    stage: Mapped[DealStage] = mapped_column(
        SQLEnum(DealStage), default=DealStage.PROSPECTING, nullable=False
    )
    win_probability: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)  # 0.0 to 1.0
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id"), nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id"), nullable=True)

    # Relationships
    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="deals")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="deals")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="deal")
