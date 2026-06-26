#!/usr/bin/env python3
"""Initialize database and import all product configs."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.database.session import SessionLocal, init_db
from app.repositories.product import ProductRepository


def main() -> None:
    init_db()
    settings = get_settings()
    db = SessionLocal()
    repo = ProductRepository(db)

    for json_file in sorted(settings.products_config_dir.glob("*.json")):
        product = repo.import_from_file(json_file)
        print(f"Imported: {product.product_code} - {product.product_name}")

    db.close()
    print("Database initialized.")


if __name__ == "__main__":
    main()
