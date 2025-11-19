import tkinter as tk

try:
    import ttkbootstrap as tb
    USING_TTKB = True
except Exception:
    import tkinter.ttk as tb
    USING_TTKB = False

from .views.launcher import show_launcher

def main():
    root = tk.Tk()
    if USING_TTKB:
        tb.Style("flatly")
    show_launcher(root)
    root.mainloop()