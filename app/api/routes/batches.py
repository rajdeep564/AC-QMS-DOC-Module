from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.batch import BatchRepository
from app.repositories.product import ProductRepository
from app.schemas.batch import BatchCreate, BatchResponse

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("", response_model=BatchResponse, status_code=201)
def create_batch(data: BatchCreate, db: Session = Depends(get_db)):
    product = ProductRepository(db).get_by_id(data.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return BatchRepository(db).create(data)
