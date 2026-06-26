from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


class AcceptanceCriteria(BaseModel):
    type: Literal["range", "max", "min", "equals", "text", "nmt", "nlt", "between"]
    min: float | None = None
    max: float | None = None
    value: str | float | None = None
    unit: str | None = None
    display: str | None = None

    def to_display_string(self) -> str:
        if self.display:
            return self.display
        if self.type == "range" and self.min is not None and self.max is not None:
            unit = f" {self.unit}" if self.unit else ""
            return f"{self.min} to {self.max}{unit}"
        if self.type in ("max", "nmt") and self.value is not None:
            unit = f" {self.unit}" if self.unit else ""
            return f"NMT {self.value}{unit}"
        if self.type in ("min", "nlt") and self.value is not None:
            unit = f" {self.unit}" if self.unit else ""
            return f"NLT {self.value}{unit}"
        if self.type == "equals" and self.value is not None:
            return str(self.value)
        if self.type == "text" and self.value is not None:
            return str(self.value)
        return ""


class SubTestConfig(BaseModel):
    name: str
    procedure: str | None = None
    acceptance_criteria: AcceptanceCriteria | str | None = None
    instruments: list[str] = Field(default_factory=list)
    reagents: list[str] = Field(default_factory=list)
    tables: list["DynamicTableConfig"] = Field(default_factory=list)
    sub_tests: list["SubTestConfig"] = Field(default_factory=list)


class TestConfig(BaseModel):
    name: str
    procedure: str | None = None
    acceptance_criteria: AcceptanceCriteria | str | None = None
    instruments: list[str] = Field(default_factory=list)
    reagents: list[str] = Field(default_factory=list)
    tables: list["DynamicTableConfig"] = Field(default_factory=list)
    sub_tests: list[SubTestConfig] = Field(default_factory=list)
    section_no: str | None = None


class DynamicTableConfig(BaseModel):
    table_name: str | None = None
    columns: list[str]
    rows: list[list[Any]]
    merges: list[dict[str, int]] = Field(default_factory=list)


class RevisionHistoryEntry(BaseModel):
    document_no: str
    revision_made: str
    change_control_no: str | None = None
    effective_date: date | str


class ApprovalPerson(BaseModel):
    name: str | None = None
    designation: str | None = None
    signature: str | None = None
    date: date | str | None = None


class ApprovalBlock(BaseModel):
    prepared_by: ApprovalPerson = Field(default_factory=ApprovalPerson)
    checked_by: ApprovalPerson = Field(default_factory=ApprovalPerson)
    approved_by: ApprovalPerson = Field(default_factory=ApprovalPerson)


class SopSection(BaseModel):
    title: str
    content: str | list[str] | None = None
    subsections: list["SopSection"] = Field(default_factory=list)
    section_no: str | None = None


class ProductConfig(BaseModel):
    product_code: str
    product_name: str
    reference: str | None = None
    molecular_weight: str | None = None
    chemical_formula: str | None = None
    specification_no: str | None = None
    moa_no: str | None = None
    protocol_no: str | None = None
    department: str = "QUALITY ASSURANCE"
    tests: list[TestConfig] = Field(default_factory=list)
    additional_tests: list[TestConfig] = Field(default_factory=list)
    microbiological_tests: list[TestConfig] = Field(default_factory=list)
    sop_sections: list[SopSection] = Field(default_factory=list)
    revision_history: list[RevisionHistoryEntry] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductCreate(BaseModel):
    product_code: str
    product_name: str
    reference: str | None = None
    molecular_weight: str | None = None
    chemical_formula: str | None = None
    specification_no: str | None = None
    moa_no: str | None = None
    protocol_no: str | None = None
    department: str = "QUALITY ASSURANCE"
    tests: list[TestConfig] = Field(default_factory=list)
    additional_tests: list[TestConfig] = Field(default_factory=list)
    microbiological_tests: list[TestConfig] = Field(default_factory=list)
    sop_sections: list[SopSection] = Field(default_factory=list)
    revision_history: list[RevisionHistoryEntry] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductResponse(BaseModel):
    id: int
    product_code: str
    product_name: str
    reference: str | None
    molecular_weight: str | None
    chemical_formula: str | None

    model_config = {"from_attributes": True}


SubTestConfig.model_rebuild()
TestConfig.model_rebuild()
SopSection.model_rebuild()
