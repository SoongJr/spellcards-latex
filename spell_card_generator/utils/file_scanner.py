"""File scanning utilities for detecting existing spell cards."""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd

from spell_card_generator.utils.validators import Validators


class FileScanner:
    """Utility class for scanning existing spell card files."""

    @staticmethod
    def detect_existing_cards(
        selected_spells: List[Tuple[str, str, pd.Series]],
        base_directory: Optional[Path] = None,
    ) -> Dict[str, Path]:
        """
        Detect existing .tex files for selected spells.

        Args:
            selected_spells: List of (class_name, spell_name, spell_data) tuples
            base_directory: Base directory to search in (defaults to project root)

        Returns:
            Dictionary mapping spell names to their existing file paths
        """
        if base_directory is None:
            # Get base directory (assuming we're in spell_card_generator/)
            base_directory = Path(__file__).parent.parent.parent

        existing_cards = {}

        for class_name, spell_name, spell_data in selected_spells:
            file_path = FileScanner._get_expected_file_path(
                class_name, spell_name, spell_data, base_directory
            )

            if file_path.exists():
                existing_cards[spell_name] = file_path

        return existing_cards

    @staticmethod
    def _get_expected_file_path(
        class_name: str, spell_name: str, spell_data: pd.Series, base_directory: Path
    ) -> Path:
        """
        Get the expected file path for a spell card.

        This mirrors the logic in LaTeXGenerator._get_output_file_path()
        to ensure consistency.
        """
        # Get spell level for the class
        spell_level = str(spell_data[class_name])

        # Build path: src/spells/{class}/{level}/{spell_name}.tex
        output_dir = base_directory / "src" / "spells" / class_name / spell_level

        # Sanitize filename
        safe_name = Validators.sanitize_filename(spell_name)
        file_path: Path = output_dir / f"{safe_name}.tex"

        return file_path

    @staticmethod
    def analyze_existing_card(file_path: Path) -> Dict[str, Any]:
        """
        Analyze an existing spell card file for metadata.

        Args:
            file_path: Path to the .tex file

        Returns:
            Dictionary with analysis results including:
            - has_secondary_language: bool
            - secondary_language_urls: List[str]
            - qr_codes: List[str]
            - file_size: int
            - modification_time: float
        """
        if not file_path.exists():
            return {}

        try:
            content = file_path.read_text(encoding="utf-8")
            stats = file_path.stat()

            analysis = {
                "file_size": stats.st_size,
                "modification_time": stats.st_mtime,
                "has_secondary_language": False,
                "primary_url": "",
                "secondary_url": "",
                "secondary_language_urls": [],
                "qr_codes": [],
                "content_preview": (
                    content[:200] + "..." if len(content) > 200 else content
                ),
            }

            # Look for German/secondary language indicators
            german_patterns = [
                r"\\href\{[^}]*\.de[^}]*\}",  # German URLs
                r"\\qrcode\{[^}]*\.de[^}]*\}",  # German QR codes
                r"german",  # German language references
                r"deutsch",  # German language references
            ]

            for pattern in german_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    analysis["has_secondary_language"] = True
                    break

            # Extract URLs from \newcommand{\urlenglish} and \newcommand{\urlsecondary}
            primary_url_pattern = r"\\newcommand\{\\urlenglish\}\{([^}]+)\}"
            secondary_url_pattern = r"\\newcommand\{\\urlsecondary\}\{([^}]+)\}"

            primary_match = re.search(primary_url_pattern, content)
            secondary_match = re.search(secondary_url_pattern, content)

            analysis["primary_url"] = primary_match.group(1) if primary_match else ""
            analysis["secondary_url"] = (
                secondary_match.group(1) if secondary_match else ""
            )

            # Also extract all \href URLs for backward compatibility
            url_pattern = r"\\href\{([^}]+)\}"
            urls = re.findall(url_pattern, content)

            # If we didn't find URLs in newcommand format, fall back to href
            if not analysis["primary_url"] and urls:
                analysis["primary_url"] = urls[0] if len(urls) > 0 else ""
            if not analysis["secondary_url"] and urls:
                analysis["secondary_url"] = urls[1] if len(urls) > 1 else ""

            analysis["secondary_language_urls"] = [
                url for url in urls if ".de" in url or "german" in url.lower()
            ]

            # Extract QR codes
            qr_pattern = r"\\qrcode\{([^}]+)\}"
            qr_codes = re.findall(qr_pattern, content)
            analysis["qr_codes"] = qr_codes

            return analysis

        except (OSError, UnicodeDecodeError, PermissionError) as e:
            return {
                "error": str(e),
                "file_size": 0,
                "modification_time": 0,
                "has_secondary_language": False,
                "primary_url": "",
                "secondary_url": "",
                "secondary_language_urls": [],
                "qr_codes": [],
            }

    @staticmethod
    def extract_description(  # pylint: disable=too-many-return-statements
        file_path: Path,
    ) -> str:
        """
        Extract the description section from an existing .tex file.

        Args:
            file_path: Path to the .tex file

        Returns:
            The description text, or empty string if not found
        """
        if not file_path.exists():
            return ""

        try:
            content = file_path.read_text(encoding="utf-8")

            # Pattern: % SPELL DESCRIPTION BEGIN ... % SPELL DESCRIPTION END
            pattern = r"% SPELL DESCRIPTION BEGIN\s*\n(.*?)\n\s*% SPELL DESCRIPTION END"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
            return ""

        except (OSError, UnicodeDecodeError, PermissionError):
            return ""

    @staticmethod
    def get_conflicts_summary(existing_cards: Dict[str, Path]) -> Dict[str, Any]:
        """
        Get a summary of conflicts for display to the user.

        Args:
            existing_cards: Dictionary of spell_name -> file_path

        Returns:
            Dictionary with conflict summary statistics
        """
        if not existing_cards:
            return {
                "total_conflicts": 0,
                "has_secondary_language": 0,
                "total_size": 0,
                "newest_modification": 0,
                "oldest_modification": 0,
            }

        analyses = {}
        for spell_name, file_path in existing_cards.items():
            analyses[spell_name] = FileScanner.analyze_existing_card(file_path)

        # Calculate summary statistics
        total_conflicts = len(existing_cards)
        has_secondary_language = sum(
            1
            for analysis in analyses.values()
            if analysis.get("has_secondary_language", False)
        )
        total_size = sum(analysis.get("file_size", 0) for analysis in analyses.values())

        modification_times = [
            analysis.get("modification_time", 0)
            for analysis in analyses.values()
            if analysis.get("modification_time", 0) > 0
        ]

        return {
            "total_conflicts": total_conflicts,
            "has_secondary_language": has_secondary_language,
            "total_size": total_size,
            "newest_modification": max(modification_times) if modification_times else 0,
            "oldest_modification": min(modification_times) if modification_times else 0,
            "analyses": analyses,
        }
