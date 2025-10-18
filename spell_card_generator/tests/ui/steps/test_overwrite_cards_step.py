"""Tests for overwrite cards step."""

# some complaints pylint may throw at us do not apply to test code:
# pylint: disable=too-many-arguments,too-many-positional-arguments

from unittest.mock import MagicMock, patch
from spell_card_generator.ui.workflow_steps.overwrite_cards_step import (
    OverwriteCardsStep,
)


class TestOverwriteCardsStep:
    """Test OverwriteCardsStep initialization and setup."""

    @patch("tkinter.ttk.Frame")
    def test_initialization(self, _mock_frame_class):
        """Test OverwriteCardsStep initializes correctly."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()
        mock_overwrite_callback = MagicMock()

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
            on_overwrite_changed=mock_overwrite_callback,
        )

        assert step.parent_frame == mock_parent
        assert step.step_index == 2
        assert step.navigation_callback == mock_nav_callback
        assert step.on_overwrite_changed == mock_overwrite_callback
        assert step.conflicts_tree is None  # Not created until create_step_content
        assert step.selection_frame is None

    @patch("tkinter.ttk.Frame")
    def test_optional_callback(self, _mock_frame_class):
        """Test that on_overwrite_changed callback is optional."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )

        assert step.on_overwrite_changed is None

    @patch("tkinter.ttk.Frame")
    def test_step_name_and_description(self, _mock_frame_class):
        """Test step has correct name and description."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )

        assert step.step_name == "Overwrite Cards"
        assert "conflict" in step.step_description.lower()


class TestOverwriteCardsStepUI:
    """Test OverwriteCardsStep UI creation."""

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_create_step_content(
        self,
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
        mock_nav_callback = MagicMock()
        mock_workflow_state.existing_cards = {}

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify treeview was created
        assert step.conflicts_tree is not None
        mock_treeview_class.assert_called_once()

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.FileScanner")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_treeview_columns_configured(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_file_scanner,
        mock_workflow_state,
    ):
        """Test treeview columns are properly configured."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()
        mock_workflow_state.existing_cards = {}
        mock_file_scanner.get_conflicts_summary.return_value = {"analyses": {}}

        mock_treeview_instance = MagicMock()
        mock_treeview_class.return_value = mock_treeview_instance

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify columns were configured
        assert mock_treeview_instance.heading.call_count >= 5  # 5 columns
        assert mock_treeview_instance.column.call_count >= 5


class TestOverwriteCardsStepConflicts:
    """Test conflict detection and population."""

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.FileScanner")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_populate_conflicts_with_existing_cards(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_file_scanner,
        mock_workflow_state,
    ):
        """Test populate_conflicts adds conflicts to tree."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        # Setup existing cards
        mock_workflow_state.existing_cards = {
            "Fireball": "/path/to/fireball.tex",
            "Magic Missile": "/path/to/magic_missile.tex",
        }
        mock_workflow_state.overwrite_decisions = {}
        mock_workflow_state.preserve_description = {}
        mock_workflow_state.preserve_urls = {}

        # Setup file scanner response
        mock_file_scanner.get_conflicts_summary.return_value = {
            "analyses": {
                "Fireball": {
                    "primary_url": "https://example.com/fireball",
                    "secondary_url": "",
                    "modification_time": 1234567890,
                },
                "Magic Missile": {
                    "primary_url": "https://example.com/magic_missile",
                    "secondary_url": "",
                    "modification_time": 1234567890,
                },
            }
        }

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_class.return_value = mock_treeview_instance

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify items were inserted into tree
        assert mock_treeview_instance.insert.call_count == 2

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.FileScanner")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_populate_conflicts_with_no_conflicts(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_file_scanner,
        mock_workflow_state,
    ):
        """Test populate_conflicts with no existing cards."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        # No existing cards
        mock_workflow_state.existing_cards = {}
        mock_file_scanner.get_conflicts_summary.return_value = {"analyses": {}}

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_class.return_value = mock_treeview_instance

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Verify no items were inserted
        mock_treeview_instance.insert.assert_not_called()


