"""Tests for spell_card_generator.utils.class_categorization module."""

# pylint: disable=duplicate-code

import pytest

from spell_card_generator.utils.class_categorization import categorize_character_classes


@pytest.mark.unit
class TestClassCategorization:
    """Test cases for class categorization utilities."""

    def test_categorize_character_classes_with_core_classes(self):
        """Test categorization with core classes."""
        classes = ["wiz", "sor", "cleric", "druid"]
        categories = categorize_character_classes(classes)

        assert len(categories) > 0
        # Find the Core Classes category
        core_category = [k for k in categories if k.startswith("Core Classes")]
        assert len(core_category) == 1

        core_key = core_category[0]
        assert categories[core_key]["expanded"] is True
        assert "wiz" in categories[core_key]["classes"]
        assert "cleric" in categories[core_key]["classes"]

    def test_categorize_character_classes_with_base_classes(self):
        """Test categorization with base classes."""
        classes = ["alchemist", "summoner", "witch", "magus"]
        categories = categorize_character_classes(classes)

        # Find the Base Classes category
        base_category = [k for k in categories if k.startswith("Base Classes")]
        assert len(base_category) == 1

        base_key = base_category[0]
        assert categories[base_key]["expanded"] is False
        assert "alchemist" in categories[base_key]["classes"]
        assert "magus" in categories[base_key]["classes"]

    def test_categorize_character_classes_with_unknown_classes(self):
        """Test categorization with unknown classes."""
        classes = ["wiz", "custom_class", "homebrew_class"]
        categories = categorize_character_classes(classes)

        # Find the Other category
        other_category = [k for k in categories if k.startswith("Other")]
        assert len(other_category) == 1

        other_key = other_category[0]
        assert categories[other_key]["expanded"] is False
        assert "custom_class" in categories[other_key]["classes"]
        assert "homebrew_class" in categories[other_key]["classes"]

    def test_categorize_character_classes_counts(self):
        """Test that category names include counts."""
        classes = ["wiz", "sor", "cleric"]
        categories = categorize_character_classes(classes)

        # Check that counts are included in category names
        for category_name, category_data in categories.items():
            assert "(" in category_name
            assert ")" in category_name
            # Extract count from name like "Core Classes (3)"
            count_str = category_name.split("(")[1].split(")")[0]
            count = int(count_str)
            assert count == len(category_data["classes"])

    def test_categorize_character_classes_empty_list(self):
        """Test categorization with empty class list."""
        categories = categorize_character_classes([])

        assert len(categories) == 0

    def test_categorize_character_classes_mixed(self):
        """Test categorization with mixed class types."""
        classes = [
            "wiz",
            "sor",  # Core
            "alchemist",
            "witch",  # Base
            "bloodrager",
            "hunter",  # Hybrid
            "unknown_class",  # Other
        ]
        categories = categorize_character_classes(classes)

        # Should have at least 3 categories (Core, Base, Hybrid, possibly Other)
        assert len(categories) >= 3

        # Verify all classes are categorized
        all_categorized_classes = []
        for category_data in categories.values():
            all_categorized_classes.extend(category_data["classes"])

        for cls in classes:
            assert cls in all_categorized_classes

    def test_categorize_character_classes_structure(self):
        """Test the structure of returned categories."""
        classes = ["wiz", "cleric"]
        categories = categorize_character_classes(classes)

        for category_name, category_data in categories.items():
            assert isinstance(category_name, str)
            assert isinstance(category_data, dict)
            assert "classes" in category_data
            assert "expanded" in category_data
            assert isinstance(category_data["classes"], list)
            assert isinstance(category_data["expanded"], bool)

    def test_categorize_character_classes_no_duplicates(self):
        """Test that classes don't appear in multiple categories."""
        classes = ["wiz", "sor", "cleric", "alchemist", "bloodrager"]
        categories = categorize_character_classes(classes)

        all_classes = []
        for category_data in categories.values():
            all_classes.extend(category_data["classes"])

        # Check for duplicates
        assert len(all_classes) == len(set(all_classes))
