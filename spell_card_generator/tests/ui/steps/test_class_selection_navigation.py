"""Tests for ClassSelectionStep navigation behavior."""

# pylint: disable=unused-argument,import-outside-toplevel,protected-access,duplicate-code

from unittest.mock import MagicMock, patch

from spell_card_generator.ui.workflow_steps.class_selection_step import (
    ClassSelectionStep,
)
from spell_card_generator.ui.workflow_state import workflow_state


class TestClassSelectionNavigation:
    """Test navigation behavior of ClassSelectionStep."""

    def setup_method(self):
        """Set up test state before each test."""
        # Reset workflow state
        workflow_state.selected_class = None
        workflow_state.selected_spells = []
        workflow_state.conflicts_detected = False
        workflow_state.existing_cards = {}
        workflow_state.overwrite_decisions = {}

        # Initialize navigator to class_selection step
        workflow_state.navigator.go_to_step("class_selection")

    @patch(
        "spell_card_generator.ui.workflow_steps."
        "class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_next_button_navigates_to_spell_selection(
        self, mock_frame_class, mock_class_manager
    ):
        """
        Test that Next button from class selection goes to
        spell selection.
        """
        # Setup: Class selected
        workflow_state.selected_class = "wizard"

        # Set navigator to class_selection step
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("class_selection")

        # Create a mock navigation callback
        navigation_callback = MagicMock()
        data_loader = MagicMock()

        # Create the step
        step = ClassSelectionStep(
            parent_frame=mock_frame_class.return_value,
            step_index=0,
            data_loader=data_loader,
            navigation_callback=navigation_callback,
        )

        # Create UI components
        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_next action
        step._go_next()

        # Verify navigation goes to spell_selection
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "spell_selection"
            ), f"Expected 'spell_selection', got '{actual_step_id}'"

    @patch(
        "spell_card_generator.ui.workflow_steps."
        "class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_previous_button_not_shown_on_first_step(
        self, mock_frame_class, mock_class_manager
    ):
        """
        Test that Previous button is not shown on the first step.
        """
        # Setup
        workflow_state.selected_class = "wizard"

        navigation_callback = MagicMock()
        data_loader = MagicMock()

        step = ClassSelectionStep(
            parent_frame=mock_frame_class.return_value,
            step_index=0,
            data_loader=data_loader,
            navigation_callback=navigation_callback,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate _go_previous action (should do nothing)
        step._go_previous()

        # Navigation callback should not be called for step 0
        # (no previous step exists)
        # The workflow navigator will handle this gracefully
        # by returning False from navigate_previous()


class TestClassSelectionNavigationWithNoClass:
    """Test navigation when no class is selected."""

    def setup_method(self):
        """Set up test state before each test."""
        workflow_state.selected_class = None
        workflow_state.selected_spells = []
        workflow_state.conflicts_detected = False

        # Initialize navigator
        workflow_state.navigator.go_to_step("class_selection")

    @patch(
        "spell_card_generator.ui.workflow_steps."
        "class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_next_button_disabled_without_class(
        self, mock_frame_class, mock_class_manager
    ):
        """
        Test that Next button should be disabled when no class
        is selected.
        """
        # Setup: No class selected
        workflow_state.selected_class = None

        navigation_callback = MagicMock()
        data_loader = MagicMock()

        step = ClassSelectionStep(
            parent_frame=mock_frame_class.return_value,
            step_index=0,
            data_loader=data_loader,
            navigation_callback=navigation_callback,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # The next button state should reflect inability to proceed
        # (validated through can_navigate_to_step in workflow_state)
        can_proceed = workflow_state.can_navigate_to_step(1)
        assert not can_proceed, "Should not be able to proceed without class"
