"""Main workflow coordinator for multi-step spell card generation."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from spell_card_generator.ui.sidebar import ModernSidebar
from spell_card_generator.ui.workflow_state import workflow_state
from spell_card_generator.data.loader import SpellDataLoader
from spell_card_generator.data.filter import SpellFilter

# Import step classes directly to avoid circular import issues
from spell_card_generator.ui.workflow_steps.class_selection_step import (
    ClassSelectionStep,
)
from spell_card_generator.ui.workflow_steps.spell_selection_step import (
    SpellSelectionStep,
)
from spell_card_generator.ui.workflow_steps.generation_options_step import (
    GenerationOptionsStep,
)
from spell_card_generator.ui.workflow_steps.documentation_urls_step import (
    DocumentationURLsStep,
)
from spell_card_generator.ui.workflow_steps.secondary_language_step import (
    SecondaryLanguageStep,
)
from spell_card_generator.ui.workflow_steps.preview_generate_step import (
    PreviewGenerateStep,
)


class WorkflowCoordinator:
    """Coordinates the multi-step workflow interface."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        data_loader: SpellDataLoader,
        spell_filter: SpellFilter,
        on_generate_callback: Optional[Callable] = None,
    ):
        self.parent_frame = parent_frame
        self.data_loader = data_loader
        self.spell_filter = spell_filter
        self.on_generate_callback = on_generate_callback

        # Use global workflow state
        self.workflow_state = workflow_state

        # UI Components
        self.sidebar: Optional[ModernSidebar] = None
        self.content_frame: Optional[ttk.Frame] = None
        self.current_step: Optional[object] = None

        # Step instances (created on demand)
        self.step_instances = {}

        self._create_workflow_ui()

    def _create_workflow_ui(self):
        """Create the main workflow UI."""
        # Main container frame
        workflow_frame = ttk.Frame(self.parent_frame)
        workflow_frame.pack(fill=tk.BOTH, expand=True)

        # Create modern sidebar navigation
        self.sidebar = ModernSidebar(
            workflow_frame, step_change_callback=self._on_step_changed
        )

        # Create content area
        self.content_frame = ttk.Frame(workflow_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        # Show initial step (Class Selection)
        self._show_step(0)

    def _on_step_changed(self, step_index: int):
        """Handle step navigation."""
        self._show_step(step_index)

        # Update sidebar state
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def _show_step(self, step_index: int):
        """Show a specific workflow step with minimal UI flashing."""
        # Disable UI updates temporarily to prevent flashing
        self.content_frame.update_idletasks()  # Ensure current state is rendered

        # Create step instance if not exists
        if step_index not in self.step_instances:
            self.step_instances[step_index] = self._create_step_instance(step_index)

        # Clean up current step
        if self.current_step and hasattr(self.current_step, "destroy"):
            self.current_step.destroy()

        # Clear content frame quickly
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Show the new step
        self.current_step = self.step_instances[step_index]
        if self.current_step and hasattr(self.current_step, "create_ui"):
            self.current_step.create_ui()

        # Force immediate update to minimize visible changes
        self.content_frame.update_idletasks()

    def _create_step_instance(
        self, step_index: int
    ):  # pylint: disable=too-many-return-statements
        """Create an instance of a specific step."""
        if step_index == 0:  # Class Selection
            return ClassSelectionStep(
                self.content_frame,
                step_index,
                self.data_loader,
                navigation_callback=self._on_step_changed,
                on_class_changed=self._on_class_changed,
            )
        if step_index == 1:  # Spell Selection
            return SpellSelectionStep(
                self.content_frame,
                step_index,
                self.data_loader,
                self.spell_filter,
                navigation_callback=self._on_step_changed,
                on_selection_changed=self._on_selection_changed,
            )
        if step_index == 2:  # Generation Options
            return GenerationOptionsStep(
                self.content_frame,
                step_index,
                navigation_callback=self._on_step_changed,
                on_options_changed=self._on_options_changed,
            )
        if step_index == 3:  # Documentation URLs
            return DocumentationURLsStep(
                self.content_frame,
                step_index,
                navigation_callback=self._on_step_changed,
                on_urls_changed=self._on_urls_changed,
            )
        if step_index == 4:  # Secondary Language
            return SecondaryLanguageStep(
                self.content_frame,
                step_index,
                navigation_callback=self._on_step_changed,
                on_language_changed=self._on_language_changed,
            )
        if step_index == 5:  # Preview & Generate
            return PreviewGenerateStep(
                self.content_frame,
                step_index,
                navigation_callback=self._on_step_changed,
                on_generate=self._on_generate,
            )
        return None

    def _on_class_changed(self):
        """Handle class selection changes."""
        # Update sidebar state
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def _on_selection_changed(self):
        """Handle spell selection changes."""
        # Update sidebar state
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def _on_options_changed(self):
        """Handle generation options changes."""
        # Update sidebar state
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def _on_urls_changed(self):
        """Handle documentation URL changes."""
        # Update sidebar state
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def _on_language_changed(self):
        """Handle secondary language changes."""
        # Update sidebar state
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def _on_generate(self):
        """Handle spell card generation."""
        if self.on_generate_callback:
            self.on_generate_callback()

    def set_selected_class(self, class_name: Optional[str]):
        """Set the selected character class."""
        self.workflow_state.selected_class = class_name

        # Refresh current step if it's spell selection
        if self.current_step and hasattr(self.current_step, "refresh_ui"):
            self.current_step.refresh_ui()

        # Update sidebar
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def get_selected_spells(self):
        """Get currently selected spells."""
        return self.workflow_state.selected_spells

    def destroy(self):
        """Clean up workflow resources."""
        # Clean up all step instances
        for step in self.step_instances.values():
            if hasattr(step, "destroy"):
                step.destroy()

        self.step_instances.clear()

        if self.current_step and hasattr(self.current_step, "destroy"):
            self.current_step.destroy()

        # Clean up UI
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
