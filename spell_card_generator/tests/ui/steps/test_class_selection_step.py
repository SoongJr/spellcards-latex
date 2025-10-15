"""Tests for class selection step."""

import pytest
from unittest.mock import MagicMock, patch, call
from spell_card_generator.ui.workflow_steps.class_selection_step import (
    ClassSelectionStep,
)


class TestClassSelectionStep:
    """Test ClassSelectionStep initialization and setup."""

    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_initialization(self, mock_frame_class, mock_manager_class):
        """Test ClassSelectionStep initializes correctly."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_callback = MagicMock()
        mock_class_changed = MagicMock()

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
            navigation_callback=mock_callback,
            on_class_changed=mock_class_changed,
        )

        assert step.parent_frame == mock_parent
        assert step.step_index == 0
        assert step.data_loader == mock_data_loader
        assert step.navigation_callback == mock_callback
        assert step.on_class_changed == mock_class_changed
        assert step.class_manager is None  # Not created until create_step_content

    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_create_step_content_creates_manager(
        self,
        mock_button_class,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_manager_class,
    ):
        """Test create_step_content creates class selection manager."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_data_loader.character_classes = {"Core": ["Wizard", "Cleric"]}
        mock_manager_instance = MagicMock()
        mock_manager_class.return_value = mock_manager_instance

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
        )
        step.content_frame = MagicMock()  # Mock the content frame
        step.create_step_content()

        # Verify manager was created
        assert step.class_manager is not None
        mock_manager_class.assert_called_once()

    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_create_step_content_sets_up_tree(
        self,
        mock_button_class,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_manager_class,
    ):
        """Test create_step_content sets up class tree with data."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_data_loader.character_classes = {"Core": ["Wizard", "Cleric"]}
        mock_manager_instance = MagicMock()
        mock_manager_class.return_value = mock_manager_instance

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify setup_class_tree was called
        mock_manager_instance.setup_class_tree.assert_called_once_with(
            {"Core": ["Wizard", "Cleric"]}
        )

    @patch("spell_card_generator.ui.workflow_steps.class_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_restores_previous_selection(
        self,
        mock_button_class,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_manager_class,
        mock_workflow_state,
    ):
        """Test that previously selected class is restored."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_data_loader.character_classes = {"Core": ["Wizard"]}
        mock_manager_instance = MagicMock()
        mock_manager_instance.tree = MagicMock()
        mock_manager_class.return_value = mock_manager_instance
        mock_workflow_state.selected_class = "Wizard"

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify restoration was attempted (tree interactions)
        assert mock_manager_instance.tree.get_children.called

    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_on_class_changed_callback_optional(
        self, mock_frame_class, mock_manager_class
    ):
        """Test that on_class_changed callback is optional."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
            on_class_changed=None,
        )

        assert step.on_class_changed is None


class TestClassSelectionStepInteraction:
    """Test user interaction handling in ClassSelectionStep."""

    @patch("spell_card_generator.ui.workflow_steps.class_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_class_selection_updates_state(
        self, mock_frame_class, mock_manager_class, mock_workflow_state
    ):
        """Test that class selection updates workflow state."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_data_loader.character_classes = {"Core": ["Wizard"]}

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
        )

        # Simulate class selection change
        step._on_class_selection_changed("Wizard")

        # Verify workflow state was updated
        assert mock_workflow_state.selected_class == "Wizard"

    @patch("spell_card_generator.ui.workflow_steps.class_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_class_change_triggers_callback(
        self, mock_frame_class, mock_manager_class, mock_workflow_state
    ):
        """Test that class change triggers on_class_changed callback."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_callback = MagicMock()

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
            on_class_changed=mock_callback,
        )

        # Simulate class selection change
        step._on_class_selection_changed("Wizard")

        # Verify callback was invoked
        mock_callback.assert_called_once()

    @patch("spell_card_generator.ui.workflow_steps.class_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_double_click_navigation(
        self,
        mock_button_class,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_manager_class,
        mock_workflow_state,
    ):
        """Test that double-click is bound for navigation."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()
        mock_data_loader.character_classes = {"Core": ["Wizard"]}
        mock_manager_instance = MagicMock()
        mock_tree = MagicMock()
        mock_manager_instance.tree = mock_tree
        mock_manager_class.return_value = mock_manager_instance

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify double-click binding
        mock_tree.bind.assert_called_with("<Double-1>", step._on_double_click)

    @patch("spell_card_generator.ui.workflow_steps.class_selection_step.workflow_state")
    @patch(
        "spell_card_generator.ui.workflow_steps.class_selection_step.SingleClassSelectionManager"
    )
    @patch("tkinter.ttk.Frame")
    def test_validates_step_when_class_selected(
        self, mock_frame_class, mock_manager_class, mock_workflow_state
    ):
        """Test that step is validated when class is selected."""
        mock_parent = MagicMock()
        mock_data_loader = MagicMock()

        step = ClassSelectionStep(
            parent_frame=mock_parent,
            step_index=0,
            data_loader=mock_data_loader,
        )

        # Simulate class selection
        step._on_class_selection_changed("Wizard")

        # Step should update validation (workflow_state.selected_class is set)
        assert mock_workflow_state.selected_class == "Wizard"
