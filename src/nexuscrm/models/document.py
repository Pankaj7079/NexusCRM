"""Document and AgentLog ORM models."""

from typing import Optional
from sqlalchemy import String, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from nexuscrm.core.db import Base


class Document(Base):
    """Document record for RAG Knowledge Base."""

    __tablename__ = "documents"

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, docx, txt
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, indexed, failed
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AgentLog(Base):
    """Execution audit log for AI agents."""

    __tablename__ = "agent_logs"

    agent_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    task_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    input_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    output_result: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    success: Mapped[bool] = mapped_column(default=True, nullable=False)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
