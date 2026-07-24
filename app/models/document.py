from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    batch_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("batches.id"), nullable=True, index=True
    )
    document_type: Mapped[str] = mapped_column(String(32), index=True)
    document_no: Mapped[str] = mapped_column(String(128), index=True)
    revision_no: Mapped[str] = mapped_column(String(16), default="01")
    subject: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    department: Mapped[str] = mapped_column(String(128), default="QUALITY ASSURANCE")
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    superseded_revision: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="GENERATED")
    context_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    docx_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    product: Mapped["Product"] = relationship(back_populates="documents")
    batch: Mapped[Optional["Batch"]] = relationship(back_populates="documents")
