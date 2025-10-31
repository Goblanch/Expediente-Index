from pathlib import Path
from typing import List, Tuple

def list_pdf_titles(directory: Path) -> Tuple[List[str], List[Path]]:
    """
    Devuelve una tupla (titles, path) con los títulos (stem) ordenados alfabéticamente
    y la lista de rutas de PDFs.
    """
    pdfs = sorted(
        [p for p in directory.glob("*.pdf") if p.is_file()],
        key=lambda p: p.name.lower()
    )

    return [p.stem for p in pdfs], pdfs