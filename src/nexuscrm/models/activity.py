"""Activity Model for interactions (emails, calls, meetings, notes, support tickets)."""

from enum import Enum
from typing import Optional
from sqlalchemy import String, Text, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nexuscrm.core.db import Base


class ActivityType(str, Enum):
    EMAIL = "email"
    CALL = "call"
    MEETING = "meeting"
    NOTE = "note"
    SUPPORT_TICKET = "support_ticket"


class Activity(Base):
    """Customer interaction activity record."""

    __tablename__ = "activities"

    type: Mapped[ActivityType] = mapped_column(SQLEnum(ActivityType), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # -1.0 to 1.0

    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id"), nullable=True)
    deal_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("deals.id"), nullable=True)

    # Relationships
    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="activities")
    deal: Mapped[Optional["Deal"]] = relationship("Deal", back_populates="activities")
