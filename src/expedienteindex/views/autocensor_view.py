import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from collections import Counter, defaultdict
import re

try:
    import ttkbootstrap as tb
    USING_TTKB = True
    from ttkbootstrap.constants import PRIMARY, SUCCESS, INFO
except Exception:
    import tkinter.ttk as tb
    USING_TTKB = False
    PRIMARY = "primary"; SUCCESS = "success"; INFO = "info"

from .nav import back_to_launcher
from ..nlp.ner import NEREngine, DetectedEntity

SUPPORTED = {".pdf", ".docx"}

LABEL_NAMES = {
    "PERSON": "Persona",
    "ORG": "Organización",
    "LOC": "Lugar",
    "GPE": "Entidad geopolítica",
    "MISC": "Miscelánea",
    "DATE": "Fecha",
    "TIME": "Hora",
    "NORP": "Grupo/Nacionalidad",
    "CARDINAL": "Número (cardinal)",
    "QUANTITY": "Cantidad",
    "ORDINAL": "Ordinal",
    "LAW": "Referencia legal",
    "EMAIL": "Correo electrónico",
    "PHONE": "Teléfono",
    "ID_NUMBER": "Documento ID"
}

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
        self.detected: list[DetectedEntity] = []
        self.ignored: set[str] = set()
        self.manual_terms: list[str] = []

        self._last_text: str = ""

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
            nice = LABEL_NAMES.get(lbl, lbl)
            tb.Checkbutton(
                wrap, text=f"{nice}", variable=self.label_vars[lbl],
                bootstyle= SUCCESS if USING_TTKB else None
            ).grid(row=i//5, column=i%5, sticky="w", padx=8, pady=4)

        # Añadir manualmente
        add_row = tb.Frame(ent_box); add_row.pack(fill="x", pady=(8, 0))
        self.manual_text = tk.StringVar()
        tb.Entry(add_row, textvariable=self.manual_text, width=40).pack(side="left")
        tb.Checkbutton(add_row, text="Case sensitive", variable=self.case_sensitive).pack(side="left", padx=8)
        tb.Button(add_row, text="Añadir término", command=self.add_manual).pack(side="left")

        # Lista de términos añadidos manualmente
        manual_box = tb.Labelframe(frm, text="Textos añadidos", padding=8)
        manual_box.pack(fill="x", pady=(8, 4))
        mwrap = tb.Frame(manual_box); mwrap.pack(fill="x")
        self.manual_listbox = tk.Listbox(mwrap, height=5)
        self.manual_listbox.pack(side="left", fill="x", expand=True)
        m_sb = tk.Scrollbar(mwrap, command=self.manual_listbox.yview)
        self.manual_listbox.configure(yscrollcommand=m_sb.set)
        m_sb.pack(side="left", fill="y")
        tb.Button(manual_box, text="Eliminar seleccionado", command=self.remove_manual).pack(anchor="e", pady=(6, 0))

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
        tb.Button(actions, text="Analizar", command=self.analyze, bootstyle=INFO if USING_TTKB else None).pack(side="left")
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
        if not path.exists() or path.suffix.lower() not in SUPPORTED:
            messagebox.showwarning("Archivo inválido", "Selecciona un PDF o un DOCX")
            return

        text = self._read_text(path)
        if not text.strip():
            messagebox.showinfo("Sin texto", "No se pudo extraer todo el texto del documento.")
            return

        self._last_text = text
        
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

        ents.extend(self._manual_matches_as_entities(text))

        self.detected = ents
        self._refresh_counts()
        self.status.config(text=f"Detectadas {len(ents)} entidades (antes de agrupar)")

    def ignore_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        item = self.listbox.get(sel[0])
        term = item.split(" — ", 1)[0].strip()
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
        # Evitar duplicados exactos
        if term not in self.manual_terms:
            self.manual_terms.append(term)
            self.manual_listbox.insert(tk.END, term)
        self.manual_text.set("")
        if self._last_text:
            self._refresh_after_manual_update()

    def remove_manual(self):
        sel = self.manual_listbox.curselection()
        if not sel:
            return
        term = self.manual_listbox.get(sel[0])
        try:
            self.manual_terms.remove(term)
        except ValueError:
            pass
        self.manual_listbox.delete(sel[0])
        if self._last_text:
            self._refresh_after_manual_update()

    # -------- HELPERS --------
    def _refresh_after_manual_update(self):
        try:
            ents = self.ner.detect(self._last_text, use_regex=True, include_email_phone=True)
            active = {k for k, v in self.label_vars.items() if v.get()}
            ents = [e for e in ents if e.label in active]
            ents.extend(self._manual_matches_as_entities(self._last_text))
            self.detected = ents
            self._refresh_counts()
        except Exception:
            # si algo falla, sólo refresca la lista agrupada con lo que hubiera
            self._refresh_counts()

    def _manual_matches_as_entities(self, text: str) -> list[DetectedEntity]:
        """Devuelve entidades MISC creadas a partir de *todas* las coincidencias en el texto
        para cada término manual. Respeta Case sensitive."""
        if not self.manual_terms:
            return []
        flags = 0 if self.case_sensitive.get() else re.IGNORECASE
        out: list[DetectedEntity] = []
        for term in self.manual_terms:
            if not term:
                continue
            try:
                pat = re.compile(re.escape(term), flags)
            except re.error:
                # por si meten algo raro, saltar ese término
                continue
            for m in pat.finditer(text):
                # Usamos el texto tal cual aparece en el documento (casing real)
                out.append(DetectedEntity(text=m.group(0), start=m.start(), end=m.end(),
                                          label="MISC", source="manual"))
        return out

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
        norm_fn = (lambda s: s) if cs else (lambda s: s.lower())

        counts: Counter[str] = Counter()
        display_by_norm: dict[str, str] = {}
        label_by_norm: dict[str, str] = {}

        for e in self.detected:
            key = norm_fn(e.text)
            if key in self.ignored:
                continue
            counts[key] += 1
            display_by_norm.setdefault(key, e.text)   # muestra el primer casing visto
            label_by_norm.setdefault(key, e.label)

        for key, n in counts.most_common():
            display = display_by_norm.get(key, key)
            tech = label_by_norm.get(key, "")
            nice = LABEL_NAMES.get(tech, tech) if tech else ""
            # usa siempre “ — ” como separador
            if nice:
                self.listbox.insert(tk.END, f"{display} — {nice} (x{n})")
            else:
                self.listbox.insert(tk.END, f"{display} (x{n})")