# AC-QMS-DOC-Module — Read-Only Repository Audit

**Date:** 2026-07-09  
**Scope:** `AC-QMS-DOC-Module` (primary); peek at `AC-QMS-API-Gateway` for Epic 21 seam only  
**Method:** Code read-only — no installs, no service runs, no file changes except this report  
**Context:** Rev 2.3.1 Node backend is complete; Python render integration (Epic 21) is deferred. This audit maps what the DOC-Module actually is to plan (a) SOP-on-SOP extraction and (b) render integration.

---

## 1. Repo Map & Stack

### Directory tree (2–3 levels)

```
AC-QMS-DOC-Module/
├── app/
│   ├── main.py                      # FastAPI app factory, lifespan, /health
│   ├── api/routes/
│   │   ├── batches.py               # POST /batches
│   │   ├── documents.py             # generate + document record endpoints
│   │   ├── products.py              # product CRUD + JSON import
│   │   └── validation.py            # POST /validation/results
│   ├── core/
│   │   ├── config.py                # Settings (fonts, margins, dirs)
│   │   └── constants.py             # DocumentType enum, prefixes
│   ├── database/                    # SQLAlchemy engine, init_db, session
│   ├── document_engine/
│   │   ├── components/              # moa, protocol, spec, sop layouts; header_footer
│   │   ├── context_builder.py
│   │   ├── renderer.py
│   │   ├── section_numbering.py
│   │   ├── styles.py
│   │   └── table_renderer.py
│   ├── models/                      # Product, Batch, Document ORM
│   ├── repositories/                # product.py, batch.py (no document.py)
│   ├── schemas/                     # Pydantic request/response models
│   ├── services/                    # document_service, pdf_service
│   └── validators/                  # acceptance criteria
├── config/products/                 # glycine_ip.json, sop_on_sop.json, etc.
├── generated/                       # Runtime DOCX/PDF output
├── scripts/                         # init_db, build_templates, generate_example
├── static/                          # logo.jpeg
├── templates/                       # base_*.docx (docxtpl bases)
├── template_builder/                # Programmatic template generation
├── tests/
├── main.py                          # Stale pointer (see below)
├── requirements.txt
├── requirements-postgres.txt
├── .env.example
├── qms.db                           # SQLite dev DB (present on disk)
├── ARCHITECTURE.md
└── README.md
```

**Note:** `ARCHITECTURE.md` and `README.md` still refer to legacy folder name `sop/`; actual repo root is `AC-QMS-DOC-Module`.

### Python version & key libraries

| Item | Source |
|------|--------|
| Python | README: **3.12 or 3.13** required |
| No `pyproject.toml` | Dependencies only in `requirements.txt` |
| FastAPI | `fastapi>=0.115.0` (INFERRED installed: **0.139.0** in `.venv`) |
| Uvicorn | `uvicorn>=0.32.0` |
| Pydantic | `pydantic>=2.9.0`, `pydantic-settings>=2.6.0` |
| ORM | `sqlalchemy>=2.0.36`, `aiosqlite` (SQLite); Postgres via `psycopg` in `requirements-postgres.txt` |
| DOCX | `python-docx>=1.1.2`, `docxtpl>=0.18.0` |
| Templating | `Jinja2>=3.1.4` (used by docxtpl) |
| PDF | **LibreOffice headless** (`soffice --headless`) via `pdf_service.py` — not reportlab/weasyprint |
| HTTP client | `httpx>=0.28.0` listed but **no imports in `app/`** |
| Tests | `pytest`, `pytest-asyncio` |

### How it is run

```bash
pip install -r requirements.txt
python scripts/build_templates.py   # if templates missing
python scripts/init_db.py           # optional: seed products from JSON
uvicorn app.main:app --reload --app-dir .
```

| Item | Value |
|------|-------|
| Default port | **8000** (not set in code; Uvicorn default) |
| Health | `GET /health` → `{"status":"ok","app":"Pharmaceutical QMS Document Platform"}` |
| Swagger | `http://127.0.0.1:8000/docs` |

Root `main.py` is stale:

