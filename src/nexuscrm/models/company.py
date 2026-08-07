"""Company Model."""

from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nexuscrm.core.db import Base


class Company(Base):
    """Company/Organization entity model."""

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    employee_count: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    annual_revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationships
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    deals: Mapped[list["Deal"]] = relationship("Deal", back_populates="company")
