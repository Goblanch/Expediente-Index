# Expediente-Index
A small desktop application (Tkinter + ttkbootstrap) that generates a **Document Index** from all **PDF** files in a folder, exporting to **Word (.docx)** and/or **PDF (.pdf)**.

> **Status**: Working MVP on `main`. Upcoming improvements will land on feature branches.  
> **Download**: no public binaries yet; build locally (see Build .exe).  
> **Español?** Ver [README.md](./README.md)

---

## Why does this tool exist?

This idea comes from a real need: **my sister is a lawyer** and told me that when submitting a set of legal documents, an **index** (a first page listing all document names) is often created **manually**. **ExpedienteIndex** automates that step: it takes all the PDFs in a folder and generates a clean index in Word or PDF.

Within the **Spanish judicial system**, it is common to attach an **index** to briefs and supporting documentation in order to make it easier for courts and other parties to review the case file. This tool does not replace any official format nor validate legal content; it simply speeds up the **organization** of the documents submitted.

---

## Features (MVP)

- Select a folder containing **PDF** files.
- Preview titles (filename without extension).
- Export to **Word (.docx)** and/or **PDF (.pdf)**.
- Simple interface built with **Tkinter** and **ttkbootstrap**.

---

## Roadmap (next improvements)

- **Font selector** (from fonts installed on the system).
- **Header options**: show/hide **title** and **date**, **size**, **alignment**, and **editable title**.
- **Default preferences**: Word enabled by default, PDF disabled by default.
- (Future) Custom templates (logo, corporate margins), CLI, and persistent settings.

---

## Installation (from source)

Requirements:
- **Python 3.10+**
- Windows/macOS/Linux

```bash
# Clone
git clone https://github.com/Goblanch/Expediente-Index.git
cd Expediente-Index

# Virtual environment (recommended)
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

# Dependencies
pip install -r requirements.txt

# (Optional) install the package in editable mode
pip install -e .
```

Run the app:
```bash
python -m expedienteindex
```

Tests
```bash
# Test dependencies
pip install pytest pypdf

# Run
pytest -q
```

---

## Project structure

```bash
Expediente-Index/
├─ src/
│  └─ expedienteindex/
│     ├─ __init__.py
│     ├─ __main__.py        # run with: python -m expedienteindex
│     ├─ app.py             # Tkinter UI + ttkbootstrap
│     ├─ indexing.py        # PDF discovery/sorting
│     └─ exporters.py       # export to DOCX/PDF
├─ tests/
│  ├─ test_indexing.py
│  └─ test_exporters.py
├─ entrypoint.py            # PyInstaller entry point
├─ requirements.txt
└─ README.en.md
```

---

## Contributing

Branching:
- `main`: stable
- `feature/<nombre>`: one improvement or bug fix per branch
- (Opcional) `develop`: integration branch before `main`

Commit style (recommended):
- `feat`: new feature.
- `fix`: bug fix.
- `refactor`: internal changes.
- `docs`: documentation.
- `tests`
- `build/chore`: tooling, CI, packaging.

Examples:
```
feat(ui): add header config (title text, show/hide date, sizes, align)
feat(fonts): allow selecting system fonts for title and body
feat(export): apply header options to docx and pdf export
fix(ui): correct ttkbootstrap style typos and list insertion
```