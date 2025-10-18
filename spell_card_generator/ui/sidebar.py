"""Modern sidebar navigation for multi-step workflow."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Optional, Any

from spell_card_generator.ui.workflow_state import workflow_state
from spell_card_generator.ui.step_utils import format_step_info


class ModernSidebar:
    """Modern vertical sidebar navigation component."""

    # Base step definitions with icon names
    BASE_STEPS = [
        {
            "name": "Class Selection",
            "icon": "class",
            "description": "Choose character class",
            "required": True,
        },
        {
            "name": "Spell Selection",
            "icon": "spell",
            "description": "Select spells to generate",
            "required": True,
        },
        {
            "name": "Overwrite Cards",
            "icon": "warning",
            "description": "Manage existing card conflicts",
            "required": True,
            "conditional": True,  # Only shown when conflicts detected
        },
        {
            "name": "Generation Options",
            "icon": "settings",
            "description": "Configure output settings",
            "required": False,
        },
        {
            "name": "Documentation & Language URLs",
            "icon": "link",
            "description": "Custom spell references and multi-language support",
            "required": False,
        },
        {
            "name": "Preview & Generate",
            "icon": "generate",
            "description": "Review and generate cards",
            "required": True,
        },
    ]

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_change_callback: Callable[[str], None],  # Changed to accept step_id
    ):
        self.parent_frame = parent_frame
        self.step_change_callback = step_change_callback

        # UI State - sync with workflow navigator
        self.current_step = workflow_state.navigator.get_current_step_index()
        self.step_buttons: List[ttk.Button] = []

        # UI Components (initialized here to avoid W0201)
        self.sidebar_frame: Optional[ttk.Frame] = None
        self.buttons_frame: Optional[ttk.Frame] = None

        # Create UI
        self._create_sidebar_ui()

    def get_visible_steps(self) -> List[Dict]:
        """Get list of steps that should be visible based on current state."""
        # Always show all steps, but with proper accessibility state
        # This gives users a clear view of the entire workflow
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )

        # Get ALL steps (not just visible ones) for the sidebar
        all_steps = []
        step = workflow_state.navigator.first_step
        while step:
            all_steps.append(step)
            step = step.next_step

        # Convert to the format expected by the UI with forced visibility
        current_step = workflow_state.navigator.get_current_step()
        return [
            {
                **format_step_info(step, step == current_step),
                "is_visible": True,  # Always visible in sidebar for better UX
            }
            for step in all_steps
        ]

    def _create_sidebar_ui(self):
        """Create the modern vertical sidebar navigation UI."""
        # Main sidebar frame
        self.sidebar_frame = ttk.Frame(
            self.parent_frame, relief=tk.RAISED, borderwidth=1
        )
        self.sidebar_frame.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 2))

        # Configure sidebar width
        self.sidebar_frame.configure(width=200)
        self.sidebar_frame.pack_propagate(False)  # Maintain fixed width

        # Step buttons container
        self.buttons_frame = ttk.Frame(self.sidebar_frame)
        self.buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create step buttons
        self._create_step_buttons()

    def _create_step_buttons(self):
        """Create step buttons based on visible steps."""
        # Clear existing buttons
        for button in self.step_buttons:
            button.destroy()
        self.step_buttons.clear()

        # Create buttons for visible steps
        visible_steps = self.get_visible_steps()
        for i, step in enumerate(visible_steps):
            self._create_modern_step_button(i, step)

    def _create_modern_step_button(self, _step_index: int, step_info: Dict[str, Any]):
        """Create a modern navigation button for a workflow step."""
        # Create button with step name (no icons)
        button_text = step_info["name"]
        button_width = 18

        # Use step ID for navigation instead of index
        step_id = step_info["id"]
        button = ttk.Button(
            self.buttons_frame,
            text=button_text,
            command=lambda: self._navigate_to_step_by_id(step_id),
            width=button_width,
        )

        # Set initial button state based on accessibility
        if step_info["is_accessible"]:
            button.config(state="normal")
            if step_info["is_current"]:
                button.config(style="Accent.TButton")  # Highlight current step
            else:
                button.config(style="TButton")
        else:
            button.config(state="disabled", style="TButton")

        button.pack(fill=tk.X, pady=(0, 3))

        # Store button reference with step info for later updates
        button.step_info = step_info  # type: ignore[attr-defined]
        self.step_buttons.append(button)

    def _navigate_to_step_by_id(self, step_id: str):
        """Navigate to a specific workflow step by ID."""
        if not workflow_state.navigate_to_step(step_id):
            self._show_navigation_warning_by_id(step_id)
            return

        # Get the updated current step index from navigator
        step_index = workflow_state.navigator.get_current_step_index()

        # Update current step tracking
        self.current_step = step_index
        workflow_state.current_step = step_index

        # Refresh navigation states
        self._update_navigation_state()

        # Notify the callback with the step ID instead of index
        self.step_change_callback(step_id)

    def _show_navigation_warning_by_id(self, step_id: str):
        """Show warning when user tries to access unavailable step by ID."""
        if step_id == "spell_selection" and not workflow_state.selected_class:
            print("Please select a character class first.")
        elif (
            step_id in ["generation_options", "documentation_urls", "preview_generate"]
            and len(workflow_state.selected_spells) == 0
        ):
            print("Please select spells before proceeding to later steps.")
        elif step_id == "overwrite_cards" and not workflow_state.conflicts_detected:
            print("No file conflicts detected.")

    def _show_navigation_warning(self, step_index: int):
        """Show warning when user tries to access unavailable step."""
        if step_index == 1 and not workflow_state.selected_class:
            # Show simple message (could be enhanced with a popup)
            print("Please select a character class first.")
        elif step_index > 1 and len(workflow_state.selected_spells) == 0:
            print("Please select spells before proceeding to later steps.")

    def _update_navigation_state(self):
        """Update button states based on current workflow state."""
        # Get current step information
        current_step_info = workflow_state.get_current_step_info()
        current_step_id = current_step_info["id"] if current_step_info else None

        # Update each button based on its accessibility and current status
        for button in self.step_buttons:
            if hasattr(button, "step_info"):
                step_info = button.step_info
                step_id = step_info["id"]

                # Refresh accessibility state
                step = workflow_state.navigator.get_step_by_id(step_id)
                if step:
                    is_accessible = step.is_accessible
                    is_current = step_id == current_step_id

                    if is_accessible:
                        button.config(state="normal")
                        if is_current:
                            button.config(
                                style="Accent.TButton"
                            )  # Highlight current step
                        else:
                            button.config(style="TButton")
                    else:
                        button.config(state="disabled", style="TButton")

    def _can_navigate_to_step(self, step_index: int) -> bool:
        """Check if user can navigate to a specific step with new workflow."""
        return workflow_state.can_navigate_to_step(step_index)

    def refresh_navigation(self):
        """Refresh navigation state and visual indicators."""
        # Refresh workflow state first to ensure everything is current
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )

        # Update navigation state (accessibility, current step highlighting)
        self._update_navigation_state()

        # Update step styles
        self._update_step_styles()

    def _update_step_styles(self):
        """Update visual styles for step buttons."""
        for i, button in enumerate(self.step_buttons):
            if i == self.current_step:
                button.config(style="Accent.TButton")  # Highlight current step
            else:
                button.config(style="TButton")
