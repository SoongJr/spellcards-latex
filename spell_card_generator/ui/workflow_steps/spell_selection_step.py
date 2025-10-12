"""Spell Selection workflow step."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from spell_card_generator.ui.workflow_state import workflow_state
from spell_card_generator.ui.spell_tabs import SpellTabManager
from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep
from spell_card_generator.data.loader import SpellDataLoader
from spell_card_generator.data.filter import SpellFilter


class SpellSelectionStep(BaseWorkflowStep):
    """Spell selection step in the workflow."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        data_loader: SpellDataLoader,
        spell_filter: SpellFilter,
        navigation_callback: Optional[Callable[[int], None]] = None,
        on_selection_changed: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.data_loader = data_loader
        self.spell_filter = spell_filter
        self.on_selection_changed = on_selection_changed

        # Spell selection specific components
        self.spell_tab_manager: Optional[SpellTabManager] = None

    def create_step_content(self):
        """Create the spell selection content."""
        # Configure content frame to expand
        self.content_frame.rowconfigure(
            2, weight=1
        )  # Spell interface area should expand
        self.content_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            self.content_frame, text="Select Spells", font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Instructions
        if workflow_state.selected_class:
            class_name = workflow_state.selected_class
            display_name = class_name.replace("_", " ").title()
            instruction_text = (
                f"Select spells for {display_name} class.\n"
                "Click checkboxes or highlight spells and press Space to toggle selection:"
            )
        else:
            instruction_text = "Please select a character class first."

        instruction_label = ttk.Label(
            self.content_frame, text=instruction_text, font=("TkDefaultFont", 10)
        )
        instruction_label.pack(pady=(0, 15))

        if workflow_state.selected_class:
            # Create spell selection interface
            self._create_spell_interface()
        else:
            # Show message to select class first
            self._create_class_selection_prompt()

    def _create_spell_interface(self):
        """Create the spell selection interface."""
        # Create a frame for the spell interface that will expand
        spell_interface_frame = ttk.Frame(self.content_frame)
        spell_interface_frame.pack(fill=tk.BOTH, expand=True)

        # Create spell tab manager for the selected class
        self.spell_tab_manager = SpellTabManager(
            spell_interface_frame,
            self.data_loader,
            self.spell_filter,
            spell_selection_callback=self._on_spell_selection_changed,
            double_click_callback=self._on_double_click,
        )

        # Load spells for the selected class
        if workflow_state.selected_class:
            self.spell_tab_manager.update_tabs({workflow_state.selected_class})

            # Restore previously selected spells if any
            self._restore_spell_selections()

    def _create_class_selection_prompt(self):
        """Create prompt to select character class first."""
        prompt_frame = ttk.Frame(self.content_frame)
        prompt_frame.pack(expand=True)

        message_label = ttk.Label(
            prompt_frame,
            text="⚠️ No character class selected",
            font=("TkDefaultFont", 12, "bold"),
            foreground="orange",
        )
        message_label.pack(pady=(0, 10))

        help_label = ttk.Label(
            prompt_frame,
            text=(
                "Please select a character class from the main selection\n"
                "before proceeding to spell selection."
            ),
            font=("TkDefaultFont", 10),
            justify=tk.CENTER,
        )
        help_label.pack()

    def _on_spell_selection_changed(self):
        """Handle spell selection changes."""
        if self.spell_tab_manager:
            # Update workflow state with current selection
            workflow_state.selected_spells = (
                self.spell_tab_manager.get_selected_spells()
            )

            # Validate spell selection step (step 1)
            has_spells = len(workflow_state.selected_spells) > 0
            workflow_state.set_step_valid(1, has_spells)

            # Update navigation state
            self.on_step_validation_changed()

            # Notify parent component
            if self.on_selection_changed:
                self.on_selection_changed()

    def _on_double_click(self):
        """Handle double-click on spell list."""
        # Only proceed if we have spells selected and can navigate to next step
        if len(
            workflow_state.selected_spells
        ) > 0 and workflow_state.can_navigate_to_step(self.step_index + 1):
            self._go_next()

    def _restore_spell_selections(self):
        """Restore previously selected spells from workflow state."""
        if not self.spell_tab_manager or not workflow_state.selected_spells:
            return

        # Update the spell tab manager's persistent state from workflow state
        selected_spell_names = {spell[1] for spell in workflow_state.selected_spells}

        # Sync the persistent state
        for spell_name in selected_spell_names:
            self.spell_tab_manager.selected_spells_state[spell_name] = True

    def refresh_ui(self):
        """Refresh the UI when workflow state changes."""
        if workflow_state.selected_class and not self.spell_tab_manager:
            # Class was selected, create interface
            self.create_ui()
        elif not workflow_state.selected_class and self.spell_tab_manager:
            # Class was deselected, show prompt
            self.create_ui()
        elif self.spell_tab_manager:
            # Update existing interface
            self.spell_tab_manager.update_tabs(
                {workflow_state.selected_class}
                if workflow_state.selected_class
                else set()
            )

    def destroy(self):
        """Clean up resources."""
        self.spell_tab_manager = None
        super().destroy()
