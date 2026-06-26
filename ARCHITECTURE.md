# Architecture — Pharmaceutical QMS Document Platform

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI REST Layer                        │
│  /products  /batches  /moa/generate  /protocols/generate  ...  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Service Layer                                │
│  ProductService │ DocumentService │ PDFService                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  PostgreSQL   │  │ Document Engine │  │ Validation Eng. │
│  / SQLite     │  │                 │  │                 │
└───────────────┘  └────────┬────────┘  └─────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        Context Builder  docxtpl     python-docx
        Section Numbering  Jinja2    Header/Footer/Tables
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                    base_*.docx templates
                            │
                            ▼
                      generated/*.docx
                            │
                            ▼
                  LibreOffice Headless → PDF
```

## Design Principles

1. **Templates are product-agnostic** — `base_moa.docx` works for Glycine, Zinc, or any future product
2. **Data drives content** — JSON configs define tests, procedures, criteria
3. **Components are reusable** — header, footer, revision history shared across document types
4. **SOP is source of truth** — page setup, fonts, margins from QA 01 SOP ON SOP
5. **PDF is pluggable** — `PDFConverter` ABC allows swapping LibreOffice for Aspose.Words

## Folder Structure

```
sop/
├── app/
│   ├── api/routes/          # FastAPI endpoints
│   ├── core/                # Config, constants
│   ├── database/            # SQLAlchemy engine, session
│   ├── models/              # ORM models
│   ├── schemas/             # Pydantic request/response models
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   ├── validators/          # Acceptance criteria validation
│   └── document_engine/
│       ├── context_builder.py
│       ├── renderer.py
│       ├── section_numbering.py
│       ├── table_renderer.py
│       └── components/
│           └── header_footer.py
├── template_builder/        # Programmatic DOCX template creation
├── templates/               # base_moa.docx, base_protocol.docx, ...
├── config/products/         # Product JSON configurations
├── generated/               # Output documents
├── static/                  # Company logo, assets
├── scripts/                 # CLI utilities
└── tests/
```

## Database Schema

### products

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| product_code | VARCHAR UNIQUE | e.g. FG00038 |
| product_name | VARCHAR | Display name |
| reference | VARCHAR | IP, USP, etc. |
| molecular_weight | VARCHAR | |
| chemical_formula | VARCHAR | |
| config_json | TEXT | Full product configuration |
| created_at / updated_at | DATETIME | Timestamps |

### batches

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | |
| product_id | FK → products | |
| batch_no | VARCHAR | |
| mfg_date / exp_date | DATE | |
| batch_size | VARCHAR | |
| ar_no | VARCHAR | Analytical reference number |

### documents

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | |
| product_id | FK → products | |
| batch_id | FK → batches (nullable) | |
| document_type | VARCHAR | MOA, PROTOCOL, SOP, ... |
| document_no | VARCHAR | MOA/FG00038/01 |
| revision_no | VARCHAR | 01 |
| subject | VARCHAR | |
| department | VARCHAR | |
| effective_date / review_date | DATE | |
| superseded_revision | VARCHAR | |
| status | VARCHAR | GENERATED, APPROVED, ... |
| context_json | TEXT | Render context snapshot |
| docx_path / pdf_path | VARCHAR | File paths |

## Document Generation Pipeline

```
1. Load product config (DB or JSON)
2. build_document_context()
   ├── Assign document numbers
   ├── number_tests() → section 1.0, 2.0, 1.1, ...
   ├── Build protocol_summary table rows
   └── Serialize dates, approval block
3. docxtpl.DocxTemplate.render(context)
4. python-docx post-processing
   ├── Revision history table (SOP)
   ├── Dynamic tables
   ├── Universal header (logo, doc no, page X of Y)
   └── Universal footer (prepared/checked/approved)
5. Save to generated/
6. Optional: PDFService → LibreOffice headless
```

## Template Architecture

Templates contain **Jinja2 placeholders only** — no product-specific values.

| Template | Key loops |
|----------|-----------|
| `base_moa.docx` | `{% for test in tests %}` |
| `base_protocol.docx` | `protocol_summary`, `all_tests` |
| `base_sop.docx` | `{% for section in sop_sections %}` |
| `base_annexure.docx` | `subject`, `content` |
| `base_specification.docx` | `protocol_summary` |

Templates are generated programmatically by `template_builder/builder.py` — no manual Word editing required for new document types.

## Section Numbering Engine

`SectionNumberingEngine` produces hierarchical numbers:

- `next_section()` → 1.0, 2.0, 3.0
- `next_subsection()` → 1.1, 1.2 (under current section)
- `next_subsubsection()` → 1.1.1, 1.1.2

Applied automatically in `context_builder.py` — templates never hardcode section numbers.

## Header / Footer (per SOP Annexure-I)

**Header (every page):**

| Left | Right |
|------|-------|
| Company Logo + Name | Document Type |
| DEPARTMENT | PAGE NO. (Page X of Y) |
| DOCUMENT NO. | EFFECTIVE DATE |
| SUBJECT | REVIEW DATE |
| | SUPERSEDED |

**Footer (every page):**

| PREPARED BY | CHECKED BY | APPROVED BY |
| Sign / Date / Name / Designation | | |
| "For Restricted Circulation Only" | | |

## Validation Engine

Machine-readable acceptance criteria → automatic PASS/FAIL:

```python
validate_result(6.1, {"type": "range", "min": 5.9, "max": 6.3})  # → PASS
validate_result(7.0, {"type": "range", "min": 5.9, "max": 6.3})  # → FAIL
```

Exposed via `POST /validation/results` for batch result entry workflows.

## Step-by-Step Implementation Plan

### Phase 1 — Foundation (Complete)
- [x] Project structure and dependencies
- [x] Database models (Product, Batch, Document)
- [x] Pydantic schemas and product JSON schema
- [x] Core configuration (SOP page standards)

### Phase 2 — Document Engine (Complete)
- [x] Section numbering engine
- [x] Context builder
- [x] docxtpl renderer
- [x] Header/footer/revision history components
- [x] Dynamic table renderer
- [x] Template builder (programmatic DOCX)

### Phase 3 — API & Services (Complete)
- [x] Product CRUD and JSON import
- [x] Batch management
- [x] MOA / Protocol / SOP / Annexure generation endpoints
- [x] Document download and PDF conversion
- [x] Validation API

### Phase 4 — Configuration & Examples (Complete)
- [x] Glycine IP, Zinc Bisglycinate, Magnesium Aspartate, Calcium Citrate configs
- [x] Example generation script
- [x] Unit tests

### Phase 5 — Production Hardening (Future)
- [ ] Alembic migrations
- [ ] Authentication / role-based access
- [ ] Document approval workflow state machine
- [ ] Aspose.Words PDF adapter
- [ ] Web UI for result entry
- [ ] Change control integration

## PostgreSQL Setup

```bash
# .env
DATABASE_URL=postgresql://qms_user:password@localhost:5432/qms
```

Tables are auto-created on startup via `init_db()`. For production, add Alembic migrations.

## Extending Document Types

1. Add enum value to `DocumentType`
2. Add template mapping in `TEMPLATE_MAP`
3. Add `build_*_template()` in `TemplateBuilder`
4. Add API route in `documents.py`
5. Run `python scripts/build_templates.py`

No product-specific code changes required.
