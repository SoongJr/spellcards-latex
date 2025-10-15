"""Tests for preview and generate step."""

# pylint: disable=unused-argument,import-outside-toplevel,protected-access

from unittest.mock import MagicMock, patch
import pandas as pd

from spell_card_generator.ui.workflow_steps.preview_generate_step import (
    PreviewGenerateStep,
)
from spell_card_generator.ui.workflow_state import workflow_state


class TestPreviewGenerateStep:
    """Tests for PreviewGenerateStep."""

    @patch("tkinter.ttk.Frame")
    def test_initialization(self, mock_frame_class):
        """Test PreviewGenerateStep can be initialized."""
        mock_parent = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )

        assert step is not None
        assert step.parent_frame == mock_parent
        assert step.step_index == 4
        assert step.on_generate is None

    @patch("tkinter.scrolledtext.ScrolledText")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    def test_create_step_content(
        self,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_button_class,
        mock_scrolled_text_class,
    ):
        """Test create_step_content creates UI components."""
        mock_parent = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )
        step.content_frame = MagicMock()

        # Should not raise an error
        step.create_step_content()

        # Verify UI components were created
        assert mock_label_class.called
        assert mock_labelframe_class.called
        assert mock_button_class.called
        assert mock_scrolled_text_class.called

    @patch("tkinter.ttk.Frame")
    def test_inherits_from_base_step(self, mock_frame_class):
        """Test PreviewGenerateStep inherits from BaseWorkflowStep."""
        from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep

        mock_parent = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )

        assert isinstance(step, BaseWorkflowStep)

    @patch("tkinter.ttk.Frame")
    def test_accepts_optional_navigation_callback(self, mock_frame_class):
        """Test navigation callback parameter is accepted."""
        mock_parent = MagicMock()
        mock_callback = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
            navigation_callback=mock_callback,
        )

        assert step.navigation_callback == mock_callback

    @patch("tkinter.ttk.Frame")
    def test_accepts_optional_generate_callback(self, mock_frame_class):
        """Test on_generate callback parameter is accepted."""
        mock_parent = MagicMock()
        mock_generate_callback = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
            on_generate=mock_generate_callback,
        )

        assert step.on_generate == mock_generate_callback

    @patch("tkinter.scrolledtext.ScrolledText")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    def test_update_summary_with_no_data(
        self,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_button_class,
        mock_scrolled_text_class,
    ):
        """Test _update_summary works with no workflow data."""
        # Clear workflow state
        workflow_state.selected_class = None
        workflow_state.selected_spells = []
        workflow_state.conflicts_detected = False

        mock_parent = MagicMock()
        mock_text_widget = MagicMock()
        mock_scrolled_text_class.return_value = mock_text_widget

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Should not raise an error even with no data
        step._update_summary()

        # Verify text widget was updated
        assert mock_text_widget.config.called
        assert mock_text_widget.delete.called
        assert mock_text_widget.insert.called

    @patch("tkinter.scrolledtext.ScrolledText")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    def test_update_summary_with_complete_data(
        self,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_button_class,
        mock_scrolled_text_class,
    ):
        """Test _update_summary displays complete workflow data."""
        # Setup workflow state with complete data
        workflow_state.selected_class = "Wizard"

        # Create mock spell data
        mock_spell_data = pd.Series(
            {
                "name": "Fireball",
                "Wizard": "3",
                "school": "Evocation",
            }
        )

        workflow_state.selected_spells = [
            ("Fireball", "Wizard", mock_spell_data),
        ]
        workflow_state.conflicts_detected = False

        mock_parent = MagicMock()
        mock_text_widget = MagicMock()
        mock_scrolled_text_class.return_value = mock_text_widget

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        step._update_summary()

        # Verify text widget operations
        assert mock_text_widget.config.called
        assert mock_text_widget.delete.called

        # Verify content includes class and spell information
        insert_calls = list(mock_text_widget.insert.call_args_list)
        assert len(insert_calls) > 0

    @patch("tkinter.scrolledtext.ScrolledText")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    def test_update_summary_with_conflicts(
        self,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_button_class,
        mock_scrolled_text_class,
    ):
        """Test _update_summary displays conflict information."""
        # Setup workflow state with conflicts
        workflow_state.selected_class = "Wizard"

        mock_spell_data = pd.Series(
            {
                "name": "Fireball",
                "Wizard": "3",
            }
        )

        workflow_state.selected_spells = [
            ("Fireball", "Wizard", mock_spell_data),
        ]
        workflow_state.conflicts_detected = True
        workflow_state.existing_cards = {"Fireball": "/path/to/fireball.tex"}
        workflow_state.overwrite_decisions = {"Fireball": True}
        workflow_state.preserve_description = {"Fireball": False}
        workflow_state.preserve_urls = {"Fireball": True}

        mock_parent = MagicMock()
        mock_text_widget = MagicMock()
        mock_scrolled_text_class.return_value = mock_text_widget

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        step._update_summary()

        # Verify summary was updated
        assert mock_text_widget.insert.called

    @patch("tkinter.ttk.Frame")
    def test_on_generate_clicked_calls_callback(self, mock_frame_class):
        """Test _on_generate_clicked calls the on_generate callback."""
        mock_parent = MagicMock()
        mock_callback = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
            on_generate=mock_callback,
        )

        step._on_generate_clicked()

        mock_callback.assert_called_once()

    @patch("tkinter.ttk.Frame")
    def test_on_generate_clicked_handles_none_callback(self, mock_frame_class):
        """Test _on_generate_clicked handles None callback gracefully."""
        mock_parent = MagicMock()

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
            on_generate=None,
        )

        # Should not raise an error
        step._on_generate_clicked()

    @patch("tkinter.scrolledtext.ScrolledText")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    def test_refresh_ui_updates_summary(
        self,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_button_class,
        mock_scrolled_text_class,
    ):
        """Test refresh_ui calls _update_summary."""
        mock_parent = MagicMock()
        mock_text_widget = MagicMock()
        mock_scrolled_text_class.return_value = mock_text_widget

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Reset mock to track calls after initialization
        mock_text_widget.reset_mock()

        # Call refresh_ui
        step.refresh_ui()

        # Verify summary was updated
        assert mock_text_widget.config.called
        assert mock_text_widget.delete.called
        assert mock_text_widget.insert.called

    @patch("tkinter.scrolledtext.ScrolledText")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    def test_generate_button_state_with_ready_workflow(
        self,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_button_class,
        mock_scrolled_text_class,
    ):
        """Test generate button is enabled when workflow is ready."""
        # Setup complete workflow
        workflow_state.selected_class = "Wizard"
        mock_spell_data = pd.Series({"name": "Fireball", "Wizard": "3"})
        workflow_state.selected_spells = [("Fireball", "Wizard", mock_spell_data)]

        mock_parent = MagicMock()
        mock_button = MagicMock()
        mock_button_class.return_value = mock_button

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify button state was set to normal (enabled)
        config_calls = [
            call
            for call in mock_button.config.call_args_list
            if len(call[1]) > 0 and "state" in call[1]
        ]

        # The button should have been configured with state="normal"
        assert any(
            "state" in str(call) and "normal" in str(call) for call in config_calls
        )

    @patch("tkinter.scrolledtext.ScrolledText")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    def test_generate_button_state_with_incomplete_workflow(
        self,
        mock_frame_class,
        mock_label_class,
        mock_labelframe_class,
        mock_button_class,
        mock_scrolled_text_class,
    ):
        """Test generate button is disabled when workflow is incomplete."""
        # Setup incomplete workflow
        workflow_state.selected_class = None
        workflow_state.selected_spells = []

        mock_parent = MagicMock()
        mock_button = MagicMock()
        mock_button_class.return_value = mock_button

        step = PreviewGenerateStep(
            parent_frame=mock_parent,
            step_index=4,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify button state was set to disabled
        config_calls = [
            call
            for call in mock_button.config.call_args_list
            if len(call[1]) > 0 and "state" in call[1]
        ]

        # The button should have been configured with state="disabled"
        assert any(
            "state" in str(call) and "disabled" in str(call) for call in config_calls
        )
