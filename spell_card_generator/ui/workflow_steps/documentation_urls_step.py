"""Documentation URLs workflow step."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep


# Placeholder for Documentation URLs step
class DocumentationURLsStep(BaseWorkflowStep):
    """Documentation URLs configuration step."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        navigation_callback: Optional[Callable[[int], None]] = None,
        on_urls_changed: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.on_urls_changed = on_urls_changed

    def create_step_content(self):
        """Create the documentation URLs content."""
        title_label = ttk.Label(
            self.content_frame,
            text="Documentation URLs",
            font=("TkDefaultFont", 14, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Placeholder content
        ttk.Label(
            self.content_frame,
            text="Configure custom documentation URLs and external links.\n"
            "(Coming in next iteration)",
            justify=tk.CENTER,
        ).pack(expand=True)
