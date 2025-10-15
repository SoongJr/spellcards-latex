"""Tests for documentation URLs step."""

# pylint: disable=protected-access,unused-argument,too-many-arguments
# pylint: disable=too-many-positional-arguments,too-many-locals,import-outside-toplevel

from unittest.mock import MagicMock, patch

from spell_card_generator.ui.workflow_steps.documentation_urls_step import (
    DocumentationURLsStep,
)


class TestDocumentationURLsStep:
    """Test DocumentationURLsStep initialization and setup."""

    @patch("tkinter.ttk.Frame")
    def test_initialization(self, _mock_frame_class):
        """Test DocumentationURLsStep initializes correctly."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()
        mock_urls_callback = MagicMock()

        step = DocumentationURLsStep(
            parent_frame=mock_parent,
            step_index=3,
            navigation_callback=mock_nav_callback,
            on_urls_changed=mock_urls_callback,
        )

        assert step.parent_frame == mock_parent
        assert step.step_index == 3
        assert step.navigation_callback == mock_nav_callback
        assert step.on_urls_changed == mock_urls_callback
        assert step.spells_tree is None
        assert not step.primary_urls
        assert not step.secondary_urls

    @patch("tkinter.ttk.Frame")
    def test_optional_callback(self, _mock_frame_class):
        """Test that on_urls_changed callback is optional."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        step = DocumentationURLsStep(
            parent_frame=mock_parent,
            step_index=3,
            navigation_callback=mock_nav_callback,
        )

        assert step.on_urls_changed is None

    @patch("tkinter.ttk.Frame")
    def test_step_name_and_description(self, _mock_frame_class):
        """Test step has correct name and description."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        step = DocumentationURLsStep(
            parent_frame=mock_parent,
            step_index=3,
            navigation_callback=mock_nav_callback,
        )

        assert step.step_name == "Documentation URLs"
        assert "URLs" in step.step_description

    @patch("tkinter.ttk.Frame")
    def test_validation_states_defined(self, _mock_frame_class):
        """Test validation state constants are defined."""
        mock_parent = MagicMock()

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)

        assert hasattr(step, "STATE_VALID")
        assert hasattr(step, "STATE_INVALID")
        assert hasattr(step, "STATE_UNVALIDATED")
        assert step.STATE_VALID == "valid"
        assert step.STATE_INVALID == "invalid"
        assert step.STATE_UNVALIDATED == "unvalidated"

    @patch("tkinter.ttk.Frame")
    def test_symbols_defined(self, _mock_frame_class):
        """Test validation symbols are defined."""
        mock_parent = MagicMock()

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)

        assert hasattr(step, "SYMBOL_VALID")
        assert hasattr(step, "SYMBOL_INVALID")
        assert hasattr(step, "SYMBOL_UNVALIDATED")
        assert step.SYMBOL_VALID == "✓"
        assert step.SYMBOL_INVALID == "✗"
        assert step.SYMBOL_UNVALIDATED == "○"


class TestDocumentationURLsStepUI:
    """Test DocumentationURLsStep UI creation."""

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.Progressbar")
    def test_create_step_content(
        self,
        _mock_progressbar_class,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_workflow_state,
    ):
        """Test create_step_content creates UI components."""
        mock_parent = MagicMock()
        mock_workflow_state.selected_spells = []

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify treeview was created
        assert step.spells_tree is not None
        mock_treeview_class.assert_called_once()

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.Progressbar")
    def test_treeview_columns_configured(
        self,
        _mock_progressbar_class,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_workflow_state,
    ):
        """Test treeview columns are properly configured."""
        mock_parent = MagicMock()
        mock_workflow_state.selected_spells = []

        mock_treeview_instance = MagicMock()
        mock_treeview_class.return_value = mock_treeview_instance

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify columns were configured (7 columns)
        assert mock_treeview_instance.heading.call_count >= 7
        assert mock_treeview_instance.column.call_count >= 7

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.Progressbar")
    def test_bulk_action_buttons_created(
        self,
        _mock_progressbar_class,
        mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        _mock_treeview_class,
        mock_workflow_state,
    ):
        """Test bulk action buttons are created."""
        mock_parent = MagicMock()
        mock_workflow_state.selected_spells = []

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify buttons were created (at least Reset and Guess buttons)
        assert mock_button_class.call_count >= 2

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.Progressbar")
    def test_progress_indicator_created(
        self,
        mock_progressbar_class,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        _mock_treeview_class,
        mock_workflow_state,
    ):
        """Test progress indicator components are created."""
        mock_parent = MagicMock()
        mock_workflow_state.selected_spells = []

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify progress indicator was created
        assert step.progress_frame is not None
        assert step.progress_bar is not None
        assert step.progress_label is not None
        mock_progressbar_class.assert_called_once()


class TestDocumentationURLsStepSpellLoading:
    """Test spell data loading functionality."""

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Frame")
    def test_load_spell_data_empty_list(
        self,
        _mock_frame_class,
        mock_treeview_class,
        mock_workflow_state,
    ):
        """Test load_spell_data with no selected spells."""
        mock_parent = MagicMock()
        mock_workflow_state.selected_spells = []

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_class.return_value = mock_treeview_instance

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.spells_tree = mock_treeview_instance
        step._load_spell_data()

        # Should not insert any items
        mock_treeview_instance.insert.assert_not_called()

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Frame")
    def test_load_spell_data_with_spells(
        self,
        _mock_frame_class,
        mock_treeview_class,
        mock_workflow_state,
    ):
        """Test load_spell_data populates tree with spells."""
        mock_parent = MagicMock()

        # Mock selected spells (class_name, spell_name, spell_data)
        mock_spell_data = MagicMock()
        mock_spell_data.__getitem__.return_value = "3"  # spell level
        mock_workflow_state.selected_spells = [
            ("wizard", "Fireball", mock_spell_data),
            ("wizard", "Magic Missile", mock_spell_data),
        ]
        mock_workflow_state.preserve_urls = {}

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_class.return_value = mock_treeview_instance

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.spells_tree = mock_treeview_instance

        # Mock URL validation to avoid actual HTTP requests
        with patch.object(step, "_validate_url", return_value=True):
            with patch.object(step, "_update_tree_item"):
                step._load_spell_data()

        # Verify URLs were initialized for both spells
        assert "Fireball" in step.primary_urls
        assert "Magic Missile" in step.primary_urls


class TestDocumentationURLsStepURLGeneration:
    """Test URL generation functionality."""

    @patch("tkinter.ttk.Frame")
    def test_generate_default_url(self, _mock_frame_class):
        """Test default URL generation."""
        mock_parent = MagicMock()

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)

        url = step._generate_default_url("Fireball")

        assert isinstance(url, str)
        assert len(url) > 0
        assert "http" in url.lower()

    @patch("tkinter.ttk.Frame")
    def test_generate_default_url_handles_spaces(self, _mock_frame_class):
        """Test default URL generation handles spaces in spell names."""
        mock_parent = MagicMock()

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)

        url = step._generate_default_url("Magic Missile")

        assert isinstance(url, str)
        assert " " not in url  # Spaces should be replaced


class TestDocumentationURLsStepURLValidation:
    """Test URL validation functionality."""

    @patch("tkinter.ttk.Frame")
    def test_validate_url_empty_string(self, _mock_frame_class):
        """Test URL validation with empty string."""
        mock_parent = MagicMock()

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)

        result = step._validate_url("")

        assert result is True  # Empty URLs are considered valid


class TestDocumentationURLsStepBulkActions:
    """Test bulk action functionality."""

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Frame")
    def test_reset_all_primary_urls(
        self,
        _mock_frame_class,
        mock_workflow_state,
    ):
        """Test reset all primary URLs to default."""
        mock_parent = MagicMock()
        mock_workflow_state.selected_spells = []

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)

        # Set up some custom URLs
        step.default_primary_urls = {
            "Fireball": "http://default.com/fireball",
            "Magic Missile": "http://default.com/magic-missile",
        }
        step.primary_urls = {
            "Fireball": "http://custom.com/fireball",
            "Magic Missile": "http://custom.com/magic-missile",
        }

        # Mock tree update
        with patch.object(step, "_update_tree_item"):
            step._reset_all_primary()

        # Verify URLs were reset to defaults
        assert step.primary_urls["Fireball"] == "http://default.com/fireball"
        assert step.primary_urls["Magic Missile"] == "http://default.com/magic-missile"


class TestDocumentationURLsStepInteraction:
    """Test user interaction with URLs tree."""

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Frame")
    def test_tree_double_click_cancelled(
        self,
        _mock_frame_class,
        mock_workflow_state,
    ):
        """Test double-clicking with cancelled dialog doesn't change URL."""
        mock_parent = MagicMock()
        mock_workflow_state.selected_spells = []

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.spells_tree = MagicMock()

        step.spells_tree.identify.side_effect = lambda what, x, y: {
            "region": "cell",
            "column": "primary_url",
            "item": "item1",
        }.get(what)

        step.spells_tree.item.side_effect = lambda item, key=None: (
            ("Fireball",) if key == "tags" else {}
        )

        step.primary_urls = {"Fireball": "http://example.com"}
        original_url = step.primary_urls["Fireball"]

        mock_event = MagicMock()
        mock_event.x = 10
        mock_event.y = 10

        with patch("tkinter.simpledialog.askstring") as mock_askstring:
            mock_askstring.return_value = None  # Cancelled

            step._on_tree_double_click(mock_event)

        # Verify URL was not changed
        assert step.primary_urls["Fireball"] == original_url


