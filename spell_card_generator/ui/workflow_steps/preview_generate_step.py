"""Preview and Generate workflow step."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional

from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep


# Placeholder for Preview & Generate step
class PreviewGenerateStep(BaseWorkflowStep):
    """Preview and generation step."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        navigation_callback: Optional[Callable[[int], None]] = None,
        on_generate: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.on_generate = on_generate
        self.summary_text: Optional[scrolledtext.ScrolledText] = None

    def create_step_content(self):
        """Create the preview and generate content."""
        title_label = ttk.Label(
            self.content_frame,
            text="Preview & Generate",
            font=("TkDefaultFont", 14, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Summary section
        summary_frame = ttk.LabelFrame(
            self.content_frame, text="Generation Summary", padding=10
        )
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Summary text
        self.summary_text = scrolledtext.ScrolledText(
            summary_frame, height=10, wrap=tk.WORD, state=tk.DISABLED
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Generate button
        generate_button = ttk.Button(
            self.content_frame,
            text="🎯 Generate Spell Cards",
            command=self._on_generate_clicked,
            style="Accent.TButton",
        )
        generate_button.pack(pady=10)

        self._update_summary()

    def _update_summary(self):
        """Update the generation summary."""
        # This will be implemented to show current selections
        summary = (
            "Generation summary will be displayed here.\n(Coming in next iteration)"
        )

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)

    def _on_generate_clicked(self):
        """Handle generate button click."""
        if self.on_generate:
            self.on_generate()

    def refresh_ui(self):
        """Refresh the UI when workflow state changes."""
        if hasattr(self, "summary_text"):
            self._update_summary()
