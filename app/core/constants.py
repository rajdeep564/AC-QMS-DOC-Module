from enum import StrEnum


class DocumentType(StrEnum):
    MOA = "MOA"
    PROTOCOL = "PROTOCOL"
    SOP = "SOP"
    ANNEXURE = "ANNEXURE"
    SPECIFICATION = "SPECIFICATION"
    STANDARD_FORMAT = "STANDARD_FORMAT"
    COA = "COA"
    AWS = "AWS"


class DocumentStatus(StrEnum):
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


class ValidationResult(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


# Document numbering prefixes (configurable per document type)
DOCUMENT_NUMBER_PREFIX = {
    DocumentType.MOA: "MOA/FG",
    DocumentType.PROTOCOL: "PROT/FG",
    DocumentType.SOP: "SOP",
    DocumentType.ANNEXURE: "ANNEXURE",
    DocumentType.SPECIFICATION: "SPEC/FG",
    DocumentType.STANDARD_FORMAT: "SF",
    DocumentType.COA: "COA",
    DocumentType.AWS: "AWS",
}

FOOTER_RESTRICTED_TEXT = "For Restricted Circulation Only"
