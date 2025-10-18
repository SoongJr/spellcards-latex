"""Tests for spell selection step."""

from unittest.mock import MagicMock, patch
from spell_card_generator.ui.workflow_steps.spell_selection_step import (
    SpellSelectionStep,
)


class TestSpellSelectionStep:
    """Test SpellSelectionStep initialization and setup."""

    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_initialization(self, _mock_frame_class, _mock_tab_manager_class):
        """Test SpellSelectionStep initializes correctly."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_nav_callback = MagicMock()
        mock_selection_callback = MagicMock()

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
            navigation_callback=mock_nav_callback,
            on_selection_changed=mock_selection_callback,
        )

        assert step.parent_frame == mock_parent
        assert step.step_index == 1
        assert step.data_loader == mock_data_loader
        assert step.spell_filter == mock_spell_filter
        assert step.navigation_callback == mock_nav_callback
        assert step.on_selection_changed == mock_selection_callback
        assert step.spell_tab_manager is None  # Not created until create_step_content

    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_optional_callbacks(self, _mock_frame_class, _mock_tab_manager_class):
        """Test that callbacks are optional."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )

        assert step.navigation_callback is None
        assert step.on_selection_changed is None


class TestSpellSelectionStepWithClass:
    """Test SpellSelectionStep when class is selected."""

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_create_content_with_class_selected(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        mock_tab_manager_class,
        mock_workflow_state,
    ):
        """Test create_step_content when class is selected."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = "wizard"
        mock_workflow_state.selected_spells = []

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify SpellTabManager was created
        assert step.spell_tab_manager is not None
        mock_tab_manager_class.assert_called_once()

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_updates_tabs_with_selected_class(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        mock_tab_manager_class,
        mock_workflow_state,
    ):
        """Test that tabs are updated with the selected class."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = "wizard"
        mock_workflow_state.selected_spells = []
        mock_tab_manager_instance = MagicMock()
        mock_tab_manager_class.return_value = mock_tab_manager_instance

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify update_tabs was called with the selected class
        mock_tab_manager_instance.update_tabs.assert_called_once_with({"wizard"})

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_restores_previous_spell_selections(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        mock_tab_manager_class,
        mock_workflow_state,
    ):
        """Test that previously selected spells are restored."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = "wizard"
        mock_workflow_state.selected_spells = [
            ("wizard", "Fireball", MagicMock()),
            ("wizard", "Magic Missile", MagicMock()),
        ]
        mock_tab_manager_instance = MagicMock()
        mock_tab_manager_instance.selected_spells_state = {}
        mock_tab_manager_class.return_value = mock_tab_manager_instance

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify spell selections were restored
        assert "Fireball" in mock_tab_manager_instance.selected_spells_state
        assert "Magic Missile" in mock_tab_manager_instance.selected_spells_state


class TestSpellSelectionStepWithoutClass:
    """Test SpellSelectionStep when no class is selected."""

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_create_content_without_class(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        mock_tab_manager_class,
        mock_workflow_state,
    ):
        """Test create_step_content when no class is selected."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = None

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify SpellTabManager was NOT created
        assert step.spell_tab_manager is None
        mock_tab_manager_class.assert_not_called()

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_shows_prompt_without_class(
        self,
        _mock_button_class,
        _mock_frame_class,
        mock_label_class,
        mock_workflow_state,
    ):
        """Test that prompt is shown when no class selected."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = None

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify warning label was created
        assert mock_label_class.called
        # Check for warning text in calls
        label_calls = [str(call) for call in mock_label_class.call_args_list]
        assert any("No character class" in str(call) for call in label_calls)


class TestSpellSelectionStepInteraction:
    """Test user interaction with SpellSelectionStep."""

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_spell_selection_updates_workflow_state(
        self, _mock_frame_class, mock_tab_manager_class, mock_workflow_state
    ):
        """Test that spell selection updates workflow state."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = "wizard"
        mock_workflow_state.selected_spells = []

        mock_tab_manager_instance = MagicMock()
        mock_tab_manager_instance.get_selected_spells.return_value = [
            ("wizard", "Fireball", MagicMock())
        ]
        mock_tab_manager_class.return_value = mock_tab_manager_instance

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.spell_tab_manager = mock_tab_manager_instance

        # Simulate spell selection change
        step._on_spell_selection_changed()

        # Verify workflow state was updated (check structure, not identity)
        assert len(mock_workflow_state.selected_spells) == 1
        assert mock_workflow_state.selected_spells[0][0] == "wizard"
        assert mock_workflow_state.selected_spells[0][1] == "Fireball"
        assert isinstance(mock_workflow_state.selected_spells[0][2], MagicMock)

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_spell_selection_validates_step(
        self, _mock_frame_class, _mock_tab_manager_class, mock_workflow_state
    ):
        """Test that spell selection validates the step."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = "wizard"
        mock_workflow_state.selected_spells = []

        mock_tab_manager_instance = MagicMock()
        mock_tab_manager_instance.get_selected_spells.return_value = [
            ("wizard", "Fireball", MagicMock())
        ]

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.spell_tab_manager = mock_tab_manager_instance

        # Simulate spell selection change
        step._on_spell_selection_changed()

        # Verify step was marked as valid
        mock_workflow_state.set_step_valid.assert_called_with(1, True)

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_spell_selection_triggers_callback(
        self, _mock_frame_class, _mock_tab_manager_class, mock_workflow_state
    ):
        """Test that spell selection triggers on_selection_changed callback."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_callback = MagicMock()
        mock_workflow_state.selected_class = "wizard"
        mock_workflow_state.selected_spells = []

        mock_tab_manager_instance = MagicMock()
        mock_tab_manager_instance.get_selected_spells.return_value = [
            ("wizard", "Fireball", MagicMock())
        ]

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
            on_selection_changed=mock_callback,
        )
        step.spell_tab_manager = mock_tab_manager_instance

        # Simulate spell selection change
        step._on_spell_selection_changed()

        # Verify callback was invoked
        mock_callback.assert_called_once()

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_double_click_navigation(
        self, _mock_frame_class, _mock_tab_manager_class, mock_workflow_state
    ):
        """Test double-click triggers navigation when spells selected."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_spells = [("wizard", "Fireball", MagicMock())]
        mock_workflow_state.can_navigate_to_step.return_value = True

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step._go_next = MagicMock()  # type: ignore[method-assign]

        # Simulate double-click
        step._on_double_click()

        # Verify navigation was triggered
        step._go_next.assert_called_once()


class TestSpellSelectionStepRefresh:
    """Test SpellSelectionStep UI refresh functionality."""

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_refresh_creates_interface_when_class_selected(
        self, _mock_frame_class, _mock_tab_manager_class, mock_workflow_state
    ):
        """Test refresh creates interface when class is selected."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = "wizard"

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.create_ui = MagicMock()  # type: ignore[method-assign]

        # Simulate class selection (no manager yet)
        step.refresh_ui()

        # Verify UI was recreated
        step.create_ui.assert_called_once()

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.spell_selection_step.SpellTabManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_refresh_updates_existing_interface(
        self, _mock_frame_class, _mock_tab_manager_class, mock_workflow_state
    ):
        """Test refresh updates existing interface."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()
        mock_workflow_state.selected_class = "cleric"
        mock_tab_manager_instance = MagicMock()

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.spell_tab_manager = mock_tab_manager_instance

        # Refresh with existing manager
        step.refresh_ui()

        # Verify tabs were updated
        mock_tab_manager_instance.update_tabs.assert_called_once_with({"cleric"})

    @patch("spell_card_generator.ui.workflow_steps.spell_selection_step.workflow_state")
    @patch("tkinter.ttk.Frame")
    def test_destroy_cleans_up_resources(self, _mock_frame_class, _mock_workflow_state):
        """Test destroy method cleans up resources."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_spell_filter = MagicMock()

        step = SpellSelectionStep(
            parent_frame=mock_parent,
            step_index=1,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )
        step.spell_tab_manager = MagicMock()

        # Create a mock frame to track destroy calls
        mock_main_frame = MagicMock()
        step.main_frame = mock_main_frame

        # Destroy
        step.destroy()

        # Verify cleanup
        assert step.spell_tab_manager is None
        assert step.main_frame is None  # Set to None by parent's destroy()
        assert (
            mock_main_frame.destroy.called
        )  # But destroy was called on the original frame
