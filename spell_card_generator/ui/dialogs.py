"""Dialogs and message boxes."""

import tkinter as tk
from tkinter import messagebox

class DialogManager:
    """Manages application dialogs and message boxes."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
    
    def show_info(self, title: str, message: str):
        """Show information dialog."""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title: str, message: str):
        """Show warning dialog."""
        messagebox.showwarning(title, message)
    
    def show_error(self, title: str, message: str):
        """Show error dialog."""
        messagebox.showerror(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """Ask yes/no question."""
        return messagebox.askyesno(title, message)
    
    def ask_ok_cancel(self, title: str, message: str) -> bool:
        """Ask OK/Cancel question."""
        return messagebox.askokcancel(title, message)
