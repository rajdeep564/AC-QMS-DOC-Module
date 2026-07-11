"""Parity tests: sop_style.yaml values must match legacy styles.py constants."""

from __future__ import annotations

import app.document_engine.styles as styles
from app.core.constants import DocumentType
from app.document_engine import sop_style
from app.document_engine.sop_style import _STYLE_PATH, load_sop_style

# Frozen legacy PAGE_SETUP (pre-B2) — parity anchor after dict removed from styles.py
EXPECTED_PAGE_SETUP = {
    DocumentType.PROTOCOL: {
        "top": 1.0,
        "right": 0.5,
        "bottom": 0.5,
        "left": 0.5,
        "header": 0.5,
        "footer": 0.33,
        "border": "double",
    },
    DocumentType.MOA: {
        "top": 0.5,
        "right": 0.5,
        "bottom": 0.5,
        "left": 0.5,
        "header": 0.5,
        "footer": 0.40,
        "border": "single",
    },
    DocumentType.SOP: {
        "top": 1.0,
        "right": 1.0,
        "bottom": 1.0,
        "left": 1.0,
        "header": 1.0,
        "footer": 0.5,
        "border": "double",
    },
    DocumentType.ANNEXURE: {
        "top": 1.0,
        "right": 1.0,
        "bottom": 1.0,
        "left": 1.0,
        "header": 1.0,
        "footer": 0.3,
        "border": "double",
    },
    DocumentType.SPECIFICATION: {
        "top": 0.5,
        "right": 0.5,
        "bottom": 0.5,
        "left": 0.5,
        "header": 0.5,
        "footer": 0.5,
        "border": None,
    },
    DocumentType.COA: {
        "top": 0.5,
        "right": 0.5,
        "bottom": 0.5,
        "left": 0.5,
        "header": 0.5,
        "footer": 0.5,
        "border": None,
    },
    DocumentType.AWS: {
        "top": 1.0,
        "right": 0.5,
        "bottom": 0.5,
        "left": 0.5,
        "header": 0.5,
        "footer": 0.33,
        "border": "double",
    },
}


def test_yaml_page_setup_matches_legacy():
    for doc_type, expected in EXPECTED_PAGE_SETUP.items():
        actual = sop_style.get_page_setup(doc_type)
        assert actual == expected, f"{doc_type.name}: {actual} != {expected}"


def test_yaml_protocol_table_constants():
    cfg = load_sop_style()
    p = cfg.tables.protocol
    t = cfg.tables
    assert styles.PROTOCOL_TABLE_WIDTH_DXA == p.table_width_dxa
    assert styles.BATCH_TABLE_WIDTH_DXA == p.batch_table_width_dxa
    assert styles.SUMMARY_TABLE_WIDTH_DXA == p.summary_table_width_dxa
    assert styles.SIGNOFF_TABLE_WIDTH_DXA == p.signoff_table_width_dxa
    assert styles.COLON_COL_WIDTH_DXA == t.colon_col_width_dxa
    assert styles.BATCH_GRID_COLS == p.batch_grid_cols
    assert styles.SUMMARY_GRID_COLS == p.summary_grid_cols
    assert styles.SIGNOFF_GRID_COLS == p.signoff_grid_cols
    assert styles.FOOTER_GRID_COLS == t.footer_grid_cols
    assert styles.FOOTER_TABLE_WIDTH_DXA == t.footer_table_width_dxa
    assert styles.FOOTER_TABLE_INDENT_DXA == t.footer_table_indent_dxa
    assert styles.DETAIL_GRID_COLS == p.detail_grid_cols
    assert styles.HEADER_GRID_COLS == p.header_grid_cols
    assert styles.HEADER_TABLE_WIDTH_DXA == p.header_table_width_dxa
    assert styles.PROTOCOL_REVISION_GRID_COLS == p.protocol_revision_grid_cols
    assert styles.PROTOCOL_REVISION_TABLE_WIDTH_DXA == p.protocol_revision_table_width_dxa
    assert styles.PROTOCOL_REVISION_TABLE_INDENT_DXA == p.protocol_revision_table_indent_dxa
    assert styles.HEADER_TABLE_INDENT_DXA == t.header_table_indent_dxa
    assert styles.SIGNOFF_TABLE_INDENT_DXA == t.signoff_table_indent_dxa


