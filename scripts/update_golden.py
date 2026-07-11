#!/usr/bin/env python3
"""Regenerate golden DOCX and structural fingerprint baselines.

Review diffs before commit. Do not run in CI.
"""

from __future__ import annotations

import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.document_engine.renderer import DocumentRenderer
from template_builder.builder import TemplateBuilder
from tests.conftest import (
    GOLDEN_DOCX_DIR,
    GOLDEN_FP_DIR,
    RENDER_CASES,
    golden_docx_path,
    golden_fingerprint_path,
    load_product_config,
)
from tests.docx_structure import extract_docx_fingerprint, fingerprint_to_json

FIXTURES_DIR = ROOT / "tests" / "fixtures"


def _common_kwargs() -> dict:
    approval = {
        "prepared_by": {"name": "A", "designation": "QA", "date": "01 JAN 2025"},
        "checked_by": {"name": "B", "designation": "QA", "date": "01 JAN 2025"},
        "approved_by": {"name": "C", "designation": "QA Head", "date": "01 JAN 2025"},
    }
    return {
        "revision_no": "01",
        "effective_date": date(2025, 1, 1),
        "review_date": date(2028, 1, 1),
        "superseded_revision": "New",
        "approval": approval,
    }


def main() -> None:
    print("Review diff before commit. Do not run in CI.")
    get_settings.cache_clear()

    import os

    os.environ["STATIC_DIR"] = str(FIXTURES_DIR)
    generated = ROOT / "generated" / "golden_capture"
    generated.mkdir(parents=True, exist_ok=True)
    os.environ["GENERATED_DIR"] = str(generated)

    templates_dir = ROOT / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    if not (templates_dir / "base_annexure.docx").exists():
        TemplateBuilder().build_all_base_templates(templates_dir)

    settings = get_settings()
    renderer = DocumentRenderer(templates_dir=templates_dir)
    kwargs = _common_kwargs()

    GOLDEN_DOCX_DIR.mkdir(parents=True, exist_ok=True)
    GOLDEN_FP_DIR.mkdir(parents=True, exist_ok=True)

    for case in RENDER_CASES:
        key = case["key"]
        config = load_product_config(case["config_name"])
        path = renderer.render(
            case["doc_type"],
            config,
            case["output_name"],
            **kwargs,
            **case["extra"],
        )
        dest = golden_docx_path(key)
        shutil.copy2(path, dest)
        fp = extract_docx_fingerprint(dest)
        golden_fingerprint_path(key).write_text(fingerprint_to_json(fp), encoding="utf-8")
        print(f"  {key}: {dest} + {golden_fingerprint_path(key)}")

    print("Done. Review golden files before commit.")


if __name__ == "__main__":
    main()
