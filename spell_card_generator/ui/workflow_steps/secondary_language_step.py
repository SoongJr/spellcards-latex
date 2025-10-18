"""Secondary Language workflow step."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Union

from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep


# Placeholder for Secondary Language step
class SecondaryLanguageStep(BaseWorkflowStep):
    """Secondary language configuration step."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        navigation_callback: Optional[Callable[[Union[int, str]], None]] = None,
        on_language_changed: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.on_language_changed = on_language_changed

    def create_step_content(self):
        """Create the secondary language content."""
        title_label = ttk.Label(
            self.content_frame,
            text="Secondary Language",
            font=("TkDefaultFont", 14, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Placeholder content
        ttk.Label(
            self.content_frame,
            text="Configure secondary language support and QR codes.\n(Coming in next iteration)",
            justify=tk.CENTER,
        ).pack(expand=True)
