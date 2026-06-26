#!/usr/bin/env python3
"""Generate example MOA, Protocol, Specification, and SOP documents."""

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.core.constants import DocumentType
from app.database.session import init_db
from app.document_engine.renderer import DocumentRenderer
from app.schemas.product import ProductConfig


def main() -> None:
    settings = get_settings()
    renderer = DocumentRenderer()
    approval = {
        "prepared_by": {
            "name": "Jayrajsinh Chauhan",
            "designation": "QA Executive",
            "date": "21 MAY 2025",
        },
        "checked_by": {
            "name": "Aryan Prajapati",
            "designation": "QA Executive",
            "date": "21 MAY 2025",
        },
        "approved_by": {
            "name": "Anupsinh Gadhavi",
            "designation": "QA Head",
            "date": "21 MAY 2025",
        },
    }

    common = {
        "revision_no": "01",
        "effective_date": date(2025, 5, 21),
        "review_date": date(2028, 5, 20),
        "superseded_revision": "New",
        "approval": approval,
    }

    glycine_path = settings.products_config_dir / "glycine_ip.json"
    glycine = ProductConfig.model_validate_json(glycine_path.read_text(encoding="utf-8"))

    print(renderer.render(DocumentType.MOA, glycine, "example_glycine_moa.docx", document_no=glycine.moa_no, **common))
    print(
        renderer.render(
            DocumentType.PROTOCOL,
            glycine,
            "example_glycine_protocol.docx",
            document_no=glycine.protocol_no,
            batch={
                "batch_no": "BATCH-001",
                "mfg_date": "JAN 2025",
                "exp_date": "JAN 2028",
                "ar_no": "AR-2025-001",
            },
            **common,
        )
    )
    print(
        renderer.render(
            DocumentType.SPECIFICATION,
            glycine,
            "example_glycine_spec.docx",
            document_no=glycine.specification_no,
            **common,
        )
    )

    sop_path = settings.products_config_dir / "sop_on_sop.json"
    sop_config = ProductConfig.model_validate_json(sop_path.read_text(encoding="utf-8"))
    print(
        renderer.render(
            DocumentType.SOP,
            sop_config,
            "example_sop_on_sop.docx",
            document_no="QA 01",
            subject="SOP ON SOP",
            **common,
        )
    )

    init_db()
    print("Done. Check the generated/ folder.")


if __name__ == "__main__":
    main()
