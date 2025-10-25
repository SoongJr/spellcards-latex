"""Tests for DocumentationURLsStep navigation behavior."""

# pylint: disable=unused-argument,import-outside-toplevel,protected-access,duplicate-code

from unittest.mock import MagicMock, patch
import pandas as pd

from spell_card_generator.ui.workflow_steps.documentation_urls_step import (
    DocumentationURLsStep,
)
from spell_card_generator.ui.workflow_state import workflow_state


class TestDocumentationURLsNavigation:
    """Test navigation behavior of DocumentationURLsStep."""

    def setup_method(self):
        """Set up test state before each test."""
        # Reset workflow state
        workflow_state.selected_class = None
        workflow_state.selected_spells = []
        workflow_state.conflicts_detected = False
        workflow_state.existing_cards = {}
        workflow_state.overwrite_decisions = {}

        # Initialize navigator to documentation_urls step (step_id="documentation_urls")
        workflow_state.navigator.go_to_step("documentation_urls")

    @patch("tkinter.ttk.Frame")
    def test_next_button_navigates_to_preview_when_no_conflicts(self, mock_frame_class):
        """
        Test that Next button from URLs step goes to Preview
        when no conflicts exist.
        """
        # Setup: No conflicts detected
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = False  # No conflicts

        # Set navigator to documentation_urls step FIRST
        workflow_state.navigator.refresh_step_states(
            workflow_state.selected_class,
            workflow_state.selected_spells,
            workflow_state.conflicts_detected,
        )
        workflow_state.navigator.go_to_step("documentation_urls")

        # Create a mock navigation callback to track where we navigate
        navigation_callback = MagicMock()

        # Create the step (step_index=3 for documentation_urls)
        step = DocumentationURLsStep(
            parent_frame=mock_frame_class.return_value,
            step_index=3,
            navigation_callback=navigation_callback,
        )

        # Create UI components
        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_next action triggered by the Next button
        # This should navigate to preview_generate (ID "preview_generate")
        step._go_next()

        # Verify navigation callback called with "preview_generate" ID
        # This should be the step AFTER documentation_urls
        assert navigation_callback.called, "Navigation callback should be called"

        # Get the actual call argument
        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "preview_generate"
            ), f"Expected 'preview_generate', got '{actual_step_id}'"

    @patch("tkinter.ttk.Frame")
    def test_next_button_navigates_to_preview_when_conflicts_exist(
        self, mock_frame_class
    ):
        """
        Test that Next button from URLs step goes to Preview even
        when conflicts exist.
        """
        # Setup: Conflicts detected (but already resolved in earlier step)
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = True  # Conflicts exist

        # Create a mock navigation callback to track where we navigate
        navigation_callback = MagicMock()

        # Create the step (step_index=3 for documentation_urls)
        step = DocumentationURLsStep(
            parent_frame=mock_frame_class.return_value,
            step_index=3,
            navigation_callback=navigation_callback,
        )

        # Create UI components
        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_next action
        step._go_next()

        # Verify navigation goes to preview_generate
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "preview_generate"
            ), f"Expected 'preview_generate', got '{actual_step_id}'"

    @patch("tkinter.ttk.Frame")
    def test_previous_button_navigates_correctly_without_conflicts(
        self, mock_frame_class
    ):
        """
        Test that Previous button from URLs step goes back to
        spell selection when no conflicts.
        """
        # Setup: No conflicts
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = False

        navigation_callback = MagicMock()

        step = DocumentationURLsStep(
            parent_frame=mock_frame_class.return_value,
            step_index=3,
            navigation_callback=navigation_callback,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_previous action
        step._go_previous()

        # Should go back to spell_selection (step 1)
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "spell_selection"
            ), f"Expected 'spell_selection', got '{actual_step_id}'"

    @patch("tkinter.ttk.Frame")
    def test_previous_button_navigates_correctly_with_conflicts(self, mock_frame_class):
        """
        Test that Previous button from URLs step goes back to
        overwrite_cards when conflicts exist.
        """
        # Setup: Conflicts detected
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = True

        navigation_callback = MagicMock()

        step = DocumentationURLsStep(
            parent_frame=mock_frame_class.return_value,
            step_index=3,
            navigation_callback=navigation_callback,
        )

        step.main_frame = MagicMock()
        step.content_frame = MagicMock()
        step.navigation_frame = MagicMock()

        # Simulate the _go_previous action
        step._go_previous()

        # Should go back to overwrite_cards (step 2)
        assert navigation_callback.called, "Navigation callback should be called"

        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            assert (
                actual_step_id == "overwrite_cards"
            ), f"Expected 'overwrite_cards', got '{actual_step_id}'"


class TestOtherStepsNavigationComparison:
    """Test that other steps navigate correctly for comparison."""

    def setup_method(self):
        """Set up test state before each test."""
        workflow_state.selected_class = None
        workflow_state.selected_spells = []
        workflow_state.conflicts_detected = False

        # Initialize navigator to appropriate step for testing
        workflow_state.navigator.go_to_step("spell_selection")

    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_spell_selection_next_navigates_correctly(
        self, mock_frame_class, mock_tab_manager
    ):
        """Test that Spell Selection step navigates correctly (for comparison)."""
        from spell_card_generator.ui.workflow_steps.spell_selection_step import (
            SpellSelectionStep,
        )

        # Setup
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = False

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

        # Navigate next
        step._go_next()

        # Should navigate forward (not stay on the same step)
        assert navigation_callback.called
        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            # Should NOT be spell_selection again
            assert (
                actual_step_id != "spell_selection"
            ), "Should navigate forward, not stay on same step"

    @patch("tkinter.ttk.Frame")
    def test_overwrite_cards_next_navigates_correctly(self, mock_frame_class):
        """Test that Overwrite Cards step navigates correctly (for comparison)."""
        from spell_card_generator.ui.workflow_steps.overwrite_cards_step import (
            OverwriteCardsStep,
        )

        # Setup
        workflow_state.selected_class = "wizard"
        spell_data = pd.Series({"name": "Fireball", "level": "3"})
        workflow_state.selected_spells = [("wizard", "Fireball", spell_data)]
        workflow_state.conflicts_detected = True

        # Set navigator to overwrite_cards step FIRST
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

        # Navigate next
        step._go_next()

        # Should navigate forward to documentation_urls
        assert navigation_callback.called
        call_args = navigation_callback.call_args
        if call_args:
            actual_step_id = call_args[0][0]
            # Should go to documentation_urls
            assert (
                actual_step_id == "documentation_urls"
            ), f"Expected 'documentation_urls', got '{actual_step_id}'"
