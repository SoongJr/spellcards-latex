"""Tests for spell_card_generator.models.spell module."""

import pytest

from spell_card_generator.models.spell import Spell


@pytest.mark.unit
class TestSpell:
    """Test cases for Spell class."""

    def test_spell_creation(self):
        """Test creating a Spell instance."""
        spell = Spell(
            name="Fireball",
            school="Evocation",
            source="Core",
            description="A ball of fire",
            description_formatted="<p>A ball of fire</p>",
            casting_time="1 standard action",
            components="V, S, M",
            range="Long",
            duration="Instantaneous",
            saving_throw="Reflex half",
            spell_resistance="yes",
            class_levels={"wizard": "3", "sorcerer": "3"},
            descriptor="fire",
        )

        assert spell.name == "Fireball"
        assert spell.school == "Evocation"
        assert spell.descriptor == "fire"
        assert "wizard" in spell.class_levels
        assert spell.class_levels["wizard"] == "3"

    def test_from_series(self, sample_spell_series):
        """Test creating Spell from pandas Series."""
        class_columns = ["wizard", "sorcerer", "cleric", "bard"]
        spell = Spell.from_series(sample_spell_series, class_columns)

        assert spell.name == "Fireball"
        assert spell.school == "Evocation"
        assert "wizard" in spell.class_levels
        assert spell.class_levels["wizard"] == "3"
        assert "cleric" not in spell.class_levels  # Should exclude NULL values

    def test_is_available_for_class(self):
        """Test checking if spell is available for a class."""
        spell = Spell(
            name="Fireball",
            school="Evocation",
            source="Core",
            description="A ball of fire",
            description_formatted="<p>A ball of fire</p>",
            casting_time="1 standard action",
            components="V, S, M",
            range="Long",
            duration="Instantaneous",
            saving_throw="Reflex half",
            spell_resistance="yes",
            class_levels={"wizard": "3", "sorcerer": "3"},
        )

        assert spell.is_available_for_class("wizard")
        assert spell.is_available_for_class("sorcerer")
        assert not spell.is_available_for_class("cleric")

    def test_get_level_for_class(self):
        """Test getting spell level for a class."""
        spell = Spell(
            name="Fireball",
            school="Evocation",
            source="Core",
            description="A ball of fire",
            description_formatted="<p>A ball of fire</p>",
            casting_time="1 standard action",
            components="V, S, M",
            range="Long",
            duration="Instantaneous",
            saving_throw="Reflex half",
            spell_resistance="yes",
            class_levels={"wizard": "3", "sorcerer": "3"},
        )

        assert spell.get_level_for_class("wizard") == "3"
        assert spell.get_level_for_class("sorcerer") == "3"
        assert spell.get_level_for_class("cleric") is None

    def test_optional_fields(self):
        """Test that optional fields default to None."""
        spell = Spell(
            name="Test",
            school="Evocation",
            source="Core",
            description="Test",
            description_formatted="Test",
            casting_time="1 standard action",
            components="V",
            range="Medium",
            duration="Instantaneous",
            saving_throw="none",
            spell_resistance="no",
            class_levels={},
        )

        assert spell.subschool is None
        assert spell.descriptor is None
        assert spell.area is None
        assert spell.effect is None
        assert spell.targets is None
        assert spell.dismissible is None
        assert spell.shapeable is None
