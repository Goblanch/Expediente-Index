import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from collections import Counter

try:
    import ttkbootstrap as tb
    USING_TTKB = True
    from ttkbootstrap import PRIMARY, SUCCESS, INFO
except Exception:
    import tkinter.ttk as tb
    USING_TTKB = False
    PRIMATY = "primary"; SUCCESS = "success"; INFO = "info"

from .nav import back_to_launcher
from ..nlp.ner import NEREngine

SUPPORTED = {".pdf", ".docx"}

class AutoCensorView:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Autocensura - Detección (spaCy + regex)")
        self.file_path = tk.StringVar()
        self.case_sensitive = tk.BooleanVar(value=False)

        # Entidades activables. Por defecto: PERSON, ORG, ID, EMAIL, PHONE
        self.labels = [
            "PERSON", "ORG", "LOC", "GPE", "MISC", "DATE", "TIME", "NORP",
            "CARDINAL", "QUANTITY", "ORDINAL", "LAW", "EMAIL", "PHONE", "ID_NUMBER"
        ]
        self.label_vars = {
            lbl: tk.BooleanVar(value=lbl in {"PERSON", "ORG", "ID_NUMBER", "EMAIL", "PHONE"})
            for lbl in self.labels
        }

        self.ner = NEREngine(lang="es", prefer_small=False)
        self.detected = []
        self.ignored = set()
        self.manual_terms = set()

        self._build_ui()

    def _build_ui(self):
        # Backbar
        bar = tb.Frame(self.root, padding=(10, 6)); bar.pack(fill="x")
        tb.Button(bar, text="← Back", command=lambda: back_to_launcher(self.root)).pack(side="left")

        frm = tb.Frame(self.root, padding=15); frm.pack(fill="both", expand=True)

        title = tb.Label(frm, text="Autocensura", font=("", 16, "bold"))
        title.pack(anchor="w", pady=(0, 8))

        # Selector de archivo
        row = tb.Frame(frm); row.pack(fill="x", pady=(0, 8))
        tb.Label(row, text="Documento (PDF/DOCX):").pack(side="left")
        tb.Entry(row, textvariable=self.file_path).pack(side="left", fill="x", expand=True, padx=8)
        tb.Button(row, text="Elegir...", command=self.choose_file, bootstyle=PRIMARY if USING_TTKB else None).pack(side="left")

        # Filtro de entidades
        ent_box = tb.Labelframe(frm, text="Entidades a detectar", padding=8); ent_box.pack(fill="x", pady=8)
        wrap = tb.Frame(ent_box); wrap.pack(fill="x")
        for i, lbl in enumerate(self.labels):
            tb.Checkbutton(
                wrap, text=lbl, variable=self.label_vars[lbl],
                bootstyle= SUCCESS if USING_TTKB else None
            ).grid(row=i//5, column=i%5, sticky="w", padx=8, pady=4)

        # Añadir manualmente
        add_row = tb.Frame(ent_box); add_row.pack(fill="x", pady=(8, 0))
        self.manual_text = tk.StringVar()
        tb.Entry(add_row, textvariable=self.manual_text, width=40).pack(side="left")
        tb.Checkbutton(add_row, text="Case sensitive", variable=self.case_sensitive).pack(side="left", padx=8)
        tb.Button(add_row, text="Añadir término", command=self.add_manual).pack(side="left")

        # Lista y conteos
        list_box = tb.Labelframe(frm, text="Términos detectados (agrupados)", padding=8)
        list_box.pack(fill="both", expand=True, pady=8)
        inner = tb.Frame(list_box); inner.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(inner, height=14)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(inner, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # Acciones
        actions = tb.Frame(frm); actions.pack(fill="x", pady=(10, 0))
        tb.Button(actions, text="Analilzar", command=self.analyze, bootstyle=INFO if USING_TTKB else None).pack(side="left")
        tb.Button(actions, text="Ignorar seleccionado", command=self.ignore_selected).pack(side="left", padx=8)
        tb.Button(actions, text="Limpiar ignorados", command=self.clear_ignored).pack(side="left")

        # Estado
        self.status = tb.Label(frm, text="Listo.", anchor="w"); self.status.pack(fill="x", pady=(8, 0))

    # -------- EVENTOS --------
    def choose_file(self):
        p = filedialog.askopenfilename(filetypes=[("Documentos", "*.pdf;*.docx")])
        if p:
            self.file_path.set(p)

    def analyze(self):
        path = Path(self.file_path.get().strip())
        if not path.exists or path.suffix.lower() not in SUPPORTED:
            messagebox.showwarning("Archivo inválido", "Selecciona un PDF o un DOCX")
            return

        text = self._read_text(path)
        if not text.strip():
            messagebox.showinfo("Sin texto", "No se pudo extraer todo el texto del documento.")
            return
        
        try:
            ents = self.ner.detect(text, use_regex=True, include_email_phone=True)
        except RuntimeError as e:
            messagebox.showerror("NLP no disponible", str(e))
            return
        except Exception as e:
            messagebox.showerror("Error NER", str(e))
            return

        # Filtrar por etiquetas activas
        active = {k for k, v in self.label_vars.items() if v.get()}
        ents = [e for e in ents if e.label in active]

        # Inyectar términos manuales como entidades MISC para controlarlas
        for term in sorted(self.manual_terms):
            from ..nlp.ner import DetectedEntity
            ents.append(DetectedEntity(text=term, start=-1, end=-1, label="MISC", source="manual"))

        self.detected = ents
        self._refresh_counts()
        self.status.config(text=f"Detectadas {len(ents)} entidades (antes de agrupar)")

    def ignore_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        item = self.listbox.get(sel[0])
        term = item.rsplit(" (x", 1)[0]
        norm = term if self.case_sensitive.get() else term.lower()
        self.ignored.add(norm)
        self._refresh_counts()

    def clear_ignored(self):
        self.ignored.clear()
        self._refresh_counts()

    def add_manual(self):
        term = (self.manual_text.get() or "").strip()
        if not term:
            return

        self.manual_terms.add(term)
        norm = term if self.case_sensitive.get() else term.lower()
        self.ignored.discard(norm)
        self._refresh_counts()

    # -------- HELPERS --------
    def _read_text(self, path: Path) -> str:
        if path.suffix.lower() == ".docx":
            try:
                from docx import Document
            except Exception:
                messagebox.showerror("Falta dependencia", "Instala python-docx para leer DOCX: pip install python-docx")
                return ""

            d = Document(str(path))
            return "\n".join(p.text for p in d.paragraphs)
        elif path.suffix.lower() == ".pdf":
            try:
                import pdfplumber
            except Exception:
                messagebox.showerror("Falta dependencia", "Instala pdfplumber para leer PDF: pip install pdfplumber")
                return ""
            
            out = []
            with pdfplumber.open(str(path)) as pdf:
                for pg in pdf.pages:
                    out.append(pg.extract_text() or "")
            
            return "\n".join(out)
        return ""

    def _refresh_counts(self):
        self.listbox.delete(0, tk.END)
        cs = self.case_sensitive.get()
        norm = (lambda s: s) if cs else (lambda s: s.lower())
        # Agrupar por término normalizado y excluir ignorados
        counts = Counter(norm(e.text) for e in self.detected if norm(e.text) not in self.ignored)
        for key, n in counts.most_common():
            self.listbox.insert(tk.END, f"{key} (x{n})")