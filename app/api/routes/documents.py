import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.core.constants import DocumentType
from app.database.session import get_db
from app.schemas.document import DocumentGenerateRequest, DocumentResponse, InlineGenerateRequest
from app.schemas.render_request import InlineAwsRenderRequest, InlineCoaRenderRequest, RenderRequest
from app.services.document_service import DocumentService
from app.services.pdf_service import PDFService

router = APIRouter(tags=["documents"], dependencies=[Depends(verify_api_key)])

_DOC_TYPE_MAP = {
    "moa": DocumentType.MOA,
    "protocol": DocumentType.PROTOCOL,
    "specification": DocumentType.SPECIFICATION,
    "sop": DocumentType.SOP,
    "annexure": DocumentType.ANNEXURE,
}


def _generate(document_type: DocumentType, request: DocumentGenerateRequest, db: Session):
    try:
        return DocumentService(db).generate(document_type, request)
    except FileNotFoundError as e:
        raise HTTPException(500, str(e)) from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


# ── DB-backed generate endpoints (product must exist in DB first) ─────────────

@router.post("/moa/generate", response_model=DocumentResponse, status_code=201)
def generate_moa(request: DocumentGenerateRequest, db: Session = Depends(get_db)):
    return _generate(DocumentType.MOA, request, db)


@router.post("/protocols/generate", response_model=DocumentResponse, status_code=201)
def generate_protocol(request: DocumentGenerateRequest, db: Session = Depends(get_db)):
    return _generate(DocumentType.PROTOCOL, request, db)


@router.post("/specification/generate", response_model=DocumentResponse, status_code=201)
def generate_specification(request: DocumentGenerateRequest, db: Session = Depends(get_db)):
    return _generate(DocumentType.SPECIFICATION, request, db)


@router.post("/sop/generate", response_model=DocumentResponse, status_code=201)
def generate_sop(request: DocumentGenerateRequest, db: Session = Depends(get_db)):
    return _generate(DocumentType.SOP, request, db)


@router.post("/annexure/generate", response_model=DocumentResponse, status_code=201)
def generate_annexure(request: DocumentGenerateRequest, db: Session = Depends(get_db)):
    return _generate(DocumentType.ANNEXURE, request, db)


# ── Inline generate endpoint (pass product data directly, returns .docx) ──────

