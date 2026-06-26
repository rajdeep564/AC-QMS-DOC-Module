from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.product import ProductRepository
from app.schemas.batch import BatchCreate, BatchResponse
from app.schemas.product import ProductCreate, ProductResponse
from app.repositories.batch import BatchRepository

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    if repo.get_by_code(data.product_code):
        raise HTTPException(400, f"Product code already exists: {data.product_code}")
    return repo.create(data)


@router.get("", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return ProductRepository(db).list_all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = ProductRepository(db).get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.post("/import", response_model=ProductResponse, status_code=201)
async def import_product(file: UploadFile = File(...), db: Session = Depends(get_db)):
    import json
    import tempfile
    from pathlib import Path

    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e}") from e

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(data, tmp)
        tmp_path = Path(tmp.name)

    try:
        return ProductRepository(db).import_from_file(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
