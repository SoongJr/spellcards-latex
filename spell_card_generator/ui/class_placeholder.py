"""Placeholder widget for when no character class is selected."""

import tkinter as tk
from tkinter import ttk


class ClassSelectionPlaceholder:
    """Placeholder widget shown when no character class is selected."""

    def __init__(self, parent_frame: ttk.Frame):
        self.parent_frame = parent_frame
        self.placeholder_frame: ttk.Frame = None

    def show(self):
        """Show the placeholder message."""
        self.hide()  # Clear any existing content

        # Create centered placeholder frame
        self.placeholder_frame = ttk.Frame(self.parent_frame)
        self.placeholder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.placeholder_frame.columnconfigure(0, weight=1)
        self.placeholder_frame.rowconfigure(0, weight=1)

        # Create inner content frame for centering
        content_frame = ttk.Frame(self.placeholder_frame)
        content_frame.grid(row=0, column=0)

        # Icon/symbol
        icon_label = ttk.Label(content_frame, text="🎲", font=("TkDefaultFont", 48))
        icon_label.pack(pady=(0, 20))

        # Main message
        message_label = ttk.Label(
            content_frame,
            text="Please select a character class",
            font=("TkDefaultFont", 14, "bold"),
            foreground="gray",
        )
        message_label.pack(pady=(0, 10))

        # Secondary message
        secondary_label = ttk.Label(
            content_frame,
            text="Choose a character class from the left panel\nto view and generate spell cards.",
            font=("TkDefaultFont", 10),
            foreground="gray",
            justify=tk.CENTER,
        )
        secondary_label.pack(pady=(0, 20))

    def hide(self):
        """Hide the placeholder."""
        if self.placeholder_frame:
            self.placeholder_frame.destroy()
            self.placeholder_frame = None
