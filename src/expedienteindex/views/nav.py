import tkinter as tk
try:
    import ttkbootstrap as tb
except Exception:
    import tkinter.ttk as tb

def back_to_launcher(root: tk.Tk) -> None:
    """Limpia la ventana y vuelve al launcher."""
    for w in root.winfo_children():
        w.destroy()
    # Para evitar import circular: launcher -> autoindex_view -> nav -> launcher
    from .launcher import show_launcher
    show_launcher(root)