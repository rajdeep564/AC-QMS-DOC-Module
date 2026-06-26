"""PDF generation via LibreOffice headless — swappable service layer."""

import logging
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class PDFConverter(ABC):
    @abstractmethod
    def convert(self, docx_path: Path, pdf_path: Path | None = None) -> Path:
        pass


class LibreOfficePDFConverter(PDFConverter):
    def __init__(self, libreoffice_path: str | None = None, timeout: int | None = None) -> None:
        settings = get_settings()
        self.libreoffice_path = libreoffice_path or settings.libreoffice_path
        self.timeout = timeout or settings.pdf_timeout_seconds

    def convert(self, docx_path: Path, pdf_path: Path | None = None) -> Path:
        docx_path = Path(docx_path).resolve()
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX not found: {docx_path}")

        output_dir = docx_path.parent
        if pdf_path is None:
            pdf_path = output_dir / f"{docx_path.stem}.pdf"
        else:
            pdf_path = Path(pdf_path).resolve()

        soffice = self._resolve_soffice()
        cmd = [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(docx_path),
        ]

        logger.info("Running PDF conversion: %s", " ".join(cmd))
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice conversion failed (code {result.returncode}): "
                f"{result.stderr or result.stdout}"
            )

        generated = output_dir / f"{docx_path.stem}.pdf"
        if not generated.exists():
            raise RuntimeError("PDF was not created by LibreOffice")

        if generated != pdf_path:
            shutil.move(str(generated), str(pdf_path))

        return pdf_path

    def _resolve_soffice(self) -> str:
        if Path(self.libreoffice_path).exists():
            return self.libreoffice_path

        candidates = [
            "soffice",
            "libreoffice",
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for candidate in candidates:
            resolved = shutil.which(candidate) or (
                candidate if Path(candidate).exists() else None
            )
            if resolved:
                return resolved

        raise FileNotFoundError(
            "LibreOffice not found. Install LibreOffice or set LIBREOFFICE_PATH."
        )


class PDFService:
    """Facade for PDF generation — replace converter implementation as needed."""

    def __init__(self, converter: PDFConverter | None = None) -> None:
        self.converter = converter or LibreOfficePDFConverter()

    def generate_pdf(self, docx_path: Path, pdf_path: Path | None = None) -> Path:
        return self.converter.convert(docx_path, pdf_path)
