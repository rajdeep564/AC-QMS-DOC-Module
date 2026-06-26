from datetime import date

from pydantic import BaseModel, Field


class BatchCreate(BaseModel):
    product_id: int
    batch_no: str
    mfg_date: date | None = None
    exp_date: date | None = None
    batch_size: str | None = None
    ar_no: str | None = None


class BatchResponse(BaseModel):
    id: int
    product_id: int
    batch_no: str
    mfg_date: date | None
    exp_date: date | None
    batch_size: str | None
    ar_no: str | None

    model_config = {"from_attributes": True}
