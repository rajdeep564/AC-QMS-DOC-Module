"""Build layout context from AwsRenderInput — literal mapping only."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.core.config import get_settings
from app.core.constants import FOOTER_RESTRICTED_TEXT, DocumentType
from app.schemas.aws_render import AwsRenderInput


def _serialize_dates(obj: Any) -> Any:
    if isinstance(obj, date):
        return obj.strftime("%d %b %Y").upper()
    if isinstance(obj, dict):
        return {k: _serialize_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_dates(i) for i in obj]
    return obj


def _resolve_logo_path(payload: AwsRenderInput) -> str | None:
    if payload.logo_path:
        return payload.logo_path
    settings = get_settings()
    for logo_name in ("logo.jpeg", "logo.png", "logo.jpg"):
        candidate = settings.static_dir / logo_name
        if candidate.exists():
            return str(candidate)
    return None


def build_aws_context(payload: AwsRenderInput) -> dict[str, Any]:
    """Map AwsRenderInput to layout context dict — no derivation."""
    product = payload.product.model_dump()
    batch = payload.batch.model_dump()
    if batch.get("arn_no") and not batch.get("ar_no"):
        batch["ar_no"] = batch["arn_no"]
    approval = payload.approval.model_dump()

    context: dict[str, Any] = {
        "company_name": payload.company_name,
        "department": payload.department,
        "document_no": payload.document_no,
        "document_no_label": payload.document_no_label,
        "document_type": DocumentType.AWS.value,
        "document_type_label": payload.document_type_label,
        "revision_no": payload.revision_no,
        "effective_date": payload.effective_date,
        "review_date": payload.review_date,
        "superseded_revision": payload.superseded_revision,
        "product_name": product.get("product_name", ""),
        "product_code": product.get("product_code"),
        "reference": product.get("reference"),
        "specification_no": product.get("specification_no"),
        "moa_no": product.get("moa_no"),
        "product": product,
        "batch": batch,
        "sections": [section.model_dump() for section in payload.sections],
        "summary_rows": payload.summary_rows,
        "compliance_note": payload.compliance_note,
        "approval": approval,
        "prepared_by": approval.get("prepared_by", {}),
        "checked_by": approval.get("checked_by", {}),
        "approved_by": approval.get("approved_by", {}),
        "revision_history": [entry.model_dump() for entry in payload.revision_history],
        "logo_path": _resolve_logo_path(payload),
        "footer_text": FOOTER_RESTRICTED_TEXT,
        "metadata": payload.metadata,
    }

    return _serialize_dates(context)
