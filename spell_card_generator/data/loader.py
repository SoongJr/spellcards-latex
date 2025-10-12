"""Data loading functionality."""

from pathlib import Path
from typing import Set, List, Optional
import pandas as pd

from spell_card_generator.config.constants import Config, CharacterClasses
from spell_card_generator.utils.exceptions import DataLoadError
from spell_card_generator.utils.class_categorization import categorize_character_classes


class SpellDataLoader:
    """Handles loading and basic processing of spell data."""

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = (
            data_file or Path(__file__).parent.parent / Config.SPELL_DATA_FILE
        )
        self.spells_df: Optional[pd.DataFrame] = None
        self.character_classes: List[str] = []
        self.spell_sources: Set[str] = set()

    def load_data(self) -> pd.DataFrame:
        """Load spell data from TSV file."""
        if not self.data_file.exists():
            raise DataLoadError(f"Could not find spell data file at {self.data_file}")

        try:
            self.spells_df = pd.read_csv(self.data_file, sep="\t", dtype=str)
            self.spells_df = self.spells_df.fillna(Config.NULL_VALUE)

            self._extract_character_classes()
            self._extract_spell_sources()

            return self.spells_df

        except Exception as e:
            raise DataLoadError(f"Failed to load spell data: {e}")

    def _extract_character_classes(self):
        """Extract available character classes from data."""
        all_classes = []
        for category_classes in CharacterClasses.CATEGORIES.values():
            all_classes.extend(category_classes)

        # Add any additional classes found in the data
        all_classes.extend(["adept"])  # Known additional class

        self.character_classes = [
            cls for cls in all_classes if cls in self.spells_df.columns
        ]

    def _extract_spell_sources(self):
        """Extract available spell sources from data."""
        if "source" in self.spells_df.columns:
            self.spell_sources = set(self.spells_df["source"].unique())
            self.spell_sources.discard(Config.NULL_VALUE)

    def get_spells_for_class(self, class_name: str) -> pd.DataFrame:
        """Get all spells available for a specific class."""
        if self.spells_df is None:
            raise DataLoadError("Spell data not loaded")

        if class_name not in self.spells_df.columns:
            raise DataLoadError(f"Class {class_name} not found in data")

        return self.spells_df[self.spells_df[class_name] != Config.NULL_VALUE]

    def get_class_categories(self) -> dict:
        """Get character classes organized by categories."""
        if not self.character_classes:
            return {}

        return categorize_character_classes(self.character_classes)