@router.post("/generate", summary="Generate document from inline product data")
def generate_inline(request: InlineGenerateRequest):
    """
    Generate a .docx document directly from product data.

    Your main app calls this endpoint with the full product config and
    document parameters — no prior product registration in this service needed.
    Returns the .docx file as a direct download.

    Example request body:
    {
      "document_type": "moa",
      "product": {
        "product_code": "FG00038",
        "product_name": "Glycine IP",
        "chemical_formula": "C2H5NO2",
        "molecular_weight": "75.03",
        "reference": "IP",
        "specification_no": "SPEC/FG00038/01",
        "moa_no": "MOA/FG00038/01",
        "tests": [ ... ]
      },
      "revision_no": "01",
      "effective_date": "2025-05-21",
      "review_date": "2028-05-20",
      "superseded_revision": "New",
      "approval": {
        "prepared_by": {"name": "...", "designation": "QA Executive"},
        "checked_by":  {"name": "...", "designation": "QA Executive"},
        "approved_by": {"name": "...", "designation": "QA Head"}
      }
    }
    """
    from app.document_engine.context_builder import build_document_context
    from app.document_engine.renderer import DocumentRenderer

    doc_type = _DOC_TYPE_MAP.get(request.document_type)
    if not doc_type:
        raise HTTPException(400, f"Unknown document_type: {request.document_type}")

    context_kwargs = {
        "document_no": request.document_no,
        "revision_no": request.revision_no,
        "subject": request.subject,
        "department": request.department,
        "effective_date": request.effective_date,
        "review_date": request.review_date,
        "superseded_revision": request.superseded_revision,
        "approval": request.approval.model_dump(),
        "revision_history": [r.model_dump() for r in request.revision_history],
        "batch": request.batch,
        "extra_context": request.extra_context,
    }

    renderer = DocumentRenderer()
    product_code = request.product.product_code
    filename = f"{request.document_type}_{product_code}_{request.revision_no}.docx"

    try:
        output_path = renderer.render(doc_type, request.product, filename, **context_kwargs)
    except Exception as e:
        raise HTTPException(500, str(e)) from e

    return FileResponse(
        str(output_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


@router.post("/render", summary="Render batch document from render-ready payload")
def render_document(request: RenderRequest):
    """
    Discriminated render endpoint for batch documents (COA, future AWS).

    Standing documents continue to use POST /generate with ProductConfig.
    Malformed payloads return HTTP 422 from Pydantic validation.
    """
    from app.document_engine.renderer import DocumentRenderer

    if isinstance(request, InlineCoaRenderRequest):
        payload = request.payload
        filename = f"coa_{payload.batch.batch_no.replace('/', '_')}_{payload.revision_no}.docx"
        try:
            output_path = DocumentRenderer().render_coa(payload, filename)
        except Exception as e:
            raise HTTPException(500, str(e)) from e
        return FileResponse(
            str(output_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
        )

    if isinstance(request, InlineAwsRenderRequest):
        payload = request.payload
        filename = f"aws_{payload.batch.batch_no.replace('/', '_')}_{payload.revision_no}.docx"
        try:
            output_path = DocumentRenderer().render_aws(payload, filename)
        except Exception as e:
            raise HTTPException(500, str(e)) from e
        return FileResponse(
            str(output_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
        )

    raise HTTPException(400, f"Unsupported document_type: {request.document_type}")


# ── Inline DOCX → PDF (no DB document row required) ───────────────────────────

@router.post("/convert/pdf", summary="Convert an uploaded DOCX to PDF via LibreOffice")
async def convert_docx_to_pdf(file: UploadFile = File(...)):
    """
    Accept a .docx upload and return PDF bytes.
    Used by the API Gateway after POST /generate or POST /render (Epic 21).
    Requires LibreOffice (soffice) on the host.
    """
    filename = file.filename or "document.docx"
    if not filename.lower().endswith(".docx"):
        raise HTTPException(400, "Only .docx uploads are supported")

    raw = await file.read()
    if not raw:
        raise HTTPException(400, "Empty upload")

    with tempfile.TemporaryDirectory(prefix="acqms-pdf-") as tmp:
        tmp_dir = Path(tmp)
        docx_path = tmp_dir / "input.docx"
        pdf_path = tmp_dir / "output.pdf"
        docx_path.write_bytes(raw)

        try:
            PDFService().generate_pdf(docx_path, pdf_path)
        except FileNotFoundError as e:
            raise HTTPException(500, str(e)) from e
        except RuntimeError as e:
            raise HTTPException(500, str(e)) from e

        if not pdf_path.exists():
            raise HTTPException(500, "PDF was not created")

        pdf_bytes = pdf_path.read_bytes()

    out_name = Path(filename).stem + ".pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )


# ── Document record endpoints ─────────────────────────────────────────────────

@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    from app.repositories.document import DocumentRepository

    doc = DocumentRepository(db).get_by_id(document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/documents/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    from app.repositories.document import DocumentRepository

    doc = DocumentRepository(db).get_by_id(document_id)
    if not doc or not doc.docx_path or not Path(doc.docx_path).exists():
        raise HTTPException(404, "Document file not found")
    return FileResponse(
        doc.docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=Path(doc.docx_path).name,
    )


@router.get("/documents/{document_id}/pdf")
def get_document_pdf(document_id: int, db: Session = Depends(get_db)):
    service = DocumentService(db)
    try:
        doc = service.generate_pdf(document_id)
    except FileNotFoundError as e:
        raise HTTPException(500, str(e)) from e
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e

    if not doc.pdf_path or not Path(doc.pdf_path).exists():
        raise HTTPException(404, "PDF not found")

    return FileResponse(
        doc.pdf_path,
        media_type="application/pdf",
        filename=Path(doc.pdf_path).name,
    )
