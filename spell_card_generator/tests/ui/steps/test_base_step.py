"""Tests for base workflow step."""

# pylint: disable=unused-argument

from unittest.mock import MagicMock, patch

import pytest

from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep


class ConcreteStep(BaseWorkflowStep):
    """Concrete implementation of BaseWorkflowStep for testing."""

    def create_step_content(self):
        """Create minimal step content."""


class TestBaseWorkflowStep:
    """Test BaseWorkflowStep abstract base class."""

    @patch("tkinter.ttk.Frame")
    def test_initialization(self, mock_frame_class):
        """Test BaseWorkflowStep initializes correctly."""
        mock_parent = MagicMock()
        mock_callback = MagicMock()

        step = ConcreteStep(
            parent_frame=mock_parent,
            step_index=0,
            navigation_callback=mock_callback,
        )

        assert step.parent_frame == mock_parent
        assert step.step_index == 0
        assert step.navigation_callback == mock_callback
        assert step.main_frame is None
        assert step.content_frame is None
        assert step.navigation_frame is None
        assert step.previous_button is None
        assert step.next_button is None

    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_create_ui_creates_frames(self, mock_button_class, mock_frame_class):
        """Test create_ui creates main, content, and navigation frames."""
        mock_parent = MagicMock()
        mock_frame_instance = MagicMock()
        mock_frame_class.return_value = mock_frame_instance

        step = ConcreteStep(parent_frame=mock_parent, step_index=0)
        step.create_ui()

        # Verify frames were created
        assert step.main_frame is not None
        assert step.content_frame is not None
        assert step.navigation_frame is not None

    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_create_ui_configures_grid(self, mock_button_class, mock_frame_class):
        """Test create_ui configures grid layout correctly."""
        mock_parent = MagicMock()
        mock_frame_instance = MagicMock()
        mock_frame_class.return_value = mock_frame_instance

        step = ConcreteStep(parent_frame=mock_parent, step_index=0)
        step.create_ui()

        # Verify grid configuration was called
        assert mock_parent.rowconfigure.called
        assert mock_parent.columnconfigure.called

    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_navigation_callback_is_optional(self, mock_button_class, mock_frame_class):
        """Test that navigation callback is optional."""
        mock_parent = MagicMock()

        step = ConcreteStep(parent_frame=mock_parent, step_index=0)

        assert step.navigation_callback is None

    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_step_index_stored(self, mock_button_class, mock_frame_class):
        """Test that step index is properly stored."""
        mock_parent = MagicMock()

        step = ConcreteStep(parent_frame=mock_parent, step_index=3)

        assert step.step_index == 3

    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_destroy_clears_frame(self, mock_button_class, mock_frame_class):
        """Test destroy method clears the main frame."""
        mock_parent = MagicMock()
        mock_frame_instance = MagicMock()
        mock_frame_class.return_value = mock_frame_instance

        step = ConcreteStep(parent_frame=mock_parent, step_index=0)
        step.create_ui()

        # Destroy should call destroy on main frame
        step.destroy()

        assert mock_frame_instance.destroy.called

    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_create_ui_destroys_existing_frame(
        self, mock_button_class, mock_frame_class
    ):
        """Test create_ui destroys existing frame before creating new one."""
        mock_parent = MagicMock()

        # Use default return value instead of side_effect to avoid StopIteration
        mock_frame_class.return_value = MagicMock()
        mock_button_class.return_value = MagicMock()

        step = ConcreteStep(parent_frame=mock_parent, step_index=0)

        # Create UI once
        step.create_ui()
        first_frame = step.main_frame

        # Create UI again - should destroy first frame
        step.create_ui()

        # Verify destroy was called on the first frame
        assert first_frame is not None
        assert isinstance(first_frame, MagicMock)
        first_frame.destroy.assert_called_once()  # pylint: disable=no-member


class TestBaseWorkflowStepNavigation:
    """Test navigation functionality in BaseWorkflowStep."""

    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_navigation_buttons_created(self, mock_button_class, mock_frame_class):
        """Test that navigation area is created with buttons."""
        mock_parent = MagicMock()
        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance
        mock_frame_class.return_value = MagicMock()

        step = ConcreteStep(parent_frame=mock_parent, step_index=0)
        step.create_ui()

        # Verify navigation area was created
        # (Buttons are created in _create_navigation_area)
        assert step.navigation_frame is not None
        # At least one button should be created
        assert mock_button_class.called

    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_navigation_callback_invoked(self, mock_button_class, mock_frame_class):
        """Test that navigation callback can be invoked."""
        mock_parent = MagicMock()
        mock_callback = MagicMock()

        step = ConcreteStep(
            parent_frame=mock_parent,
            step_index=0,
            navigation_callback=mock_callback,
        )

        # Directly test callback (button click would trigger this)
        if step.navigation_callback:
            step.navigation_callback(1)

        mock_callback.assert_called_once_with(1)


class TestBaseWorkflowStepAbstractMethod:
    """Test abstract method requirements."""

    def test_create_step_content_is_abstract(self):
        """Test that create_step_content must be implemented."""
        # BaseWorkflowStep itself cannot be instantiated
        with pytest.raises(TypeError, match="abstract"):
            # pylint: disable=abstract-class-instantiated
            BaseWorkflowStep(MagicMock(), 0)  # type: ignore[abstract]

    def test_concrete_implementation_works(self):
        """Test that concrete implementation can be created."""
        mock_parent = MagicMock()

        # ConcreteStep implements create_step_content
        step = ConcreteStep(parent_frame=mock_parent, step_index=0)

        assert step is not None
        assert isinstance(step, BaseWorkflowStep)
