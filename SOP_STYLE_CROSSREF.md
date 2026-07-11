# SOP Style Cross-Reference — QA-01 vs DOC-Module Code

**Date:** 2026-07-10  
**Mode:** Read-only — no code or config changes  
**SOP authority:** [AC-QMS-DEV-DOCS/reference-sops/02_document_styling.md](../AC-QMS-DEV-DOCS/reference-sops/02_document_styling.md) (QA-01 SOP-on-SOP extract)  
**Note:** `QA-01-01_STYLE_SPEC.md` was not found in the workspace; this extract is the comparison baseline.  
**Code scope:** `AC-QMS-DOC-Module/app/core/config.py`, `app/document_engine/styles.py`, `components/header_footer.py`, `components/qa_layout_common.py`, `components/*_layout.py`, `section_numbering.py`, `app/core/constants.py`

**Rule (per [ARCHITECTURE.md](ARCHITECTURE.md)):** QA-01 is source of truth for styling. Where code disagrees with a SOP-stated value, the divergence is logged as a **code issue**, not a spec change.

---

## 1. How margins and fonts are applied

Rendering does **not** use `Settings.page_margin_inch` / `footer_distance_inch` at runtime. Those values in `config.py` are **unused** (grep: only defined in `config.py`, never read elsewhere).

Actual page setup is **`PAGE_SETUP[DocumentType]`** in `styles.py`, applied via `configure_page_setup()` → `_set_margins()` (`styles.py:219-227`, `279-284`).

Default body font comes from `Settings.default_font` / `default_font_size` via `style_run()` (`config.py:28-29`, `styles.py:87-91`).

### Document type → layout → page setup

| DocumentType | Layout module | Header builder | `configure_page_setup` source |
|--------------|---------------|----------------|-------------------------------|
| SOP | `sop_layout.py` | `build_sop_header` (2-col, bordered) | `PAGE_SETUP[SOP]` |
| ANNEXURE | `header_footer.py` (docxtpl post-process) | `build_header_table` (2-col) | `PAGE_SETUP[ANNEXURE]` |
| PROTOCOL | `protocol_layout.py` | `build_protocol_header` (6-col) | `PAGE_SETUP[PROTOCOL]` |
| MOA | `moa_layout.py` | `build_six_col_metadata_header` | `PAGE_SETUP[MOA]` |
| SPECIFICATION | `spec_layout.py` | `build_six_col_metadata_header` | `PAGE_SETUP[SPECIFICATION]` |

---

## 2. Footer two-profile question (explicit answer)

**SOP defines two margin profiles:**

| Profile | Top / Bottom / Left / Right / Header | Footer distance |
|---------|--------------------------------------|-----------------|
| Procedural / body | all **1.0"** | **0.5"** |
| Format & annexure | all **1.0"** | **0.3"** |

**What the code does:** Per-document-type `PAGE_SETUP` in `styles.py:230-276` — **not** a single global footer distance, and **not** driven by `config.footer_distance_inch`.

| DocumentType | Code footer | Code body margins (T/R/B/L/H) | vs SOP procedural | vs SOP format |
|--------------|-------------|-------------------------------|-------------------|---------------|
| **SOP** | 0.5" | 1.0 / 1.0 / 1.0 / 1.0 / 1.0 | **Match** procedural | N/A |
| **ANNEXURE** | 0.3" | 1.0 / 1.0 / 1.0 / 1.0 / 1.0 | Footer wrong for procedural class | **Match** format |
| **PROTOCOL** | **0.33"** | 1.0 / **0.5** / **0.5** / **0.5** / **0.5** | **Divergence** (footer + sides) | Footer 0.33 ≠ 0.3 |
| **MOA** | **0.40"** | **0.5** / **0.5** / **0.5** / **0.5** / **0.5** | **Divergence** (all) | N/A |
| **SPECIFICATION** | 0.5" | **0.5** / **0.5** / **0.5** / **0.5** / **0.5** | Footer OK; **body margins diverge** | N/A |

