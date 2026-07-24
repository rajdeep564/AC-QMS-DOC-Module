from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.constants import DocumentStatus, DocumentType
from app.document_engine.renderer import DocumentRenderer
from app.models.document import Document
from app.repositories.product import ProductRepository
from app.schemas.document import DocumentGenerateRequest
from app.services.pdf_service import PDFService


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_record(
        self,
        *,
        product_id: int,
        document_type: DocumentType,
        document_no: str,
        revision_no: str,
        subject: str | None,
        department: str,
        effective_date: date | None,
        review_date: date | None,
        superseded_revision: str | None,
        batch_id: int | None = None,
        context_json: str | None = None,
        docx_path: str | None = None,
        pdf_path: str | None = None,
    ) -> Document:
        doc = Document(
            product_id=product_id,
            batch_id=batch_id,
            document_type=document_type.value,
            document_no=document_no,
            revision_no=revision_no,
            subject=subject,
            department=department,
            effective_date=effective_date,
            review_date=review_date,
            superseded_revision=superseded_revision,
            status=DocumentStatus.GENERATED.value,
            context_json=context_json,
            docx_path=docx_path,
            pdf_path=pdf_path,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, document_id: int) -> Document | None:
        return self.db.get(Document, document_id)


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_repo = ProductRepository(db)
        self.doc_repo = DocumentRepository(db)
        self.renderer = DocumentRenderer()
        self.pdf_service = PDFService()

    def generate(
        self,
        document_type: DocumentType,
        request: DocumentGenerateRequest,
    ) -> Document:
        product = self.product_repo.get_by_id(request.product_id)
        if not product:
            raise ValueError(f"Product not found: {request.product_id}")

        product_config = self.product_repo.get_config(product)
        batch_data: dict | None = None

        if request.batch_id:
            from app.repositories.batch import BatchRepository

            batch = BatchRepository(self.db).get_by_id(request.batch_id)
            if batch:
                batch_data = {
                    "batch_no": batch.batch_no,
                    "mfg_date": batch.mfg_date,
                    "exp_date": batch.exp_date,
                    "batch_size": batch.batch_size,
                    "ar_no": batch.ar_no,
                }

        approval = request.approval.model_dump()
        revision_history = [r.model_dump() for r in request.revision_history]

        context_kwargs = {
            "document_no": request.document_no,
            "revision_no": request.revision_no,
            "subject": request.subject or product.product_name,
            "department": request.department,
            "effective_date": request.effective_date,
            "review_date": request.review_date,
            "superseded_revision": request.superseded_revision,
            "approval": approval,
            "revision_history": revision_history,
            "batch": batch_data,
            "extra_context": request.extra_context,
        }

        from app.document_engine.context_builder import build_document_context

        context = build_document_context(
            product_config, document_type, **context_kwargs
        )

        doc_no = context["document_no"]
        filename = f"{document_type.value}_{product.product_code}_{doc_no.replace('/', '_')}.docx"

        output_path = self.renderer.render(
            document_type,
            product_config,
            filename,
            **context_kwargs,
        )

        return self.doc_repo.create_record(
            product_id=product.id,
            batch_id=request.batch_id,
            document_type=document_type,
            document_no=doc_no,
            revision_no=request.revision_no,
            subject=context.get("subject"),
            department=request.department,
            effective_date=request.effective_date,
            review_date=request.review_date,
            superseded_revision=request.superseded_revision,
            context_json=json.dumps(context, default=str),
            docx_path=str(output_path),
        )

    def generate_pdf(self, document_id: int) -> Document:
        doc = self.doc_repo.get_by_id(document_id)
        if not doc or not doc.docx_path:
            raise ValueError("Document or DOCX path not found")

        pdf_path = self.pdf_service.generate_pdf(
            Path(doc.docx_path),
            Path(doc.docx_path).with_suffix(".pdf"),
        )
        doc.pdf_path = str(pdf_path)
        self.db.commit()
        self.db.refresh(doc)
        return doc
