import tkinter as tk
try:
    import ttkbootstrap as tb
except Exception:
    import tkinter.ttk as tb

from .nav import back_to_launcher

class AutoCensorView:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Autocensura - Próximamente")
        # Backbar
        bar = tb.Frame(self.root, padding=(10, 6)); bar.pack(fill="x")
        tb.Button(bar, text="← Volver", command=lambda: back_to_launcher(self.root)).pack(side="left")
        # Contenido
        frm = tb.Frame(self.root, padding=20); frm.pack(fill="both", expand=True)
        tb.Label(frm, text="Autocensura llegará en la siguiente rama.", font=("", 14)).pack(anchor="w", pady=(8,0))