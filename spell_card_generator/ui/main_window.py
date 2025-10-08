"""Main application window."""

import tkinter as tk
from tkinter import ttk

from config.constants import UIConfig


class MainWindow:
    """Main application window manager."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self._setup_window()
        self._create_main_layout()

    def _setup_window(self):
        """Configure the main window."""
        self.root.title(UIConfig.WINDOW_TITLE)
        self.root.geometry(UIConfig.WINDOW_SIZE)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _create_main_layout(self):
        """Create the main layout frames."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=UIConfig.MAIN_PADDING)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure main frame grid weights
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Class selection frame
        self.class_frame = ttk.LabelFrame(
            self.main_frame,
            text="Select Character Classes",
            padding=UIConfig.MAIN_PADDING,
        )
        self.class_frame.grid(
            row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        self.class_frame.columnconfigure(0, weight=1)

        # Content frame for spell tabs
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        # Options frame
        self.options_frame = ttk.LabelFrame(
            self.main_frame, text="Options", padding=UIConfig.MAIN_PADDING
        )
        self.options_frame.grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        self.options_frame.columnconfigure(0, weight=1)

        # Control frame for buttons
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))

        # Progress frame
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Status frame
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=5, column=0, columnspan=3)
