"""COA render contract — render-ready payload (no derivation in renderer)."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.product import RevisionHistoryEntry
from app.schemas.render_common import BatchIdentity, DocumentApproval, ProductIdentity


class CoaResultRow(BaseModel):
    sort_order: int
    test_name: str
    result: str
    acceptance_limits: str | None = None
    conclusion: str | None = None


class CoaRenderInput(BaseModel):
    document_no: str
    document_no_label: str = "COA NO."
    document_type_label: str = "ANALYTICAL REPORT"
    revision_no: str = "01"
    effective_date: date | str | None = None
    review_date: date | str | None = None
    company_name: str = "Aditya Chemicals"
    product: ProductIdentity
    batch: BatchIdentity
    coa_results: list[CoaResultRow]
    compliance_verdict: Literal["COMPLIES", "DOES_NOT_COMPLY"]
    compliance_remark: str
    approval: DocumentApproval = Field(default_factory=DocumentApproval)
    revision_history: list[RevisionHistoryEntry] = Field(default_factory=list)
    logo_path: str | None = None