class TestDocumentationURLsStepValidation:
    """Test step validation logic."""

    @patch(
        "spell_card_generator.ui.workflow_steps.documentation_urls_step.workflow_state"
    )
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    @patch("tkinter.ttk.Progressbar")
    def test_step_always_valid(
        self,
        _mock_progressbar_class,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        _mock_treeview_class,
        mock_workflow_state,
    ):
        """Test step is always valid (URLs are optional)."""
        mock_parent = MagicMock()
        mock_workflow_state.selected_spells = []

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify step was marked as valid
        mock_workflow_state.set_step_valid.assert_called_with(3, True)


class TestDocumentationURLsStepProgress:
    """Test progress indicator functionality."""

    @patch("tkinter.ttk.Frame")
    def test_show_progress(self, _mock_frame_class):
        """Test showing progress indicator."""
        mock_parent = MagicMock()

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.progress_frame = MagicMock()
        step.progress_bar = MagicMock()
        step.progress_label = MagicMock()
        step.content_frame = MagicMock()

        step._show_progress("Testing...", 100)

        step.progress_label.config.assert_called_with(text="Testing...")
        step.progress_bar.config.assert_called_with(maximum=100, value=0)
        step.progress_frame.pack.assert_called()

    @patch("tkinter.ttk.Frame")
    def test_update_progress(self, _mock_frame_class):
        """Test updating progress bar value."""
        mock_parent = MagicMock()

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.progress_bar = MagicMock()
        step.progress_label = MagicMock()
        step.content_frame = MagicMock()

        step._update_progress(50, "Half way...")

        step.progress_bar.config.assert_called_with(value=50)
        step.progress_label.config.assert_called_with(text="Half way...")

    @patch("tkinter.ttk.Frame")
    def test_hide_progress(self, _mock_frame_class):
        """Test hiding progress indicator."""
        mock_parent = MagicMock()

        step = DocumentationURLsStep(parent_frame=mock_parent, step_index=3)
        step.progress_frame = MagicMock()
        step.content_frame = MagicMock()

        step._hide_progress()

        step.progress_frame.pack_forget.assert_called_once()