```1:1:AC-QMS-DOC-Module/main.py
"""Run with: uvicorn app.main:app --reload --app-dir sop"""
```

### Docker / compose

**None found** in `AC-QMS-DOC-Module` or parent monorepo (INFERRED from file search). No Dockerfile, no compose entry for this service.

---

## 2. Endpoint Inventory

All routes registered in `app/main.py` via routers: `products`, `batches`, `documents`, `validation`.

| Method | Path | Purpose | State |
|--------|------|---------|-------|
| `GET` | `/health` | Liveness | **Working** |
| `POST` | `/products` | Create product in DB | **Working** |
| `GET` | `/products` | List products | **Working** |
| `GET` | `/products/{product_id}` | Get product by ID | **Working** |
| `POST` | `/products/import` | Multipart JSON product import | **Working** |
| `POST` | `/batches` | Create batch (requires product in DB) | **Working** |
| `POST` | `/moa/generate` | MOA DOCX + DB record | **Working** — styled programmatic render |
| `POST` | `/protocols/generate` | Protocol DOCX + DB record | **Working** — styled programmatic render |
| `POST` | `/specification/generate` | Specification DOCX + DB record | **Working** — styled programmatic render |
| `POST` | `/sop/generate` | SOP DOCX + DB record | **Working** — styled programmatic render |
| `POST` | `/annexure/generate` | Annexure DOCX + DB record | **Working** — docxtpl path |
| `POST` | `/generate` | Inline product data → DOCX download | **Working** — no DB row; `FileResponse` |
| `GET` | `/documents/{document_id}` | Document metadata | **Broken** — imports missing `app.repositories.document` |
| `GET` | `/documents/{document_id}/download` | DOCX file download | **Broken** — same missing import |
| `GET` | `/documents/{document_id}/pdf` | PDF conversion + download | **Working** — uses `DocumentService` inline |
| `POST` | `/validation/results` | Acceptance-criteria PASS/FAIL | **Working** |

**Absent (not implemented, not 501 stub):**

- `/aws/generate`, `/coa/generate`, or any AWS/COA-specific routes
- Auth middleware, API keys, JWT
- Explicit `501 Not Implemented` responses anywhere in DOC-Module routes

**Broken route detail:** `GET /documents/{id}` and `/download` import `app.repositories.document.DocumentRepository`, but `app/repositories/` contains only `product.py` and `batch.py`. `DocumentRepository` is defined inside `app/services/document_service.py` and is not exported from a repository module — these routes will raise `ModuleNotFoundError` at request time.

---

## 3. Rendering Capability — What Actually Works

### Pipeline overview

```
Request
  → build_document_context(product_config, document_type, …)
  → DocumentRenderer.render()
       ├─ MOA / PROTOCOL / SPECIFICATION / SOP → PROGRAMMATIC_LAYOUTS (python-docx from scratch)
       └─ ANNEXURE → docxtpl(base_annexure.docx) + _post_process (header/footer, tables)
  → generated/<filename>.docx
  → (optional) PDFService → LibreOffice headless → generated/<filename>.pdf
```

From `app/document_engine/renderer.py`:

```33:39:AC-QMS-DOC-Module/app/document_engine/renderer.py
PROGRAMMATIC_LAYOUTS = {
    DocumentType.PROTOCOL: apply_protocol_layout,
    DocumentType.MOA: apply_moa_layout,
    DocumentType.SPECIFICATION: apply_spec_layout,
    DocumentType.SOP: apply_sop_layout,
}
```

MOA/Protocol/Spec/SOP **bypass** their `base_*.docx` templates at runtime; templates exist for annexure and as legacy/alternate path.

### Classification: styled vs unstyled vs stub vs missing

