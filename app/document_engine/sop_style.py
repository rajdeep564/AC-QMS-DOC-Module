"""Load and validate document styling from sop_style.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

from app.core.constants import DocumentType

_STYLE_PATH = Path(__file__).resolve().parent / "sop_style.yaml"


class MarginProfile(BaseModel):
    top: float
    right: float
    bottom: float
    left: float
    header: float
    footer: float


class DocumentTypeStyle(BaseModel):
    margin_profile: str
    page_border: str | None = None
    footer: float | None = None
    header_layout: Literal["two_column", "six_column"] = "two_column"
    margin_overrides: dict[str, float] = Field(default_factory=dict)


class PageStyle(BaseModel):
    width_inches: float = 8.27
    height_inches: float = 11.69
    font: str = "Times New Roman"
    font_size_pt: int = 12


class PageNumberStyle(BaseModel):
    format: Literal["n_of_total", "page_n_of_total"] = "n_of_total"


class LogoStyle(BaseModel):
    width_inches: float = 1.33
    row_height_twips: int = 943


class SpacingStyle(BaseModel):
    protocol_spacer_twips: int = 360
    protocol_section_gap_twips: int = 120
    detail_compact_twips: int = 240
    detail_cell_margin_twips: int = 40
    detail_cell_margin_lr_dxa: int = 108


class PageBorderSpaces(BaseModel):
    top: int = 2
    left: int = 20
    bottom: int = 1
    right: int = 20


class BordersStyle(BaseModel):
    cell_val: str = "single"
    cell_sz: str = "4"
    page_sz: str = "4"
    page_border_spaces: PageBorderSpaces = Field(default_factory=PageBorderSpaces)


class ProtocolTables(BaseModel):
    table_width_dxa: int
    batch_table_width_dxa: int
    summary_table_width_dxa: int
    signoff_table_width_dxa: int
    batch_grid_cols: list[int]
    summary_grid_cols: list[int]
    signoff_grid_cols: list[int]
    detail_grid_cols: list[int]
    header_grid_cols: list[int]
    header_table_width_dxa: int
    protocol_revision_grid_cols: list[int]
    protocol_revision_table_width_dxa: int
    protocol_revision_table_indent_dxa: int = 0


class MoaTables(BaseModel):
    table_width_dxa: int
    detail_grid_cols: list[int]
    header_table_width_dxa: int
    header_table_indent_dxa: int
    header_grid_cols: list[int]
    footer_table_width_dxa: int
    footer_grid_cols: list[int]
    revision_grid_cols: list[int]
    revision_table_width_dxa: int
    revision_table_indent_dxa: int = 0


class SpecificationTables(BaseModel):
    table_width_dxa: int
    header_table_width_dxa: int
    header_table_indent_dxa: int
    header_grid_cols: list[int]
    footer_table_width_dxa: int
    footer_grid_cols: list[int]
    footer_table_indent_dxa: int = 0
    product_grid_cols: list[int]
    param_grid_cols: list[int]
    micro_grid_cols: list[int]
    revision_grid_cols: list[int]
    revision_table_width_dxa: int
    revision_table_indent_dxa: int = 0


class SopTables(BaseModel):
    header_grid_cols: list[int]
    header_table_width_dxa: int
    revision_grid_cols: list[int]
    revision_table_width_dxa: int


class CoaTables(BaseModel):
    header_table_width_dxa: int
    header_table_indent_dxa: int = 0
    header_grid_cols: list[int]
    footer_table_width_dxa: int
    footer_grid_cols: list[int]
    footer_table_indent_dxa: int = 0
    results_table_width_dxa: int
    results_grid_cols: list[int]
    revision_grid_cols: list[int]
    revision_table_width_dxa: int
    revision_table_indent_dxa: int = 0


class AwsTables(BaseModel):
    table_width_dxa: int
    batch_table_width_dxa: int
    summary_table_width_dxa: int
    signoff_table_width_dxa: int
    batch_grid_cols: list[int]
    summary_grid_cols: list[int]
    signoff_grid_cols: list[int]
    detail_grid_cols: list[int]
    header_grid_cols: list[int]
    header_table_width_dxa: int
    header_table_indent_dxa: int = 0
    footer_table_width_dxa: int
    footer_grid_cols: list[int]
    footer_table_indent_dxa: int = 0
    aws_revision_grid_cols: list[int]
    aws_revision_table_width_dxa: int
    aws_revision_table_indent_dxa: int = 0


class SharedTables(BaseModel):
    shared_table_width_dxa: int = 10400
    colon_col_width_dxa: int = 279
    footer_grid_cols: list[int]
    footer_table_width_dxa: int = 10400
    footer_table_indent_dxa: int = 0
    header_table_indent_dxa: int = 0
    signoff_table_indent_dxa: int = 0


class TablesStyle(BaseModel):
    shared_table_width_dxa: int = 10400
    colon_col_width_dxa: int = 279
    footer_grid_cols: list[int]
    footer_table_width_dxa: int = 10400
    footer_table_indent_dxa: int = 0
    header_table_indent_dxa: int = 0
    signoff_table_indent_dxa: int = 0
    protocol: ProtocolTables
    moa: MoaTables
    specification: SpecificationTables
    sop: SopTables
    coa: CoaTables
    aws: AwsTables


class SopStyleConfig(BaseModel):
    version: str = "1"
    page: PageStyle = Field(default_factory=PageStyle)
    margin_profiles: dict[str, MarginProfile]
    document_types: dict[str, DocumentTypeStyle]
    page_number: PageNumberStyle = Field(default_factory=PageNumberStyle)
    logo: LogoStyle = Field(default_factory=LogoStyle)
    document_labels: dict[str, str]
    document_type_labels: dict[str, str]
    spacing: SpacingStyle = Field(default_factory=SpacingStyle)
    borders: BordersStyle = Field(default_factory=BordersStyle)
    tables: TablesStyle


def clear_sop_style_cache() -> None:
    load_sop_style.cache_clear()


def _load_yaml(path: Path | None = None) -> dict[str, Any]:
    yaml_path = path or _STYLE_PATH
    with yaml_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def load_sop_style(yaml_path: str | None = None) -> SopStyleConfig:
    path = Path(yaml_path) if yaml_path else _STYLE_PATH
    return SopStyleConfig.model_validate(_load_yaml(path))


def get_page_setup(document_type: DocumentType) -> dict[str, Any]:
    """Resolved page margins + border for a document type (matches legacy PAGE_SETUP shape)."""
    style = load_sop_style()
    key = document_type.name
    if key not in style.document_types:
        key = DocumentType.SOP.name
    cfg = style.document_types[key]
    profile = style.margin_profiles[cfg.margin_profile]
    margins = {
        "top": profile.top,
        "right": profile.right,
        "bottom": profile.bottom,
        "left": profile.left,
        "header": profile.header,
        "footer": cfg.footer if cfg.footer is not None else profile.footer,
    }
    for field, value in cfg.margin_overrides.items():
        if field in margins:
            margins[field] = value
    return {**margins, "border": cfg.page_border}


def get_document_label(document_type: DocumentType) -> str:
    style = load_sop_style()
    return style.document_labels.get(document_type.name, "DOCUMENT NO.")


def get_document_type_label(document_type: DocumentType) -> str:
    style = load_sop_style()
    return style.document_type_labels.get(document_type.name, document_type.value)


def get_page_border_spaces() -> dict[str, str]:
    spaces = load_sop_style().borders.page_border_spaces
    return {
        "top": str(spaces.top),
        "left": str(spaces.left),
        "bottom": str(spaces.bottom),
        "right": str(spaces.right),
    }
