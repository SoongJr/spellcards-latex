"""Tests for OverwriteCardsStep navigation behavior."""

# pylint: disable=unused-argument,import-outside-toplevel,protected-access

from unittest.mock import MagicMock, patch
import pandas as pd

from spell_card_generator.ui.workflow_steps.overwrite_cards_step import (
    OverwriteCardsStep,
)
from spell_card_generator.ui.workflow_state import workflow_state


class TestOverwriteCardsNavigation:
    """Test navigation behavior of OverwriteCardsStep."""

    def setup_method(self):
        """Set up test state before each test."""
        # Reset workflow state
        workflow_state.selected_class = None
        workflow_state.selected_spells = []
        workflow_state.conflicts_detected = False
        workflow_state.existing_cards = {}
        workflow_state.overwrite_decisions = {}

        # Initialize navigator to overwrite_cards step
        workflow_state.navigator.go_to_step("overwrite_cards")

    @patch("tkinter.ttk.Frame")
    def test_next_button_navigates_to_documentation_urls(self, mock_frame_class):
        """
        Test that Next button from overwrite cards goes to
        documentation URLs.
        """
        # Setup: Conflicts exist and are resolved
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = True
        workflow_state.existing_cards = {"Fireball": {}}
        workflow_state.overwrite_decisions = {"Fireball": True}

        # Set navigator to overwrite_cards step
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("overwrite_cards")

        # Create a mock navigation callback
        navigation_callback = MagicMock()

        # Create the step
        step = OverwriteCardsStep(
            parent_frame=mock_frame_class.return_value,
            step_index=2,
            navigation_callback=navigation_callback,
        )

        # Create UI components
        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_next action
        step._go_next()

        # Verify navigation goes to documentation_urls
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "documentation_urls"
            ), f"Expected 'documentation_urls', got '{actual_step_id}'"

    @patch("tkinter.ttk.Frame")
    def test_previous_button_navigates_to_spell_selection(self, mock_frame_class):
        """
        Test that Previous button from overwrite cards goes back
        to spell selection.
        """
        # Setup
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = True

        # Set navigator to overwrite_cards step
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("overwrite_cards")

        navigation_callback = MagicMock()

        step = OverwriteCardsStep(
            parent_frame=mock_frame_class.return_value,
            step_index=2,
            navigation_callback=navigation_callback,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_previous action
        step._go_previous()

        # Should go back to spell_selection
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "spell_selection"
            ), f"Expected 'spell_selection', got '{actual_step_id}'"

    @patch("tkinter.ttk.Frame")
    def test_navigation_skips_overwrite_when_no_conflicts(self, mock_frame_class):
        """
        Test that overwrite step is skipped when no conflicts exist.
        This verifies the conditional step visibility logic.
        """
        # Setup: No conflicts
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = False

        # Refresh navigator state
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )

        # Verify overwrite_cards step is not accessible
        overwrite_step = workflow_state.navigator.get_step_by_id("overwrite_cards")
        assert overwrite_step is not None
        assert (
            not overwrite_step.is_accessible
        ), "Overwrite step should not be accessible without conflicts"