class TestOverwriteCardsStepInteraction:
    """Test user interaction with conflict tree."""

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.FileScanner")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_tree_click_toggles_overwrite(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_file_scanner,
        mock_workflow_state,
    ):
        """Test clicking tree toggles overwrite checkbox."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        mock_workflow_state.existing_cards = {"Fireball": "/path/to/fireball.tex"}
        mock_workflow_state.overwrite_decisions = {"Fireball": False}
        mock_workflow_state.preserve_description = {}
        mock_workflow_state.preserve_urls = {}
        mock_file_scanner.get_conflicts_summary.return_value = {
            "analyses": {
                "Fireball": {
                    "primary_url": "",
                    "secondary_url": "",
                    "modification_time": 1234567890,
                }
            }
        }

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_instance.identify.side_effect = lambda what, x, y: {
            "region": "cell",
            "column": "#1",  # Overwrite column
            "item": "item1",
        }.get(what)
        # item(item_id, "tags") returns the tags tuple directly, not a dict
        mock_treeview_instance.item.side_effect = lambda item, key=None: (
            ("Fireball",) if key == "tags" else {}
        )
        mock_treeview_class.return_value = mock_treeview_instance

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Simulate click event
        mock_event = MagicMock()
        mock_event.x = 10
        mock_event.y = 10
        step._on_tree_click(mock_event)

        # Verify overwrite decision was toggled to True
        assert mock_workflow_state.overwrite_decisions["Fireball"] is True

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.FileScanner")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_tree_click_toggles_preserve_description(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_file_scanner,
        mock_workflow_state,
    ):
        """Test clicking tree toggles preserve description checkbox."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        mock_workflow_state.existing_cards = {"Fireball": "/path/to/fireball.tex"}
        mock_workflow_state.overwrite_decisions = {}
        mock_workflow_state.preserve_description = {"Fireball": False}
        mock_workflow_state.preserve_urls = {}
        mock_file_scanner.get_conflicts_summary.return_value = {
            "analyses": {
                "Fireball": {
                    "primary_url": "",
                    "secondary_url": "",
                    "modification_time": 1234567890,
                }
            }
        }

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_instance.identify.side_effect = lambda what, x, y: {
            "region": "cell",
            "column": "#2",  # Preserve description column
            "item": "item1",
        }.get(what)
        # item(item_id, "tags") returns the tags tuple directly, not a dict
        mock_treeview_instance.item.side_effect = lambda item, key=None: (
            ("Fireball",) if key == "tags" else {}
        )
        mock_treeview_class.return_value = mock_treeview_instance

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.content_frame = MagicMock()
        step.create_step_content()

        # Simulate click event
        mock_event = MagicMock()
        mock_event.x = 10
        mock_event.y = 10
        step._on_tree_click(mock_event)

        # Verify preserve description was toggled to True
        assert mock_workflow_state.preserve_description["Fireball"] is True


class TestOverwriteCardsStepValidation:
    """Test step validation logic."""

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.FileScanner")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_validation_when_all_conflicts_resolved(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_file_scanner,
        mock_workflow_state,
    ):
        """Test step is valid when all conflicts have decisions."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        # All conflicts have overwrite decisions
        mock_workflow_state.existing_cards = {
            "Fireball": "/path/to/fireball.tex",
            "Magic Missile": "/path/to/magic_missile.tex",
        }
        mock_workflow_state.overwrite_decisions = {
            "Fireball": True,
            "Magic Missile": False,
        }
        mock_workflow_state.preserve_description = {}
        mock_workflow_state.preserve_urls = {}
        mock_file_scanner.get_conflicts_summary.return_value = {"analyses": {}}

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_class.return_value = mock_treeview_instance

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.content_frame = MagicMock()
        step.on_step_validation_changed = MagicMock()  # type: ignore[method-assign]
        step.create_step_content()

        # Verify step was marked as valid
        mock_workflow_state.set_step_valid.assert_called_with(2, True)

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.FileScanner")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Scrollbar")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.Button")
    def test_validation_when_conflicts_unresolved(
        self,
        _mock_button_class,
        _mock_frame_class,
        _mock_label_class,
        _mock_labelframe_class,
        _mock_scrollbar_class,
        mock_treeview_class,
        mock_file_scanner,
        mock_workflow_state,
    ):
        """Test step is invalid when NO decisions have been made."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        # Conflicts exist but NO decisions have been made
        mock_workflow_state.existing_cards = {
            "Fireball": "/path/to/fireball.tex",
            "Magic Missile": "/path/to/magic_missile.tex",
        }
        mock_workflow_state.overwrite_decisions = {}  # No decisions at all
        mock_workflow_state.preserve_description = {}
        mock_workflow_state.preserve_urls = {}
        mock_file_scanner.get_conflicts_summary.return_value = {"analyses": {}}

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_class.return_value = mock_treeview_instance

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.content_frame = MagicMock()
        step.on_step_validation_changed = MagicMock()  # type: ignore[method-assign]
        step.create_step_content()

        # Verify step was marked as invalid (no decisions made)
        mock_workflow_state.set_step_valid.assert_called_with(2, False)


class TestOverwriteCardsStepRefresh:
    """Test UI refresh functionality."""

    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.workflow_state")
    @patch("spell_card_generator.ui.workflow_steps.overwrite_cards_step.FileScanner")
    @patch("tkinter.ttk.Treeview")
    @patch("tkinter.ttk.Frame")
    def test_refresh_ui_repopulates_conflicts(
        self,
        _mock_frame_class,
        mock_treeview_class,
        mock_file_scanner,
        mock_workflow_state,
    ):
        """Test refresh_ui repopulates the conflicts tree."""
        mock_parent = MagicMock()
        mock_nav_callback = MagicMock()

        mock_workflow_state.existing_cards = {"Fireball": "/path/to/fireball.tex"}
        mock_workflow_state.overwrite_decisions = {}
        mock_workflow_state.preserve_description = {}
        mock_workflow_state.preserve_urls = {}
        mock_file_scanner.get_conflicts_summary.return_value = {"analyses": {}}

        mock_treeview_instance = MagicMock()
        mock_treeview_instance.get_children.return_value = []
        mock_treeview_class.return_value = mock_treeview_instance

        step = OverwriteCardsStep(
            parent_frame=mock_parent,
            step_index=2,
            navigation_callback=mock_nav_callback,
        )
        step.conflicts_tree = mock_treeview_instance

        # Call refresh
        step.refresh_ui()

        # Verify tree was repopulated (clear + insert)
        assert mock_treeview_instance.get_children.called
        assert mock_treeview_instance.insert.call_count >= 1
