"""Base class for workflow steps with navigation support."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from abc import ABC, abstractmethod

from spell_card_generator.ui.workflow_state import workflow_state


class BaseWorkflowStep(ABC):
    """Base class for all workflow steps with navigation support."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        navigation_callback: Optional[Callable[[int], None]] = None,
    ):
        self.parent_frame = parent_frame
        self.step_index = step_index
        self.navigation_callback = navigation_callback

        # Main container frames
        self.main_frame: Optional[ttk.Frame] = None
        self.content_frame: Optional[ttk.Frame] = None
        self.navigation_frame: Optional[ttk.Frame] = None

        # Navigation buttons
        self.previous_button: Optional[ttk.Button] = None
        self.next_button: Optional[ttk.Button] = None

    def create_ui(self):
        """Create the complete UI including content and navigation."""
        # Clear any existing content
        if self.main_frame:
            self.main_frame.destroy()

        # Create main container using grid for better control over resizing priorities
        self.main_frame = ttk.Frame(self.parent_frame)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure parent to expand the main frame
        self.parent_frame.rowconfigure(0, weight=1)
        self.parent_frame.columnconfigure(0, weight=1)

        # Configure main frame grid - content gets most weight, navigation has fixed size
        self.main_frame.rowconfigure(0, weight=1)  # Content area expandable
        self.main_frame.rowconfigure(1, weight=0)  # Navigation area fixed size
        self.main_frame.columnconfigure(0, weight=1)

        # Create content area (most of the space) - using grid for precise control
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20
        )

        # Create step-specific content
        self.create_step_content()

        # Create navigation area (bottom) - fixed height, full width
        self._create_navigation_area()

        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()

        # Initial navigation state update
        self._update_navigation_state()

    @abstractmethod
    def create_step_content(self):
        """Create the step-specific content. Must be implemented by subclasses."""

    def _create_navigation_area(self):
        """Create the navigation buttons area with high priority."""
        # Navigation frame at bottom - using grid for priority control
        self.navigation_frame = ttk.Frame(self.main_frame)
        self.navigation_frame.grid(
            row=1, column=0, sticky=(tk.W, tk.E), padx=20, pady=(0, 20)
        )

        # Configure navigation frame to expand horizontally
        self.navigation_frame.columnconfigure(0, weight=1)

        # Button container on the right side - this will stay visible even when window shrinks
        button_container = ttk.Frame(self.navigation_frame)
        button_container.grid(row=0, column=0, sticky=tk.E)

        # Previous button (left in container)
        if self.step_index > 0:  # Don't show Previous on first step
            self.previous_button = ttk.Button(
                button_container,
                text="Previous",
                command=self._go_previous,
            )
            # Set underline for 'P' character (position 0)
            self.previous_button.configure(underline=0)
            self.previous_button.grid(row=0, column=0, padx=(0, 5))

        # Next button (right in container)
        if self.step_index < 5:  # Don't show Next on last step
            self.next_button = ttk.Button(
                button_container,
                text="Next",
                command=self._go_next,
            )
            # Set underline for 'N' character (position 0)
            self.next_button.configure(underline=0)
            next_col = 1 if self.step_index > 0 else 0
            self.next_button.grid(row=0, column=next_col, padx=5)

    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for navigation."""
        # Bind keyboard shortcuts to the parent frame so they work when step is active
        self.parent_frame.bind_all("<Alt-p>", lambda e: self._go_previous())
        self.parent_frame.bind_all("<Alt-P>", lambda e: self._go_previous())
        self.parent_frame.bind_all("<Alt-n>", lambda e: self._go_next())
        self.parent_frame.bind_all("<Alt-N>", lambda e: self._go_next())

    def _go_previous(self):
        """Navigate to previous step."""
        if self.step_index > 0 and self.navigation_callback:
            self.navigation_callback(self.step_index - 1)

    def _go_next(self):
        """Navigate to next step."""
        self._navigate_to_next_step()

    def _navigate_to_next_step(self):
        """Common navigation logic for going to next step."""
        if self.step_index < 5:  # Total of 6 steps (0-5)
            # Check if we can navigate to next step
            next_step = self.step_index + 1
            if workflow_state.can_navigate_to_step(next_step):
                if self.navigation_callback:
                    self.navigation_callback(next_step)
            else:
                self._show_navigation_warning(next_step)

    def _show_navigation_warning(self, step_index: int):
        """Show warning when user tries to access unavailable step."""
        # This can be overridden by subclasses for custom warnings
        if step_index == 1 and not workflow_state.selected_class:
            self._show_warning("Please select a character class first.")
        elif step_index > 1 and len(workflow_state.selected_spells) == 0:
            self._show_warning("Please select spells before proceeding to later steps.")

    def _show_warning(self, message: str):
        """Show a simple warning message (can be overridden for better UI)."""
        # For now, just print - could be enhanced with proper dialog
        print(f"Navigation Warning: {message}")

    def _update_navigation_state(self):
        """Update navigation button states based on workflow state."""
        # Update Next button state
        if self.next_button:
            next_step = self.step_index + 1
            can_proceed = workflow_state.can_navigate_to_step(next_step)
            self.next_button.config(state="normal" if can_proceed else "disabled")

        # Previous button is always enabled (if it exists)
        if self.previous_button:
            self.previous_button.config(state="normal")

    def refresh_ui(self):
        """Refresh the UI when workflow state changes."""
        self._update_navigation_state()
        # Can be overridden by subclasses for additional refresh logic

    def on_step_validation_changed(self):
        """Called when this step's validation state changes."""
        # Update navigation state when step validation changes
        self._update_navigation_state()

    def destroy(self):
        """Clean up resources."""
        # Unbind keyboard shortcuts
        if self.parent_frame:
            try:
                self.parent_frame.unbind_all("<Alt-p>")
                self.parent_frame.unbind_all("<Alt-P>")
                self.parent_frame.unbind_all("<Alt-n>")
                self.parent_frame.unbind_all("<Alt-N>")
            except tk.TclError:
                # Widget may already be destroyed
                pass

        if self.main_frame:
            self.main_frame.destroy()
            self.main_frame = None

        self.content_frame = None
        self.navigation_frame = None
        self.previous_button = None
        self.next_button = None