**Conclusion:** The code implements **two distinct footer distances** (0.5" and 0.3") but **not** as a clean procedural-vs-format class split mapped to document intent. SOP and Annexure match their respective profiles; **analytical docs (MOA, Protocol, Specification) use reference-DOCX-tuned margins that contradict SOP procedural 1.0"**. PROTOCOL footer **0.33"** matches neither SOP value exactly. `config.py:34` (`footer_distance_inch = 0.5`) is misleading dead configuration.

---

## 3. Comparison table

| Property | QA-01 says | Code currently has | Status | Evidence |
|----------|------------|-------------------|--------|----------|
| Page size | A4 | 8.27" × 11.69" (A4) | **Match** | `styles.py:220-221` |
| Body font family | Times New Roman ("Roman") | `"Times New Roman"` | **Match** | `config.py:28`; applied `styles.py:90` |
| Body font size | 12 pt | `default_font_size: int = 12` → `Pt(12)` | **Match** | `config.py:29`; `styles.py:91` |
| Company name | Aditya Chemicals (logo + name) | `company_name: str = "Aditya Chemicals"` | **Match** | `config.py:27`; headers use context/settings |
| Procedural margins (T/B/L/R) | 1.0" each | **SOP/ANNEXURE:** 1.0"; **MOA/PROTOCOL/SPEC:** 0.5" (PROTOCOL top 1.0) | **Divergence** for analytical types | `styles.py:230-275` |
| Procedural header distance | 1.0" | **SOP/ANNEXURE:** 1.0"; **MOA/PROTOCOL/SPEC:** 0.5" | **Divergence** for analytical types | `styles.py:230-275` |
| Procedural footer distance | 0.5" | **SOP/SPEC:** 0.5"; **MOA:** 0.40"; **PROTOCOL:** 0.33" | **Divergence** MOA/PROTOCOL | `styles.py:237,246,255,273` |
| Format/annexure footer distance | 0.3" | **ANNEXURE:** 0.3" | **Match** | `styles.py:264` |
| Format/annexure body margins | 1.0" all sides | **ANNEXURE:** 1.0" all sides | **Match** | `styles.py:258-263` |
| `config.page_margin_inch` | (SOP silent) | 1.0 — **unused at runtime** | **Code-only** (dead) | `config.py:32` |
| `config.footer_distance_inch` | (SOP silent) | 0.5 — **unused at runtime** | **Code-only** (dead/misleading) | `config.py:34` |
| Header: logo + company left | Yes | Row 0 left: company text or logo image | **Match** (structure) | `header_footer.py:44-45,71-77`; `qa_layout_common.py:249-266` |
| Header: document title right | "STANDARD OPERATING PROCEDURE" or doc title | `document_type_label` / product title in row 0 right | **Match** | `header_footer.py:36,45`; `sop_layout.py:47,56` |
| Header: DEPARTMENT | Present | Row 2 left: `DEPARTMENT\n{value}` | **Match** | `header_footer.py:46`; `sop_layout.py:57` |
| Header: PAGE NO. | Present; value `(n / total)` | Label `PAGE NO.` + page fields | **Match** (label) | `header_footer.py:63`; `sop_layout.py:69` |
| Header: document number label | SOP: `SOP NO.` | **SOP layout:** `SOP NO.`; **generic/annexure:** `DOCUMENT NO.` (default) | **Divergence** on non-SOP 2-col path | `sop_layout.py:58`; `header_footer.py:48` |
| Header: EFFECTIVE DATE | Present | Row 3 right | **Match** | `header_footer.py:49`; `sop_layout.py:58` |
| Header: SUBJECT | Present | Row 4 left | **Match** | `header_footer.py:53`; `sop_layout.py:59` |
| Header: REVIEW DATE | Present | Row 4 right | **Match** | `header_footer.py:53`; `sop_layout.py:59` |
| Header: SUPERSEDED | Present | Row 5 right | **Match** | `header_footer.py:54`; `sop_layout.py:60` |
| Page number format | `(n / total)` | **Path A:** `"Page X of Y"` (`add_page_number_field`); **Path B:** `"X of Y"` (`add_protocol_page_number_field`) | **Divergence** (wording) | `qa_layout_common.py:87-100` |
| Footer: PREPARED / CHECKED / APPROVED | Three columns, Sign + Date | 6-col table: labels row 0; SIGN/DATE row 1; names row 3; designations row 4 | **Match** (structure) | `qa_layout_common.py:141-186` |
| Footer legend | "For Restricted Circulation Only" | `FOOTER_RESTRICTED_TEXT` same string, bold centered | **Match** | `constants.py:36`; `qa_layout_common.py:192-198` |
| Heading font size | (SOP silent — [CONFIRM-CODE]) | **12 pt bold** — same as body; no separate heading pt | **Code-only** | `sop_layout.py:88-89` via `style_run(..., bold=True)` |
| Body line spacing | (SOP silent) | `PROTOCOL_SPACER_LINE_TWIPS = 360` (18 pt line) default in QA cells | **Code-only** | `styles.py:76`; `qa_layout_common.py:117` |
| Detail cell line spacing | (SOP silent) | `DETAIL_COMPACT_LINE_TWIPS = 240` | **Code-only** | `styles.py:79` |
| Section gap | (SOP silent) | `PROTOCOL_SECTION_GAP_TWIPS = 120` | **Code-only** | `styles.py:77` |
| Table/cell border weight | (SOP silent) | `sz="4"` (single grid borders) | **Code-only** | `styles.py:165-193` |
| Page border | (SOP silent) | Double (SOP/Protocol/Annexure/MOA single); Spec: none | **Code-only** | `styles.py:200-216,230-275` |
| Page border offset spaces | (SOP silent) | top 2, left 20, bottom 1, right 20 (twips) | **Code-only** | `styles.py:208` |
| Logo width | (SOP silent) | **1.2"** (2-col header); **1.33"** (6-col protocol/QA header) | **Code-only** (inconsistent) | `header_footer.py:77`; `protocol_layout.py:60`; `qa_layout_common.py:249` |
| Logo row height | (SOP silent) | `HEADER_LOGO_ROW_HEIGHT_TWIPS = 943` | **Code-only** | `styles.py:84`; `qa_layout_common.py:303` |
| Header table width | (SOP silent) | **6.5"** (2-col); **7.67"** (6-col) | **Code-only** | `header_footer.py:32`; `qa_layout_common.py:156,297` |
| Section numbering | Hierarchical decimal 1.0 / 1.1 / 1.1.1 | `SectionNumberingEngine` same scheme | **Match** | `section_numbering.py:12-38` |
| SOP sub-heading structure | Objective, Scope, … History | Driven by `sop_sections` in product config | **Match** (content model) | `sop_layout.py:112-115` |
| MASTER COPY / CONTROLLED COPY watermark | Physical stamp/watermark "as applicable" | **No** watermark or copy overlay rendered | **SOP-only-not-in-code** (physical) | grep `app/`: no matches |
| Issuance stamp field | (SOP deeper read) | Protocol batch table label **"Issuance Stamp by QA"** — empty value cell, not an image | **Code-only** field label | `protocol_layout.py:268-269` |

