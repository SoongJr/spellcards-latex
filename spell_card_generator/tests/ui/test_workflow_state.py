"""Tests for workflow state management."""

import pandas as pd

from spell_card_generator.ui.workflow_state import WorkflowState


class TestWorkflowState:
    """Test WorkflowState data class and state management."""

    def test_workflow_state_initialization(self):
        """Test that WorkflowState initializes with correct defaults."""
        state = WorkflowState()

        assert state.selected_class is None
        assert state.selected_spells == []
        assert state.overwrite_existing is False
        assert state.output_directory is None
        assert state.enable_secondary_language is False
        assert state.conflicts_detected is False
        assert isinstance(state.existing_cards, dict)
        assert isinstance(state.overwrite_decisions, dict)
        assert isinstance(state.spell_data_cache, dict)

    def test_spell_data_cache_operations(self):
        """Test spell data cache get/set/remove operations."""
        state = WorkflowState()

        # Test setting data
        state.set_spell_data("Fireball", "primary_url", "http://example.com")
        assert state.get_spell_data("Fireball", "primary_url") == "http://example.com"

        # Test getting with default
        assert state.get_spell_data("Fireball", "nonexistent", "default") == "default"

        # Test multiple keys for same spell
        state.set_spell_data("Fireball", "secondary_url", "http://example.de")
        assert state.get_spell_data("Fireball", "primary_url") == "http://example.com"
        assert state.get_spell_data("Fireball", "secondary_url") == "http://example.de"

        # Test removing spell data
        state.remove_spell_data("Fireball")
        assert state.get_spell_data("Fireball", "primary_url") is None

    def test_spell_filter_state_operations(self):
        """Test spell filter state get/set/reset operations."""
        state = WorkflowState()

        # Test default values
        assert state.get_spell_filter_state("level_filter") == "All"
        assert state.get_spell_filter_state("source_filter") == "All"
        assert state.get_spell_filter_state("search_term") == ""

        # Test setting values
        state.set_spell_filter_state("level_filter", "3")
        state.set_spell_filter_state("search_term", "fire")
        assert state.get_spell_filter_state("level_filter") == "3"
        assert state.get_spell_filter_state("search_term") == "fire"

        # Test reset
        state.reset_spell_filter_state()
        assert state.get_spell_filter_state("level_filter") == "All"
        assert state.get_spell_filter_state("search_term") == ""

    def test_conflict_detection(self):
        """Test conflict detection and management."""
        state = WorkflowState()

        # Initially no conflicts
        assert not state.conflicts_detected
        assert len(state.existing_cards) == 0

        # Add conflicts
        existing_cards = {
            "Fireball": "/path/to/fireball.tex",
            "Magic Missile": "/path/to/magic_missile.tex",
        }
        state.update_conflicts(existing_cards)

        assert state.conflicts_detected
        assert len(state.existing_cards) == 2
        assert len(state.overwrite_decisions) == 2
        assert (
            state.overwrite_decisions["Fireball"] is False
        )  # Default to not overwrite
        assert state.overwrite_decisions["Magic Missile"] is False

    def test_update_conflicts_preserves_existing_decisions(self):
        """Test that updating conflicts preserves existing overwrite decisions."""
        state = WorkflowState()

        # Set initial conflicts with user decisions
        initial_cards = {"Fireball": "/path/to/fireball.tex"}
        state.update_conflicts(initial_cards)
        state.overwrite_decisions["Fireball"] = True

        # Update with additional conflicts
        updated_cards = {
            "Fireball": "/path/to/fireball.tex",
            "Magic Missile": "/path/to/magic_missile.tex",
        }
        state.update_conflicts(updated_cards)

        # Original decision should be preserved
        assert state.overwrite_decisions["Fireball"] is True
        # New spell should have default decision
        assert state.overwrite_decisions["Magic Missile"] is False

    def test_selected_spells_management(self):
        """Test managing selected spells list."""
        state = WorkflowState()

        # Create mock spell data
        spell_series = pd.Series(
            {
                "name": "Fireball",
                "school": "Evocation",
                "wizard": "3",
            }
        )

        # Add spell
        state.selected_spells.append(("Fireball", "3", spell_series))
        assert len(state.selected_spells) == 1
        assert state.selected_spells[0][0] == "Fireball"
        assert state.selected_spells[0][1] == "3"

        # Clear spells
        state.selected_spells.clear()
        assert len(state.selected_spells) == 0

    def test_workflow_navigation_helpers(self):
        """Test workflow navigation helper methods."""
        state = WorkflowState()

        # Test can_navigate_to_step
        assert state.can_navigate_to_step(0)  # Class selection always accessible
        assert not state.can_navigate_to_step(1)  # Spell selection needs class

        # Select a class
        state.selected_class = "wizard"
        assert state.can_navigate_to_step(1)  # Now spell selection is accessible

        # Add spells
        spell_series = pd.Series({"name": "Fireball", "wizard": "3"})
        state.selected_spells.append(("Fireball", "3", spell_series))
        assert state.can_navigate_to_step(3)  # Documentation URLs accessible

        # Overwrite step is navigable (will be skipped if no conflicts)
        assert state.can_navigate_to_step(2)  # Navigable even without conflicts
        state.conflicts_detected = True
        assert state.can_navigate_to_step(2)  # Still accessible with conflicts

    def test_step_validation_state(self):
        """Test step validation state management."""
        state = WorkflowState()

        # Test default validation state
        assert not state.is_step_valid(0)
        assert not state.is_step_valid(1)

        # Set step as valid
        state.set_step_valid(0, True)
        assert state.is_step_valid(0)
        assert not state.is_step_valid(1)  # Other steps still invalid

        # Invalidate step
        state.set_step_valid(0, False)
        assert not state.is_step_valid(0)

    def test_get_next_step_after_spells(self):
        """Test determining next step after spell selection."""
        state = WorkflowState()

        # Without conflicts, skip to generation options
        state.conflicts_detected = False
        assert state.get_next_step_after_spells() == 3

        # With conflicts, go to overwrite management
        state.conflicts_detected = True
        assert state.get_next_step_after_spells() == 2

    def test_reset_step_data(self):
        """Test resetting data for specific steps."""
        state = WorkflowState()

        # Set up spell filter state
        state.set_spell_filter_state("level_filter", "3")
        state.set_spell_filter_state("search_term", "fire")

        # Reset spell selection step (step 1)
        state.reset_step_data(1)

        # Filter state should be reset
        assert state.get_spell_filter_state("level_filter") == "All"
        assert state.get_spell_filter_state("search_term") == ""

        # Set up overwrite data
        state.overwrite_decisions = {"Fireball": True}
        state.conflicts_detected = True

        # Reset overwrite step (step 2)
        state.reset_step_data(2)

        # Overwrite data should be cleared
        assert len(state.overwrite_decisions) == 0
        assert not state.conflicts_detected

    def test_selected_class_management(self):
        """Test class selection state management."""
        state = WorkflowState()

        assert state.selected_class is None

        state.selected_class = "wizard"
        assert state.selected_class == "wizard"

        state.selected_class = "cleric"
        assert state.selected_class == "cleric"

        state.selected_class = None
        assert state.selected_class is None

    def test_output_directory_management(self):
        """Test output directory state management."""
        state = WorkflowState()

        assert state.output_directory is None

        state.output_directory = "/path/to/output"
        assert state.output_directory == "/path/to/output"

    def test_secondary_language_settings(self):
        """Test secondary language configuration."""
        state = WorkflowState()

        # Test defaults
        assert not state.enable_secondary_language
        assert state.secondary_language_code == "de"

        # Enable secondary language
        state.enable_secondary_language = True
        state.secondary_language_code = "fr"

        assert state.enable_secondary_language
        assert state.secondary_language_code == "fr"
