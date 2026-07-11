"""Build layout context from CoaRenderInput — literal mapping only."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.core.config import get_settings
from app.core.constants import FOOTER_RESTRICTED_TEXT, DocumentType
from app.schemas.coa_render import CoaRenderInput


def _serialize_dates(obj: Any) -> Any:
    if isinstance(obj, date):
        return obj.strftime("%d %b %Y").upper()
    if isinstance(obj, dict):
        return {k: _serialize_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_dates(i) for i in obj]
    return obj


def _resolve_logo_path(payload: CoaRenderInput) -> str | None:
    if payload.logo_path:
        return payload.logo_path
    settings = get_settings()
    for logo_name in ("logo.jpeg", "logo.png", "logo.jpg"):
        candidate = settings.static_dir / logo_name
        if candidate.exists():
            return str(candidate)
    return None


def build_coa_context(payload: CoaRenderInput) -> dict[str, Any]:
    """Map CoaRenderInput to layout context dict — no derivation."""
    product = payload.product.model_dump()
    batch = payload.batch.model_dump()
    approval = payload.approval.model_dump()

    context: dict[str, Any] = {
        "company_name": payload.company_name,
        "document_no": payload.document_no,
        "document_no_label": payload.document_no_label,
        "document_type": DocumentType.COA.value,
        "document_type_label": payload.document_type_label,
        "revision_no": payload.revision_no,
        "effective_date": payload.effective_date,
        "review_date": payload.review_date,
        "product_name": product.get("product_name", ""),
        "product_code": product.get("product_code"),
        "reference": product.get("reference"),
        "specification_no": product.get("specification_no"),
        "moa_no": product.get("moa_no"),
        "product": product,
        "batch": batch,
        "coa_results": [row.model_dump() for row in payload.coa_results],
        "compliance_verdict": payload.compliance_verdict,
        "compliance_remark": payload.compliance_remark,
        "approval": approval,
        "prepared_by": approval.get("prepared_by", {}),
        "checked_by": approval.get("checked_by", {}),
        "approved_by": approval.get("approved_by", {}),
        "revision_history": [entry.model_dump() for entry in payload.revision_history],
        "logo_path": _resolve_logo_path(payload),
        "footer_text": FOOTER_RESTRICTED_TEXT,
    }

    return _serialize_dates(context)
