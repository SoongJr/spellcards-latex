"""Generation Options workflow step."""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Callable, Optional, Union

from spell_card_generator.ui.workflow_state import workflow_state
from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep


class GenerationOptionsStep(BaseWorkflowStep):
    """Generation options configuration step."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        navigation_callback: Optional[Callable[[Union[int, str]], None]] = None,
        on_options_changed: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.on_options_changed = on_options_changed

        # UI variables
        self.output_dir_var: Optional[tk.StringVar] = None

    def create_step_content(self):
        """Create the generation options content."""
        # Title
        title_label = ttk.Label(
            self.content_frame,
            text="Generation Options",
            font=("TkDefaultFont", 14, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Create options sections
        self._create_output_directory_section()
        self._create_format_options_section()

        # Load current values
        self._load_current_values()

        # Validate step
        self._validate_step()

    def _create_output_directory_section(self):
        """Create output directory selection section."""
        output_frame = ttk.LabelFrame(
            self.content_frame, text="Output Directory", padding=10
        )
        output_frame.pack(fill=tk.X, pady=(0, 15))

        # Directory selection frame
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X)
        dir_frame.columnconfigure(0, weight=1)

        self.output_dir_var = tk.StringVar(value=workflow_state.output_directory or "")

        dir_entry = ttk.Entry(
            dir_frame, textvariable=self.output_dir_var, state="readonly"
        )
        dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))  # type: ignore[arg-type]

        browse_button = ttk.Button(
            dir_frame, text="Browse...", command=self._browse_output_directory
        )
        browse_button.grid(row=0, column=1)

        # Default directory info
        default_label = ttk.Label(
            output_frame,
            text="Files will be generated in the default 'src/spells/' directory.",
            font=("TkDefaultFont", 8),
            foreground="gray",
        )
        default_label.pack(anchor=tk.W, pady=(5, 0))

    def _create_format_options_section(self):
        """Create format options section."""
        format_frame = ttk.LabelFrame(
            self.content_frame, text="Format Options", padding=10
        )
        format_frame.pack(fill=tk.X, pady=(0, 15))

        # Card size option (future expansion)
        size_label = ttk.Label(format_frame, text="Card Size:")
        size_label.pack(anchor=tk.W)

        size_combo = ttk.Combobox(
            format_frame, values=["Standard", "A6 on A4", "A7 on A4"], state="readonly"
        )
        size_combo.set("Standard")
        size_combo.pack(anchor=tk.W, pady=(2, 10))

        # Language option
        lang_label = ttk.Label(format_frame, text="Primary Language:")
        lang_label.pack(anchor=tk.W)

        lang_combo = ttk.Combobox(
            format_frame, values=["English", "German"], state="readonly"
        )
        lang_combo.set("English")
        lang_combo.pack(anchor=tk.W, pady=(2, 0))

    def _browse_output_directory(self):
        """Open directory browser for output selection."""
        initial_dir = workflow_state.output_directory or str(
            Path.cwd() / "src" / "spells"
        )

        directory = filedialog.askdirectory(
            title="Select Output Directory", initialdir=initial_dir
        )

        if directory:
            assert (
                self.output_dir_var is not None
            ), "Output directory var must be initialized"
            self.output_dir_var.set(directory)
            workflow_state.output_directory = directory
            self._validate_step()

            if self.on_options_changed:
                self.on_options_changed()

    def _load_current_values(self):
        """Load current values from workflow state."""
        assert (
            self.output_dir_var is not None
        ), "Output directory var must be initialized"
        self.output_dir_var.set(workflow_state.output_directory or "")

    def _validate_step(self):
        """Validate the current step configuration."""
        # Generation options are always valid (all are optional with defaults)
        workflow_state.set_step_valid(2, True)
        self.on_step_validation_changed()

    def refresh_ui(self):
        """Refresh the UI when workflow state changes."""
        self._load_current_values()
