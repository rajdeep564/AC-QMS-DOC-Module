from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    batch_no: Mapped[str] = mapped_column(String(64), index=True)
    mfg_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exp_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    batch_size: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ar_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="batches")
    documents: Mapped[list["Document"]] = relationship(back_populates="batch")
