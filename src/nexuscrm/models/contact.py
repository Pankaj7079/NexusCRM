"""Contact Model."""

from enum import Enum
from typing import Optional
from sqlalchemy import String, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nexuscrm.core.db import Base


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CUSTOMER = "customer"


class Contact(Base):
    """Customer Contact entity model."""

    __tablename__ = "contacts"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    lead_status: Mapped[LeadStatus] = mapped_column(
        SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False
    )
    lead_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0 to 100
    churn_risk: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0.0 to 1.0

    company_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id"), nullable=True)

    # Relationships
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="contacts")
    deals: Mapped[list["Deal"]] = relationship("Deal", back_populates="contact")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="contact")
