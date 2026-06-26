"""Document styling: margins, page borders, table borders, fonts."""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from app.core.config import get_settings
from app.core.constants import DocumentType

# Protocol table widths (dxa twips) — scaled to fit A4 content area (10468 dxa)
# A4 page (8.27") with 0.5" L+R margins: content = 11908 - 720 - 720 = 10468 dxa
# Target 10400 gives ~68 dxa safety margin on each side
PROTOCOL_TABLE_WIDTH_DXA = 10400
BATCH_TABLE_WIDTH_DXA = 10400
SUMMARY_TABLE_WIDTH_DXA = 10400
SIGNOFF_TABLE_WIDTH_DXA = 10400

# Colon separator column — matches reference batch table colon column (296 dxa)
COLON_COL_WIDTH_DXA = 279

# Column grids scaled proportionally from reference to fit 10400 dxa
BATCH_GRID_COLS = [2447, 279, 2851, 2027, 279, 2517]
# Sr | Tests | (divider 6 dxa) | Results | Limits — 5 cols
SUMMARY_GRID_COLS = [937, 2469, 6, 2641, 4347]
SIGNOFF_GRID_COLS = [2544, 2286, 2905, 2665]
# Footer sign-off row: 6 equal columns (SIGN | DATE × 3)
FOOTER_GRID_COLS = [1734, 1733, 1733, 1733, 1733, 1734]
FOOTER_TABLE_WIDTH_DXA = 10400
FOOTER_TABLE_INDENT_DXA = 0
DETAIL_GRID_COLS = [599, 32, 9769]

# All tables share a single target width (10400 dxa) and zero indent so every
# table — header, body, footer — starts at the same left edge and ends at the
# same right edge.  A4 content = 11908 - 720 - 720 = 10468 dxa; 10400 leaves
# a ~34 dxa safety buffer on each side.
_TW = 10400  # shared table width for all docs

# MOA — column grids scaled proportionally from reference to _TW
MOA_TABLE_WIDTH_DXA = _TW
MOA_DETAIL_GRID_COLS = [694, 162, 54, 9490]          # ref [709,166,55,9702] sum=10632
MOA_HEADER_TABLE_WIDTH_DXA = _TW
MOA_HEADER_TABLE_INDENT_DXA = 0
MOA_HEADER_GRID_COLS = [2185, 262, 3146, 2401, 229, 2177]  # ref sum=10710
MOA_FOOTER_TABLE_WIDTH_DXA = _TW
MOA_FOOTER_GRID_COLS = [1734, 1733, 1733, 1733, 1733, 1734]  # ref sum=10710
MOA_REVISION_GRID_COLS = [2949, 3986, 1629, 1836]    # ref sum=10710
MOA_REVISION_TABLE_WIDTH_DXA = _TW
MOA_REVISION_TABLE_INDENT_DXA = 0

# SPECIFICATION — exact reference dimensions (tables wider than content, jc=center)
SPEC_TABLE_WIDTH_DXA = 11155          # reference body table width (centered, wider than A4 content)
SPEC_HEADER_TABLE_WIDTH_DXA = 11160  # reference header table width
SPEC_HEADER_TABLE_INDENT_DXA = -365  # reference negative indent (extends left into margin)
SPEC_HEADER_GRID_COLS = [2250, 293, 3487, 2036, 304, 2790]  # reference exact col widths
SPEC_FOOTER_TABLE_WIDTH_DXA = _TW
SPEC_FOOTER_GRID_COLS = [1734, 1733, 1733, 1733, 1733, 1734]
SPEC_FOOTER_TABLE_INDENT_DXA = 0
SPEC_PRODUCT_GRID_COLS = [2263, 1701, 1985, 5206]   # reference table 1 exact
SPEC_PARAM_GRID_COLS = [2263, 2152, 1534, 5206]     # reference table 2 exact
SPEC_MICRO_GRID_COLS = [2263, 3686, 5206]           # reference table 3 exact
SPEC_REVISION_GRID_COLS = [2813, 3487, 2430, 2430]  # reference revision history exact
SPEC_REVISION_TABLE_WIDTH_DXA = 11160
SPEC_REVISION_TABLE_INDENT_DXA = 0

