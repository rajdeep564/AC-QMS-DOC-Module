"""Shared render-contract types for batch documents (COA, AWS)."""

from datetime import date

from pydantic import BaseModel, Field


class PersonSignature(BaseModel):
    name: str | None = None
    designation: str | None = None
    signature: str | None = None
    date: date | str | None = None


class DocumentApproval(BaseModel):
    """Three-stage approval block.

  COA semantics (values arrive pre-resolved from backend):
  - prepared_by: AWS document creator
  - checked_by: AWS QC approver
  - approved_by: issuing QA_MGR at COA sign-and-issue
    """

    prepared_by: PersonSignature = Field(default_factory=PersonSignature)
    checked_by: PersonSignature = Field(default_factory=PersonSignature)
    approved_by: PersonSignature = Field(default_factory=PersonSignature)


class ProductIdentity(BaseModel):
    product_name: str
    product_code: str | None = None
    reference: str | None = None
    specification_no: str | None = None
    moa_no: str | None = None


class BatchIdentity(BaseModel):
    batch_no: str
    arn_no: str | None = None
    mfg_date: str | None = None
    exp_date: str | None = None
    batch_size: str | None = None
    quantity_sampled: str | None = None
    test_request_no: str | None = None
    received_date: str | None = None
    testing_date: str | None = None
    completion_date: str | None = None
