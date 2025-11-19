import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from ..indexing import list_pdf_titles
from ..exporters import export_docx, export_pdf
from .. import __app_name__, __version__

# TODO: añadir selección de fuente con las fuentes del sistema.

# Try modern UI with ttkbootstrap, if not available, use classic ttk
try:
    import ttkbootstrap as tb
    USING_TTKB = True
    from ttkbootstrap.constants import PRIMARY, SUCCESS, INFO
except Exception:
    import tkinter.ttk as tb
    USING_TTKB = False
    PRIMARY = "primary"; SUCCESS = "success"; INFO = "info"

def _system_fonts() -> list[str]:
    try:
        from matplotlib import font_manager
        names = sorted({f.name for f in font_manager.fontManager.ttflist})
        preferred = ["Calibri", "Times New Roman", "Arial", "Helvetica", "Courier New"]
        ordered = [n for n in preferred if n in names]
        others = [n for n in names if n not in ordered]
        return ordered + others
    except Exception:
        return ["Helvetica", "Times-Roman", "Courier"]

class AutoIndexView:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{__app_name__} v{__version__} - Índice de Documentos")
        self.root.geometry("880x780")

        if USING_TTKB:
            tb.Style(theme="flatly")

        # State/UI vars
        self.directory = tk.StringVar()
        self.export_docx_var = tk.BooleanVar(value=True)
        self.export_pdf_var = tk.BooleanVar(value=True)
        self.output_basename = tk.StringVar(value="00Índice_Documentos")  # sin tilde por si acaso
        self.doc_title_var = tk.StringVar(value="Índice de Documentos")
        self.show_title_var = tk.BooleanVar(value=True)
        self.show_date_var = tk.BooleanVar(value=False)
        self.title_align_var = tk.StringVar(value="left")
        self.output_dir = tk.StringVar(value="")
        self.font_family_var = tk.StringVar(value="Calibri")
        self.title_size_var = tk.IntVar(value=18)
        self.body_size_var = tk.IntVar(value=11)

        self.build_ui()

    def build_ui(self):
        frm = tb.Frame(self.root, padding=15)
        frm.pack(fill="both", expand=True)

        title = tb.Label(frm, text="Crear índice de documentos legales", font=("", 16, "bold"))
        title.pack(anchor="w", pady=(0, 8))

        subtitle = tb.Label(frm, text="Selecciona la carpeta con PDFs. Generaremos un índice en Word y/o PDF.")
        subtitle.pack(anchor="w", pady=(0, 12))

        # Folder selector
        row = tb.Frame(frm); row.pack(fill="x", pady=(0, 8))
        tb.Label(row, text="Carpeta:").pack(side="left", padx=(0, 8))
        tb.Entry(row, textvariable=self.directory).pack(side="left", fill="x", expand=True)
        tb.Button(
            row, text="Elegir...", command=self.choose_directory,
            bootstyle=PRIMARY if USING_TTKB else None
        ).pack(side="left", padx=(8, 0))

        # Output folder
        outrow = tb.Frame(frm); outrow.pack(fill="x", pady=(0, 8))
        tb.Label(outrow, text="Carpeta de salida (opcional):").pack(side="left", padx=(0, 8))
        tb.Entry(outrow, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        tb.Button(outrow, text="Elegir...", command=self.choose_output_dir,
                  bootstyle=INFO if USING_TTKB else None).pack(side="left", padx=(8, 0))
        tb.Button(outrow, text="Restablecer", command=self.clear_output_dir).pack(side="left", padx=(8, 0))

        # Detected list
        list_frame = tb.Labelframe(frm, text="Documentos PDF detectados")
        list_frame.pack(fill="both", expand=True, pady=(8, 8))
        self.listbox = tk.Listbox(list_frame, height=14)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=8)

        # Header panel
        header = tb.LabelFrame(frm, text="Cabecera del índice")
        header.pack(fill="x", pady=(8, 8))

        # First row: editable title + show/hide
        row1 = tb.Frame(header); row1.pack(fill="x", padx=8, pady=6)
        tb.Label(row1, text="Título:").pack(side="left", padx=(0, 8))
        tb.Entry(row1, textvariable=self.doc_title_var).pack(side="left", fill="x", expand=True)
        tb.Checkbutton(
            row1, text="Mostrar título", variable=self.show_title_var,
            bootstyle=SUCCESS if USING_TTKB else None
        ).pack(side="left", padx=(12, 0))

        # Secod row: include date + alignment
        row2 = tb.Frame(header); row2.pack(fill="x", padx=8, pady=6)
        tb.Checkbutton(
            row2, text="Incluir fecha (hoy)", variable=self.show_date_var,
            bootstyle=SUCCESS if USING_TTKB else None
        ).pack(side="left")
        tb.Label(row2, text="Alineación título:").pack(side="left", padx=(16, 8))
        align = tb.Combobox(
            row2, state="readonly", values=["left", "center", "right"],
            textvariable=self.title_align_var, width=10
        )
        align.pack(side="left")

        # Font and sizes
        fonts_row = tb.Frame(header); fonts_row.pack(fill="x", padx=8, pady=6)
        tb.Label(fonts_row, text="Fuente:").pack(side="left", padx=(0, 8))
        fonts = _system_fonts()
        font_cb = tb.Combobox(fonts_row, state="readonly", values=fonts, textvariable=self.font_family_var, width=30)
        font_cb.pack(side="left")

        sizes_row = tb.Frame(header); sizes_row.pack(fill="x", padx=8, pady=6)
        tb.Label(sizes_row, text="Tamaño título:").pack(side="left", padx=(0, 8))
        title_size = tb.Spinbox(sizes_row, from_=9, to=96, textvariable=self.title_size_var, width=6)
        title_size.pack(side="left")

        tb.Label(sizes_row, text="Tamaño cuerpo:").pack(side="left", padx=(16, 8))
        body_size = tb.Spinbox(sizes_row, from_=6, to=48, textvariable=self.body_size_var, width=6)
        body_size.pack(side="left")

        # Export options
        opts = tb.Frame(frm); opts.pack(fill="x", pady=(8, 8))
        tb.Label(opts, text="Nombre de salida (sin extensión):").pack(side="left", padx=(0, 8))
        tb.Entry(opts, textvariable=self.output_basename, width=32).pack(side="left")

        cbx = tb.Frame(frm); cbx.pack(fill="x")
        tb.Checkbutton(
            cbx, text="Exportar a Word (.docx)", variable=self.export_docx_var,
            bootstyle=SUCCESS if USING_TTKB else None
        ).pack(side="left", padx=(0, 16))
        tb.Checkbutton(
            cbx, text="Exportar a PDF (.pdf)", variable=self.export_pdf_var,
            bootstyle=SUCCESS if USING_TTKB else None
        ).pack(side="left")

        # Actions
        actions = tb.Frame(frm); actions.pack(fill="x", pady=(12, 0))
        tb.Button(
            actions, text="Escanear carpeta", command=self.scan_folder,
            bootstyle=INFO if USING_TTKB else None
        ).pack(side="left")
        tb.Button(
            actions, text="Crear índice", command=self.generate_index,
            bootstyle=PRIMARY if USING_TTKB else None
        ).pack(side="right")

        # Status
        self.status = tb.Label(frm, text="Listo.", anchor="w")
        self.status.pack(fill="x", pady=(10, 0))

    def choose_directory(self):
        chosen = filedialog.askdirectory(title="Selecciona la carpeta con los PDFs")
        if chosen:
            self.directory.set(chosen)
            if not self.output_dir.get().strip():
                self.output_dir.set(chosen)
            self.scan_folder()

    def choose_output_dir(self):
        chosen = filedialog.askdirectory(title="Selecciona la carpeta de salida (opcional)")
        if chosen:
            self.output_dir.set(chosen)

    def clear_output_dir(self):
        if self.directory.get().strip():
            self.output_dir.set(self.directory.get())
        else:
            self.output_dir.set("")

    def scan_folder(self):
        self.listbox.delete(0, tk.END)
        path = Path(self.directory.get().strip())
        if not path.exists() or not path.is_dir():
            messagebox.showwarning("Carpeta no válida", "Selecciona una carpeta válida.")
            self.status.config(text="Carpeta no válida.")
            return

        titles, pdfs = list_pdf_titles(path)
        if not pdfs:
            self.status.config(text="No se encontraron PDFs en la carpeta.")
            messagebox.showinfo("Sin PDFs", "No se encontraron archivos .pdf en la carpeta seleccionada.")
            return

        for t in titles:
            self.listbox.insert(tk.END, t)

        self.status.config(text=f"Encontrados {len(titles)} PDFs.")

    def generate_index(self):
        src_dir = Path(self.directory.get().strip())
        if not src_dir.exists() or not src_dir.is_dir():
            messagebox.showwarning("Carpeta no válida", "Selecciona una carpeta válida.")
            return

        if not (self.export_docx_var.get() or self.export_pdf_var.get()):
            messagebox.showwarning("Seleccione formato", "Selecciona al menos un formato (Word o PDF).")
            return

        titles, pdfs = list_pdf_titles(src_dir)
        if not titles:
            messagebox.showinfo("Sin PDFs", "No se encontraron archivos .pdf en la carpeta seleccionada.")
            return
        
        dest_dir = self._resolve_output_dir(src_dir)

        base = (self.output_basename.get().strip() or "Indice_Documentos")
        generated = []

        header_kwargs = dict(
            title_text=(self.doc_title_var.get().strip() or "Índice de Documentos"),
            show_title=bool(self.show_title_var.get()),
            show_date=bool(self.show_date_var.get()),
            title_align=self.title_align_var.get(),
            font_name=self.font_family_var.get(),
            title_font_size=int(self.title_size_var.get()),
            body_font_size=int(self.body_size_var.get())
        )

        try:
            if self.export_docx_var.get():
                out_docx = dest_dir / f"{base}.docx"
                export_docx(titles, out_docx, **header_kwargs)
                generated.append(out_docx)

            if self.export_pdf_var.get():
                out_pdf = dest_dir / f"{base}.pdf"
                export_pdf(titles, out_pdf, **header_kwargs)
                generated.append(out_pdf)

        except ImportError as e:
            messagebox.showerror("Dependencia faltante", str(e))
            self.status.config(text="Falta una dependencia.")
            return
        except Exception as e:
            messagebox.showerror("Error de exportación", f"Ocurrió un error exportando el índice:\n{e}")
            self.status.config(text="Error durante la exportación.")
            return

        messagebox.showinfo("Índice creado", "Generado:\n" + "\n".join(str(p) for p in generated))
        self.status.config(text=f"Índice creado correctamente en: {dest_dir}")

    def _resolve_output_dir(self, src_dir: Path) -> Path:
        chosen = self.output_dir.get().strip()
        dest = Path(chosen) if chosen else src_dir
        dest.mkdir(parents=True, exist_ok=True)
        return dest

def main():
    root = tk.Tk()
    if USING_TTKB:
        tb.Style(theme="flatly") 
    App(root)
    root.mainloop()