---

## 4. DIVERGENCES (ranked by significance)

Compliance-relevant formatting issues where code contradicts SOP-stated values:

### 1. Body margins on analytical documents (MOA, Specification, Protocol sides)

- **SOP:** Procedural profile — Top/Bottom/Left/Right **1.0"** for generated analytical docs (SPEC/MOA/AWS/COA per QA-01 closing section).
- **Code:** MOA and Specification use **0.5"** on all sides including header distance (`styles.py:241-246`, `267-272`). Protocol uses **0.5"** left/right/bottom/header (`styles.py:233-236`).
- **Impact:** Rendered MOA/Spec/Protocol pages have wider printable area than SOP allows — compliance-relevant, not cosmetic.

### 2. Footer distance on MOA (0.40") and Protocol (0.33")

- **SOP:** Procedural footer **0.5"**; format footer **0.3"**.
- **Code:** MOA `footer: 0.40`; Protocol `footer: 0.33` (`styles.py:246`, `237`).
- **Impact:** Footer content sits at wrong distance from page edge for both SOP profiles.

### 3. Dead / misleading `config.py` margin settings

- **SOP:** Two explicit profiles (procedural vs format/annexure).
- **Code:** `page_margin_inch`, `header_distance_inch`, `footer_distance_inch` in `config.py:32-34` suggest a single global setup but are **never consumed**; real values are scattered in `PAGE_SETUP` tuned to reference DOCXs.
- **Impact:** Future SOP config layer cannot trust `Settings` as the styling seam without refactoring.

