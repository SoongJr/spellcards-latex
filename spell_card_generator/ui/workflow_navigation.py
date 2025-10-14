"""Linked list-based workflow navigation system."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class StepCondition(Enum):
    """Conditions that determine step visibility and accessibility."""

    ALWAYS_VISIBLE = "always_visible"
    REQUIRES_CLASS = "requires_class"
    REQUIRES_SPELLS = "requires_spells"
    REQUIRES_CONFLICTS = "requires_conflicts"


@dataclass
class WorkflowStep:
    """A single step in the workflow with navigation links."""

    # Step identity
    step_id: str
    name: str
    icon: str
    description: str

    # Navigation links (like a doubly-linked list)
    previous_step: Optional["WorkflowStep"] = None
    next_step: Optional["WorkflowStep"] = None

    # Step behavior
    required: bool = True
    condition: StepCondition = StepCondition.ALWAYS_VISIBLE

    # State tracking
    is_valid: bool = False
    is_accessible: bool = False
    is_visible: bool = True

    # Additional metadata
    step_data: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize step data dictionary."""
        if self.step_data is None:
            self.step_data = {}


class WorkflowNavigator:
    """Manages workflow navigation using a linked list of steps."""

    def __init__(self):
        self.first_step: Optional[WorkflowStep] = None
        self.current_step: Optional[WorkflowStep] = None
        self.steps_by_id: Dict[str, WorkflowStep] = {}

        # Note: Condition evaluation is now done through method parameters to avoid circular imports

    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow chain."""
        self.steps_by_id[step.step_id] = step

        if self.first_step is None:
            # First step in the chain
            self.first_step = step
            self.current_step = step
        else:
            # Find the last step and link the new step
            last_step = self._find_last_step()
            last_step.next_step = step
            step.previous_step = last_step

    def insert_step_after(self, step: WorkflowStep, after_step_id: str) -> None:
        """Insert a step after another step in the chain."""
        after_step = self.steps_by_id.get(after_step_id)
        if not after_step:
            raise ValueError(f"Step '{after_step_id}' not found")

        # Store references
        old_next = after_step.next_step

        # Link the new step
        after_step.next_step = step
        step.previous_step = after_step
        step.next_step = old_next

        # Update old next step's previous link
        if old_next:
            old_next.previous_step = step

        # Add to lookup
        self.steps_by_id[step.step_id] = step

    def remove_step(self, step_id: str) -> bool:
        """Remove a step from the workflow chain."""
        step = self.steps_by_id.get(step_id)
        if not step:
            return False

        # Update navigation links
        if step.previous_step:
            step.previous_step.next_step = step.next_step
        else:
            # This was the first step
            self.first_step = step.next_step

        if step.next_step:
            step.next_step.previous_step = step.previous_step

        # Update current step if needed
        if self.current_step == step:
            self.current_step = step.next_step or step.previous_step

        # Remove from lookup
        del self.steps_by_id[step_id]
        return True

    def go_to_step(self, step_id: str) -> bool:
        """Navigate to a specific step."""
        step = self.steps_by_id.get(step_id)
        if not step:
            return False

        if not step.is_accessible:
            return False

        self.current_step = step
        return True

    def go_to_next(self) -> bool:
        """Navigate to the next accessible step."""
        if not self.current_step or not self.current_step.next_step:
            return False

        next_step = self._find_next_accessible_step(self.current_step)
        if next_step:
            self.current_step = next_step
            return True

        return False

    def go_to_previous(self) -> bool:
        """Navigate to the previous accessible step."""
        if not self.current_step or not self.current_step.previous_step:
            return False

        prev_step = self._find_previous_accessible_step(self.current_step)
        if prev_step:
            self.current_step = prev_step
            return True

        return False

    def has_next(self) -> bool:
        """Check if there's a next accessible step."""
        if not self.current_step:
            return False
        return self._find_next_accessible_step(self.current_step) is not None

    def has_previous(self) -> bool:
        """Check if there's a previous accessible step."""
        if not self.current_step:
            return False
        return self._find_previous_accessible_step(self.current_step) is not None

    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get the current step."""
        return self.current_step

    def get_current_step_index(self) -> int:
        """Get the current step's index (for compatibility)."""
        if not self.current_step:
            return 0

        index = 0
        step = self.first_step
        while step and step != self.current_step:
            if step.is_visible:
                index += 1
            step = step.next_step
        return index

    def get_step_by_id(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by its ID."""
        return self.steps_by_id.get(step_id)

    def get_visible_steps(self) -> list[WorkflowStep]:
        """Get all currently visible steps in order."""
        visible_steps = []
        step = self.first_step
        while step:
            if step.is_visible:
                visible_steps.append(step)
            step = step.next_step
        return visible_steps

    def refresh_step_states(
        self, selected_class=None, selected_spells=None, conflicts_detected=False
    ) -> None:
        """Refresh visibility and accessibility of all steps based on conditions."""
        step = self.first_step
        while step:
            # Evaluate visibility condition
            step.is_visible = self._evaluate_visibility(
                step.condition, selected_class, selected_spells, conflicts_detected
            )

            # Evaluate accessibility (visible + prerequisites met)
            step.is_accessible = step.is_visible and self._evaluate_accessibility(
                step, selected_class, selected_spells, conflicts_detected
            )

            step = step.next_step

    def _find_last_step(self) -> WorkflowStep:
        """Find the last step in the chain."""
        step = self.first_step
        while step.next_step:
            step = step.next_step
        return step

    def _find_next_accessible_step(
        self, from_step: WorkflowStep
    ) -> Optional[WorkflowStep]:
        """Find the next accessible step from a given step."""
        step = from_step.next_step
        while step:
            if step.is_accessible:
                return step
            step = step.next_step
        return None

    def _find_previous_accessible_step(
        self, from_step: WorkflowStep
    ) -> Optional[WorkflowStep]:
        """Find the previous accessible step from a given step."""
        step = from_step.previous_step
        while step:
            if step.is_accessible:
                return step
            step = step.previous_step
        return None

    def _evaluate_accessibility(
        self,
        step: WorkflowStep,
        selected_class=None,
        selected_spells=None,
        conflicts_detected=False,
    ) -> bool:
        """Evaluate if a step is accessible based on workflow logic."""
        if step.step_id == "class_selection":
            return True  # Always accessible

        if step.step_id == "spell_selection":
            return bool(selected_class)

        if step.step_id == "overwrite_cards":
            return bool(selected_spells and conflicts_detected)

        # All other steps require spells to be selected
        return bool(selected_spells)

    def _evaluate_visibility(
        self,
        condition: StepCondition,
        selected_class=None,
        selected_spells=None,
        conflicts_detected=False,
    ) -> bool:
        """Evaluate if a step is visible based on its condition."""
        if condition == StepCondition.ALWAYS_VISIBLE:
            return True
        if condition == StepCondition.REQUIRES_CLASS:
            return bool(selected_class)
        if condition == StepCondition.REQUIRES_SPELLS:
            return bool(selected_spells)
        if condition == StepCondition.REQUIRES_CONFLICTS:
            return bool(conflicts_detected)

        return True  # Default to visible


def create_default_workflow() -> WorkflowNavigator:
    """Create the default spell card generation workflow."""
    navigator = WorkflowNavigator()

    # Define all steps
    steps = [
        WorkflowStep(
            step_id="class_selection",
            name="Class Selection",
            icon="class",
            description="Choose character class",
            required=True,
            condition=StepCondition.ALWAYS_VISIBLE,
        ),
        WorkflowStep(
            step_id="spell_selection",
            name="Spell Selection",
            icon="spell",
            description="Select spells to generate",
            required=True,
            condition=StepCondition.REQUIRES_CLASS,
        ),
        WorkflowStep(
            step_id="overwrite_cards",
            name="Overwrite Cards",
            icon="warning",
            description="Manage existing card conflicts",
            required=True,
            condition=StepCondition.REQUIRES_CONFLICTS,
        ),
        WorkflowStep(
            step_id="documentation_urls",
            name="Documentation & Language URLs",
            icon="link",
            description="Custom spell references and multi-language support",
            required=False,
            condition=StepCondition.REQUIRES_SPELLS,
        ),
        WorkflowStep(
            step_id="preview_generate",
            name="Preview & Generate",
            icon="generate",
            description="Review and generate cards",
            required=True,
            condition=StepCondition.REQUIRES_SPELLS,
        ),
    ]

    # Add steps to navigator (creates the linked list)
    for step in steps:
        navigator.add_step(step)

    return navigator
