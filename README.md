# AC-QMS-DOC-Module

Pharmaceutical QMS document generation platform — reusable Python service for generating MOA, protocols, SOPs, annexures, and product specifications from JSON configuration.

## Features

- **Document types**: MOA, Analysis Protocol, SOP, Annexure, Product Specification
- **Product-agnostic**: One set of base templates (`base_moa.docx`, `base_protocol.docx`, etc.)
- **JSON-driven**: Products, tests, acceptance criteria, and SOP sections from configuration
- **SOP-compliant layout**: A4, Times New Roman 12pt, 1" margins, page borders, universal header/footer
- **Auto section numbering**: 1.0 → 1.1 → 1.1.1 → 2.0
- **Validation engine**: PASS/FAIL from machine-readable acceptance criteria
- **PDF export**: DOCX → LibreOffice headless → PDF (swappable service layer)
- **FastAPI REST API**: Product import, batch tracking, document generation

## Quick Start

### 1. Install dependencies

**Requires Python 3.12 or 3.13** (not 3.15 beta — many packages lack pre-built wheels).

```bash
cd sop
py -3.13 -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

For PostgreSQL production, also run: `pip install -r requirements-postgres.txt`

### 2. Build base templates

```bash
python scripts/build_templates.py
```

### 3. Initialize database and import products

```bash
python scripts/init_db.py
```

### 4. Generate example documents

```bash
python scripts/generate_example.py
```

Output appears in `generated/`.

### 5. Start API server

```bash
uvicorn app.main:app --reload --app-dir .
```

Open http://127.0.0.1:8000/docs for Swagger UI.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products` | Create product from JSON body |
| POST | `/products/import` | Import product JSON file |
| GET | `/products` | List products |
| POST | `/batches` | Create batch record |
| POST | `/moa/generate` | Generate MOA document |
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