### 4. Page number wording inconsistency

- **SOP:** `PAGE NO. | (n / total)` — implies numeric `n / total` without leading "Page".
- **Code:** SOP/Annexure 2-col path inserts `"Page "` prefix (`qa_layout_common.py:89`). MOA/Protocol/Spec 6-col path uses `"X of Y"` without "Page" (`qa_layout_common.py:95-100`).
- **Impact:** Same QMS system produces two page-number formats depending on document type.

### 5. Logo width inconsistency between header implementations

- **SOP:** Silent on dimensions.
- **Code:** `Inches(1.2)` in `header_footer.py:77` vs `HEADER_LOGO_WIDTH_INCHES = 1.33` in `protocol_layout.py:60` / `qa_layout_common.py:249`.
- **Impact:** Visual inconsistency across document families; should be unified when style config layer is built.

### 6. Document number header label on generic 2-col path

- **SOP:** `SOP NO.` in header field row.
- **Code:** Default `DOCUMENT NO.` unless context sets `document_no_label` (`header_footer.py:48`). SOP layout correctly uses `SOP NO.` (`sop_layout.py:58`).
- **Impact:** Annexure/docxtpl post-process path may show wrong label for SOP-numbered documents.

---

## 5. FILLED VALUES — [CONFIRM-CODE] gaps completed from code

Values the SOP does not state numerically; **code is authoritative** for these:

### Fonts and spacing

| Constant | Value | Meaning | Evidence |
|----------|-------|---------|----------|
| `default_font_size` | 12 pt | Body and headings | `config.py:29` |
| Heading treatment | 12 pt **bold** | No separate heading size | `styles.py:87-91`; `sop_layout.py:89` |
| `PROTOCOL_SPACER_LINE_TWIPS` | 360 | ~18 pt line spacing in QA cells | `styles.py:76` |
| `DETAIL_COMPACT_LINE_TWIPS` | 240 | Tighter procedure/detail cells | `styles.py:79` |
| `PROTOCOL_SECTION_GAP_TWIPS` | 120 | Gap between body tables | `styles.py:77` |
| `DETAIL_CELL_MARGIN_TWIPS` | 40 | Cell internal margin | `styles.py:80` |
| Default cell margin L/R | 108 dxa | Detail cells | `styles.py:141-142` |

### Borders

| Constant | Value | Evidence |
|----------|-------|----------|
| Table/cell border `sz` | `"4"` | `styles.py:165-193` |
| Page border `sz` | `"4"` | `styles.py:200-212` |
| Page border `val` | `double` (default) or `single` (MOA) | `styles.py:200,247` |
| Page border spaces (twips) | top 2, left 20, bottom 1, right 20 | `styles.py:208` |

### Logo and header geometry

| Constant | Value | Evidence |
|----------|-------|----------|
| Logo width (2-col) | 1.2" | `header_footer.py:77` |
| Logo width (6-col) | 1.33" | `protocol_layout.py:60`; `qa_layout_common.py:249` default |
| `HEADER_LOGO_ROW_HEIGHT_TWIPS` | 943 | `styles.py:84` |
| 2-col header table width | 6.5" | `header_footer.py:32`; `sop_layout.py:38` |
| 6-col header/footer table width | 7.67" | `qa_layout_common.py:156,297`; `protocol_layout.py:88` |
| `SOP_HEADER_GRID_COLS` | [4680, 4680] | `sop_layout.py:29` |
| `SOP_HEADER_TABLE_WIDTH_DXA` | 9360 | `sop_layout.py:30` |

### Table widths and column grids (dxa twips)

