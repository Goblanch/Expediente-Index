import tkinter as tk
try:
    import ttkbootstrap as tb
    USING_TTKB = True
except Exception:
    import tkinter.ttk as tb
    USING_TTKB = False

from .autoindex_view import AutoIndexView
from .autocensor_view import AutoCensorView

def show_launcher(root: tk.Tk):
    frm = tb.Frame(root, padding=20)
    frm.pack(fill="both", expand=True)

    title = tb.Label(frm, text="Herramientas", font=("", 18, "bold"))
    title.pack(anchor="w", pady=(0, 12))

    grid = tb.Frame(frm); grid.pack(fill="both", expand=True)

    def open_autoindex():
        for w in root.winfo_children(): w.destroy()
        AutoIndexView(root)

    def open_autocensor():
        for w in root.winfo_children(): w.destroy()
        AutoCensorView(root)

    card1 = tb.LabelFrame(grid, text="AutoÍndice", padding=12)
    card1.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
    tb.Label(card1, text="Genera un índice a partir de PDFs.").pack(anchor="w")
    tb.Button(card1, text="Abrir", command=open_autoindex).pack(anchor="e", pady=(8, 0))

    card2 = tb.LabelFrame(grid, text="Autocensura", padding=12)
    card2.grid(row=0, column=1, padx=12, pady=12, sticky="nsew")
    tb.Label(card2, text="Analiza y censura entidades en documentos.").pack(anchor="w")
    tb.Button(card2, text="Abrir", command=open_autocensor).pack(anchor="e", pady=(8, 0))