def test_yaml_moa_table_constants():
    cfg = load_sop_style().tables.moa
    assert styles.MOA_TABLE_WIDTH_DXA == cfg.table_width_dxa
    assert styles.MOA_DETAIL_GRID_COLS == cfg.detail_grid_cols
    assert styles.MOA_HEADER_TABLE_WIDTH_DXA == cfg.header_table_width_dxa
    assert styles.MOA_HEADER_TABLE_INDENT_DXA == cfg.header_table_indent_dxa
    assert styles.MOA_HEADER_GRID_COLS == cfg.header_grid_cols
    assert styles.MOA_FOOTER_TABLE_WIDTH_DXA == cfg.footer_table_width_dxa
    assert styles.MOA_FOOTER_GRID_COLS == cfg.footer_grid_cols
    assert styles.MOA_REVISION_GRID_COLS == cfg.revision_grid_cols
    assert styles.MOA_REVISION_TABLE_WIDTH_DXA == cfg.revision_table_width_dxa
    assert styles.MOA_REVISION_TABLE_INDENT_DXA == cfg.revision_table_indent_dxa


def test_yaml_specification_table_constants():
    cfg = load_sop_style().tables.specification
    assert styles.SPEC_TABLE_WIDTH_DXA == cfg.table_width_dxa
    assert styles.SPEC_HEADER_TABLE_WIDTH_DXA == cfg.header_table_width_dxa
    assert styles.SPEC_HEADER_TABLE_INDENT_DXA == cfg.header_table_indent_dxa
    assert styles.SPEC_HEADER_GRID_COLS == cfg.header_grid_cols
    assert styles.SPEC_FOOTER_TABLE_WIDTH_DXA == cfg.footer_table_width_dxa
    assert styles.SPEC_FOOTER_GRID_COLS == cfg.footer_grid_cols
    assert styles.SPEC_FOOTER_TABLE_INDENT_DXA == cfg.footer_table_indent_dxa
    assert styles.SPEC_PRODUCT_GRID_COLS == cfg.product_grid_cols
    assert styles.SPEC_PARAM_GRID_COLS == cfg.param_grid_cols
    assert styles.SPEC_MICRO_GRID_COLS == cfg.micro_grid_cols
    assert styles.SPEC_REVISION_GRID_COLS == cfg.revision_grid_cols
    assert styles.SPEC_REVISION_TABLE_WIDTH_DXA == cfg.revision_table_width_dxa
    assert styles.SPEC_REVISION_TABLE_INDENT_DXA == cfg.revision_table_indent_dxa


def test_yaml_coa_table_constants():
    cfg = load_sop_style().tables.coa
    assert styles.COA_HEADER_TABLE_WIDTH_DXA == cfg.header_table_width_dxa
    assert styles.COA_HEADER_TABLE_INDENT_DXA == cfg.header_table_indent_dxa
    assert styles.COA_HEADER_GRID_COLS == cfg.header_grid_cols
    assert styles.COA_FOOTER_TABLE_WIDTH_DXA == cfg.footer_table_width_dxa
    assert styles.COA_FOOTER_GRID_COLS == cfg.footer_grid_cols
    assert styles.COA_FOOTER_TABLE_INDENT_DXA == cfg.footer_table_indent_dxa
    assert styles.COA_RESULTS_TABLE_WIDTH_DXA == cfg.results_table_width_dxa
    assert styles.COA_RESULTS_GRID_COLS == cfg.results_grid_cols
    assert styles.COA_REVISION_GRID_COLS == cfg.revision_grid_cols
    assert styles.COA_REVISION_TABLE_WIDTH_DXA == cfg.revision_table_width_dxa
    assert styles.COA_REVISION_TABLE_INDENT_DXA == cfg.revision_table_indent_dxa


