"""Utility functions for character class operations."""

from typing import Dict, List
from spell_card_generator.config.constants import CharacterClasses


def categorize_character_classes(character_classes: List[str]) -> Dict[str, Dict]:
    """
    Organize character classes into categories with counts.

    Args:
        character_classes: List of character class names available in the data

    Returns:
        Dictionary mapping category display names to category data containing
        classes and expansion state
    """
    categories = {}

    # Filter categories to only include classes that exist in the data
    for category_name, class_list in CharacterClasses.CATEGORIES.items():
        existing_classes = [cls for cls in class_list if cls in character_classes]
        if existing_classes:
            categories[f"{category_name} ({len(existing_classes)})"] = {
                "classes": existing_classes,
                "expanded": category_name
                == "Core Classes",  # Only Core Classes start expanded
            }

    # Find unknown classes and add them to "Other"
    known_classes = set()
    for classes in CharacterClasses.CATEGORIES.values():
        known_classes.update(classes)

    unknown_classes = [cls for cls in character_classes if cls not in known_classes]
    if unknown_classes:
        categories[f"Other ({len(unknown_classes)})"] = {
            "classes": unknown_classes,
            "expanded": False,
        }

    return categories
