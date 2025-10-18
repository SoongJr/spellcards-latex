"""Common fixtures for testing."""

# pylint: disable=redefined-outer-name,unused-argument,import-outside-toplevel

from unittest.mock import MagicMock

import pandas as pd
import pytest


@pytest.fixture
def sample_spell_data():
    """Sample spell data for testing."""
    data = {
        "name": [
            "Fireball",
            "Magic Missile",
            "Cure Light Wounds",
            "Shield",
            "Teleport",
        ],
        "school": [
            "Evocation",
            "Evocation",
            "Conjuration",
            "Abjuration",
            "Conjuration",
        ],
        "source": ["Core", "Core", "Core", "Core", "Core"],
        "description": [
            "A ball of fire",
            "Missiles of magical force",
            "Heals minor wounds",
            "Creates an invisible shield",
            "Instantly transports",
        ],
        "description_formatted": [
            "<p>A ball of fire</p>",
            "<p>Missiles of magical force</p>",
            "<p>Heals minor wounds</p>",
            "<p>Creates an invisible shield</p>",
            "<p>Instantly transports</p>",
        ],
        "casting_time": [
            "1 standard action",
            "1 standard action",
            "1 standard action",
            "1 standard action",
            "1 standard action",
        ],
        "components": ["V, S, M", "V, S", "V, S", "V, S", "V"],
        "range": ["Long", "Medium", "Touch", "Personal", "Unlimited"],
        "duration": [
            "Instantaneous",
            "Instantaneous",
            "Instantaneous",
            "1 min/level",
            "Instantaneous",
        ],
        "saving_throw": ["Reflex half", "none", "Will half", "none", "none"],
        "spell_resistance": ["yes", "yes", "yes", "no", "no"],
        "wizard": ["3", "1", "NULL", "1", "5"],
        "sorcerer": ["3", "1", "NULL", "1", "5"],
        "cleric": ["NULL", "NULL", "1", "NULL", "NULL"],
        "bard": ["NULL", "1", "NULL", "NULL", "NULL"],
        "subschool": ["NULL", "NULL", "healing", "NULL", "teleportation"],
        "descriptor": ["fire", "force", "NULL", "NULL", "NULL"],
        "area": ["20-ft.-radius spread", "NULL", "NULL", "NULL", "NULL"],
        "effect": ["NULL", "NULL", "NULL", "NULL", "NULL"],
        "targets": [
            "NULL",
            "NULL",
            "creature touched",
            "you",
            "you and touched objects",
        ],
        "dismissible": ["NULL", "NULL", "NULL", "NULL", "NULL"],
        "shapeable": ["NULL", "NULL", "NULL", "NULL", "NULL"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_spell_file(tmp_path, sample_spell_data):
    """Create temporary TSV file with spell data."""
    file_path = tmp_path / "spell_full.tsv"
    sample_spell_data.to_csv(file_path, sep="\t", index=False)
    return file_path


@pytest.fixture
def sample_spell_series(sample_spell_data):
    """Get a single spell as a Series."""
    return sample_spell_data.iloc[0]


@pytest.fixture
def mock_spell_classes():
    """Get list of character classes for testing."""
    return ["wizard", "sorcerer", "cleric", "bard", "druid", "paladin", "ranger"]


# ============================================================================
# UI Testing Fixtures
# ============================================================================


@pytest.fixture
def mock_tk_root(mocker):
    """Create a mocked tkinter root window."""
    mock_root = MagicMock()
    mock_root.tk = MagicMock()
    mock_root.winfo_exists.return_value = True
    return mock_root


@pytest.fixture
def mock_tk_frame(mocker):
    """Create a mocked tkinter Frame."""
    mock_frame = MagicMock()
    mock_frame.winfo_exists.return_value = True
    mock_frame.pack = MagicMock()
    mock_frame.grid = MagicMock()
    mock_frame.place = MagicMock()
    return mock_frame


@pytest.fixture
def mock_tk_widget(mocker):
    """Create a generic mocked tkinter widget."""
    mock_widget = MagicMock()
    mock_widget.winfo_exists.return_value = True
    mock_widget.pack = MagicMock()
    mock_widget.grid = MagicMock()
    mock_widget.place = MagicMock()
    mock_widget.config = MagicMock()
    mock_widget.configure = MagicMock()
    return mock_widget


@pytest.fixture
def mock_data_loader(mocker, sample_spell_data):
    """Create a mocked SpellDataLoader."""
    mock_loader = MagicMock()
    mock_loader.spells = sample_spell_data
    mock_loader.get_available_classes.return_value = [
        "wizard",
        "sorcerer",
        "cleric",
        "bard",
    ]
    mock_loader.load_data.return_value = sample_spell_data
    return mock_loader


@pytest.fixture
def mock_spell_filter(mocker):
    """Create a mocked SpellFilter."""
    mock_filter = MagicMock()
    mock_filter.get_available_levels.return_value = ["0", "1", "2", "3"]
    mock_filter.get_available_sources.return_value = ["Core", "Advanced"]
    mock_filter.filter_spells.return_value = pd.DataFrame()
    return mock_filter


@pytest.fixture
def reset_workflow_state():
    """Reset the global workflow state before each test."""
    from spell_card_generator.ui.workflow_state import workflow_state

    # Store original state
    original_state = {
        "selected_class": workflow_state.selected_class,
        "selected_spells": workflow_state.selected_spells.copy(),
        "overwrite_existing": workflow_state.overwrite_existing,
        "conflicts_detected": workflow_state.conflicts_detected,
    }

    # Reset to defaults
    workflow_state.selected_class = None
    workflow_state.selected_spells = []
    workflow_state.overwrite_existing = False
    workflow_state.conflicts_detected = False
    workflow_state.existing_cards = {}
    workflow_state.overwrite_decisions = {}
    workflow_state.spell_data_cache = {}

    yield workflow_state

    # Restore original state after test (assignments match original state types)
    workflow_state.selected_class = original_state[
        "selected_class"
    ]  # type: ignore[assignment]
    workflow_state.selected_spells = original_state[
        "selected_spells"
    ]  # type: ignore[assignment]
    workflow_state.overwrite_existing = original_state[
        "overwrite_existing"
    ]  # type: ignore[assignment]
    workflow_state.conflicts_detected = original_state[
        "conflicts_detected"
    ]  # type: ignore[assignment]
