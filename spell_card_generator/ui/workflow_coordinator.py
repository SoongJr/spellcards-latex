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
from spell_card_generator.ui.workflow_steps.overwrite_cards_step import (
    OverwriteCardsStep,
)
from spell_card_generator.ui.workflow_steps.documentation_urls_step import (
    DocumentationURLsStep,
)
from spell_card_generator.ui.workflow_steps.preview_generate_step import (
    PreviewGenerateStep,
)
from spell_card_generator.utils.file_scanner import FileScanner


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

        # Step instances (created on demand) - mapped by step_index
        self.step_instances: dict[int, object] = {}

        # Step ID to index mapping for backward compatibility
        self.step_id_to_index = {
            "class_selection": 0,
            "spell_selection": 1,
            "overwrite_cards": 2,
            "documentation_urls": 3,
            "preview_generate": 4,
        }
        self.index_to_step_id = {v: k for k, v in self.step_id_to_index.items()}

        self._create_workflow_ui()

    def _create_workflow_ui(self):
        """Create the main workflow UI."""
        # Main container frame
        workflow_frame = ttk.Frame(self.parent_frame)
        workflow_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize workflow navigator state
        self.workflow_state.navigator.refresh_step_states(
            self.workflow_state.selected_class,
            self.workflow_state.selected_spells,
            self.workflow_state.conflicts_detected,
        )

        # Create modern sidebar navigation
        self.sidebar = ModernSidebar(
            workflow_frame, step_change_callback=self._on_step_changed
        )

        # Create content area
        self.content_frame = ttk.Frame(workflow_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        # Show initial step (Class Selection - index 0)
        self._show_step(0)

    def _show_step(self, step_index: int):
        """Show a specific workflow step with minimal UI flashing."""
        assert self.content_frame is not None, "Content frame must be initialized"

        # Disable UI updates temporarily to prevent flashing
        self.content_frame.update_idletasks()  # Ensure current state is rendered

        # Create step instance if not exists (use step_index as key)
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

        # Update workflow state current step
        self.workflow_state.current_step = step_index

        # Update navigator to match (convert index to step_id)
        step_id = self.index_to_step_id.get(step_index)
        if step_id:
            workflow_state.navigate_to_step(step_id)

        # Force immediate update to minimize visible changes
        self.content_frame.update_idletasks()

    def _create_step_instance(
        self, step_index: int
    ):  # pylint: disable=too-many-return-statements
        """Create an instance of a specific step."""
        assert self.content_frame is not None, "Content frame must be initialized"

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
        if step_index == 2:  # Overwrite Cards (conditional)
            return OverwriteCardsStep(
                self.content_frame,
                step_index,
                navigation_callback=self._on_step_changed,
                on_overwrite_changed=self._on_overwrite_changed,
            )
        if step_index == 3:  # Documentation & Language URLs
            return DocumentationURLsStep(
                self.content_frame,
                step_index,
                navigation_callback=self._on_step_changed,
                on_urls_changed=self._on_urls_changed,
            )
        if step_index == 4:  # Preview & Generate
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
        # Detect conflicts when spells are selected
        self._detect_conflicts()

        # Update sidebar state
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def _detect_conflicts(self):
        """Detect conflicts with existing spell card files."""
        if not self.workflow_state.selected_spells:
            # No spells selected, clear conflicts
            self.workflow_state.update_conflicts({})
            return

        # Scan for existing cards
        existing_cards = FileScanner.detect_existing_cards(
            self.workflow_state.selected_spells
        )

        # Update workflow state with conflicts
        self.workflow_state.update_conflicts(existing_cards)

        # Clear overwrite step instance if conflicts state changed
        if 2 in self.step_instances:
            # Remove cached instance so it gets recreated with new data
            if hasattr(self.step_instances[2], "destroy"):
                self.step_instances[2].destroy()
            del self.step_instances[2]

    def _on_step_changed(self, step_id_or_index):
        """Handle step navigation with smart conflict handling.

        Args:
            step_id_or_index: Either a step ID (str) or step index (int) for backward compatibility
        """
        # Convert step_id to index if needed
        if isinstance(step_id_or_index, str):
            step_index = self.step_id_to_index.get(step_id_or_index, 0)
        else:
            step_index = step_id_or_index

        # If navigating from spell selection (step 1) to next step
        if (
            step_index > 1
            and self.current_step
            and hasattr(self.current_step, "step_index")
        ):
            if getattr(self.current_step, "step_index", -1) == 1:
                # Coming from spell selection, use smart navigation
                next_step = self.workflow_state.get_next_step_after_spells()
                if next_step != step_index:
                    step_index = next_step

        self._show_step(step_index)

        # Update sidebar state
        if self.sidebar:
            self.sidebar.refresh_navigation()

    def _on_overwrite_changed(self):
        """Handle overwrite decision changes."""
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
