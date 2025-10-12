"""LaTeX generation functionality."""

import re
import subprocess
from pathlib import Path
from typing import Callable, Optional, List, Tuple
import pandas as pd

from spell_card_generator.config.constants import Config
from spell_card_generator.utils.exceptions import GenerationError
from spell_card_generator.utils.validators import Validators


class LaTeXGenerator:
    """Handles LaTeX spell card generation."""

    def __init__(self):
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None

    def generate_cards(
        self,
        selected_spells: List[
            Tuple[str, str, pd.Series]
        ],  # (class_name, spell_name, spell_data)
        overwrite: bool = False,
        german_url_template: str = Config.DEFAULT_GERMAN_URL,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Generate LaTeX files for selected spells.

        Returns:
            Tuple of (generated_files, skipped_files)
        """
        self.progress_callback = progress_callback
        generated_files = []
        skipped_files = []

        try:
            total_spells = len(selected_spells)

            for i, (class_name, spell_name, spell_data) in enumerate(selected_spells):
                # Update progress
                if self.progress_callback:
                    self.progress_callback(
                        i, total_spells, f"Processing {spell_name}..."
                    )

                try:
                    output_file = self._get_output_file_path(
                        class_name, spell_name, spell_data
                    )

                    # Check if file exists
                    if output_file.exists() and not overwrite:
                        skipped_files.append(str(output_file))
                        continue

                    # Generate LaTeX content
                    latex_content = self.generate_spell_latex(
                        spell_data, class_name, german_url_template
                    )

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

            return generated_files, skipped_files

        except Exception as e:
            if not isinstance(e, GenerationError):
                raise GenerationError(f"Spell card generation failed: {e}") from e
            raise

    def _get_output_file_path(
        self, class_name: str, spell_name: str, spell_data: pd.Series
    ) -> Path:
        """Get the output file path for a spell."""
        # Get base directory (assuming we're in spell_card_generator/)
        base_dir = Path(__file__).parent.parent.parent

        # Create output directory path
        spell_level = spell_data[class_name]
        output_dir = base_dir / "src" / "spells" / class_name / spell_level

        # Sanitize filename
        safe_name = Validators.sanitize_filename(spell_name)
        output_file = output_dir / f"{safe_name}.tex"

        return output_file

    def generate_spell_latex(
        self,
        spell_data: pd.Series,
        character_class: str,
        german_url_template: str = Config.DEFAULT_GERMAN_URL,
    ) -> str:
        """Generate LaTeX code for a single spell."""
        try:
            # Get spell level for the selected class
            spell_level = spell_data[character_class]

            # Apply LaTeX fixes to relevant fields
            processed_data = self._process_spell_data(spell_data)

            # Generate URLs
            english_url = self._generate_english_url(spell_data["name"])
            german_url = german_url_template  # User can modify this manually

            # Generate LaTeX content
            latex_content = self._generate_latex_template(
                processed_data, character_class, spell_level, english_url, german_url
            )

            return latex_content

        except Exception as e:
            raise GenerationError(f"Failed to generate LaTeX for spell: {e}") from e

    def _process_spell_data(self, spell_data: pd.Series) -> pd.Series:
        """Process spell data and apply LaTeX fixes."""
        processed = spell_data.copy()

        # Apply LaTeX fixes to relevant fields
        fields_to_fix = ["effect", "range", "area", "targets", "mythic_text"]
        for field in fields_to_fix:
            if field in processed and processed[field] != Config.NULL_VALUE:
                processed[field] = self._apply_latex_fixes(processed[field])

        # Fix saving throw and spell resistance formatting
        processed["saving_throw"] = self._format_saving_throw(
            processed.get("saving_throw", "")
        )
        processed["spell_resistance"] = self._format_spell_resistance(
            processed.get("spell_resistance", "")
        )

        # Process description
        processed["description_formatted"] = self._process_description(
            processed.get("description_formatted", ""), processed.get("description", "")
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
            return "\\\\emph{N/A}"

        return re.sub(r"\\bnone\\b", r"\\\\textbf{none}", saving_throw)

    def _format_spell_resistance(self, spell_resistance: str) -> str:
        """Format spell resistance for LaTeX."""
        if not spell_resistance or spell_resistance == Config.NULL_VALUE:
            return "\\\\emph{N/A}"

        return re.sub(r"\\bno\\b", r"\\\\textbf{no}", spell_resistance)

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

    def _generate_latex_template(
        self,
        spell_data: pd.Series,
        character_class: str,
        spell_level: str,
        english_url: str,
        secondary_url: str,
    ) -> str:
        """Generate the complete LaTeX template for a spell."""

        # Helper function to get field value or empty string
        def get_field(field_name: str) -> str:
            value = spell_data.get(field_name, "")
            return value if value != Config.NULL_VALUE else ""

        return f"""%%%
%%% file content generated by spell_card_generator.py,
%%% meant to be fine-tuned manually (especially the description).
%%%
%
% open a new spellcards environment
\\begin{{spellcard}}{{{character_class}}}{{{get_field('name')}}}{{{spell_level}}}
  % make the data from TSV accessible for to the LaTeX part:
  \\newcommand{{\\name}}{{{get_field('name')}}}
  \\newcommand{{\\school}}{{{get_field('school')}}}
  \\newcommand{{\\subschool}}{{{get_field('subschool')}}}
  \\newcommand{{\\descriptor}}{{{get_field('descriptor')}}}
  \\newcommand{{\\spelllevel}}{{{spell_level}}}
  \\newcommand{{\\castingtime}}{{{get_field('casting_time')}}}
  \\newcommand{{\\components}}{{{get_field('components')}}}
  \\newcommand{{\\costlycomponents}}{{{get_field('costly_components')}}}
  \\newcommand{{\\range}}{{{get_field('range')}}}
  \\newcommand{{\\area}}{{{get_field('area')}}}
  \\newcommand{{\\effect}}{{{get_field('effect')}}}
  \\newcommand{{\\targets}}{{{get_field('targets')}}}
  \\newcommand{{\\duration}}{{{get_field('duration')}}}
  \\newcommand{{\\dismissible}}{{{get_field('dismissible')}}}
  \\newcommand{{\\shapeable}}{{{get_field('shapeable')}}}
  \\newcommand{{\\savingthrow}}{{{get_field('saving_throw')}}}
  \\newcommand{{\\spellresistance}}{{{get_field('spell_resistance')}}}
  \\newcommand{{\\source}}{{{get_field('source')}}}
  \\newcommand{{\\verbal}}{{{get_field('verbal')}}}
  \\newcommand{{\\somatic}}{{{get_field('somatic')}}}
  \\newcommand{{\\material}}{{{get_field('material')}}}
  \\newcommand{{\\focus}}{{{get_field('focus')}}}
  \\newcommand{{\\divinefocus}}{{{get_field('divine_focus')}}}
  \\newcommand{{\\deity}}{{{get_field('deity')}}}
  \\newcommand{{\\SLALevel}}{{{get_field('SLA_Level')}}}
  \\newcommand{{\\domain}}{{{get_field('domain')}}}
  \\newcommand{{\\acid}}{{{get_field('acid')}}}
  \\newcommand{{\\air}}{{{get_field('air')}}}
  \\newcommand{{\\chaotic}}{{{get_field('chaotic')}}}
  \\newcommand{{\\cold}}{{{get_field('cold')}}}
  \\newcommand{{\\curse}}{{{get_field('curse')}}}
  \\newcommand{{\\darkness}}{{{get_field('darkness')}}}
  \\newcommand{{\\death}}{{{get_field('death')}}}
  \\newcommand{{\\disease}}{{{get_field('disease')}}}
  \\newcommand{{\\earth}}{{{get_field('earth')}}}
  \\newcommand{{\\electricity}}{{{get_field('electricity')}}}
  \\newcommand{{\\emotion}}{{{get_field('emotion')}}}
  \\newcommand{{\\evil}}{{{get_field('evil')}}}
  \\newcommand{{\\fear}}{{{get_field('fear')}}}
  \\newcommand{{\\fire}}{{{get_field('fire')}}}
  \\newcommand{{\\force}}{{{get_field('force')}}}
  \\newcommand{{\\good}}{{{get_field('good')}}}
  \\newcommand{{\\languagedependent}}{{{get_field('language_dependent')}}}
  \\newcommand{{\\lawful}}{{{get_field('lawful')}}}
  \\newcommand{{\\light}}{{{get_field('light')}}}
  \\newcommand{{\\mindaffecting}}{{{get_field('mind_affecting')}}}
  \\newcommand{{\\pain}}{{{get_field('pain')}}}
  \\newcommand{{\\poison}}{{{get_field('poison')}}}
  \\newcommand{{\\shadow}}{{{get_field('shadow')}}}
  \\newcommand{{\\sonic}}{{{get_field('sonic')}}}
  \\newcommand{{\\water}}{{{get_field('water')}}}
  \\newcommand{{\\linktext}}{{{get_field('linktext')}}}
  \\newcommand{{\\id}}{{{get_field('id')}}}
  \\newcommand{{\\materialcosts}}{{{get_field('material_costs')}}}
  \\newcommand{{\\bloodline}}{{{get_field('bloodline')}}}
  \\newcommand{{\\patron}}{{{get_field('patron')}}}
  \\newcommand{{\\mythictext}}{{{get_field('mythic_text')}}}
  \\newcommand{{\\augmented}}{{{get_field('augmented')}}}
  \\newcommand{{\\hauntstatistics}}{{{get_field('haunt_statistics')}}}
  \\newcommand{{\\ruse}}{{{get_field('ruse')}}}
  \\newcommand{{\\draconic}}{{{get_field('draconic')}}}
  \\newcommand{{\\meditative}}{{{get_field('meditative')}}}
  \\newcommand{{\\urlenglish}}{{{english_url}}}
  \\newcommand{{\\urlsecondary}}{{{secondary_url}}}
  % print the tabular information at the top of the card:
  \\spellcardinfo{{}}
  % draw a QR Code pointing at online resources for this spell on the front face:
  \\spellcardqr{{\\urlenglish}}
  % \\spellcardqr{{\\urlsecondary}}
  %
  % Now follows a LaTeX-formatted description of the spell,
  % generated from the HTML-formatted description_formatted column:
  %
  {get_field('description_formatted')}
  %
\\end{{spellcard}}
"""
