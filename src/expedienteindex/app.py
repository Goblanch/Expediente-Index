import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from .indexing import list_pdf_titles
from .exporters import export_docx, export_pdf
from . import __app_name__, __version__

# Try modern UI with ttkbootstrap, if not available, use classic ttk
try:
    import ttkbootstrap as tb
    USING_TTKB = True
    from ttkbootstrap.constants import PRIMARY, SUCCESS, INFO
except Exception:
    import tkinter.ttk as tb
    USING_TTKB = False
    PRIMARY = "primary"; SUCCESS = "success"; INFO = "info"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{__app_name__} v{__version__} - Índice de Documentos")
        self.root.geometry("760x560")

        if USING_TTKB:
            tb.Style(theme="flatly")

        # State/UI vars
        self.directory = tk.StringVar()
        self.export_docx_var = tk.BooleanVar(value=True)
        self.export_pdf_var = tk.BooleanVar(value=True)
        self.output_basename = tk.StringVar(value="Indice_Documentos")  # sin tilde por si acaso

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

        # Detected list
        list_frame = tb.Labelframe(frm, text="Documentos PDF detectados")
        list_frame.pack(fill="both", expand=True, pady=(8, 8))
        self.listbox = tk.Listbox(list_frame, height=14)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=8)

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
            self.scan_folder()

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
        path = Path(self.directory.get().strip())
        if not path.exists() or not path.is_dir():
            messagebox.showwarning("Carpeta no válida", "Selecciona una carpeta válida.")  # <- fix
            return

        if not (self.export_docx_var.get() or self.export_pdf_var.get()):
            messagebox.showwarning("Seleccione formato", "Selecciona al menos un formato (Word o PDF).")
            return

        titles, pdfs = list_pdf_titles(path)
        if not titles:
            messagebox.showinfo("Sin PDFs", "No se encontraron archivos .pdf en la carpeta seleccionada.")
            return

        base = (self.output_basename.get().strip() or "Indice_Documentos")
        generated = []

        try:
            if self.export_docx_var.get():
                out_docx = path / f"{base}.docx"
                export_docx(titles, out_docx)
                generated.append(out_docx)

            if self.export_pdf_var.get():
                out_pdf = path / f"{base}.pdf"
                export_pdf(titles, out_pdf)
                generated.append(out_pdf)

        except Exception as e:
            messagebox.showerror("Error de exportación", f"Ocurrió un error exportando el índice: \n{e}")
            self.status.config(text="Error durante la exportación.")
            return

        messagebox.showinfo("Índice creado", "Generado:\n" + "\n".join(str(p) for p in generated))
        self.status.config(text="Índice creado correctamente.")

def main():
    root = tk.Tk()
    if USING_TTKB:
        tb.Style(theme="flatly")  # <- fix
    App(root)
    root.mainloop()
