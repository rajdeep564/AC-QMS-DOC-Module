import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductConfig, ProductCreate


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: ProductCreate) -> Product:
        config = ProductConfig.model_validate(data.model_dump())
        product = Product(
            product_code=data.product_code,
            product_name=data.product_name,
            reference=data.reference,
            molecular_weight=data.molecular_weight,
            chemical_formula=data.chemical_formula,
            config_json=config.model_dump_json(),
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_code(self, product_code: str) -> Product | None:
        return (
            self.db.query(Product)
            .filter(Product.product_code == product_code)
            .first()
        )

    def list_all(self) -> list[Product]:
        return self.db.query(Product).order_by(Product.product_name).all()

    def import_from_file(self, file_path: Path) -> Product:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        create_data = ProductCreate.model_validate(data)
        existing = self.get_by_code(create_data.product_code)
        if existing:
            existing.product_name = create_data.product_name
            existing.reference = create_data.reference
            existing.molecular_weight = create_data.molecular_weight
            existing.chemical_formula = create_data.chemical_formula
            existing.config_json = ProductConfig.model_validate(
                create_data.model_dump()
            ).model_dump_json()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create(create_data)

    def get_config(self, product: Product) -> ProductConfig:
        return ProductConfig.model_validate_json(product.config_json)
