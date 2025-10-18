"""Tests for FileScanner.find_all_existing_cards() method."""

# pylint: disable=unused-argument

import pandas as pd
import pytest

from spell_card_generator.utils.file_scanner import FileScanner


class TestFileScannerFindAllExistingCards:
    """Test FileScanner.find_all_existing_cards() method."""

    @pytest.fixture
    def sample_spell_data(self):
        """Create sample spell data for testing."""
        return pd.DataFrame(
            {
                "name": ["Fireball", "Magic Missile", "Lightning Bolt", "Ice Storm"],
                "wizard": ["3", "1", "3", "4"],
                "sorcerer": ["3", "1", "3", "4"],
                "source": [
                    "Core Rulebook",
                    "Core Rulebook",
                    "Core Rulebook",
                    "Advanced Player's Guide",
                ],
            }
        )

    @pytest.fixture
    def mock_file_system(self, tmp_path):
        """Create a mock file system with spell cards."""
        # Create directory structure: src/spells/wizard/{level}/
        wizard_dir = tmp_path / "src" / "spells" / "wizard"
        (wizard_dir / "1").mkdir(parents=True)
        (wizard_dir / "3").mkdir(parents=True)
        (wizard_dir / "4").mkdir(parents=True)

        # Create some .tex files (filenames match spell names exactly)
        (wizard_dir / "1" / "Magic Missile.tex").write_text("spell content")
        (wizard_dir / "3" / "Fireball.tex").write_text("spell content")
        (wizard_dir / "3" / "Lightning Bolt.tex").write_text("spell content")
        (wizard_dir / "4" / "Ice Storm.tex").write_text("spell content")

        return tmp_path

    def test_find_all_existing_cards_no_filters(
        self, sample_spell_data, mock_file_system
    ):
        """Test finding all existing cards without filters."""
        result = FileScanner.find_all_existing_cards(
            sample_spell_data, "wizard", base_directory=mock_file_system
        )

        assert len(result) == 4
        spell_names = [spell[1] for spell in result]
        assert "Fireball" in spell_names
        assert "Magic Missile" in spell_names
        assert "Lightning Bolt" in spell_names
        assert "Ice Storm" in spell_names

    def test_find_all_existing_cards_with_level_filter(
        self, sample_spell_data, mock_file_system
    ):
        """Test finding existing cards with level filter."""
        result = FileScanner.find_all_existing_cards(
            sample_spell_data,
            "wizard",
            level_filter="3",
            base_directory=mock_file_system,
        )

        assert len(result) == 2
        spell_names = [spell[1] for spell in result]
        assert "Fireball" in spell_names
        assert "Lightning Bolt" in spell_names
        assert "Magic Missile" not in spell_names
        assert "Ice Storm" not in spell_names

    def test_find_all_existing_cards_with_source_filter(
        self, sample_spell_data, mock_file_system
    ):
        """Test finding existing cards with source filter."""
        result = FileScanner.find_all_existing_cards(
            sample_spell_data,
            "wizard",
            source_filter="Core Rulebook",
            base_directory=mock_file_system,
        )

        assert len(result) == 3
        spell_names = [spell[1] for spell in result]
        assert "Fireball" in spell_names
        assert "Magic Missile" in spell_names
        assert "Lightning Bolt" in spell_names
        assert "Ice Storm" not in spell_names  # From Advanced Player's Guide

    def test_find_all_existing_cards_with_search_term(
        self, sample_spell_data, mock_file_system
    ):
        """Test finding existing cards with search term filter."""
        result = FileScanner.find_all_existing_cards(
            sample_spell_data,
            "wizard",
            search_term="bolt",
            base_directory=mock_file_system,
        )

        assert len(result) == 1
        assert result[0][1] == "Lightning Bolt"

    def test_find_all_existing_cards_with_combined_filters(
        self, sample_spell_data, mock_file_system
    ):
        """Test finding existing cards with multiple filters combined."""
        result = FileScanner.find_all_existing_cards(
            sample_spell_data,
            "wizard",
            level_filter="3",
            source_filter="Core Rulebook",
            search_term="fire",
            base_directory=mock_file_system,
        )

        assert len(result) == 1
        assert result[0][1] == "Fireball"

    def test_find_all_existing_cards_case_insensitive_search(
        self, sample_spell_data, mock_file_system
    ):
        """Test that search term is case-insensitive."""
        result = FileScanner.find_all_existing_cards(
            sample_spell_data,
            "wizard",
            search_term="FIRE",
            base_directory=mock_file_system,
        )

        assert len(result) == 1
        assert result[0][1] == "Fireball"

    def test_find_all_existing_cards_nonexistent_class(
        self, sample_spell_data, mock_file_system
    ):
        """Test finding cards for a class with no directory."""
        result = FileScanner.find_all_existing_cards(
            sample_spell_data, "cleric", base_directory=mock_file_system
        )

        assert len(result) == 0

    def test_find_all_existing_cards_empty_directory(self, sample_spell_data, tmp_path):
        """Test finding cards in an empty class directory."""
        # Create empty wizard directory
        wizard_dir = tmp_path / "src" / "spells" / "wizard"
        wizard_dir.mkdir(parents=True)

        result = FileScanner.find_all_existing_cards(
            sample_spell_data, "wizard", base_directory=tmp_path
        )

        assert len(result) == 0

    def test_find_all_existing_cards_returns_correct_tuple_format(
        self, sample_spell_data, mock_file_system
    ):
        """Test that returned tuples have correct format."""
        result = FileScanner.find_all_existing_cards(
            sample_spell_data,
            "wizard",
            level_filter="3",
            base_directory=mock_file_system,
        )

        assert len(result) > 0
        for class_name, spell_name, spell_data in result:
            assert class_name == "wizard"
            assert isinstance(spell_name, str)
            assert isinstance(spell_data, pd.Series)
            assert spell_data["name"] == spell_name

    def test_find_all_existing_cards_ignores_invalid_files(
        self, sample_spell_data, tmp_path
    ):
        """Test that invalid files are ignored."""
        wizard_dir = tmp_path / "src" / "spells" / "wizard"
        wizard_dir.mkdir(parents=True)

        # Create level subdirectory
        (wizard_dir / "1").mkdir(exist_ok=True)

        # Create files that should be ignored
        (wizard_dir / "README.md").write_text("documentation")
        (wizard_dir / "1" / "Magic Missile.tex").write_text("spell content")

        # File in wrong location (not in level subdirectory)
        (wizard_dir / "Spell.tex").write_text("spell content")

        result = FileScanner.find_all_existing_cards(
            sample_spell_data, "wizard", base_directory=tmp_path
        )

        # Should only find the properly structured file
        assert len(result) == 1
        assert result[0][1] == "Magic Missile"

    def test_find_all_existing_cards_no_matching_spells_in_database(
        self, sample_spell_data, tmp_path
    ):
        """Test handling files that don't match any spell in database."""
        wizard_dir = tmp_path / "src" / "spells" / "wizard" / "3"
        wizard_dir.mkdir(parents=True)

        # Create a file for a spell not in our sample data
        (wizard_dir / "Unknown-Spell.tex").write_text("spell content")

        result = FileScanner.find_all_existing_cards(
            sample_spell_data, "wizard", base_directory=tmp_path
        )

        assert len(result) == 0

    def test_find_all_existing_cards_level_mismatch(self, sample_spell_data, tmp_path):
        """Test that spells in wrong level directory are ignored."""
        wizard_dir = tmp_path / "src" / "spells" / "wizard" / "5"  # Wrong level
        wizard_dir.mkdir(parents=True)

        # Fireball is level 3, not level 5
        (wizard_dir / "Fireball.tex").write_text("spell content")

        result = FileScanner.find_all_existing_cards(
            sample_spell_data, "wizard", base_directory=tmp_path
        )

        assert len(result) == 0
