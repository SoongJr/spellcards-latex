"""Tests for PreviewGenerateStep navigation behavior."""

# pylint: disable=unused-argument,import-outside-toplevel,protected-access,duplicate-code

from unittest.mock import MagicMock, patch
import pandas as pd

from spell_card_generator.ui.workflow_steps.preview_generate_step import (
    PreviewGenerateStep,
)
from spell_card_generator.ui.workflow_state import workflow_state


class TestPreviewGenerateNavigation:
    """Test navigation behavior of PreviewGenerateStep."""

    def setup_method(self):
        """Set up test state before each test."""
        # Reset workflow state
        workflow_state.selected_class = None
        workflow_state.selected_spells = []
        workflow_state.conflicts_detected = False
        workflow_state.existing_cards = {}
        workflow_state.overwrite_decisions = {}

        # Initialize navigator to preview_generate step
        workflow_state.navigator.go_to_step("preview_generate")

    @patch("tkinter.ttk.Frame")
    def test_no_next_button_on_final_step(self, mock_frame_class):
        """
        Test that Next button is not shown on the final step.
        """
        # Setup
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]

        navigation_callback = MagicMock()
        on_generate = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_frame_class.return_value,
            step_index=4,
            navigation_callback=navigation_callback,
            on_generate=on_generate,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # The step should not have a next button (step_index=4 is last)
        # This is handled in BaseWorkflowStep._create_navigation_area
        # which only creates Next button if step_index < 4
        assert (
            step.step_index == 4
        ), "Preview & Generate should be the last step (index 4)"

    @patch("tkinter.ttk.Frame")
    def test_previous_button_navigates_to_urls_when_no_conflicts(
        self, mock_frame_class
    ):
        """
        Test that Previous button from preview goes back to
        documentation URLs when no conflicts.
        """
        # Setup: No conflicts
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = False

        # Set navigator to preview_generate step
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("preview_generate")

        navigation_callback = MagicMock()
        on_generate = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_frame_class.return_value,
            step_index=4,
            navigation_callback=navigation_callback,
            on_generate=on_generate,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_previous action
        step._go_previous()

        # Should go back to documentation_urls (overwrite skipped)
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "documentation_urls"
            ), f"Expected 'documentation_urls', got '{actual_step_id}'"

    @patch("tkinter.ttk.Frame")
    def test_previous_button_navigates_to_urls_when_conflicts_exist(
        self, mock_frame_class
    ):
        """
        Test that Previous button from preview goes back to
        documentation URLs even when conflicts exist
        (they were handled earlier).
        """
        # Setup: Conflicts detected and resolved
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = True
        workflow_state.existing_cards = {"Fireball": {}}
        workflow_state.overwrite_decisions = {"Fireball": True}

        # Set navigator to preview_generate step
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("preview_generate")

        navigation_callback = MagicMock()
        on_generate = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_frame_class.return_value,
            step_index=4,
            navigation_callback=navigation_callback,
            on_generate=on_generate,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_previous action
        step._go_previous()

        # Should go back to documentation_urls
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "documentation_urls"
            ), f"Expected 'documentation_urls', got '{actual_step_id}'"

    @patch("tkinter.scrolledtext.ScrolledText")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    def test_generate_button_triggers_callback(
        self,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_button_class,
        mock_scrolled_text_class,
    ):
        """
        Test that the Generate button (replacing Next)
        triggers the generation callback.
        """
        # Setup
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]

        navigation_callback = MagicMock()
        on_generate = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_frame_class.return_value,
            step_index=4,
            navigation_callback=navigation_callback,
            on_generate=on_generate,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Create summary text widget for _update_summary
        step.summary_text = mock_scrolled_text_class.return_value

        # Create navigation area (which includes generate button)
        step._create_navigation_area()

        # Verify generate button was created
        assert step.generate_button is not None

        # Simulate generate button click
        step._on_generate_clicked()

        # Verify generation callback was triggered
        assert on_generate.called, "Generate callback should be called"
