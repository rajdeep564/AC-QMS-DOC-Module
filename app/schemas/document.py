from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.product import ApprovalBlock, ProductConfig, RevisionHistoryEntry


class DocumentGenerateRequest(BaseModel):
    """Generate a document by looking up a pre-stored product by ID."""
    product_id: int
    batch_id: int | None = None
    document_no: str | None = None
    revision_no: str = "01"
    subject: str | None = None
    department: str = "QUALITY ASSURANCE"
    effective_date: date | None = None
    review_date: date | None = None
    superseded_revision: str | None = None
    approval: ApprovalBlock = Field(default_factory=ApprovalBlock)
    revision_history: list[RevisionHistoryEntry] = Field(default_factory=list)
    extra_context: dict[str, Any] = Field(default_factory=dict)


class InlineGenerateRequest(BaseModel):
    """Generate a document directly from product data — no DB lookup needed.

    Pass this from your main app to get a .docx back without pre-registering
    the product in this service's database.
    """
    document_type: Literal["moa", "protocol", "specification", "sop", "annexure"]
    product: ProductConfig
    document_no: str | None = None
    revision_no: str = "01"
    subject: str | None = None
    department: str = "QUALITY ASSURANCE"
    effective_date: date | None = None
    review_date: date | None = None
    superseded_revision: str | None = None
    approval: ApprovalBlock = Field(default_factory=ApprovalBlock)
    revision_history: list[RevisionHistoryEntry] = Field(default_factory=list)
    batch: dict[str, Any] = Field(default_factory=dict)
    extra_context: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    id: int
    product_id: int
    batch_id: int | None
    document_type: str
    document_no: str
    revision_no: str
    subject: str | None
    department: str
    effective_date: date | None
    review_date: date | None
    status: str
    docx_path: str | None
    pdf_path: str | None

    model_config = {"from_attributes": True}


class TestResultInput(BaseModel):
    test_name: str
    section_no: str | None = None
    result_value: str | float | None = None
    acceptance_criteria: dict[str, Any] | str | None = None
    remarks: str | None = None


class ValidationResponse(BaseModel):
    test_name: str
    section_no: str | None
    result_value: str | float | None
    status: str
    remarks: str | None = None
    acceptance_display: str | None = None
