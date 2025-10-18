"""Path utilities for the spell card generator."""

from pathlib import Path


class PathConfig:
    """Central configuration for file system paths."""

    @staticmethod
    def get_output_base_path() -> Path:
        """
        Get the base output directory for spell cards.

        Returns:
            Path to the base directory (typically project root)
        """
        # Navigate up from utils/ to spell_card_generator/ to project root
        return Path(__file__).parent.parent.parent

    @staticmethod
    def get_spells_output_dir(
        base_path: Path, class_name: str, spell_level: str
    ) -> Path:
        """
        Get the output directory for a specific spell level.

        Args:
            base_path: Base directory path
            class_name: Character class (e.g., "wizard")
            spell_level: Spell level (e.g., "3")

        Returns:
            Path to the output directory: {base}/src/spells/{class}/{level}/
        """
        return base_path / "src" / "spells" / class_name / spell_level

    @staticmethod
    def get_class_spells_dir(base_path: Path, class_name: str) -> Path:
        """
        Get the directory containing all spells for a class.

        Args:
            base_path: Base directory path
            class_name: Character class (e.g., "wizard")

        Returns:
            Path to the class directory: {base}/src/spells/{class}/
        """
        return base_path / "src" / "spells" / class_name
