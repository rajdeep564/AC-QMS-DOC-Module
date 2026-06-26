"""Build Jinja2/docxtpl rendering context from product config and request data."""

import json
from datetime import date
from typing import Any

from app.core.config import get_settings
from app.core.constants import DOCUMENT_NUMBER_PREFIX, DocumentType
from app.document_engine.section_numbering import number_sop_sections, number_tests
from app.schemas.product import ProductConfig


def _serialize_dates(obj: Any) -> Any:
    if isinstance(obj, date):
        return obj.strftime("%d %b %Y").upper()
    if isinstance(obj, dict):
        return {k: _serialize_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_dates(i) for i in obj]
    return obj


def build_document_context(
    product_config: ProductConfig | dict,
    document_type: DocumentType,
    *,
    document_no: str | None = None,
    revision_no: str = "01",
    subject: str | None = None,
    department: str = "QUALITY ASSURANCE",
    effective_date: date | None = None,
    review_date: date | None = None,
    superseded_revision: str | None = None,
    approval: dict | None = None,
    revision_history: list[dict] | None = None,
    batch: dict | None = None,
    extra_context: dict | None = None,
) -> dict[str, Any]:
    settings = get_settings()

    if isinstance(product_config, ProductConfig):
        config = product_config.model_dump()
    else:
        config = dict(product_config)

    product_name = config.get("product_name", "")
    reference = config.get("reference", "")

    if not document_no:
        prefix = DOCUMENT_NUMBER_PREFIX.get(document_type, "DOC")
        code = config.get("product_code", "00000")
        document_no = f"{prefix}{code}/{revision_no}"
        if reference:
            document_no = f"{document_no} ({reference})"

    doc_no_labels = {
        DocumentType.MOA: "MOA NO.",
        DocumentType.PROTOCOL: "PROTOCOL NO.",
        DocumentType.SOP: "SOP NO.",
        DocumentType.ANNEXURE: "ANNEXURE NO.",
        DocumentType.SPECIFICATION: "SPECIFICATION NO.",
        DocumentType.STANDARD_FORMAT: "FORMAT NO.",
    }

    doc_type_labels = {
        DocumentType.MOA: "METHOD OF ANALYSIS",
        DocumentType.PROTOCOL: "ANALYSIS PROTOCOL",
        DocumentType.SOP: "STANDARD OPERATING PROCEDURE",
        DocumentType.ANNEXURE: "ANNEXURE",
        DocumentType.SPECIFICATION: "PRODUCT SPECIFICATION",
        DocumentType.STANDARD_FORMAT: "STANDARD FORMAT",
    }

    tests_raw = config.get("tests", [])
    additional = config.get("additional_tests", [])
    micro = config.get("microbiological_tests", [])
    sop_sections_raw = config.get("sop_sections", [])

    tests = number_tests([t if isinstance(t, dict) else t for t in tests_raw])
    additional_tests = number_tests(
        [t if isinstance(t, dict) else t for t in additional],
        start=len(tests) + 1,
    )
    micro_tests = number_tests(
        [t if isinstance(t, dict) else t for t in micro],
        start=len(tests) + len(additional_tests) + 1,
    )
    sop_sections = number_sop_sections(
        [s if isinstance(s, dict) else s for s in sop_sections_raw]
    )

    # Protocol summary table rows — supports grouped tests (e.g. Identification + sub-tests)
    protocol_summary: list[dict[str, Any]] = []
    sr = 1

    def add_test_rows(test_list: list[dict]) -> None:
        nonlocal sr
        for test in test_list:
            sub_tests = test.get("sub_tests") or []
            if sub_tests:
                protocol_summary.append(
                    {
                        "row_type": "group_header",
                        "sr_no": sr,
                        "name": test.get("name", ""),
                        "result": "",
                        "limit": "",
                    }
                )
                for sub in sub_tests:
                    protocol_summary.append(
                        {
                            "row_type": "sub_test",
                            "sr_no": "",
                            "name": sub.get("name", ""),
                            "result": "",
                            "limit": sub.get("acceptance_criteria_display", ""),
                        }
                    )
                sr += 1
            else:
                protocol_summary.append(
                    {
                        "row_type": "standard",
                        "sr_no": sr,
                        "name": test.get("name", ""),
                        "result": "",
                        "limit": test.get("acceptance_criteria_display", ""),
                    }
                )
                sr += 1

    add_test_rows(tests)
    if additional_tests:
        protocol_summary.append(
            {"row_type": "section_label", "sr_no": "", "name": "Additional Tests", "result": "", "limit": ""}
        )
        add_test_rows(additional_tests)
    if micro_tests:
        protocol_summary.append(
            {
                "row_type": "section_label",
                "sr_no": "",
                "name": "Microbiological parameters",
                "result": "",
                "limit": "",
            }
        )
        add_test_rows(micro_tests)

    logo_path = None
    for logo_name in ("logo.jpeg", "logo.png", "logo.jpg"):
        candidate = settings.static_dir / logo_name
        if candidate.exists():
            logo_path = candidate
            break

    context: dict[str, Any] = {
        "company_name": settings.company_name,
        "product_name": product_name,
        "product_code": config.get("product_code"),
        "reference": reference,
        "molecular_weight": config.get("molecular_weight"),
        "chemical_formula": config.get("chemical_formula"),
        "specification_no": config.get("specification_no"),
        "moa_no": config.get("moa_no") or document_no,
        "protocol_no": config.get("protocol_no") or document_no,
        "document_no": document_no,
        "document_no_label": doc_no_labels.get(document_type, "DOCUMENT NO."),
        "document_type": document_type.value,
        "document_type_label": doc_type_labels.get(document_type, document_type.value),
        "revision_no": revision_no,
        "subject": subject or product_name,
        "department": department,
        "effective_date": effective_date,
        "review_date": review_date,
        "superseded_revision": superseded_revision or "",
        "approval": approval or {},
        "prepared_by": (approval or {}).get("prepared_by", {}),
        "checked_by": (approval or {}).get("checked_by", {}),
        "approved_by": (approval or {}).get("approved_by", {}),
        "revision_history": revision_history or config.get("revision_history", []),
        "tests": tests,
        "additional_tests": additional_tests,
        "microbiological_tests": micro_tests,
        "all_tests": tests + additional_tests + micro_tests,
        "protocol_summary": protocol_summary,
        "sop_sections": sop_sections,
        "batch": batch or {},
        "logo_path": str(logo_path) if logo_path else None,
        "footer_text": "For Restricted Circulation Only",
        "metadata": config.get("metadata", {}),
    }

    if extra_context:
        context.update(extra_context)

    return _serialize_dates(context)


def product_config_from_json(data: str | dict) -> ProductConfig:
    if isinstance(data, str):
        return ProductConfig.model_validate(json.loads(data))
    return ProductConfig.model_validate(data)
