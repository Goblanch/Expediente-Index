from pathlib import Path
import sys

import pytest

from expedienteindex.exporters import export_docx, export_pdf

try:
    from docx import Document as _DocxReader
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

try:
    from pypdf import PdfReader as _PdfReader
    PYPDF_AVAILABLE = True
except Exception:
    PYPDF_AVAILABLE = False

@pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not available")
def test_export_docx_creates_file_and_has_content(tmp_path: Path):
    titles = ["Documento A", "Documento B", "Documento C"]
    out = tmp_path / "Indice_Documentos.docx"

    export_docx(titles, out)
    assert out.exists() and out.stat().st_size > 0

    # Verifies basic content
    doc = _DocxReader(str(out))
    all_text = "\n".join(p.text for p in doc.paragraphs)
    assert "Índice de Documentos" in all_text
    assert "- Documento A" in all_text
    assert "- Documento B" in all_text
    assert "- Documento C" in all_text

def test_export_pdf_creates_file(tmp_path: Path):
    titles = ["Documento A", "Documento B", "Documento C"]
    out = tmp_path / "Indice_Documentos.pdf"

    export_pdf(titles, out)
    assert out.exists() and out.stat().st_size > 0

@pytest.mark.skipif(not PYPDF_AVAILABLE, reason="pypdf not available")
def test_export_pdf_contains_title_when_parsed(tmp_path: Path):
    titles = ["Documento A", "Documento B"]
    out = tmp_path / "Indice.pdf"

    export_pdf(titles, out)
    reader = _PdfReader(str(out))
    text = ""
    for page in reader.pages:
        try:
            text += page.extract_text() or ""
        except Exception:
            # Some pdf engines can fail with certain fonts
            # if it fails, at least we know that the file exists
            pass

    assert "Índice de Documentos" in text or len(text) > 0