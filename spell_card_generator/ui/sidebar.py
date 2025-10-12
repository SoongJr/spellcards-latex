"""Modern sidebar navigation for multi-step workflow."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Optional

from spell_card_generator.ui.workflow_state import workflow_state
from spell_card_generator.ui.icons import get_icon


class ModernSidebar:
    """Modern vertical sidebar navigation component."""

    # Step definitions with icon names
    STEPS = [
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
            "name": "Generation Options",
            "icon": "settings",
            "description": "Configure output settings",
            "required": False,
        },
        {
            "name": "Documentation URLs",
            "icon": "link",
            "description": "Custom spell references",
            "required": False,
        },
        {
            "name": "Secondary Language",
            "icon": "globe",
            "description": "Multi-language support",
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
        self, parent_frame: ttk.Frame, step_change_callback: Callable[[int], None]
    ):
        self.parent_frame = parent_frame
        self.step_change_callback = step_change_callback
        self.step_buttons: List[ttk.Button] = []
        self.current_step = 0
        self.expanded = False

        # UI components
        self.sidebar_frame: Optional[ttk.Frame] = None
        self.expand_button: Optional[ttk.Button] = None

        self._create_modern_sidebar()
        self._update_navigation_state()

    def _create_modern_sidebar(self):
        """Create the modern vertical sidebar navigation UI."""
        # Main sidebar frame - minimal width when collapsed
        self.sidebar_frame = ttk.Frame(
            self.parent_frame, relief=tk.RAISED, borderwidth=1
        )
        self.sidebar_frame.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 2))

        # Configure sidebar width based on expanded state
        self.sidebar_frame.configure(width=60 if not self.expanded else 200)
        self.sidebar_frame.pack_propagate(False)  # Maintain fixed width

        # Step buttons container
        self.buttons_frame = ttk.Frame(self.sidebar_frame)
        self.buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create step buttons
        for i, step in enumerate(self.STEPS):
            self._create_modern_step_button(i, step)

        # Spacer to push expand button to bottom
        spacer = ttk.Frame(self.buttons_frame)
        spacer.pack(fill=tk.BOTH, expand=True)

        # Expand/collapse button at bottom
        self._create_expand_button()

    def _create_modern_step_button(self, step_index: int, step_info: Dict[str, str]):
        """Create a modern navigation button for a workflow step."""
        # Get icon from icon manager
        icon_char = get_icon(step_info["icon"])

        # Create button with icon only or icon + text based on expanded state
        if self.expanded:
            button_text = f"{icon_char} {step_info['name']}"
            button_width = 18
        else:
            button_text = icon_char
            button_width = 4

        button = ttk.Button(
            self.buttons_frame,
            text=button_text,
            command=lambda idx=step_index: self._navigate_to_step(idx),
            width=button_width,
        )

        # ttk.Button doesn't support font option directly - we'll use style
        # or just rely on system fonts

        button.pack(fill=tk.X, pady=(0, 3))

        # Store button for later updates
        self.step_buttons.append(button)

        # Tooltip for collapsed mode
        if not self.expanded:
            self._create_tooltip(
                button, f"{step_info['name']}\n{step_info['description']}"
            )

    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget."""

        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip,
                text=text,
                background="lightyellow",
                relief=tk.SOLID,
                borderwidth=1,
                font=("TkDefaultFont", 9),
            )
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):  # pylint: disable=unused-argument
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _create_expand_button(self):
        """Create expand/collapse button at bottom of sidebar."""
        expand_icon = get_icon("collapse" if self.expanded else "expand")
        self.expand_button = ttk.Button(
            self.buttons_frame,
            text=expand_icon,
            command=self._toggle_sidebar,
            width=4 if not self.expanded else 18,
        )

        # ttk.Button doesn't support font option directly

        self.expand_button.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

    def _toggle_sidebar(self):
        """Toggle sidebar expanded/collapsed state."""
        self.expanded = not self.expanded

        # Recreate sidebar with new state
        self.sidebar_frame.destroy()
        self.step_buttons.clear()
        self._create_modern_sidebar()
        self._update_navigation_state()

    def _create_progress_indicator(self):
        """Create a minimal progress indicator (only in expanded mode)."""
        if not self.expanded:
            return

        # Simple progress indicator at bottom when expanded
        progress_frame = ttk.Frame(self.buttons_frame)
        progress_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5))

        completed_steps = sum(
            1 for i in range(len(self.STEPS)) if workflow_state.is_step_valid(i)
        )

        progress_text = f"{completed_steps}/{len(self.STEPS)} Complete"
        progress_label = ttk.Label(
            progress_frame,
            text=progress_text,
            font=("TkDefaultFont", 8),
            foreground="gray",
        )
        progress_label.pack()

    def _create_help_text(self):
        """Help is now handled by tooltips in collapsed mode."""

    def _navigate_to_step(self, step_index: int):
        """Navigate to a specific workflow step."""
        if not workflow_state.can_navigate_to_step(step_index):
            self._show_navigation_warning(step_index)
            return

        self.current_step = step_index
        workflow_state.current_step = step_index
        self._update_navigation_state()
        self.step_change_callback(step_index)

    def _show_navigation_warning(self, step_index: int):
        """Show warning when user tries to access unavailable step."""
        if step_index == 1 and not workflow_state.selected_class:
            # Show simple message (could be enhanced with a popup)
            print("Please select a character class first.")
        elif step_index > 1 and len(workflow_state.selected_spells) == 0:
            print("Please select spells before proceeding to later steps.")

    def _update_navigation_state(self):
        """Update button states based on current workflow state."""
        for i, button in enumerate(self.step_buttons):
            # Updated navigation logic for new step order
            can_navigate = self._can_navigate_to_step(i)

            if can_navigate:
                button.config(state="normal")
                if i == self.current_step:
                    button.config(style="Accent.TButton")  # Highlight current step
                else:
                    button.config(style="TButton")
            else:
                button.config(state="disabled", style="TButton")

        # Recreate progress indicator if expanded
        if self.expanded:
            self._create_progress_indicator()

    def _can_navigate_to_step(self, step_index: int) -> bool:
        """Check if user can navigate to a specific step with new workflow."""
        return workflow_state.can_navigate_to_step(step_index)

    def refresh_navigation(self):
        """Refresh navigation state (call when workflow state changes)."""
        self._update_navigation_state()
