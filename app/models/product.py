from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    product_name: Mapped[str] = mapped_column(String(255))
    reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    molecular_weight: Mapped[str | None] = mapped_column(String(64), nullable=True)
    chemical_formula: Mapped[str | None] = mapped_column(String(128), nullable=True)
    config_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    batches: Mapped[list["Batch"]] = relationship(back_populates="product")
    documents: Mapped[list["Document"]] = relationship(back_populates="product")
