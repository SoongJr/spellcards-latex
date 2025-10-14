"""Shared test fixtures and utilities."""

import pandas as pd
import pytest
from pathlib import Path


@pytest.fixture
def sample_spell_data():
    """Create sample spell DataFrame for testing."""
    data = {
        "name": [
            "Fireball",
            "Magic Missile",
            "Cure Light Wounds",
            "Shield",
            "Teleport",
        ],
        "school": ["Evocation", "Evocation", "Conjuration", "Abjuration", "Conjuration"],
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
        "duration": ["Instantaneous", "Instantaneous", "Instantaneous", "1 min/level", "Instantaneous"],
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
        "targets": ["NULL", "NULL", "creature touched", "you", "you and touched objects"],
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