# Protocol revision history
PROTOCOL_REVISION_GRID_COLS = [2546, 3882, 2008, 1964]  # ref sum=11057, scaled to _TW
PROTOCOL_REVISION_TABLE_WIDTH_DXA = _TW
PROTOCOL_REVISION_TABLE_INDENT_DXA = 0

# Protocol header grid (kept for SOP/Annexure) — scaled to _TW
HEADER_GRID_COLS = [2278, 279, 2640, 1864, 279, 3060]
HEADER_TABLE_WIDTH_DXA = _TW

# Spacing between body tables (twips) — reference uses line=360 (18pt)
PROTOCOL_SPACER_LINE_TWIPS = 360
PROTOCOL_SECTION_GAP_TWIPS = 120
# Tight line spacing inside procedure/detail cells — height follows content only
DETAIL_COMPACT_LINE_TWIPS = 240
DETAIL_CELL_MARGIN_TWIPS = 40

HEADER_TABLE_INDENT_DXA = 0
SIGNOFF_TABLE_INDENT_DXA = 0
HEADER_LOGO_ROW_HEIGHT_TWIPS = 943  # logo.jpeg at 1.33" wide = 0.655" tall = 943 twips


def style_run(run, *, bold: bool = False, size: int | None = None, font: str | None = None) -> None:
    settings = get_settings()
    run.bold = bold
    run.font.name = font or settings.default_font
    run.font.size = Pt(size or settings.default_font_size)


def set_cell_text(
    cell,
    text: str,
    *,
    bold: bool = False,
    align: WD_ALIGN_PARAGRAPH | None = None,
    line_twips: int | None = None,
) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    if line_twips is not None:
        set_paragraph_spacing_twips(p, line=line_twips)
    if text:
        run = p.add_run(text)
        style_run(run, bold=bold)


def set_cell_paragraphs(
    cell,
    lines: list[str],
    *,
    bold_first: bool = False,
    compact: bool = False,
) -> None:
    """Multiple paragraphs inside one cell. Use compact=True for tight, content-sized rows."""
    cell.text = ""
    para_idx = 0
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        p = cell.paragraphs[0] if para_idx == 0 else cell.add_paragraph()
        para_idx += 1
        if compact:
            set_paragraph_spacing_twips(
                p, before=0, after=0, line=DETAIL_COMPACT_LINE_TWIPS
            )
        run = p.add_run(line)
        style_run(run, bold=(bold_first and i == 0))


def set_cell_margins_dxa(
    cell,
    *,
    top: int = DETAIL_CELL_MARGIN_TWIPS,
    bottom: int = DETAIL_CELL_MARGIN_TWIPS,
    left: int = 108,
    right: int = 108,
) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    existing = tc_pr.find(qn("w:tcMar"))
    if existing is not None:
        tc_pr.remove(existing)
    tc_mar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        tc_mar.append(el)
    tc_pr.append(tc_mar)


def clear_row_height(row) -> None:
    """Let Word size the row to fit cell content."""
    tr_pr = row._tr.get_or_add_trPr()
    existing = tr_pr.find(qn("w:trHeight"))
    if existing is not None:
        tr_pr.remove(existing)


def _border_element(side: str, val: str = "single", sz: str = "4", space: str = "0", color: str = "auto"):
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:val"), val)
    el.set(qn("w:sz"), sz)
    el.set(qn("w:space"), space)
    el.set(qn("w:color"), color)
    return el


def apply_cell_borders(cell, val: str = "single", sz: str = "4") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    existing = tc_pr.find(qn("w:tcBorders"))
    if existing is not None:
        tc_pr.remove(existing)
    tc_borders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        tc_borders.append(_border_element(side, val, sz))
    tc_pr.append(tc_borders)


