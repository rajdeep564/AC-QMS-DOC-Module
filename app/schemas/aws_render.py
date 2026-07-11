"""AWS render contract — render-ready payload (no derivation in renderer)."""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.product import RevisionHistoryEntry
from app.schemas.render_common import (
    BatchIdentity,
    DocumentApproval,
    PersonSignature,
    ProductIdentity,
)


class AwsSectionRender(BaseModel):
    sort_order: int
    section_no: str | None = None
    test_name: str
    limits_display: str
    procedure_text: str | None = None
    readings_display: str | None = None
    calculated_result: str | None = None
    result_display: str
    conclusion_display: str
    is_oos: bool = False
    oos_acknowledged: bool = False
    oos_ack_comment: str | None = None
    instrument_display: str | None = None
    reagent_display: str | None = None
    instrument_expired_ack: bool = False
    reagent_expired_ack: bool = False
    expiry_ack_comment: str | None = None
    analyst: PersonSignature = Field(default_factory=PersonSignature)
    checker: PersonSignature = Field(default_factory=PersonSignature)


class AwsRenderInput(BaseModel):
    document_no: str
    document_no_label: str = "AWS NO."
    document_type_label: str = "FINISHED PRODUCT ANALYSIS PROTOCOL"
    revision_no: str = "01"
    effective_date: date | str | None = None
    review_date: date | str | None = None
    superseded_revision: str | None = None
    company_name: str = "Aditya Chemicals"
    department: str = "QUALITY ASSURANCE"
    product: ProductIdentity
    batch: BatchIdentity
    sections: list[AwsSectionRender]
    summary_rows: list[dict] | None = None
    compliance_note: str | None = None
    approval: DocumentApproval
    revision_history: list[RevisionHistoryEntry] = Field(default_factory=list)
    logo_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
