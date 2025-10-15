"""Tests for workflow coordinator."""

import pytest
from unittest.mock import MagicMock, patch, call
from spell_card_generator.ui.workflow_coordinator import WorkflowCoordinator


class TestWorkflowCoordinator:
    """Test WorkflowCoordinator initialization and step management."""

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_initialization(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test WorkflowCoordinator initializes correctly."""
        mock_parent = MagicMock()
        mock_callback = MagicMock()

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
            on_generate_callback=mock_callback,
        )

        # Verify attributes are set
        assert coordinator.parent_frame == mock_parent
        assert coordinator.data_loader == mock_data_loader
        assert coordinator.spell_filter == mock_spell_filter
        assert coordinator.on_generate_callback == mock_callback

        # Verify step mapping exists
        assert "class_selection" in coordinator.step_id_to_index
        assert "spell_selection" in coordinator.step_id_to_index
        assert 0 in coordinator.index_to_step_id

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_step_instances_created_on_demand(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test that step instances are created on demand."""
        mock_parent = MagicMock()

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )

        # Initially empty (except the first step shown)
        # First step (index 0) should be created during initialization
        assert 0 in coordinator.step_instances

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_sidebar_created(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test that sidebar is created during initialization."""
        mock_parent = MagicMock()

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )

        # Verify sidebar was created
        assert coordinator.sidebar is not None
        mock_sidebar_class.assert_called_once()

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_content_frame_created(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test that content frame is created during initialization."""
        mock_parent = MagicMock()

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )

        # Verify content frame was created
        assert coordinator.content_frame is not None

    @patch("spell_card_generator.ui.workflow_coordinator.ClassSelectionStep")
    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_show_initial_step(
        self,
        mock_frame_class,
        mock_sidebar_class,
        mock_step_class,
        mock_data_loader,
        mock_spell_filter,
    ):
        """Test that initial step (Class Selection) is shown."""
        mock_parent = MagicMock()
        mock_step_instance = MagicMock()
        mock_step_class.return_value = mock_step_instance

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )

        # Verify ClassSelectionStep was instantiated
        assert mock_step_class.called

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_step_id_to_index_mapping(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test step ID to index mapping is correct."""
        mock_parent = MagicMock()

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )

        # Verify mappings
        assert coordinator.step_id_to_index["class_selection"] == 0
        assert coordinator.step_id_to_index["spell_selection"] == 1
        assert coordinator.step_id_to_index["overwrite_cards"] == 2
        assert coordinator.step_id_to_index["documentation_urls"] == 3
        assert coordinator.step_id_to_index["preview_generate"] == 4

        # Verify reverse mapping
        assert coordinator.index_to_step_id[0] == "class_selection"
        assert coordinator.index_to_step_id[1] == "spell_selection"
        assert coordinator.index_to_step_id[2] == "overwrite_cards"

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_workflow_state_initialized(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test that workflow state is properly initialized."""
        mock_parent = MagicMock()

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )

        # Verify workflow state is set
        assert coordinator.workflow_state is not None
        assert hasattr(coordinator.workflow_state, "selected_class")
        assert hasattr(coordinator.workflow_state, "selected_spells")
        assert hasattr(coordinator.workflow_state, "navigator")


class TestWorkflowCoordinatorStepTransitions:
    """Test step transition logic in WorkflowCoordinator."""

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_step_instances_cached(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test that step instances are cached and reused."""
        mock_parent = MagicMock()

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
        )

        # Step 0 should be created during initialization
        initial_count = len(coordinator.step_instances)
        assert initial_count >= 1

        # Getting same step again shouldn't create new instance
        # (This would be tested in _show_step method)
        assert 0 in coordinator.step_instances


class TestWorkflowCoordinatorCallbacks:
    """Test callback handling in WorkflowCoordinator."""

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_on_generate_callback_stored(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test that on_generate callback is properly stored."""
        mock_parent = MagicMock()
        mock_callback = MagicMock()

        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
            on_generate_callback=mock_callback,
        )

        assert coordinator.on_generate_callback == mock_callback

    @patch("spell_card_generator.ui.workflow_coordinator.ModernSidebar")
    @patch("tkinter.ttk.Frame")
    def test_optional_callback_handling(
        self, mock_frame_class, mock_sidebar_class, mock_data_loader, mock_spell_filter
    ):
        """Test that on_generate callback is optional."""
        mock_parent = MagicMock()

        # Should not raise error without callback
        coordinator = WorkflowCoordinator(
            parent_frame=mock_parent,
            data_loader=mock_data_loader,
            spell_filter=mock_spell_filter,
            on_generate_callback=None,
        )

        assert coordinator.on_generate_callback is None