def apply_table_grid_borders(table, val: str = "single", sz: str = "4") -> None:
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    if tbl_pr is None:
        tbl_pr = OxmlElement("w:tblPr")
        tbl.insert(0, tbl_pr)
    tbl_borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tbl_borders.append(_border_element(side, val, sz))
    existing = tbl_pr.find(qn("w:tblBorders"))
    if existing is not None:
        tbl_pr.remove(existing)
    tbl_pr.append(tbl_borders)


def set_page_border(section, *, val: str = "double", sz: str = "4") -> None:
    sect_pr = section._sectPr
    existing = sect_pr.find(qn("w:pgBorders"))
    if existing is not None:
        sect_pr.remove(existing)

    pg_borders = OxmlElement("w:pgBorders")
    # Default offsetFrom=text — borders sit inside margins (matches GLYCINE IP.docx).
    spaces = {"top": "2", "left": "20", "bottom": "1", "right": "20"}
    for border_name in ("top", "left", "bottom", "right"):
        border = OxmlElement(f"w:{border_name}")
        border.set(qn("w:val"), val)
        border.set(qn("w:sz"), sz)
        border.set(qn("w:space"), spaces.get(border_name, "2"))
        border.set(qn("w:color"), "auto")
        pg_borders.append(border)
    sect_pr.append(pg_borders)


def _set_margins(section, margins: dict[str, float]) -> None:
    section.page_height = Inches(11.69)
    section.page_width = Inches(8.27)
    section.top_margin = Inches(margins["top"])
    section.bottom_margin = Inches(margins["bottom"])
    section.left_margin = Inches(margins["left"])
    section.right_margin = Inches(margins["right"])
    section.header_distance = Inches(margins["header"])
    section.footer_distance = Inches(margins["footer"])


PAGE_SETUP = {
    DocumentType.PROTOCOL: {
        "top": 1.0,   # 1440 dxa — matches GLYCINE IP.docx
        "right": 0.5,
        "bottom": 0.5,
        "left": 0.5,
        "header": 0.5,
        "footer": 0.33,
        "border": "double",
    },
    DocumentType.MOA: {
        "top": 0.5,   # 720 dxa — matches MOA Glycine IP.docx
        "right": 0.5,
        "bottom": 0.5,
        "left": 0.5,
        "header": 0.5,
        "footer": 0.40,
        "border": "single",  # MOA uses single border, not double
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
        "top": 0.5,   # 720 dxa — matches Spec Glycine IP.docx
        "right": 0.5,
        "bottom": 0.5,
        "left": 0.5,
        "header": 0.5,
        "footer": 0.5,
        "border": None,  # Spec has NO page border
    },
}


def configure_page_setup(section, document_type: DocumentType) -> None:
    setup = PAGE_SETUP.get(document_type, PAGE_SETUP[DocumentType.SOP])
    _set_margins(section, setup)
    border = setup.get("border")
    if border is not None:
        set_page_border(section, val=border)


def clear_document_body(doc) -> None:
    body = doc.element.body
    sect_pr = body.find(qn("w:sectPr"))
    for child in list(body):
        if child is sect_pr:
            continue
        body.remove(child)


def _get_or_create_tbl_pr(table):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    if tbl_pr is None:
        tbl_pr = OxmlElement("w:tblPr")
        tbl.insert(0, tbl_pr)
    return tbl_pr


def table_fixed_width_dxa(table, width_dxa: int | None = PROTOCOL_TABLE_WIDTH_DXA) -> None:
    if width_dxa is None:
        return
    tbl_pr = _get_or_create_tbl_pr(table)
    tbl_w = OxmlElement("w:tblW")
    tbl_w.set(qn("w:w"), str(width_dxa))
    tbl_w.set(qn("w:type"), "dxa")
    existing = tbl_pr.find(qn("w:tblW"))
    if existing is not None:
        tbl_pr.remove(existing)
    tbl_pr.append(tbl_w)


