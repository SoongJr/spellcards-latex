"""Main application window."""

import tkinter as tk
from tkinter import ttk

from spell_card_generator.config.constants import UIConfig


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
        self.main_frame.rowconfigure(0, weight=1)

        # Class selection frame (left side)
        self.class_frame = ttk.LabelFrame(
            self.main_frame,
            text="Character Class Selection",
            padding=UIConfig.MAIN_PADDING,
        )
        self.class_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10)
        )
        self.class_frame.columnconfigure(0, weight=1)
        self.class_frame.rowconfigure(0, weight=1)

        # Right side container - separate content from controls
        right_container = ttk.Frame(self.main_frame)
        right_container.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(0, weight=1)  # Only content area expands
        # Rows 1, 2, 3 for controls have no weight (fixed size)

        # Content frame for spell tabs (main expandable area)
        self.content_frame = ttk.Frame(right_container)
        self.content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Control frame for buttons (fixed size at bottom)
        self.control_frame = ttk.Frame(right_container)
        self.control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Progress frame (fixed size at bottom)
        self.progress_frame = ttk.Frame(right_container)
        self.progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Status frame (fixed size at bottom)
        self.status_frame = ttk.Frame(right_container)
        self.status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
