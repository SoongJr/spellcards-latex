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
    url_configuration: Dict[str, List[Tuple[Optional[str], bool]]] = field(
        default_factory=dict
    )  # spell_name -> [(url, is_valid), ...] where [0] is primary, [1] is secondary, etc.
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
                    # url_configuration is: spell_name -> [(url, is_valid), ...]
                    # where [0] is primary, [1] is secondary, etc.
                    url_list = url_configuration.get(spell_name, [])

                    # Extract primary URL and validation status (index 0)
                    primary_url = None
                    primary_url_valid = True
                    if len(url_list) > 0 and url_list[0][0] is not None:
                        primary_url = url_list[0][0]
                        primary_url_valid = url_list[0][1]

                    # Extract secondary URL and validation status (index 1)
                    secondary_url = None
                    secondary_url_valid = True
                    if len(url_list) > 1 and url_list[1][0] is not None:
                        secondary_url = url_list[1][0]
                        secondary_url_valid = url_list[1][1]

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
                        primary_url_valid=primary_url_valid,
                        secondary_url_valid=secondary_url_valid,
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

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # pylint: disable=too-many-locals
    def generate_spell_latex(
        self,
        spell_data: pd.Series,
        character_class: str,
        german_url_template: str = Config.DEFAULT_GERMAN_URL,
        preserved_description: Optional[str] = None,
        custom_primary_url: Optional[str] = None,
        custom_secondary_url: Optional[str] = None,
        primary_url_valid: bool = True,
        secondary_url_valid: bool = True,
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
            primary_url_valid: Whether primary URL is valid
            secondary_url_valid: Whether secondary URL is valid
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

            # Detect attack roll requirement from description
            description = spell_data.get("description", "")
            attackroll = self._detect_attack_roll(description)

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
                primary_url_valid,
                secondary_url_valid,
                attackroll,  # Pass computed attack roll value
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

        # description needs to be indented to the proper level, currently two spaces:
        if (
            processed["descriptionformatted"]
            and processed["descriptionformatted"] != Config.NULL_VALUE
        ):
            desc_lines = processed["descriptionformatted"].splitlines()
            # Only indent non-empty lines to avoid trailing whitespace on blank lines
            indented_lines = [f"  {line}" if line else "" for line in desc_lines]
            processed["descriptionformatted"] = "\n".join(indented_lines)

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

    @staticmethod
    def _detect_attack_roll(description: str) -> str:
        """
        Detect attack roll requirement from spell description.

        Returns one of: "none", "ranged touch", "melee touch", "ranged",
                        "melee", or "inconclusive"

        Priority order:
        1. Ranged touch attack (high confidence)
        2. Melee touch attack (high confidence)
        3. Context-based ranged/melee attack detection
        4. Inconclusive (mentions attacks but unclear context, or missing description)
        5. None (no attack mention)
        """
        if not description:
            return "inconclusive"

        desc_lower = description.lower()

        # HIGH CONFIDENCE: Touch attacks
        if "ranged touch attack" in desc_lower:
            return "ranged touch"
        if "melee touch attack" in desc_lower or "touch attack" in desc_lower:
            # "touch attack" defaults to melee unless "ranged" is nearby
            return "melee touch"

        # Define context patterns
        attack_patterns = [
            # makes normal attack
            r"\bmake(?:s)?\s+a\s+(?:\w+\s+)?(ranged|melee)\s+attack\b",
            r"\bsucceed\s+(?:at|on)\s+(?:a\s+)?(ranged|melee)\s+attack\b",
            r"\b(ranged|melee)\s+attack\s+to\s+hit\b",
            r"\brequires?\s+(?:a\s+)?(ranged|melee)\s+attack\b",
            r"\bsuccessful\s+(ranged|melee)\s+attack\b",
            r"\bstrike\s+with\s+a\s+(ranged|melee)\s+attack\b",  # strike with attack
        ]

        buff_patterns = [
            r"\bbonus\s+to\s+(?:.*?\s+)?(ranged|melee)?\s*attack",
            r"\bpenalty\s+to\s+(?:.*?\s+)?(ranged|melee)?\s*attack",
            r"\baffects?\s+(?:.*?\s+)?(ranged|melee)?\s*attack",
            r"\bgrants?\s+(?:.*?\s+)?(ranged|melee)?\s*attack",
            r"\bapplies\s+to\s+(?:.*?\s+)?(ranged|melee)?\s*attack",
            r"\bdeflects?\s+(?:incoming\s+)?(?:.*?\s+)?(ranged|melee)?\s*attack",
        ]

        # Check for attack context (spell requires an attack)
        attack_matches = []
        for pattern in attack_patterns:
            for match in re.finditer(pattern, desc_lower):
                # Extract the attack type (ranged or melee) from the first capture group
                attack_type = match.group(1)
                if attack_type:
                    attack_matches.append(attack_type)

        # Check for buff context (spell doesn't require attack)
        has_buff_context = any(
            re.search(pattern, desc_lower) for pattern in buff_patterns
        )

        # Decision logic
        if attack_matches:
            if has_buff_context:
                return "inconclusive"  # Ambiguous - both attack and buff context
            return attack_matches[0]  # Clear attack context - "ranged" or "melee"

        # Check for general attack mentions without clear context
        if not has_buff_context and re.search(r"\battack\b", desc_lower):
            return "inconclusive"

        return r"\textbf{none}"  # Only buff context or no mention of "attack" at all

    def _generate_english_url(self, spell_name: str) -> str:
        """Generate English D20PFSRD URL for spell."""
        first_char = spell_name[0].lower()

        # Clean spell name for URL
        clean_name = re.sub(r"(, Greater| [IVX]+)$", "", spell_name)
        clean_name = clean_name.lower()
        clean_name = re.sub(r"[^a-z0-9]", "-", clean_name)
        clean_name = re.sub(r"-+", "-", clean_name).strip("-")

        return f"{Config.ENGLISH_URL_BASE}/{first_char}/{clean_name}/"

    @staticmethod
    def _looks_like_url(text: str) -> bool:
        """Check if text looks like a URL (starts with http:// or https://)."""
        if not text:
            return False
        return text.strip().startswith(("http://", "https://"))

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
        # Case: No preserved properties (new card) - use DB value (expl3 format)
        if not preserved_properties or property_name not in preserved_properties:
            return f"\\SpellProp{{{property_name}}}{{{db_value}}}", None

        user_value, original_comment = preserved_properties[property_name]

        # Case 1: Unmodified - user value matches DB (expl3 format)
        if user_value == db_value:
            return f"\\SpellProp{{{property_name}}}{{{db_value}}}", None

        # Case 2: No modification marker - DB was updated, use new DB value (expl3 format)
        if original_comment is None:
            return f"\\SpellProp{{{property_name}}}{{{db_value}}}", None

        # Case 3: User modified, DB unchanged - preserve user modification (expl3 format)
        if original_comment == db_value:
            return (
                f"\\SpellProp{{{property_name}}}{{{user_value}}}% original: {{{db_value}}}",
                None,
            )

        # Case 4: CONFLICT - user modified AND DB updated (expl3 format)
        # Preserve user value, update comment, track conflict
        conflict = PropertyConflict(
            spell_name=spell_name,
            property_name=property_name,
            old_db_value=original_comment,
            new_db_value=db_value,
        )
        return (
            f"\\SpellProp{{{property_name}}}{{{user_value}}}% original: {{{db_value}}}",
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
        primary_url_valid: bool,
        secondary_url_valid: bool,
        attackroll: str,  # Computed attack roll value
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
            "attackroll",  # Special: computed from description, not from data
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
            elif prop_name == "attackroll":
                # Special case: use computed attack roll value, not from data
                db_value = attackroll
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
                # Skip preservation - always use DB value (expl3 format)
                cmd_line = f"\\SpellProp{{{prop_name}}}{{{db_value}}}"

            # Add warning for properties requiring manual attention
            if prop_name == "attackroll" and db_value == "inconclusive":
                # Emit expl3 warning message during LaTeX compilation
                warning = (
                    r"\msg_warning:nnn { spellcard } { inconclusive-attack-roll } "
                    rf"{{ {spell_name} }}"
                )
                cmd_line += warning

            property_commands.append(cmd_line)

        # Join all property commands
        properties_section = "\n  ".join(property_commands)

        # Prepare QR code lines with direct URLs (not properties)
        # Check for placeholder (recompute since it's used here)
        is_secondary_placeholder = (
            not secondary_url
            or secondary_url == Config.DEFAULT_GERMAN_URL
            or "<german-spell-name>" in secondary_url
        )

        # Primary QR code with optional warning
        if english_url:
            primary_qr = f"\\SpellCardQR{{{english_url}}}"
            # Add warning if URL is invalid
            if not primary_url_valid:
                warning_msg = (
                    f"\\msg_warning:nnn {{ spellcard }} {{ invalid-url }} "
                    f"{{ {english_url} }}"
                )
                primary_qr += f"\n  {warning_msg}"
        else:
            primary_qr = "% \\SpellCardQR{<primary-url>}"

        # Secondary QR code with optional warning
        if not is_secondary_placeholder:
            secondary_qr = f"\\SpellCardQR{{{secondary_url}}}"
            # Add warning if URL is invalid
            if not secondary_url_valid:
                warning_msg = (
                    f"\\msg_warning:nnn {{ spellcard }} {{ invalid-url }} "
                    f"{{ {secondary_url} }}"
                )
                secondary_qr += f"\n  {warning_msg}"
        else:
            secondary_qr = "% \\SpellCardQR{<secondary-url>}"

        # Prepare \SpellCardInfo with optional width ratio
        spellcardinfo_line = (
            f"\\SpellCardInfo[{preserved_width_ratio}]{{}}"
            if preserved_width_ratio
            else "\\SpellCardInfo{}"
        )

        # Get description for template
        # Note: Column name has underscores removed
        description_content = get_field("descriptionformatted")
        spell_name_for_template = spell_data.get("name", "")

        latex_content = f"""%%%
%%% SPELL-CARD-VERSION: 2.1
%%%
%%% This file was generated by spell_card_generator.py and is designed
%%% to be fine-tuned manually (especially the description section).
%%%
%%% USER MODIFICATION GUIDELINES:
%%% - Description text: Edit freely between SPELL DESCRIPTION markers
%%% - Property values: You may edit \\SpellProp{{property}}{{value}} statements
%%%   * To preserve your changes on regeneration, add a comment after the value:
%%%     \\SpellProp{{targets}}{{modified value}}% original: {{database value}}
%%%   * The generator will preserve your modified value and update the comment
%%%     if the database changes, allowing you to review conflicts
%%% - URLs: Edit \\SpellProp{{urlenglish}}{{...}} and \\SpellProp{{urlsecondary}}{{...}}
%%% - Width ratio: Optional [ratio] parameter in \\SpellCardInfo[ratio]{{}}
%%%   preserves column width proportions if you've manually adjusted the table
%%%
%%% NOTE: Files without SPELL-CARD-VERSION are assumed to be legacy format
%%% (using \\newcommand instead of \\SpellProp).
%%%
%
% open a new spellcard environment
\\begin{{SpellCard}}{{{character_class}}}{{{spell_name_for_template}}}{{{spell_level}}}
  % make the data from TSV accessible to the LaTeX part:
  {properties_section}
  % print the tabular information at the top of the card:
  {spellcardinfo_line}
  % draw QR Codes pointing at online resources for this spell:
  {primary_qr}
  {secondary_qr}
  %
  % SPELL DESCRIPTION BEGIN
{description_content}
  % SPELL DESCRIPTION END
  %
\\end{{SpellCard}}
"""

        return latex_content, conflicts
