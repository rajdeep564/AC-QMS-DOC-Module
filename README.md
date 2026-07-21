# AC-QMS-DOC-Module

Pharmaceutical QMS document generation platform — reusable Python FastAPI service that renders SPEC, MOA, AWS, and COA (DOCX/PDF) for the AC-QMS API Gateway.

**Audits:** [docs/audits/](docs/audits/)  
**Gateway contract:** see [`AC-QMS-API-Gateway/SOP_CONTRACT.md`](../AC-QMS-API-Gateway/SOP_CONTRACT.md)

## Features

- **Document types**: MOA, Analysis Protocol, SOP, Annexure, Product Specification, AWS, COA
- **Product-agnostic**: One set of base templates (`base_moa.docx`, `base_protocol.docx`, etc.)
- **JSON-driven**: Products, tests, acceptance criteria, and SOP sections from configuration
- **SOP-compliant layout**: A4, Times New Roman 12pt, 1" margins, page borders, universal header/footer
- **Auto section numbering**: 1.0 → 1.1 → 1.1.1 → 2.0
- **Validation engine**: PASS/FAIL from machine-readable acceptance criteria
- **PDF export**: DOCX → LibreOffice headless → PDF (swappable service layer)
- **FastAPI REST API**: Stateless `/generate`, `/render`, `/convert/pdf` for the Gateway; optional product/batch DB routes

---

## How to run

### Prerequisites

- **Python 3.11–3.13** (not 3.15 beta — many packages lack wheels)
- Optional: [LibreOffice](https://www.libreoffice.org/) for PDF conversion
- For full AC-QMS stack: API Gateway on `:4000` with matching `DOC_MODULE_API_KEY`

### 1. Open this repo

Work from the **module root** (`AC-QMS-DOC-Module/`), not a nested `sop/` folder.

```bash
cd AC-QMS-DOC-Module
```

### 2. Create a virtualenv and install dependencies

**Windows (PowerShell):**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For PostgreSQL instead of the default SQLite DB:

```bash
pip install -r requirements-postgres.txt
```

### 3. Configure environment

```powershell
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `.env` as needed:

| Variable | Purpose |
|----------|---------|
| `API_KEY` | Shared secret; Gateway sends it as `X-API-Key`. Must match Gateway `DOC_MODULE_API_KEY` |
| `LIBREOFFICE_PATH` | Path to `soffice` if PDF conversion is required |
| `DATABASE_URL` | Optional Postgres URL; omit to use local SQLite |

Example (dev, matches Gateway `.env.example`):

```
API_KEY=change-me-shared-secret
DEBUG=true
# LIBREOFFICE_PATH=C:\Program Files\LibreOffice\program\soffice.exe
```

### 4. (First time) Build templates and seed local DB

Only needed once (or after template changes):

```bash
python scripts/build_templates.py
python scripts/init_db.py
```

Optional smoke generate into `generated/`:

```bash
python scripts/generate_example.py
```

### 5. Start the API server

From the module root, with the venv **activated**:

```bash
uvicorn app.main:app --reload --app-dir . --host 127.0.0.1 --port 8000
```

You should see uvicorn listening on **http://127.0.0.1:8000**.

### 6. Verify it is up

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{ "status": "ok", "app": "Pharmaceutical QMS Document Platform" }
```

- Swagger UI: http://127.0.0.1:8000/docs  
- Routes used by the Gateway (`/generate`, `/render`, `/convert/pdf`) require header: `X-API-Key: <API_KEY>`

### Run alongside the API Gateway

1. Start this DOC-Module on **:8000** (steps above).
2. In `AC-QMS-API-Gateway/.env` set:

```
DOC_MODULE_URL=http://localhost:8000
DOC_MODULE_API_KEY=change-me-shared-secret
```

(`DOC_MODULE_API_KEY` must equal this service’s `API_KEY`.)

3. Start the Gateway (`npm run dev` in `AC-QMS-API-Gateway`). SPEC/MOA/AWS/COA renders will call this service.

If LibreOffice is not installed, set Gateway `DOC_MODULE_PDF_OPTIONAL=true` so DOCX-only success is accepted.

---

## Quick Start (short)

```powershell
cd AC-QMS-DOC-Module
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python scripts/build_templates.py
python scripts/init_db.py
uvicorn app.main:app --reload --app-dir . --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs for Swagger UI.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness (no auth) |
| POST | `/generate` | Inline SPEC/MOA/… generate (Gateway; requires `X-API-Key`) |
| POST | `/render` | Batch AWS/COA render (Gateway; requires `X-API-Key`) |
| POST | `/convert/pdf` | DOCX → PDF (Gateway; requires `X-API-Key`) |
| POST | `/products` | Create product from JSON body |
| POST | `/products/import` | Import product JSON file |
| GET | `/products` | List products |
| POST | `/batches` | Create batch record |
| POST | `/moa/generate` | Generate MOA document (DB-backed) |
| POST | `/protocols/generate` | Generate Analysis Protocol |
| POST | `/sop/generate` | Generate SOP |
| POST | `/annexure/generate` | Generate Annexure |
| GET | `/documents/{id}` | Get document metadata |
| GET | `/documents/{id}/download` | Download DOCX |
| GET | `/documents/{id}/pdf` | Generate/download PDF |
| POST | `/validation/results` | Validate test results |

## Adding a New Product

Create `config/products/my_product.json`:

```json
{
  "product_code": "FG00099",
  "product_name": "My New Product",
  "reference": "IP",
  "tests": [
    {
      "name": "pH",
      "procedure": "Measure using calibrated pH meter.",
      "acceptance_criteria": { "type": "range", "min": 5.0, "max": 7.0 }
    }
  ]
}
```

Import via API or run `python scripts/init_db.py`.

## Acceptance Criteria Types

| Type | Example | Validation |
|------|---------|------------|
| `range` | `{"type":"range","min":5.9,"max":6.3}` | Numeric in range |
| `nmt` / `max` | `{"type":"nmt","value":10,"unit":"ppm"}` | Not more than |
| `nlt` / `min` | `{"type":"nlt","value":98.5,"unit":"%"}` | Not less than |
| `equals` | `{"type":"equals","value":"White powder"}` | Exact text match |
| `text` | `{"type":"text","value":"..."}` | Descriptive |

## PDF Generation

Requires [LibreOffice](https://www.libreoffice.org/) installed. Set path in `.env`:

```
LIBREOFFICE_PATH=C:\Program Files\LibreOffice\program\soffice.exe
```

## Project Structure

See [ARCHITECTURE.md](ARCHITECTURE.md) for full design documentation.

## Reference Documents

Layout and standards derived from:

- `QA 01 SOP ON SOP.pdf` — formatting, header/footer, numbering
- `MOA Glycine IP.docx` — MOA structure and test layout
- `GLYCINE IP.docx` — Analysis Protocol structure

Glycine is used only as an **example configuration**, not as hardcoded logic.