def set_cell_no_wrap(cell) -> None:
    """Prevent Word from wrapping header text character-by-character in narrow cells."""
    tc_pr = cell._tc.get_or_add_tcPr()
    if tc_pr.find(qn("w:noWrap")) is None:
        tc_pr.append(OxmlElement("w:noWrap"))


def set_cell_width_dxa(cell, width_dxa: int) -> None:
    """Set explicit cell width — Word ignores tblGrid without tcW on each cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    existing = tc_pr.find(qn("w:tcW"))
    if existing is not None:
        tc_pr.remove(existing)
    tc_w = OxmlElement("w:tcW")
    tc_w.set(qn("w:w"), str(width_dxa))
    tc_w.set(qn("w:type"), "dxa")
    tc_pr.append(tc_w)


def _cell_grid_span(cell) -> int:
    tc_pr = cell._tc.tcPr
    if tc_pr is None:
        return 1
    gs = tc_pr.find(qn("w:gridSpan"))
    if gs is None:
        return 1
    return int(gs.get(qn("w:val")))


def set_table_layout_fixed(table) -> None:
    tbl_pr = _get_or_create_tbl_pr(table)
    existing = tbl_pr.find(qn("w:tblLayout"))
    if existing is not None:
        tbl_pr.remove(existing)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)


def apply_table_column_widths(table, col_widths: list[int]) -> None:
    """Apply tcW on every cell from gridCol widths (respects gridSpan merges).

    Uses row._tr.tc_lst instead of row.cells — python-docx exposes duplicate
  ghost cells after horizontal merge, which would misalign column indices.
    """
    from docx.table import _Cell

    for row in table.rows:
        col_idx = 0
        for tc in row._tr.tc_lst:
            cell = _Cell(tc, row)
            span = _cell_grid_span(cell)
            width = sum(col_widths[col_idx : col_idx + span])
            set_cell_width_dxa(cell, width)
            col_idx += span


def finalize_protocol_table(table, col_widths: list[int]) -> None:
    """Lock column widths after all merges — call once table content is complete."""
    set_table_layout_fixed(table)
    apply_table_column_widths(table, col_widths)


def set_table_grid_columns(table, col_widths: list[int]) -> None:
    tbl = table._tbl
    existing_grid = tbl.find(qn("w:tblGrid"))
    if existing_grid is not None:
        tbl.remove(existing_grid)
    grid = OxmlElement("w:tblGrid")
    for width in col_widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    tbl_pr = _get_or_create_tbl_pr(table)
    tbl.insert(tbl.index(tbl_pr) + 1, grid)


def set_grid_span(cell, span: int) -> None:
    if span <= 1:
        return
    tc_pr = cell._tc.get_or_add_tcPr()
    grid_span = OxmlElement("w:gridSpan")
    grid_span.set(qn("w:val"), str(span))
    existing = tc_pr.find(qn("w:gridSpan"))
    if existing is not None:
        tc_pr.remove(existing)
    tc_pr.append(grid_span)


def merge_row_cells(row, start: int, end: int) -> None:
    row.cells[start].merge(row.cells[end])


def set_table_style_grid(table) -> None:
    """Apply Word 'Table Grid' style — visible borders on all cells (matches reference header)."""
    try:
        table.style = "Table Grid"
    except KeyError:
        apply_table_grid_borders(table)


def set_table_jc(table, jc: str = "center") -> None:
    """Set table horizontal alignment (jc). Use 'center' for spec body tables."""
    tbl_pr = _get_or_create_tbl_pr(table)
    existing = tbl_pr.find(qn("w:jc"))
    if existing is not None:
        tbl_pr.remove(existing)
    el = OxmlElement("w:jc")
    el.set(qn("w:val"), jc)
    tbl_pr.append(el)


def set_table_indent(table, indent_dxa: int) -> None:
    tbl_pr = _get_or_create_tbl_pr(table)
    existing = tbl_pr.find(qn("w:tblInd"))
    if existing is not None:
        tbl_pr.remove(existing)
    tbl_ind = OxmlElement("w:tblInd")
    tbl_ind.set(qn("w:w"), str(indent_dxa))
    tbl_ind.set(qn("w:type"), "dxa")
    tbl_pr.append(tbl_ind)


def set_row_height(row, height_twips: int) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    existing = tr_pr.find(qn("w:trHeight"))
    if existing is not None:
        tr_pr.remove(existing)
    tr_height = OxmlElement("w:trHeight")
    tr_height.set(qn("w:val"), str(height_twips))
    tr_pr.append(tr_height)


def set_cell_valign(cell, align: str = "center") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    existing = tc_pr.find(qn("w:vAlign"))
    if existing is not None:
        tc_pr.remove(existing)
    valign = OxmlElement("w:vAlign")
    valign.set(qn("w:val"), align)
    tc_pr.append(valign)


def set_paragraph_spacing_twips(
    paragraph, *, before: int = 0, after: int = 0, line: int = PROTOCOL_SPACER_LINE_TWIPS
) -> None:
    """Set paragraph spacing via OOXML twips — matches reference protocol gaps."""
    p_pr = paragraph._p.get_or_add_pPr()
    existing = p_pr.find(qn("w:spacing"))
    if existing is not None:
        p_pr.remove(existing)
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), str(before))
    spacing.set(qn("w:after"), str(after))
    spacing.set(qn("w:line"), str(line))
    spacing.set(qn("w:lineRule"), "auto")
    p_pr.append(spacing)


def add_protocol_spacer_paragraph(
    doc,
    *,
    before: int = 0,
    after: int = 0,
    line: int = PROTOCOL_SPACER_LINE_TWIPS,
    text: str = "",
    bold: bool = False,
) -> None:
    """Spacer paragraph between protocol tables — matches GLYCINE IP.docx gaps."""
    p = doc.add_paragraph()
    if text:
        run = p.add_run(text)
        style_run(run, bold=bold)
    set_paragraph_spacing_twips(p, before=before, after=after, line=line)


def add_header_trailing_paragraph(header) -> None:
    """Empty Header-style paragraph after header table — creates gap before batch table."""
    p = header.add_paragraph()
    try:
        p.style = "Header"
    except KeyError:
        set_paragraph_spacing_twips(p, after=0, line=240)


def add_footer_trailing_paragraph(footer) -> None:
    """Empty Footer-style paragraph after footer table — matches reference."""
    p = footer.add_paragraph()
    try:
        p.style = "Footer"
    except KeyError:
        set_paragraph_spacing_twips(p, after=0, line=240)


def add_zero_gap_paragraph(doc) -> None:
    """Tight spacer between tables — reference uses after=0, line=360."""
    add_protocol_spacer_paragraph(doc, before=0, after=0)


def setup_protocol_table(
    table,
    col_widths: list[int],
    *,
    width_dxa: int | None = PROTOCOL_TABLE_WIDTH_DXA,
    borders: bool = False,
    cell_borders: bool = False,
    grid_style: bool = False,
    indent_dxa: int | None = None,
) -> None:
    table_fixed_width_dxa(table, width_dxa)
    set_table_grid_columns(table, col_widths)
    if grid_style:
        set_table_style_grid(table)
    if borders:
        apply_table_grid_borders(table)
    if cell_borders and not grid_style:
        for row in table.rows:
            for cell in row.cells:
                apply_cell_borders(cell)
    if indent_dxa is not None:
        set_table_indent(table, indent_dxa)


# Backward compatible alias
def table_full_width(table) -> None:
    table_fixed_width_dxa(table)
