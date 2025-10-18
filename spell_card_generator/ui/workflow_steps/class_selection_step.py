"""Class Selection workflow step."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from spell_card_generator.ui.workflow_state import workflow_state
from spell_card_generator.ui.single_class_selection import SingleClassSelectionManager
from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep
from spell_card_generator.data.loader import SpellDataLoader


class ClassSelectionStep(BaseWorkflowStep):
    """Character class selection step in the workflow."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        data_loader: SpellDataLoader,
        navigation_callback: Optional[Callable[[int], None]] = None,
        on_class_changed: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.data_loader = data_loader
        self.on_class_changed = on_class_changed

        # Class selection specific components
        self.class_manager: Optional[SingleClassSelectionManager] = None

    def create_step_content(self):
        """Create the class selection content."""
        # Title
        title_label = ttk.Label(
            self.content_frame,
            text="Select Character Class",
            font=("TkDefaultFont", 14, "bold"),
        )
        title_label.pack(pady=(0, 15))

        # Instructions
        instruction_label = ttk.Label(
            self.content_frame,
            text=(
                "Choose a character class to generate spell cards for. "
                "Select a class and click Next to proceed:"
            ),
            font=("TkDefaultFont", 10),
        )
        instruction_label.pack(pady=(0, 20))

        # Class selection tree frame
        tree_frame = ttk.LabelFrame(
            self.content_frame, text="Available Classes", padding=10
        )
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create class selection manager
        # Note: SingleClassSelectionManager expects Frame but LabelFrame is compatible
        self.class_manager = SingleClassSelectionManager(
            tree_frame, self._on_class_selection_changed  # type: ignore[arg-type]
        )

        # Setup class tree with data
        if hasattr(self.data_loader, "character_classes"):
            self.class_manager.setup_class_tree(self.data_loader.character_classes)

        # Restore previously selected class from workflow state
        if workflow_state.selected_class:
            self._restore_class_selection(workflow_state.selected_class)

        # Add double-click navigation
        if hasattr(self.class_manager, "tree"):
            assert self.class_manager.tree is not None, "Tree must be initialized"
            self.class_manager.tree.bind("<Double-1>", self._on_double_click)

    def _restore_class_selection(self, class_name: str):
        """Restore the previously selected class in the tree."""
        if not self.class_manager or not self.class_manager.tree:
            return

        # Find and select the class in the tree
        for category_item in self.class_manager.tree.get_children():
            for class_item in self.class_manager.tree.get_children(category_item):
                tags = self.class_manager.tree.item(class_item, "tags")
                if tags and tags[0] == class_name:
                    # Select this item
                    self.class_manager.tree.selection_set(class_item)
                    self.class_manager.tree.see(class_item)
                    # Update internal state
                    self.class_manager.selected_class = class_name
                    return

    def _on_class_selection_changed(self, selected_class: Optional[str] = None):
        """Handle class selection changes."""
        # Update workflow state
        workflow_state.selected_class = selected_class

        # Validate step
        workflow_state.set_step_valid(0, selected_class is not None)

        # Clear spell selection when class changes
        if workflow_state.selected_spells and selected_class != getattr(
            workflow_state, "_last_selected_class", None
        ):
            workflow_state.selected_spells.clear()
            workflow_state.set_step_valid(1, False)  # Invalidate spell selection step

        workflow_state._last_selected_class = selected_class

        # Update navigation state
        self.on_step_validation_changed()

        # Notify parent component
        if self.on_class_changed:
            self.on_class_changed()

    def _on_double_click(self, event):  # pylint: disable=unused-argument
        """Handle double-click on class list to proceed to next step."""
        if self.on_class_changed:
            self.on_class_changed()

        # Auto-navigate to next step if possible
        self._navigate_to_next_step()

    def select_class(self, class_name: str):
        """Programmatically select a class."""
        # This would need to be implemented in the SingleClassSelectionManager
        # to programmatically select a class

    def refresh_ui(self):
        """Refresh the UI when workflow state changes."""
        # Class selection doesn't need to refresh based on external state changes

    def destroy(self):
        """Clean up resources."""
        self.class_manager = None
        super().destroy()