| Document type | DOCX | PDF | Classification | Evidence |
|---------------|------|-----|----------------|----------|
| **MOA** | Yes | Via `GET /documents/{id}/pdf` | **Styled** | `apply_moa_layout` — table widths/fonts tuned to reference Glycine IP DOCX |
| **Protocol** | Yes | Via `/pdf` | **Styled** | `apply_protocol_layout` — reference GLYCINE IP protocol |
| **Specification** | Yes | Via `/pdf` | **Styled** | `apply_spec_layout` — reference Spec Glycine IP |
| **SOP** | Yes | Via `/pdf` | **Styled** | `apply_sop_layout` — reference QA 01 SOP ON SOP |
| **Annexure** | Yes | Via `/pdf` | **Partially styled** | docxtpl generic template + `apply_header_footer_to_document` post-process |
| **AWS** | — | — | **Missing entirely** | No `DocumentType`, layout, or route |
| **COA** | — | — | **Missing entirely** | No `DocumentType`, layout, or route |
| **Gateway Epic 21** | — | — | **Stub** | `renderDocuments()` logs + audits; no HTTP call |

**Important distinction:** "It renders" is not the Epic 21 finish line. MOA/Protocol/Spec/SOP produce **styled** DOCX approximating reference samples and SOP Annexure-I header/footer conventions — but styling is **hardcoded in Python**, not driven by an extracted QA 01-01 rule set (see Section 5).

### End-to-end trace: `POST /generate` (integration path for Node)

**Input:** `InlineGenerateRequest` (`app/schemas/document.py`)

**Handler** (`app/api/routes/documents.py`):

1. Maps `document_type` string → `DocumentType` enum
2. Builds context kwargs (document_no, revision_no, approval, revision_history, batch, extra_context)
3. Calls `DocumentRenderer().render(doc_type, request.product, filename, **context_kwargs)`
4. Returns `FileResponse` with `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

**Output:** DOCX file inline in HTTP response. No DB persistence. File also written to `generated/`.

### End-to-end trace: `POST /moa/generate` (DB-backed)

**Input:** `DocumentGenerateRequest` with `product_id`, optional `batch_id`, approval block, etc.

**Service** (`DocumentService.generate`):

1. Loads product from DB; deserializes `config_json` → `ProductConfig`
2. Optionally merges batch fields into context
3. Renders via same `DocumentRenderer`
4. Persists `Document` row with `context_json` snapshot, `docx_path`
5. Returns `DocumentResponse` JSON (metadata + paths)

**PDF:** Not produced on generate. `GET /documents/{id}/pdf` calls `PDFService` → LibreOffice converts existing DOCX; path saved to `documents.pdf_path`.

### Test evidence

`tests/test_document_render.py` parametrizes MOA, Protocol, Specification, SOP — asserts rendered DOCX has sections with header/footer tables. **No** FastAPI route tests, **no** annexure render test, **no** PDF conversion test.

---

## 4. Input Contract / Data Model

This section sizes **`mapToSopConfig`** on the Node side: what payload the gateway must produce for the Python renderer.

### Primary integration endpoint (recommended for Epic 21)

**`POST /generate`** — `InlineGenerateRequest` — no pre-registration in Python DB.

```python
class InlineGenerateRequest(BaseModel):
    document_type: Literal["moa", "protocol", "specification", "sop", "annexure"]
    product: ProductConfig
    document_no: str | None = None
    revision_no: str = "01"
    subject: str | None = None
    department: str = "QUALITY ASSURANCE"
    effective_date: date | None = None
    review_date: date | None = None
    superseded_revision: str | None = None
    approval: ApprovalBlock
    revision_history: list[RevisionHistoryEntry]
    batch: dict[str, Any]           # batch_no, mfg_date, exp_date, etc.
    extra_context: dict[str, Any]   # extension point
```

### `ProductConfig` (core payload)

```python
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
    tests: list[TestConfig]                    # name, procedure, acceptance_criteria, instruments, reagents, sub_tests, tables
    additional_tests: list[TestConfig]
    microbiological_tests: list[TestConfig]
    sop_sections: list[SopSection]             # title, content, subsections
    revision_history: list[RevisionHistoryEntry]
    metadata: dict[str, Any]
