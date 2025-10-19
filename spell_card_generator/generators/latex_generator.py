"""LaTeX generation functionality."""

import re
import subprocess
from pathlib import Path
from typing import Callable, Optional, List, Tuple, Dict, NamedTuple
from dataclasses import dataclass, field
import pandas as pd

from spell_card_generator.config.constants import Config
from spell_card_generator.utils.exceptions import GenerationError
from spell_card_generator.utils.validators import Validators
from spell_card_generator.utils.file_scanner import FileScanner
from spell_card_generator.utils.paths import PathConfig


class PropertyConflict(NamedTuple):
    """Represents a conflict between user modification and database update."""

    spell_name: str
    property_name: str
    old_db_value: str
    new_db_value: str


@dataclass
class PreservationOptions:
    """Options for preserving content from existing spell cards."""

    preserve_description: Dict[str, bool] = field(
        default_factory=dict
    )  # spell_name -> bool
    preserve_urls: Dict[str, bool] = field(default_factory=dict)  # spell_name -> bool
    url_configuration: Dict[str, Tuple[Optional[str], Optional[str]]] = field(
        default_factory=dict
    )  # spell_name -> (primary, secondary)
    preserve_properties: bool = True  # Global toggle for property preservation


class LaTeXGenerator:
    """Handles LaTeX spell card generation."""

    def __init__(self):
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None

    def generate_cards(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        self,
        selected_spells: List[
            Tuple[str, str, pd.Series]
        ],  # (class_name, spell_name, spell_data)
        overwrite: bool = False,
        german_url_template: str = Config.DEFAULT_GERMAN_URL,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        preservation_options: Optional[PreservationOptions] = None,
    ) -> Tuple[List[str], List[str], List[PropertyConflict]]:
        """
        Generate LaTeX files for selected spells.

        Args:
            selected_spells: List of (class_name, spell_name, spell_data) tuples
            overwrite: Whether to overwrite existing files
            german_url_template: Template for German URLs
            progress_callback: Optional callback for progress updates
            preservation_options: Options for preserving content from existing cards

        Returns:
            Tuple of (generated_files, skipped_files, conflicts)
        """
        self.progress_callback = progress_callback
        generated_files = []
        skipped_files = []
        all_conflicts = []

        # Initialize preservation options if not provided
        if preservation_options is None:
            preservation_options = PreservationOptions()

        # Extract preservation settings for convenience
        preserve_description = preservation_options.preserve_description
        preserve_urls = preservation_options.preserve_urls
        url_configuration = preservation_options.url_configuration
        preserve_properties = preservation_options.preserve_properties

        try:
            total_spells = len(selected_spells)

            for i, (class_name, spell_name, spell_data) in enumerate(selected_spells):
                # Update progress
                if self.progress_callback:
                    self.progress_callback(
                        i, total_spells, f"Processing {spell_name}..."
                    )

                try:
                    output_file = LaTeXGenerator.get_output_file_path(
                        class_name, spell_name, spell_data
                    )

                    # Check if file exists
                    if output_file.exists() and not overwrite:
                        skipped_files.append(str(output_file))
                        continue

                    # Check for preservation settings
                    should_preserve_desc = preserve_description.get(spell_name, False)
                    should_preserve_urls = preserve_urls.get(spell_name, False)

                    # Extract preserved content if needed
                    preserved_description = None
                    preserved_primary_url = None
                    preserved_secondary_url = None
                    preserved_width_ratio = None
                    preserved_properties = None

                    if (
                        should_preserve_desc or should_preserve_urls
                    ) and output_file.exists():
                        analysis = FileScanner.analyze_existing_card(output_file)

                        if should_preserve_desc:
                            preserved_description = FileScanner.extract_description(
                                output_file
                            )

                        if should_preserve_urls:
                            preserved_primary_url = analysis.get("primary_url", "")
                            preserved_secondary_url = analysis.get("secondary_url", "")

                        # Always preserve width ratio if present (automatic)
                        preserved_width_ratio = analysis.get("width_ratio")

                    # Always extract properties from existing cards for preservation
                    if output_file.exists():
                        preserved_properties = FileScanner.extract_properties(
                            output_file
                        )

                    # Get URL configuration for this spell
                    urls = url_configuration.get(spell_name, (None, None))
                    primary_url = urls[0] if urls[0] is not None else None
                    secondary_url = urls[1] if urls[1] is not None else None

                    # Use preserved URLs if requested
                    if should_preserve_urls and preserved_primary_url:
                        primary_url = preserved_primary_url
                    if should_preserve_urls and preserved_secondary_url:
                        secondary_url = preserved_secondary_url

                    # Generate LaTeX content
                    latex_content, conflicts = self.generate_spell_latex(
                        spell_data,
                        class_name,
                        german_url_template,
                        preserved_description=preserved_description,
                        custom_primary_url=primary_url,
                        custom_secondary_url=secondary_url,
                        preserved_width_ratio=preserved_width_ratio,
                        preserved_properties=preserved_properties,
                        spell_name=spell_name,
                        preserve_properties=preserve_properties,
                    )

                    # Collect conflicts
                    all_conflicts.extend(conflicts)

                    # Write file
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(latex_content)

                    generated_files.append(str(output_file))

                except Exception as e:
                    raise GenerationError(
                        f"Failed to generate spell card for {spell_name}: {e}"
                    ) from e

            # Complete progress
            if self.progress_callback:
                self.progress_callback(
                    total_spells, total_spells, "Generation complete"
                )

            return generated_files, skipped_files, all_conflicts

        except Exception as e:
            if not isinstance(e, GenerationError):
                raise GenerationError(f"Spell card generation failed: {e}") from e
            raise

    @staticmethod
    def get_output_base_path() -> Path:
        """
        Get the output base path for spell cards.

        Deprecated: Use PathConfig.get_output_base_path() instead.
        This method is kept for backward compatibility.
        """
        return PathConfig.get_output_base_path()

    @staticmethod
    def get_output_file_path(
        class_name: str, spell_name: str, spell_data: pd.Series
    ) -> Path:
        """Get the output file path for a spell."""

        # Create output directory path
        spell_level = str(spell_data[class_name])
        base_path = PathConfig.get_output_base_path()
        output_dir = PathConfig.get_spells_output_dir(
            base_path, class_name, spell_level
        )

        # Sanitize filename
        safe_name = Validators.sanitize_filename(spell_name)
        output_file: Path = output_dir / f"{safe_name}.tex"

        return output_file

    def generate_spell_latex(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        spell_data: pd.Series,
        character_class: str,
        german_url_template: str = Config.DEFAULT_GERMAN_URL,
        preserved_description: Optional[str] = None,
        custom_primary_url: Optional[str] = None,
        custom_secondary_url: Optional[str] = None,
        preserved_width_ratio: Optional[str] = None,
        preserved_properties: Optional[Dict[str, Tuple[str, Optional[str]]]] = None,
        spell_name: Optional[str] = None,
        preserve_properties: bool = True,  # Global toggle for property preservation
    ) -> Tuple[str, List[PropertyConflict]]:
        """
        Generate LaTeX code for a single spell.

        Args:
            spell_data: Series containing spell data
            character_class: Character class for the spell
            german_url_template: Template for German URLs
            preserved_description: Optional preserved description text
            custom_primary_url: Optional custom primary URL
            custom_secondary_url: Optional custom secondary URL
            preserved_width_ratio: Optional preserved width ratio
            preserved_properties: Optional dict of preserved properties
            spell_name: Optional spell name (defaults to spell_data['name'])
            preserve_properties: Whether to apply property preservation logic

        Returns:
            Tuple of (latex_content, conflicts)
        """
        try:
            # Get spell name for conflict tracking
            if spell_name is None:
                spell_name = spell_data.get("name", "Unknown")

            # Get spell level for the selected class
            spell_level = spell_data[character_class]

            # Apply LaTeX fixes to relevant fields
            processed_data = self._process_spell_data(spell_data, preserved_description)

            # Generate URLs (use custom if provided)
            english_url = (
                custom_primary_url
                if custom_primary_url
                else self._generate_english_url(spell_data["name"])
            )
            german_url = (
                custom_secondary_url if custom_secondary_url else german_url_template
            )

            # Generate LaTeX content
            latex_content, conflicts = self._generate_latex_template(
                processed_data,
                character_class,
                spell_level,
                english_url,
                german_url,
                preserved_width_ratio,
                preserved_properties,
                spell_name,
                preserve_properties,
            )

            return latex_content, conflicts

        except Exception as e:
            raise GenerationError(f"Failed to generate LaTeX for spell: {e}") from e

    def _process_spell_data(
        self, spell_data: pd.Series, preserved_description: Optional[str] = None
    ) -> pd.Series:
        """Process spell data and apply LaTeX fixes."""
        processed = spell_data.copy()

        # Apply LaTeX fixes to relevant fields
        # Note: Column names have underscores removed, so use mythictext not mythic_text
        fields_to_fix = ["effect", "range", "area", "targets", "mythictext"]
        for field_name in fields_to_fix:
            if field_name in processed and processed[field_name] != Config.NULL_VALUE:
                processed[field_name] = self._apply_latex_fixes(processed[field_name])

        # Fix saving throw and spell resistance formatting
        processed["savingthrow"] = self._format_saving_throw(
            processed.get("savingthrow", "")
        )
        processed["spellresistance"] = self._format_spell_resistance(
            processed.get("spellresistance", "")
        )

        # Process description - use preserved if provided
        if preserved_description:
            processed["descriptionformatted"] = preserved_description
        else:
            processed["descriptionformatted"] = self._process_description(
                processed.get("descriptionformatted", ""),
                processed.get("description", ""),
            )

        return processed

    def _apply_latex_fixes(self, text: str) -> str:
        """Apply LaTeX formatting fixes."""
        if not text or text == Config.NULL_VALUE:
            return text

        # Replace double quotes with LaTeX quotes
        text = re.sub(r'"([^"]+)"', r"``\\1\'\'", text)

        # Fix spacing for measurements
        text = re.sub(r"(\\d+[ -]?ft\\.) ([a-z])", r"\\1\\\\ \\2", text)
        text = re.sub(r"sq\\. ft\\.", r"sq.~ft.", text)

        # Fix spacing after periods before emphasized text
        text = re.sub(r"\\. \\\\emph\\{", r".\\@ \\\\emph{", text)

        # Superscript ordinals
        text = re.sub(
            r"(\\b\\d+)(st|nd|rd|th)\\b", r"\\1\\\\textsuperscript{\\2}", text
        )

        return text

    def _format_saving_throw(self, saving_throw: str) -> str:
        """Format saving throw for LaTeX."""
        if not saving_throw or saving_throw == Config.NULL_VALUE:
            return "\\textbf{none}"

        # Make "none" bold to emphasize it
        return re.sub(r"\bnone\b", r"\\textbf{none}", saving_throw, flags=re.IGNORECASE)

    def _format_spell_resistance(self, spell_resistance: str) -> str:
        """Format spell resistance for LaTeX."""
        if not spell_resistance or spell_resistance == Config.NULL_VALUE:
            return "\\textbf{no}"

        # Make "no" bold to emphasize it
        return re.sub(r"\bno\b", r"\\textbf{no}", spell_resistance, flags=re.IGNORECASE)

    def _process_description(
        self, description_formatted: str, description_fallback: str
    ) -> str:
        """Process spell description, converting HTML to LaTeX if possible."""
        if description_formatted and description_formatted != Config.NULL_VALUE:
            try:
                # Use pandoc to convert HTML to LaTeX
                process = subprocess.run(
                    ["pandoc", "-f", "html", "-t", "latex"],
                    input=description_formatted,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                processed = process.stdout
                return self._apply_latex_fixes(processed)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to plain text description if pandoc fails
                pass

        return description_fallback or ""

    def _generate_english_url(self, spell_name: str) -> str:
        """Generate English D20PFSRD URL for spell."""
        first_char = spell_name[0].lower()

        # Clean spell name for URL
        clean_name = re.sub(r"(, Greater| [IVX]+)$", "", spell_name)
        clean_name = clean_name.lower()
        clean_name = re.sub(r"[^a-z0-9]", "-", clean_name)
        clean_name = re.sub(r"-+", "-", clean_name).strip("-")

        return f"{Config.ENGLISH_URL_BASE}/{first_char}/{clean_name}/"

    def _apply_property_preservation_logic(
        self,
        property_name: str,
        db_value: str,
        preserved_properties: Optional[Dict[str, Tuple[str, Optional[str]]]],
        spell_name: str,
    ) -> Tuple[str, Optional[PropertyConflict]]:
        """
        Apply 4-case decision logic for property preservation.

        Returns:
            Tuple of (latex_command_line, optional_conflict)
        """
        # Case: No preserved properties (new card) - use DB value
        if not preserved_properties or property_name not in preserved_properties:
            return f"\\newcommand{{\\{property_name}}}{{{db_value}}}", None

        user_value, original_comment = preserved_properties[property_name]

        # Case 1: Unmodified - user value matches DB
        if user_value == db_value:
            return f"\\newcommand{{\\{property_name}}}{{{db_value}}}", None

        # Case 2: No modification marker - DB was updated, use new DB value
        if original_comment is None:
            return f"\\newcommand{{\\{property_name}}}{{{db_value}}}", None

        # Case 3: User modified, DB unchanged - preserve user modification
        if original_comment == db_value:
            return (
                f"\\newcommand{{\\{property_name}}}{{{user_value}}}% original: {{{db_value}}}",
                None,
            )

        # Case 4: CONFLICT - user modified AND DB updated
        # Preserve user value, update comment, track conflict
        conflict = PropertyConflict(
            spell_name=spell_name,
            property_name=property_name,
            old_db_value=original_comment,
            new_db_value=db_value,
        )
        return (
            f"\\newcommand{{\\{property_name}}}{{{user_value}}}% original: {{{db_value}}}",
            conflict,
        )

    # pylint: disable=too-many-locals,too-many-branches
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _generate_latex_template(
        self,
        spell_data: pd.Series,
        character_class: str,
        spell_level: str,
        english_url: str,
        secondary_url: str,
        preserved_width_ratio: Optional[str] = None,
        preserved_properties: Optional[Dict[str, Tuple[str, Optional[str]]]] = None,
        spell_name: Optional[str] = None,
        preserve_properties: bool = True,  # Global toggle for property preservation
    ) -> Tuple[str, List[PropertyConflict]]:
        """
        Generate the complete LaTeX template for a spell.

        Returns:
            Tuple of (latex_content, conflicts)
        """
        conflicts = []

        # Helper function to get field value or NULL
        def get_field(field_name: str) -> str:
            value = spell_data.get(field_name, "")
            # Return "NULL" for missing/null values to match legacy behavior
            return value if value != Config.NULL_VALUE else "NULL"

        # Get spell name for conflict tracking
        if spell_name is None:
            spell_name = get_field("name")

        # Build property commands with preservation logic
        # Note: Column names in spell_data have underscores removed during loading
        # to match LaTeX property names (LaTeX commands cannot contain underscores)
        property_names = [
            "name",
            "school",
            "subschool",
            "descriptor",
            "spelllevel",  # Special: use parameter value, not from data
            "castingtime",
            "components",
            "costlycomponents",
            "range",
            "area",
            "effect",
            "targets",
            "duration",
            "dismissible",
            "shapeable",
            "savingthrow",
            "spellresistance",
            "source",
            "verbal",
            "somatic",
            "material",
            "focus",
            "divinefocus",
            "deity",
            "SLALevel",
            "domain",
            "acid",
            "air",
            "chaotic",
            "cold",
            "curse",
            "darkness",
            "death",
            "disease",
            "earth",
            "electricity",
            "emotion",
            "evil",
            "fear",
            "fire",
            "force",
            "good",
            "languagedependent",
            "lawful",
            "light",
            "mindaffecting",
            "pain",
            "poison",
            "shadow",
            "sonic",
            "water",
            "linktext",
            "id",
            "materialcosts",
            "bloodline",
            "patron",
            "mythictext",
            "augmented",
            "hauntstatistics",
            "ruse",
            "draconic",
            "meditative",
        ]

        property_commands = []

        # Generate property commands with preservation logic
        for prop_name in property_names:
            if prop_name == "spelllevel":
                # Special case: use the spell level parameter, not from data
                db_value = spell_level
            else:
                db_value = get_field(prop_name)

            # Apply preservation logic only if globally enabled
            if preserve_properties:
                cmd_line, conflict = self._apply_property_preservation_logic(
                    prop_name, db_value, preserved_properties, spell_name
                )
                if conflict:
                    conflicts.append(conflict)
            else:
                # Skip preservation - always use DB value
                cmd_line = f"\\newcommand{{\\{prop_name}}}{{{db_value}}}"

            property_commands.append(cmd_line)

        # Handle URL properties separately - URLs are either preserved or generated
        # (no comparison logic or "% original:" comments needed)
        url_cmd1 = f"\\newcommand{{\\urlenglish}}{{{english_url}}}"
        property_commands.append(url_cmd1)

        url_cmd2 = f"\\newcommand{{\\urlsecondary}}{{{secondary_url}}}"
        property_commands.append(url_cmd2)

        # Join all property commands
        properties_section = "\n  ".join(property_commands)

        # Prepare QR code lines (can't use backslashes in f-string expressions)
        primary_qr = (
            "\\spellcardqr{\\urlenglish}"
            if english_url
            else "% \\spellcardqr{\\urlenglish}"
        )
        secondary_qr = (
            "\\spellcardqr{\\urlsecondary}"
            if (secondary_url and secondary_url != Config.DEFAULT_GERMAN_URL)
            else "% \\spellcardqr{\\urlsecondary}"
        )

        # Prepare \spellcardinfo with optional width ratio
        spellcardinfo_line = (
            f"\\spellcardinfo[{preserved_width_ratio}]{{}}"
            if preserved_width_ratio
            else "\\spellcardinfo{}"
        )

        # Get description for template
        # Note: Column name has underscores removed
        description_content = get_field("descriptionformatted")
        spell_name_for_template = spell_data.get("name", "")

        latex_content = f"""%%%
%%% file content generated by spell_card_generator.py,
%%% meant to be fine-tuned manually (especially the description).
%%%
%
% open a new spellcards environment
\\begin{{spellcard}}{{{character_class}}}{{{spell_name_for_template}}}{{{spell_level}}}
  % make the data from TSV accessible for to the LaTeX part:
  {properties_section}
  % print the tabular information at the top of the card:
  {spellcardinfo_line}
  % draw a QR Code pointing at online resources for this spell on the front face:
  {primary_qr}
  {secondary_qr}
  %
  % SPELL DESCRIPTION BEGIN
  {description_content}
  % SPELL DESCRIPTION END
  %
\\end{{spellcard}}
"""

        return latex_content, conflicts
