"""Tests for spell_card_generator.data.filter module."""

import pytest

from spell_card_generator.data.filter import SpellFilter
from spell_card_generator.utils.exceptions import FilterError


@pytest.mark.unit
class TestSpellFilter:
    """Test cases for SpellFilter class."""

    def test_filter_spells_by_class(self, sample_spell_data):
        """Test filtering spells by class."""
        filtered = SpellFilter.filter_spells(sample_spell_data, "wizard")

        assert not filtered.empty
        assert all(filtered["wizard"] != "NULL")
        # Should have: Fireball, Magic Missile, Shield, Teleport (4 spells)
        assert len(filtered) == 4

    def test_filter_spells_by_class_and_level(self, sample_spell_data):
        """Test filtering spells by class and level."""
        filtered = SpellFilter.filter_spells(sample_spell_data, "wizard", level="1")

        assert not filtered.empty
        assert all(filtered["wizard"] == "1")
        # Should have: Magic Missile, Shield (2 spells)
        assert len(filtered) == 2

    def test_filter_spells_by_class_and_source(self, sample_spell_data):
        """Test filtering spells by class and source."""
        filtered = SpellFilter.filter_spells(sample_spell_data, "wizard", source="Core")

        assert not filtered.empty
        assert all(filtered["source"] == "Core")
        assert all(filtered["wizard"] != "NULL")

    def test_filter_spells_with_search_term(self, sample_spell_data):
        """Test filtering spells with search term."""
        filtered = SpellFilter.filter_spells(
            sample_spell_data, "wizard", search_term="Fire"
        )

        assert len(filtered) == 1
        assert filtered.iloc[0]["name"] == "Fireball"

    def test_filter_spells_case_insensitive_search(self, sample_spell_data):
        """Test that search is case-insensitive."""
        filtered = SpellFilter.filter_spells(
            sample_spell_data, "wizard", search_term="fire"
        )

        assert len(filtered) == 1
        assert filtered.iloc[0]["name"] == "Fireball"

    def test_filter_spells_all_level_shows_all(self, sample_spell_data):
        """Test that 'All' level filter shows all spells."""
        filtered = SpellFilter.filter_spells(sample_spell_data, "wizard", level="All")

        assert len(filtered) == 4  # All wizard spells

    def test_filter_spells_all_source_shows_all(self, sample_spell_data):
        """Test that 'All' source filter shows all spells."""
        filtered = SpellFilter.filter_spells(sample_spell_data, "wizard", source="All")

        assert len(filtered) == 4  # All wizard spells

    def test_filter_spells_empty_search_shows_all(self, sample_spell_data):
        """Test that empty search term shows all spells."""
        filtered = SpellFilter.filter_spells(
            sample_spell_data, "wizard", search_term=""
        )

        assert len(filtered) == 4  # All wizard spells

    def test_filter_spells_whitespace_search_shows_all(self, sample_spell_data):
        """Test that whitespace-only search term shows all spells."""
        filtered = SpellFilter.filter_spells(
            sample_spell_data, "wizard", search_term="   "
        )

        assert len(filtered) == 4  # All wizard spells

    def test_filter_spells_combined_filters(self, sample_spell_data):
        """Test combining multiple filters."""
        filtered = SpellFilter.filter_spells(
            sample_spell_data, "wizard", level="3", source="Core", search_term="fire"
        )

        assert len(filtered) == 1
        assert filtered.iloc[0]["name"] == "Fireball"

    def test_filter_spells_no_matches(self, sample_spell_data):
        """Test filtering with no matches."""
        filtered = SpellFilter.filter_spells(
            sample_spell_data, "wizard", search_term="Nonexistent"
        )

        assert filtered.empty

    def test_filter_spells_invalid_class(self, sample_spell_data):
        """Test filtering with invalid class."""
        with pytest.raises(FilterError, match="Class .* not found in data"):
            SpellFilter.filter_spells(sample_spell_data, "invalid_class")

    def test_filter_spells_exception_handling(self):
        """Test error handling in filter_spells."""
        # Pass invalid data structure
        with pytest.raises(FilterError, match="Failed to filter spells"):
            SpellFilter.filter_spells(None, "wizard")

    def test_get_available_levels(self, sample_spell_data):
        """Test getting available spell levels for a class."""
        levels = SpellFilter.get_available_levels(sample_spell_data, "wizard")

        assert "All" in levels
        assert "1" in levels
        assert "3" in levels
        assert "5" in levels
        # Should be sorted with "All" first
        assert levels[0] == "All"

    def test_get_available_levels_invalid_class(self, sample_spell_data):
        """Test getting levels for invalid class."""
        levels = SpellFilter.get_available_levels(sample_spell_data, "invalid_class")

        assert levels == ["All"]

    def test_get_available_levels_exception_handling(self):
        """Test error handling in get_available_levels."""
        with pytest.raises(FilterError, match="Failed to get available levels"):
            SpellFilter.get_available_levels(None, "wizard")

    def test_get_available_sources(self, sample_spell_data):
        """Test getting available sources for a class."""
        sources = SpellFilter.get_available_sources(sample_spell_data, "wizard")

        assert "All" in sources
        assert "Core" in sources
        assert sources[0] == "All"

    def test_get_available_sources_invalid_class(self, sample_spell_data):
        """Test getting sources for invalid class."""
        sources = SpellFilter.get_available_sources(sample_spell_data, "invalid_class")

        assert sources == ["All"]

    def test_get_available_sources_exception_handling(self):
        """Test error handling in get_available_sources."""
        with pytest.raises(FilterError, match="Failed to get available sources"):
            SpellFilter.get_available_sources(None, "wizard")

    def test_filter_excludes_null_values(self, sample_spell_data):
        """Test that NULL values are properly excluded."""
        cleric_spells = SpellFilter.filter_spells(sample_spell_data, "cleric")

        # Cleric should only have Cure Light Wounds
        assert len(cleric_spells) == 1
        assert cleric_spells.iloc[0]["name"] == "Cure Light Wounds"
