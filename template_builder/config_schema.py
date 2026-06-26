"""Pydantic models for programmatic template builder configuration."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class PageSetupConfig(BaseModel):
    paper_size: str = "A4"
    margin_top: float = 1.0
    margin_bottom: float = 1.0
    margin_left: float = 1.0
    margin_right: float = 1.0
    header_distance: float = 1.0
    footer_distance: float = 0.5


class HeaderConfig(BaseModel):
    show_logo: bool = True
    fields: list[str] = Field(
        default_factory=lambda: [
            "company_name",
            "document_type",
            "department",
            "document_no",
            "page_number",
            "effective_date",
            "review_date",
            "superseded_revision",
            "subject",
        ]
    )


class FooterConfig(BaseModel):
    show_approval_block: bool = True
    restricted_text: str = "For Restricted Circulation Only"


class StyleConfig(BaseModel):
    font_name: str = "Times New Roman"
    font_size: int = 12


class SectionBlock(BaseModel):
    type: Literal["heading", "paragraph", "jinja_loop", "table_placeholder"] = "paragraph"
    text: str | None = None
    loop_var: str | None = None
    template_lines: list[str] = Field(default_factory=list)


class TemplateBuilderConfig(BaseModel):
    document_type: str
    page_setup: PageSetupConfig = Field(default_factory=PageSetupConfig)
    header: HeaderConfig = Field(default_factory=HeaderConfig)
    footer: FooterConfig = Field(default_factory=FooterConfig)
    styles: StyleConfig = Field(default_factory=StyleConfig)
    sections: list[SectionBlock] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
