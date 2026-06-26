from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.schemas.batch import BatchCreate


class BatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: BatchCreate) -> Batch:
        batch = Batch(**data.model_dump())
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_by_id(self, batch_id: int) -> Batch | None:
        return self.db.get(Batch, batch_id)