```

`TestConfig` includes nested `AcceptanceCriteria` (range, max, min, equals, text, nmt, nlt, between), `SubTestConfig`, and `DynamicTableConfig` (columns, rows, merges).

`ApprovalBlock`: `prepared_by`, `checked_by`, `approved_by` — each `ApprovalPerson` (name, designation, signature, date).

### DB-backed alternative

**`DocumentGenerateRequest`:** `product_id` + `batch_id` + same metadata fields. Product must exist in Python `products` table (`config_json` column holds full `ProductConfig`).

### Mapping to Rev 2.3.1 document types (INFERRED — mapper does not exist)

| Gateway `RenderDocType` | Python `document_type` | Rev 2.3.1 data source | Mapper gap |
|-------------------------|------------------------|----------------------|------------|
| `STANDING_SPEC` | `specification` | `specs`, `spec_tests`, product master fields | Flatten tests + limits + formulas into `TestConfig[]`; doc numbers from `specNo`/`revisionNo` |
| `STANDING_SPEC` (MOA half) | `moa` (separate call) | `moa_docs`, `moa_doc_sections` | Procedures from `moa_doc_sections.procedureSnapshot` merged into test `procedure` fields; **gateway currently calls only one `STANDING_SPEC` stub** |
| `AWS` | `protocol` (closest match) | Batch snapshot: `spec_document_tests`, `moa_document_sections`, `aws_sections` readings | Inject analyst/checker names, instrument/reagent refs, computed results, OOS flags — **not in current `ProductConfig` schema** |
| `COA` | **No enum value** | `coa_results`, `compliance_verdict`, batch metadata, signature block | **New document type + layout + schema required**; `coa_results` row shape not represented in Pydantic models |

**Assessment:** Contract is **well-defined for standing document types** (SPEC/MOA/Protocol/SOP) via `ProductConfig` + `InlineGenerateRequest`. It is **not designed for per-batch AWS/COA** documents. `mapToSopConfig` must be **designed** for AWS/COA before implementation; standing-doc mapping is a clearer build.

---

## 5. Styling / Template System

### How appearance is defined today

| Layer | Location | Role |
|-------|----------|------|
| **App settings** | `app/core/config.py` | `company_name`, `default_font` (Times New Roman), `default_font_size` (12), `page_margin_inch` (1.0), header/footer distances — comment: "Page setup per QA 01 SOP ON SOP" |
| **Hardcoded layout constants** | `app/document_engine/styles.py` | Table widths in dxa twips, column grids, borders, fonts — tuned per document type to match reference DOCXs |
| **Programmatic layouts** | `app/document_engine/components/*_layout.py` | MOA, Protocol, Spec, SOP body structure built in Python |
| **Header/footer** | `app/document_engine/components/header_footer.py` | Universal header (logo, doc no, page X of Y, effective/review dates) and footer (prepared/checked/approved, "For Restricted Circulation Only") per SOP Annexure-I |
| **docxtpl + Jinja2** | `renderer.py` + `templates/base_*.docx` | Runtime path for **ANNEXURE only**; templates built by `template_builder/builder.py` |
| **Section numbering** | `section_numbering.py` + `context_builder.py` | Hierarchical 1.0 / 1.1 / 1.1.1 — not hardcoded in templates |

`ARCHITECTURE.md` states design principle: "SOP is source of truth — page setup, fonts, margins from QA 01 SOP ON SOP." In code, that truth is **encoded as Python constants**, not loaded from an external SOP document or config file.

### What does NOT exist

- External SOP rule file / theme JSON / YAML that QA 01-01 could populate
- Watermark layer
- Runtime-swappable style config without code changes
- Separate "style config" module distinct from `styles.py` hardcoding

### SOP extraction landing zone (assessment)

| Readiness | Detail |
|-----------|--------|
| **Structure exists** | Header/footer component, page setup in Settings, per-type layout modules — logical places to inject rules |
| **Config layer missing** | No `sop_style.yaml` or equivalent; changing fonts/margins requires editing `config.py` and `styles.py` |
| **INFERRED sequence** | SOP extraction → define machine-readable style spec → wire into new config layer → refactor layouts to read config → visual regression against reference DOCXs |

**Partial readiness:** The rendering engine has the right **component boundaries** to receive SOP rules, but the **pluggable config layer must be built** before extraction can feed in without code edits.

---

## 6. Statefulness

Monorepo project rules describe DOC-Module as a **"stateless renderer."** Code shows **dual behavior:**

| Path | DB | Filesystem | Notes |
|------|-----|------------|-------|
| `POST /generate` | No row created | Writes `generated/*.docx` | Returns file inline — closest to stateless |
| `POST /*/generate` (typed) | `documents` row + `context_json` snapshot | Writes `generated/*.docx` | Stateful |
| `GET /documents/{id}/pdf` | Updates `pdf_path` on row | Writes PDF beside DOCX | Stateful |
| Products / batches | `products`, `batches` tables | — | Full CRUD persistence |

**Database:** SQLAlchemy; default SQLite `qms.db` at repo root; Postgres via `DATABASE_URL` in `.env`.

**Tables** (`ARCHITECTURE.md` + models): `products` (config_json), `batches`, `documents` (type, doc_no, revision, status, context_json, docx_path, pdf_path).

**Auth:** None. CORS wide open (`allow_origins=["*"]` in `app/main.py`).

**Generated files:** Returned inline (`/generate`) or stored with integer ID lookup (`/documents/{id}/download`). No S3 or shared object store in this service.

---

## 7. Backend Integration Seam — Current State

### API Gateway (peek — read-only)

| Item | State | Location |
|------|-------|----------|
| `sop-client` | **Does not exist** | Zero matches workspace-wide |
| `mapToSopConfig` | **Does not exist** | Zero matches workspace-wide |
| `renderDocuments()` | **Stub** | `AC-QMS-API-Gateway/src/services/render-documents.service.ts` |
| `generateCoaPdf()` | **No-op stub** | `AC-QMS-API-Gateway/src/services/coa-generator.ts` |
| `DOC_MODULE_URL` / similar | **Not in `.env.example`** | INFERRED: no env config for Python service URL |

**`renderDocuments` stub behavior:**

```14:45:AC-QMS-API-Gateway/src/services/render-documents.service.ts
/** Epic 21 — Python DOCX/PDF render seam. No HTTP call in Session 2/3. */
export async function renderDocuments(...) {
  log.info({ docType, entityId }, "TODO Epic 21: queue document render via Python microservice");
  await auditLog({ action: AuditAction.GENERATE, ... });
  return { status: "queued", message: `${docType} render queued (Epic 21 — Python integration pending)` };
}
```

Does **not** return HTTP 501 — returns `{ status: "queued" }`. Marketing COA PDF download (`marketing.service.ts`) **does** throw `AppError.notImplemented` (501) — separate code path.

**Trigger points (wired, stub only):**

| Event | File | Call |
|-------|------|------|
| SPEC QA sign | `workflow-engine.ts` → `onStandingSpecSigned` | `renderDocuments("STANDING_SPEC", specId, …)` inside transaction |
| AWS QA sign | `workflow-engine.ts` → `transitionAwsDocument` | `renderDocuments("AWS", …)` + `generateCoaFromSignedAws` + `generateCoaPdf()` no-op |
| COA sign-and-issue | `documents.service.ts` → `signAndIssueCoa` | `renderDocuments("COA", …)` post-commit |

**`file_attachments`:** Prisma model exists per Dev Bible; **no render code writes rows** today.

### DOC-Module side

- No HTTP client to call API Gateway
- No service-to-service auth
- `httpx` in requirements but unused
- `POST /generate` docstring explicitly positions endpoint for "main app" inline calls

### Contract gap summary

| Gateway sends today | Python expects |
|---------------------|----------------|
| `docType` enum + `entityId` UUID + optional `docNo` | Full `InlineGenerateRequest` with embedded `ProductConfig`, approval block, batch dict, document metadata |
| Nothing | HTTP POST with JSON body |
| Nothing | DOCX bytes in response (or DB id for download endpoints) |

The gap is **large**: mapper + HTTP client + file persistence (`file_attachments`) all unbuilt.

---

## 8. SOP-on-SOP Readiness

**QA 01-01 (SOP-on-SOP)** defines document styling: fonts, headers, margins, signature blocks, watermarks.

| Aspect | Current state |
|--------|---------------|
| Global style rules | Hardcoded in `config.py`, `styles.py`, layout modules — approximates Annexure-I |
| SOP document content | `config/products/sop_on_sop.json` drives SOP **body content** via `sop_sections` |
| Extracted SOP rules as data | **Not present** — would need new config artifact |
| Watermarks | **Not implemented** |
| Signature blocks in header/footer | **Implemented** in `header_footer.py` (prepared/checked/approved table) |
| Pluggable theme | **Not implemented** |

**Assessment:** Substantial **layout and styling code exists** and was built against reference DOCXs, but it is **not SOP-extractable** today. SOP extraction work must produce a machine-readable rule set and a **new config layer** before rules can flow in without Python edits. The `sop_on_sop.json` pattern covers **product content**, not **global QA 01-01 styling rules**.

---

## 9. Gaps & Integration Assessment

### (a) Works today

- Programmatic **styled** DOCX for MOA, Protocol, Specification, SOP
- Annexure DOCX via docxtpl (partially styled)
- PDF conversion via LibreOffice (when DOCX exists and `soffice` available)
- `POST /generate` inline integration endpoint with well-defined Pydantic schema
- Product/batch CRUD, JSON product import
- Acceptance-criteria validation API
- Unit tests for four programmatic document types

### (b) Stub / incomplete

- API Gateway `renderDocuments()` — log + audit only
- `generateCoaPdf()` — no-op
- `GET /documents/{id}` and `/download` — broken import (`app.repositories.document` missing)
- Annexure — no automated test; less reference fidelity than programmatic types
- No Docker/deployment packaging

### (c) Missing entirely (needed for Epic 21)

- AWS and COA document types, layouts, and Pydantic schemas
- `mapToSopConfig` mapper (gateway)
- HTTP client / `sop-client` (gateway)
- `file_attachments` persistence after render
- External SOP style config layer (DOC-Module)
- Service-to-service auth
- MOA as separate render call from SPEC (gateway currently single `STANDING_SPEC` stub)
- Env config for DOC-Module URL on gateway

### Verdict

**Not ready-to-wire for full Epic 21.** Standing-document rendering (SPEC/MOA/Protocol/SOP) is **substantially built** and produces **styled** DOCX (hardcoded SOP Annexure-I approximation) — further along than a stub, but **not** "renders per extracted QA 01-01 rules" until the style config layer exists.

**Needs substantial building:** AWS/COA layouts and contracts, `mapToSopConfig`, HTTP wiring, `file_attachments`, SOP-extractable style config, broken document GET routes fix, deployment story.

**Natural sequence (INFERRED from Sections 4 and 5):**

1. **SOP extraction** → machine-readable style spec → config layer in DOC-Module (feeds Section 5 seam)
2. **`mapToSopConfig`** + contract design for AWS/COA (feeds Section 4)
3. **HTTP wiring** (`sop-client`, `renderDocuments` implementation, `file_attachments`)
4. **AWS/COA layouts** in DOC-Module
5. **Proof discipline:** call endpoint → receive valid DOCX/PDF → verify content and SOP styling (not "compiles")

---

## Verification Checklist

| # | Check | Result |
|---|-------|--------|
| 1 | Only `AUDIT_DocModule.md` created | **PASS** (this file only) |
| 2 | Every endpoint state (working/stub/broken/missing) reported | **PASS** — Section 2 |
| 3 | Real-render capability per type (styled/unstyled/stub/missing) | **PASS** — Section 3 table |
| 4 | Input payload schema documented for SPEC/MOA/AWS/COA mapping | **PASS** — Section 4 |
| 5 | Styling seam for SOP rules assessed | **PASS** — Section 5 |
| 6 | Backend `sop-client` / `mapToSopConfig` stub state confirmed | **PASS** — absent; `renderDocuments` stub — Section 7 |
| 7 | Verdict: ready-to-wire vs needs-building | **PASS** — needs-building (standing docs partially ready) — Section 9 |

---

*End of audit. Source: code inspection only; items marked INFERRED are not directly proven by runtime execution in this audit.*