| Constant | Value | Evidence |
|----------|-------|----------|
| `PROTOCOL_TABLE_WIDTH_DXA` / shared `_TW` | 10400 | `styles.py:14,37` |
| `BATCH_GRID_COLS` | [2447, 279, 2851, 2027, 279, 2517] | `styles.py:23` |
| `SUMMARY_GRID_COLS` | [937, 2469, 6, 2641, 4347] | `styles.py:25` |
| `FOOTER_GRID_COLS` | [1734, 1733, 1733, 1733, 1733, 1734] | `styles.py:28` |
| `MOA_HEADER_GRID_COLS` | [2185, 262, 3146, 2401, 229, 2177] | `styles.py:44` |
| `MOA_DETAIL_GRID_COLS` | [694, 162, 54, 9490] | `styles.py:41` |
| `SPEC_TABLE_WIDTH_DXA` | 11155 | `styles.py:52` |
| `SPEC_HEADER_TABLE_WIDTH_DXA` | 11160 | `styles.py:53` |
| `SPEC_HEADER_TABLE_INDENT_DXA` | -365 | `styles.py:54` |
| `SPEC_HEADER_GRID_COLS` | [2250, 293, 3487, 2036, 304, 2790] | `styles.py:55` |
| `SPEC_PRODUCT_GRID_COLS` | [2263, 1701, 1985, 5206] | `styles.py:59` |
| `SPEC_PARAM_GRID_COLS` | [2263, 2152, 1534, 5206] | `styles.py:60` |
| `SPEC_MICRO_GRID_COLS` | [2263, 3686, 5206] | `styles.py:61` |
| `SPEC_REVISION_GRID_COLS` | [2813, 3487, 2430, 2430] | `styles.py:62` |
| `PROTOCOL_REVISION_GRID_COLS` | [2546, 3882, 2008, 1964] | `styles.py:67` |
| `HEADER_GRID_COLS` | [2278, 279, 2640, 1864, 279, 3060] | `styles.py:72` |
| `COLON_COL_WIDTH_DXA` | 279 | `styles.py:20` |

### Page borders per document type (code-only; SOP silent)

| DocumentType | Page border |
|--------------|-------------|
| SOP | double |
| ANNEXURE | double |
| PROTOCOL | double |
| MOA | single |
| SPECIFICATION | none |

Evidence: `styles.py:238,247,256,265,274`.

---

## 6. Watermark / Master Copy / Controlled Copy

**Search:** `watermark`, `MASTER COPY`, `CONTROLLED COPY` in `app/` — **zero matches**.

**Finding:** The renderer produces **no** watermark overlay, Master Copy stamp image, or Controlled Copy stamp image.

**QA-01** (`02_document_styling.md:27`) describes MASTER COPY / CONTROLLED COPY as applicable to generated analytical docs — consistent with **physical** document control stamps, not digital rendering.

**Related code-only field:** Protocol batch metadata table includes an empty cell under the label **"Issuance Stamp by QA"** (`protocol_layout.py:268-269`) — a placeholder label for manual/physical stamping, not a rendered stamp.

**Conclusion:** Treat physical copy stamps as **out-of-renderer-scope**. Epic 21 / Track A style config should not require watermark rendering unless QA-01 full document (13 pp) mandates digital stamps after deeper read.

---

## 7. Complete spec artifact (for Track A config layer)

| Layer | Authority |
|-------|-----------|
| SOP-stated values (A4, TNR 12pt, margin profiles, header/footer structure, restricted legend) | **QA-01** — divergences in Section 4 are code bugs |
| Numeric precision (table grids, twips, border sz, logo dims, spacing) | **Code** — Section 5 FILLED VALUES |
| Physical stamps / watermarks | **SOP describes; code does not render** — out of scope unless full QA-01 says otherwise |

---

## 8. Verification checklist

| # | Check | Result |
|---|-------|--------|
| 1 | Only `SOP_STYLE_CROSSREF.md` created | **PASS** |
| 2 | Comparison table rows include file:line evidence | **PASS** — Section 3 |
| 3 | Footer two-profile question answered explicitly | **PASS** — Section 2 |
| 4 | Divergences ranked by significance | **PASS** — Section 4 |
| 5 | FILLED [CONFIRM-CODE] values listed | **PASS** — Section 5 |
| 6 | Watermark/stamp presence confirmed | **PASS** — Section 6 (none rendered) |

---

*End of cross-reference. Source: code inspection + QA-01 reference extract only; no runtime render verification in this report.*
