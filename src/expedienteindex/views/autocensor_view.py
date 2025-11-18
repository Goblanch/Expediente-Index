import tkinter as tk
try:
    import ttkbootstrap as tb
except Exception:
    import tkinter.ttk as tb

class AutoCensorView:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Autocensura - Próximamente")
        frm = tb.Frame(self.root, padding=20); frm.pack(fill="both", expand=True)
        tb.Label(frm, text="Autocensura llegará en la siguiente rama.", font=("", 14)).pack(anchor="w")