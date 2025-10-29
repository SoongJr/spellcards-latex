"""File scanning utilities for detecting existing spell cards."""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd

from spell_card_generator.utils.validators import Validators
from spell_card_generator.utils.paths import PathConfig


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
    def find_all_existing_cards(  # pylint: disable=too-many-branches
        spell_dataframe: Optional[pd.DataFrame],
        class_name: str,
        level_filter: str = "All",
        source_filter: str = "All",
        search_term: str = "",
        base_directory: Optional[Path] = None,
    ) -> List[Tuple[str, str, pd.Series]]:
        """
        Find all existing .tex spell card files for a class, with optional filters.

        This method scans the file system for existing spell cards and matches them
        with the spell database, applying the same filters as the spell selection UI.

        Args:
            spell_dataframe: DataFrame with all spell data
            class_name: Character class to search for (e.g., "wizard", "cleric")
            level_filter: Spell level filter ("All" or specific level like "3")
            source_filter: Source filter ("All" or specific source like "Core Rulebook")
            search_term: Search term to filter spell names (case-insensitive)
            base_directory: Base directory to search in
                            (defaults to LaTeXGenerator.get_output_base_path)

        Returns:
            List of (class_name, spell_name, spell_data) tuples for found cards
        """
        if spell_dataframe is None or spell_dataframe.empty:
            return []
        if base_directory is None:
            base_directory = PathConfig.get_output_base_path()

        spells_dir = PathConfig.get_class_spells_dir(base_directory, class_name)
        if not spells_dir.exists():
            return []

        found_spells: List[Tuple[str, str, pd.Series]] = []

        # Scan through all .tex files in src/spells/{class_name}/
        for tex_file in spells_dir.rglob("*.tex"):
            try:
                # Get relative path components: level/spellname.tex
                parts = tex_file.relative_to(spells_dir).parts
                if len(parts) != 2:  # Should be level/spell.tex
                    continue

                level, filename = parts
                spell_name_from_file = filename.replace(".tex", "")

                # Find matching spell in dataframe
                for _, row in spell_dataframe.iterrows():
                    sanitized = Validators.sanitize_filename(row["name"])
                    if sanitized != spell_name_from_file:
                        continue

                    # Verify this class has this spell at this level
                    if class_name not in row:
                        continue

                    spell_level = str(row[class_name])
                    if spell_level != level:
                        continue

                    # Apply level filter
                    if level_filter not in ("All", spell_level):
                        continue

                    # Apply source filter
                    if source_filter != "All":
                        spell_source = row.get("source", "")
                        if spell_source != source_filter:
                            continue

                    # Apply search term filter
                    if search_term:
                        spell_name_lower = row["name"].lower()
                        if search_term.lower() not in spell_name_lower:
                            continue

                    # All filters passed - add to found spells
                    found_spells.append((class_name, row["name"], row))
                    break

            except (ValueError, KeyError):
                # Skip files that don't match expected structure
                continue

        return found_spells

    @staticmethod
    def _get_expected_file_path(
        class_name: str, spell_name: str, spell_data: pd.Series, base_directory: Path
    ) -> Path:
        """
        Get the expected file path for a spell card.

        This mirrors the logic in LaTeXGenerator.get_output_file_path()
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
    def analyze_existing_card(  # pylint: disable=too-many-locals,too-many-branches
        file_path: Path,
    ) -> Dict[str, Any]:
        """
        Analyze an existing spell card file for metadata.

        Args:
            file_path: Path to the .tex file

        Returns:
            Dictionary with analysis results including:
            - has_secondary_language: bool
            - primary_url: str
            - secondary_url: str
            - secondary_language_urls: List[str]
            - qr_codes: List[str]
            - width_ratio: Optional[str] (e.g., "0.55" from \\spellcardinfo[0.55]{})
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
                "width_ratio": None,
                "content_preview": (
                    content[:200] + "..." if len(content) > 200 else content
                ),
            }

            # Look for German/secondary language indicators
            german_patterns = [
                r"\\href\{[^}]*\.de[^}]*\}",  # German URLs in href
                r"\\spellcardqr\{[^}]*\.de[^}]*\}",  # German QR codes (expl3)
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

            # Also check for expl3 format: \spellcardqr{url}
            # Skip commented lines by processing line-by-line
            if not analysis["primary_url"] or not analysis["secondary_url"]:
                spellcardqr_urls = []
                for line in content.split("\n"):
                    stripped = line.strip()
                    # Skip commented lines
                    if stripped.startswith("%"):
                        continue
                    # Extract \spellcardqr{url}
                    qr_match = re.search(r"\\spellcardqr\{([^}]+)\}", stripped)
                    if qr_match:
                        spellcardqr_urls.append(qr_match.group(1))
                # Use expl3 URLs if legacy format didn't find them
                if not analysis["primary_url"] and spellcardqr_urls:
                    analysis["primary_url"] = spellcardqr_urls[0]
                if not analysis["secondary_url"] and len(spellcardqr_urls) > 1:
                    analysis["secondary_url"] = spellcardqr_urls[1]

            # Also extract all \href URLs for backward compatibility
            url_pattern = r"\\href\{([^}]+)\}"
            urls = re.findall(url_pattern, content)

            # If we didn't find URLs in newcommand or spellcardqr format, fall back to href
            if not analysis["primary_url"] and urls:
                analysis["primary_url"] = urls[0] if len(urls) > 0 else ""
            if not analysis["secondary_url"] and urls:
                analysis["secondary_url"] = urls[1] if len(urls) > 1 else ""

            analysis["secondary_language_urls"] = [
                url for url in urls if ".de" in url or "german" in url.lower()
            ]

            # Extract width ratio from \spellcardinfo[RATIO]{}
            # Pattern: \spellcardinfo[0.55]{} or \spellcardinfo{}
            width_ratio_pattern = r"\\spellcardinfo\[([0-9.]+)\]\{\}"
            width_ratio_match = re.search(width_ratio_pattern, content)
            if width_ratio_match:
                ratio_value = width_ratio_match.group(1)
                # Validate ratio is reasonable (between 0 and 1)
                try:
                    ratio_float = float(ratio_value)
                    if 0 < ratio_float <= 1:
                        analysis["width_ratio"] = ratio_value
                except ValueError:
                    pass  # Invalid ratio, keep as None

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
                "width_ratio": None,
            }

    @staticmethod
    def extract_description(  # pylint: disable=too-many-return-statements
        file_path: Path,
    ) -> str:
        """
        Extract the description section from an existing .tex file.

        Strips the base indentation level (determined by the % SPELL DESCRIPTION BEGIN
        marker) from all lines, while preserving any additional indentation.

        Args:
            file_path: Path to the .tex file

        Returns:
            The description text with base indentation removed, or empty string if not found
        """
        if not file_path.exists():
            return ""

        try:
            content = file_path.read_text(encoding="utf-8")

            # Pattern: capture indentation before marker, then description content
            # Group 1: indentation before % SPELL DESCRIPTION BEGIN
            # Group 2: description content
            pattern = (
                r"^(\s*)% SPELL DESCRIPTION BEGIN\s*\n(.*?)\n\s*% SPELL DESCRIPTION END"
            )
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if not match:
                return ""

            base_indent = match.group(1)
            description_text = match.group(2)

            if not description_text.strip():
                return ""

            # Strip base indentation from each line
            lines = description_text.split("\n")
            dedented_lines = []

            for line in lines:
                if not line.strip():
                    # Empty or whitespace-only lines become truly empty
                    dedented_lines.append("")
                elif line.startswith(base_indent):
                    # Remove base indentation, keep any extra
                    dedented_lines.append(line[len(base_indent) :])
                else:
                    # Line has less indentation than base (shouldn't happen in well-formed files)
                    # Keep it as-is to avoid data loss
                    dedented_lines.append(line)

            # Join lines and strip trailing whitespace from the entire result
            result = "\n".join(dedented_lines).rstrip()
            return result

        except (OSError, UnicodeDecodeError, PermissionError):
            return ""

    @staticmethod
    def _detect_spell_file_version(content: str) -> str:
        """
        Detect the version of a spell card file from its header comment.

        Args:
            content: Full file content as string

        Returns:
            Version string (e.g., "2.0-expl3", "1.0-legacy", "legacy" for no version)
        """
        # Look for SPELL-CARD-VERSION comment in first 20 lines
        lines = content.split("\n", 20)
        for line in lines[:20]:
            match = re.search(r"SPELL-CARD-VERSION:\s*(\S+)", line)
            if match:
                return match.group(1)
        return "legacy"  # No version marker = legacy format

    @staticmethod
    def extract_properties(file_path: Path) -> Dict[str, Tuple[str, Optional[str]]]:
        """
        Extract all property definitions from a .tex file.

        Detects file version and uses appropriate parser:
        - Version 2.0-expl3: Uses \\spellprop{property}{value} format
        - Legacy (no version): Uses \\newcommand{\\property}{value} format

        Args:
            file_path: Path to the .tex file

        Returns:
            Dictionary mapping property names to (current_value, original_comment).
            Example: {"range": ("100 ft.", None)}
        """
        if not file_path.exists():
            return {}

        try:
            content = file_path.read_text(encoding="utf-8")
            version = FileScanner._detect_spell_file_version(content)

            # Use appropriate parser based on version
            if version.startswith("2.") or "expl3" in version:
                return FileScanner._extract_properties_expl3(content)
            return FileScanner._extract_properties_legacy(content)

        except (OSError, UnicodeDecodeError, PermissionError):
            return {}

    @staticmethod
    def _extract_properties_expl3(content: str) -> Dict[str, Tuple[str, Optional[str]]]:
        """
        Extract properties from expl3 format: \\spellprop{property}{value}.

        Also extracts URLs from \\spellcardqr{url} commands.

        Args:
            content: File content as string

        Returns:
            Dictionary mapping property names to (value, original_comment) tuples
        """
        properties: Dict[str, Tuple[str, Optional[str]]] = {}
        lines = content.split("\n")

        for line in lines:
            stripped = line.strip()
            if not stripped.startswith(r"\spellprop"):
                continue

            # Extract property name
            name_match = re.match(r"\\spellprop\{(\w+)\}", stripped)
            if not name_match:
                continue

            property_name = name_match.group(1)
            after_name = stripped[name_match.end() :]
            if not after_name.startswith("{"):
                continue

            # Extract value by counting braces
            value, value_end = FileScanner._extract_braced_value(after_name)
            if value is None:
                continue

            # Check for % original: {VALUE} comment
            original_value = None
            remainder = after_name[value_end + 1 :]
            original_match = re.search(r"%\s*original:\s*\{([^}]*)\}", remainder)
            if original_match:
                original_value = original_match.group(1)

            properties[property_name] = (value, original_value)

        # Extract URLs from \spellcardqr{url} commands (skip commented lines)
        qr_urls = []
        for line in lines:
            stripped = line.strip()
            # Skip commented lines (lines starting with % after whitespace)
            if stripped.startswith("%"):
                continue
            # Extract \spellcardqr{url} from non-commented lines
            qr_match = re.search(r"\\spellcardqr\{([^}]+)\}", stripped)
            if qr_match:
                qr_urls.append(qr_match.group(1))

        if qr_urls:
            # Store primary URL (first QR code)
            properties["urlenglish"] = (qr_urls[0], None)
            # Store secondary URL (second QR code) if present
            if len(qr_urls) > 1:
                properties["urlsecondary"] = (qr_urls[1], None)

        return properties

    @staticmethod
    def _extract_properties_legacy(
        content: str,
    ) -> Dict[str, Tuple[str, Optional[str]]]:
        """
        Extract properties from legacy format: \\newcommand{\\property}{value}.

        Legacy files store URLs in \\newcommand{\\urlenglish} and \\newcommand{\\urlsecondary}.

        Args:
            content: File content as string

        Returns:
            Dictionary mapping property names to (value, original_comment) tuples
        """
        properties: Dict[str, Tuple[str, Optional[str]]] = {}
        lines = content.split("\n")

        for line in lines:
            stripped = line.strip()
            if not stripped.startswith(r"\newcommand"):
                continue

            # Extract property name
            name_match = re.match(r"\\newcommand\{\\(\w+)\}", stripped)
            if not name_match:
                continue

            property_name = name_match.group(1)
            after_name = stripped[name_match.end() :]
            if not after_name.startswith("{"):
                continue

            # Extract value by counting braces
            value, value_end = FileScanner._extract_braced_value(after_name)
            if value is None:
                continue

            # Check for % original: {VALUE} comment
            original_value = None
            remainder = after_name[value_end + 1 :]
            original_match = re.search(r"%\s*original:\s*\{([^}]*)\}", remainder)
            if original_match:
                original_value = original_match.group(1)

            properties[property_name] = (value, original_value)

        # Legacy files have URLs in \newcommand format, already extracted above
        return properties

    @staticmethod
    def _extract_braced_value(text: str) -> Tuple[Optional[str], int]:
        """
        Extract a brace-delimited value, handling nested braces.

        Args:
            text: String starting with opening brace

        Returns:
            Tuple of (extracted_value, end_position) or (None, -1) if malformed
        """
        if not text.startswith("{"):
            return None, -1

        brace_count = 0
        value_start = 1  # Skip opening brace
        value_end = -1

        for i, char in enumerate(text):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    value_end = i
                    break

        if value_end == -1:
            return None, -1

        return text[value_start:value_end], value_end

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
