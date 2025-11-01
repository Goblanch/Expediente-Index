from pathlib import Path
from expedienteindex.indexing import list_pdf_titles

def test_list_pdf_titles_empty(tmp_path: Path):
    titles, files = list_pdf_titles(tmp_path)
    assert titles == []
    assert files == []

def test_list_pdf_titles_ignores_non_pdf_and_sorts(tmp_path: Path):
    # Create some test files
    (tmp_path / "Zeta.PDF").write_bytes(b"%PDF-1.4\n%EOF")
    (tmp_path / "alfa.pdf").write_bytes(b"%PDF-1.4\n%EOF")
    (tmp_path / "Readme.txt").write_text("no soy pdf")
    (tmp_path / "bravo.PdF").write_bytes(b"%PDF-1.4\n%EOF")

    titles, files = list_pdf_titles(tmp_path)
    # Should ignore .txt and sort alfa, bravo, zeta (case insensitive)
    assert titles == ["alfa", "bravo", "Zeta"]
    assert [p.name for p in files] == ["alfa.pdf", "bravo.PdF", "Zeta.PDF"]