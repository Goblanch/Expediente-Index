import datetime
from pathlib import Path
from typing import List

# ---- DOCX ----
def export_docx(titles: List[str], out_path: Path) -> None:
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    h = doc.add_paragraph()
    run = h.add_run("Índice de Documentos")
    run.bold = True
    run.font.size = Pt(18)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER

    date_p = doc.add_paragraph()
    date_run = date_p.add_run(datetime.date.today().strftime("%d/%m/%Y"))
    date_run.italic = True
    date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    for t in titles:
        para = doc.add_paragraph(f"- {t}")
        para.paragraph_format.space_after = Pt(4)

    doc.save(out_path)