def test_yaml_aws_table_constants():
    cfg = load_sop_style().tables.aws
    p = load_sop_style().tables.protocol
    assert styles.AWS_TABLE_WIDTH_DXA == cfg.table_width_dxa
    assert styles.AWS_BATCH_TABLE_WIDTH_DXA == cfg.batch_table_width_dxa
    assert styles.AWS_SUMMARY_TABLE_WIDTH_DXA == cfg.summary_table_width_dxa
    assert styles.AWS_SIGNOFF_TABLE_WIDTH_DXA == cfg.signoff_table_width_dxa
    assert styles.AWS_BATCH_GRID_COLS == cfg.batch_grid_cols
    assert styles.AWS_SUMMARY_GRID_COLS == cfg.summary_grid_cols
    assert styles.AWS_SIGNOFF_GRID_COLS == cfg.signoff_grid_cols
    assert styles.AWS_DETAIL_GRID_COLS == cfg.detail_grid_cols
    assert styles.AWS_HEADER_GRID_COLS == cfg.header_grid_cols
    assert styles.AWS_HEADER_TABLE_WIDTH_DXA == cfg.header_table_width_dxa
    assert styles.AWS_HEADER_TABLE_INDENT_DXA == cfg.header_table_indent_dxa
    assert styles.AWS_FOOTER_TABLE_WIDTH_DXA == cfg.footer_table_width_dxa
    assert styles.AWS_FOOTER_GRID_COLS == cfg.footer_grid_cols
    assert styles.AWS_FOOTER_TABLE_INDENT_DXA == cfg.footer_table_indent_dxa
    assert styles.AWS_REVISION_GRID_COLS == cfg.aws_revision_grid_cols
    assert styles.AWS_REVISION_TABLE_WIDTH_DXA == cfg.aws_revision_table_width_dxa
    assert styles.AWS_REVISION_TABLE_INDENT_DXA == cfg.aws_revision_table_indent_dxa
    assert cfg.batch_grid_cols == p.batch_grid_cols
    assert cfg.summary_grid_cols == p.summary_grid_cols


def test_yaml_sop_table_constants_match_sop_layout():
    from app.document_engine.components import sop_layout

    cfg = load_sop_style().tables.sop
    assert sop_layout.SOP_HEADER_GRID_COLS == cfg.header_grid_cols
    assert sop_layout.SOP_HEADER_TABLE_WIDTH_DXA == cfg.header_table_width_dxa
    assert sop_layout.SOP_REVISION_GRID_COLS == cfg.revision_grid_cols
    assert sop_layout.SOP_REVISION_TABLE_WIDTH_DXA == cfg.revision_table_width_dxa


def test_yaml_spacing_logo_borders_page():
    cfg = load_sop_style()
    assert styles.PROTOCOL_SPACER_LINE_TWIPS == cfg.spacing.protocol_spacer_twips
    assert styles.PROTOCOL_SECTION_GAP_TWIPS == cfg.spacing.protocol_section_gap_twips
    assert styles.DETAIL_COMPACT_LINE_TWIPS == cfg.spacing.detail_compact_twips
    assert styles.DETAIL_CELL_MARGIN_TWIPS == cfg.spacing.detail_cell_margin_twips
    assert styles.HEADER_LOGO_ROW_HEIGHT_TWIPS == cfg.logo.row_height_twips
    assert cfg.page.font == "Times New Roman"
    assert cfg.page.font_size_pt == 12
    assert cfg.borders.cell_sz == "4"
    assert sop_style.get_page_border_spaces() == {
        "top": "2",
        "left": "20",
        "bottom": "1",
        "right": "20",
    }


def test_analytical_margins_are_half_inch():
    """§1.2 resolved: analytical profile remains 0.5\" — not 1.0\"."""
    profile = load_sop_style().margin_profiles["analytical"]
    assert profile.top == 0.5
    assert profile.right == 0.5
    assert profile.bottom == 0.5
    assert profile.left == 0.5
    assert sop_style.get_page_setup(DocumentType.MOA)["top"] == 0.5


def test_analytical_margin_flip_is_data_only(tmp_path, monkeypatch, request):
    """Changing margin_profiles.analytical in YAML flips MOA margins without code change."""
    from app.document_engine import sop_style as ss
    from app.document_engine.sop_style import clear_sop_style_cache

    flipped = _STYLE_PATH.read_text(encoding="utf-8").replace(
        "  analytical:\n    top: 0.5",
        "  analytical:\n    top: 1.0",
        1,
    )
    test_yaml = tmp_path / "sop_style_test.yaml"
    test_yaml.write_text(flipped, encoding="utf-8")
    assert ss.get_page_setup(DocumentType.MOA)["top"] == 0.5
    monkeypatch.setattr(ss, "_STYLE_PATH", test_yaml)
    request.addfinalizer(clear_sop_style_cache)
    clear_sop_style_cache()
    assert ss.load_sop_style().margin_profiles["analytical"].top == 1.0
    assert ss.get_page_setup(DocumentType.MOA)["top"] == 1.0
