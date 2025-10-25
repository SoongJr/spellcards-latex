"""Tests for SpellSelectionStep navigation behavior."""

# pylint: disable=unused-argument,import-outside-toplevel,protected-access,duplicate-code

from unittest.mock import MagicMock, patch
import pandas as pd

from spell_card_generator.ui.workflow_steps.spell_selection_step import (
    SpellSelectionStep,
)
from spell_card_generator.ui.workflow_state import workflow_state


class TestSpellSelectionNavigation:
    """Test navigation behavior of SpellSelectionStep."""

    def setup_method(self):
        """Set up test state before each test."""
        # Reset workflow state
        workflow_state.selected_class = None
        workflow_state.selected_spells = []
        workflow_state.conflicts_detected = False
        workflow_state.existing_cards = {}
        workflow_state.overwrite_decisions = {}

        # Initialize navigator to spell_selection step
        workflow_state.navigator.go_to_step("spell_selection")

    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_next_button_navigates_to_urls_when_no_conflicts(
        self, mock_frame_class, mock_tab_manager
    ):
        """
        Test that Next button from spell selection goes to
        documentation URLs when no conflicts exist.
        """
        # Setup: Spells selected, no conflicts
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = False

        # Set navigator to spell_selection step
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("spell_selection")

        # Create a mock navigation callback
        navigation_callback = MagicMock()
        data_loader = MagicMock()
        spell_filter = MagicMock()

        # Create the step
        step = SpellSelectionStep(
            parent_frame=mock_frame_class.return_value,
            step_index=1,
            data_loader=data_loader,
            spell_filter=spell_filter,
            navigation_callback=navigation_callback,
        )

        # Create UI components
        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_next action
        step._go_next()

        # Verify navigation goes to documentation_urls (skipping overwrite)
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "documentation_urls"
            ), f"Expected 'documentation_urls', got '{actual_step_id}'"

    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_next_button_navigates_to_overwrite_when_conflicts_exist(
        self, mock_frame_class, mock_tab_manager
    ):
        """
        Test that Next button from spell selection goes to
        overwrite cards when conflicts exist.
        """
        # Setup: Spells selected, conflicts detected
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = True

        # Set navigator to spell_selection step
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("spell_selection")

        navigation_callback = MagicMock()
        data_loader = MagicMock()
        spell_filter = MagicMock()

        step = SpellSelectionStep(
            parent_frame=mock_frame_class.return_value,
            step_index=1,
            data_loader=data_loader,
            spell_filter=spell_filter,
            navigation_callback=navigation_callback,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_next action
        step._go_next()

        # Verify navigation goes to overwrite_cards
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "overwrite_cards"
            ), f"Expected 'overwrite_cards', got '{actual_step_id}'"

    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_previous_button_navigates_to_class_selection(
        self, mock_frame_class, mock_tab_manager
    ):
        """
        Test that Previous button from spell selection goes back
        to class selection.
        """
        # Setup
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = False

        # Set navigator to spell_selection step
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("spell_selection")

        navigation_callback = MagicMock()
        data_loader = MagicMock()
        spell_filter = MagicMock()

        step = SpellSelectionStep(
            parent_frame=mock_frame_class.return_value,
            step_index=1,
            data_loader=data_loader,
            spell_filter=spell_filter,
            navigation_callback=navigation_callback,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_previous action
        step._go_previous()

        # Should go back to class_selection
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "class_selection"
            ), f"Expected 'class_selection', got '{actual_step_id}'"
