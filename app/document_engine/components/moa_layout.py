"""Method of Analysis layout — matches MOA Glycine IP.docx."""

from docx import Document

from app.core.constants import DocumentType
from app.document_engine.components.qa_layout_common import (
    build_qa_approval_footer,
    build_revision_history_table,
    build_six_col_metadata_header,
    style_qa_cell,
    wire_repeating_header_footer,
)
from app.document_engine.styles import (
    MOA_DETAIL_GRID_COLS,
    MOA_FOOTER_GRID_COLS,
    MOA_FOOTER_TABLE_WIDTH_DXA,
    MOA_HEADER_GRID_COLS,
    MOA_HEADER_TABLE_INDENT_DXA,
    MOA_HEADER_TABLE_WIDTH_DXA,
    MOA_REVISION_GRID_COLS,
    MOA_REVISION_TABLE_INDENT_DXA,
    MOA_REVISION_TABLE_WIDTH_DXA,
    MOA_TABLE_WIDTH_DXA,
    clear_document_body,
    clear_row_height,
    configure_page_setup,
    finalize_protocol_table,
    merge_row_cells,
    set_cell_paragraphs,
    setup_protocol_table,
)


def build_moa_header(header, context: dict) -> None:
    mw = context.get("molecular_weight", "")
    if mw and "g/mole" not in str(mw):
        mw = f"{mw} g/mole"

    # Field order matches MOA Glycine IP.docx reference header exactly
    metadata_rows = [
        ("Name of Material", context.get("product_name", ""), "Ref. Specification No.", context.get("specification_no", "")),
        ("Chemical Formula", context.get("chemical_formula", ""), "MOA No.", context.get("moa_no", "")),
        ("Molecular Weight", mw, "Effective Date", str(context.get("effective_date", ""))),
        ("Reference", context.get("reference", ""), "Revision", context.get("revision_no", "01")),
        ("Supersedes", context.get("superseded_revision", ""), "Review Date", str(context.get("review_date", ""))),
    ]
    build_six_col_metadata_header(
        header,
        context,
        title="FINISHED PRODUCT METHOD OF ANALYSIS",
        grid_cols=MOA_HEADER_GRID_COLS,
        table_width_dxa=MOA_HEADER_TABLE_WIDTH_DXA,
        indent_dxa=MOA_HEADER_TABLE_INDENT_DXA,
        metadata_rows=metadata_rows,
        formula_value_rows={2},  # row 2: Chemical Formula value gets subscript rendering
    )


def build_moa_footer(footer, context: dict) -> None:
    build_qa_approval_footer(
        footer,
        context,
        grid_cols=MOA_FOOTER_GRID_COLS,
        table_width_dxa=MOA_FOOTER_TABLE_WIDTH_DXA,
        indent_dxa=MOA_HEADER_TABLE_INDENT_DXA,
    )


def _moa_procedure_lines(test: dict) -> list[str]:
    lines: list[str] = []
    procedure = (test.get("procedure") or "").strip()
    if procedure:
        lines.append("Procedure:")
        lines.extend(line for line in procedure.split("\n") if line.strip())
    limit = test.get("acceptance_criteria_display", "")
    if limit:
        lines.append(f"Acceptance Criteria: {limit}")
    return lines


def _count_moa_rows(tests: list[dict]) -> int:
    count = 0
    for test in tests:
        sub_tests = test.get("sub_tests") or []
        if sub_tests:
            count += 1 + len(sub_tests) * 2
        else:
            count += 2
    return count


def _build_moa_body_table(doc: Document, context: dict) -> None:
    tests = context.get("all_tests") or []
    if not tests:
        return

    table = doc.add_table(rows=_count_moa_rows(tests), cols=4)
    setup_protocol_table(table, MOA_DETAIL_GRID_COLS, width_dxa=MOA_TABLE_WIDTH_DXA, borders=True)

    row_idx = 0
    for test in tests:
        sub_tests = test.get("sub_tests") or []
        if sub_tests:
            parent_row = table.rows[row_idx]
            row_idx += 1
            style_qa_cell(parent_row.cells[0], test.get("section_no", ""))
            merge_row_cells(parent_row, 0, 1)
            style_qa_cell(parent_row.cells[2], f"{test.get('name', '')}:")
            merge_row_cells(parent_row, 2, 3)
            clear_row_height(parent_row)

            labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for i, sub in enumerate(sub_tests):
                label = f"{labels[i]})" if i < len(labels) else f"{i + 1})"
                row_idx = _write_moa_test_block(table, row_idx, sub, sub_label=label)
        else:
            row_idx = _write_moa_test_block(table, row_idx, test)

    finalize_protocol_table(table, MOA_DETAIL_GRID_COLS)


def _write_moa_test_block(table, row_idx: int, test: dict, sub_label: str | None = None) -> int:
    section_no = test.get("section_no", "") if not sub_label else ""
    name = test.get("name", "")
    title = f"{sub_label} {name}:" if sub_label else f"{name}:"

    title_row = table.rows[row_idx]
    row_idx += 1
    style_qa_cell(title_row.cells[0], section_no)
    merge_row_cells(title_row, 0, 1)
    style_qa_cell(title_row.cells[2], title)
    merge_row_cells(title_row, 2, 3)

    proc_row = table.rows[row_idx]
    row_idx += 1
    cell = proc_row.cells[0]
    set_cell_paragraphs(cell, _moa_procedure_lines(test), compact=True)
    merge_row_cells(proc_row, 0, 3)
    clear_row_height(title_row)
    clear_row_height(proc_row)
    return row_idx


def build_moa_body(doc: Document, context: dict) -> None:
    clear_document_body(doc)
    _build_moa_body_table(doc, context)
    build_revision_history_table(
        doc,
        context.get("revision_history") or [],
        grid_cols=MOA_REVISION_GRID_COLS,
        table_width_dxa=MOA_REVISION_TABLE_WIDTH_DXA,
        indent_dxa=MOA_REVISION_TABLE_INDENT_DXA,
    )


def apply_moa_layout(doc: Document, context: dict) -> None:
    doc.settings.odd_and_even_pages_header_footer = False
    for section in doc.sections:
        configure_page_setup(section, DocumentType.MOA)
        wire_repeating_header_footer(section, build_moa_header, build_moa_footer, context)
    build_moa_body(doc, context)
