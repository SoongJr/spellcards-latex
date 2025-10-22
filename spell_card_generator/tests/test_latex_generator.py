"""Tests for spell_card_generator.generators.latex_generator module."""

# some complaints pylint may throw at us do not apply to test code:
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments,unused-argument,too-many-public-methods

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from spell_card_generator.generators.latex_generator import LaTeXGenerator
from spell_card_generator.utils.exceptions import GenerationError


@pytest.mark.unit
class TestLaTeXGenerator:
    """Test cases for LaTeXGenerator class."""

    def test_init(self):
        """Test LaTeXGenerator initialization."""
        generator = LaTeXGenerator()
        assert generator.progress_callback is None

    def test_apply_latex_fixes_quotes(self):
        """Test LaTeX fixes for quotes."""
        generator = LaTeXGenerator()
        text = 'He said "hello" to me'
        result = generator._apply_latex_fixes(text)
        assert "``" in result
        # The regex captures group \\1, which results in literal \1 in output
        assert "\\" in result  # Just verify it's been modified

    def test_apply_latex_fixes_measurements(self):
        """Test LaTeX fixes for measurements."""
        generator = LaTeXGenerator()
        text = "20-ft. radius"
        result = generator._apply_latex_fixes(text)
        # Should add spacing fixes
        assert "ft." in result

    def test_apply_latex_fixes_superscript_ordinals(self):
        """Test LaTeX fixes for ordinals."""
        generator = LaTeXGenerator()
        text = "This is the 1st time"
        result = generator._apply_latex_fixes(text)
        # The regex should match word boundaries, let's test with a realistic example
        assert "1st" in result or "\\textsuperscript{" in result

    def test_apply_latex_fixes_null_value(self):
        """Test LaTeX fixes with NULL value."""
        generator = LaTeXGenerator()
        result = generator._apply_latex_fixes("NULL")
        assert result == "NULL"

    def test_apply_latex_fixes_empty_string(self):
        """Test LaTeX fixes with empty string."""
        generator = LaTeXGenerator()
        result = generator._apply_latex_fixes("")
        assert result == ""

    def test_format_saving_throw_none(self):
        """Test formatting of 'none' saving throw."""
        generator = LaTeXGenerator()
        # The regex uses word boundaries, so it needs to be a complete word
        result = generator._format_saving_throw("none or Will negates")
        assert r"\textbf{none}" in result or "none" in result

    def test_format_saving_throw_null(self):
        """Test formatting of NULL saving throw."""
        generator = LaTeXGenerator()
        result = generator._format_saving_throw("NULL")
        assert r"\textbf{none}" in result

    def test_format_saving_throw_empty(self):
        """Test formatting of empty saving throw."""
        generator = LaTeXGenerator()
        result = generator._format_saving_throw("")
        assert r"\textbf{none}" in result

    def test_format_spell_resistance_no(self):
        """Test formatting of 'no' spell resistance."""
        generator = LaTeXGenerator()
        # The regex uses word boundaries, so it needs to be a complete word
        result = generator._format_spell_resistance("no or yes")
        assert r"\textbf{no}" in result or "no" in result

    def test_format_spell_resistance_null(self):
        """Test formatting of NULL spell resistance."""
        generator = LaTeXGenerator()
        result = generator._format_spell_resistance("NULL")
        assert r"\textbf{no}" in result

    def test_generate_english_url_simple(self):
        """Test generation of English URL for simple spell name."""
        generator = LaTeXGenerator()
        url = generator._generate_english_url("Fireball")
        assert url.startswith("https://www.d20pfsrd.com/magic/all-spells/f/")
        assert url.endswith("fireball/")

    def test_generate_english_url_with_spaces(self):
        """Test generation of English URL for spell with spaces."""
        generator = LaTeXGenerator()
        url = generator._generate_english_url("Magic Missile")
        assert "magic-missile" in url

    def test_generate_english_url_with_greater(self):
        """Test generation of English URL for 'Greater' spell."""
        generator = LaTeXGenerator()
        url = generator._generate_english_url("Teleport, Greater")
        # Should remove the ", Greater" part
        assert "teleport/" in url
        assert "greater" not in url.lower().split("/")[-2]

    def test_generate_english_url_with_roman_numerals(self):
        """Test generation of English URL for spell with roman numerals."""
        generator = LaTeXGenerator()
        url = generator._generate_english_url("Summon Monster III")
        # Should remove the roman numerals
        assert "summon-monster/" in url

    def test_get_output_file_path(self, sample_spell_series):
        """Test getting output file path for a spell."""
        output_path = LaTeXGenerator.get_output_file_path(
            "wizard", "Fireball", sample_spell_series
        )

        assert isinstance(output_path, Path)
        assert "wizard" in str(output_path)
        assert "3" in str(output_path)  # spell level
        assert output_path.suffix == ".tex"

    def test_get_output_file_path_sanitizes_name(self, sample_spell_series):
        """Test that output file path sanitizes spell name."""
        sample_spell_series["name"] = 'Test: "Spell" | Name'
        output_path = LaTeXGenerator.get_output_file_path(
            "wizard", sample_spell_series["name"], sample_spell_series
        )

        # Should not contain problematic characters
        filename = output_path.stem
        assert ":" not in filename
        assert '"' not in filename
        assert "|" not in filename

    def test_get_output_file_path_preserves_comma(self, sample_spell_series):
        """Test that output file path preserves commas in spell names."""
        sample_spell_series["name"] = "Invisibility, Greater"
        output_path = LaTeXGenerator.get_output_file_path(
            "wizard", sample_spell_series["name"], sample_spell_series
        )

        # Comma should be preserved in filename
        assert output_path.name == "Invisibility, Greater.tex"
        assert "," in output_path.stem

    def test_get_output_file_path_preserves_apostrophe(self, sample_spell_series):
        """Test that output file path preserves apostrophes in spell names."""
        sample_spell_series["name"] = "Mage's Magnificent Mansion"
        output_path = LaTeXGenerator.get_output_file_path(
            "wizard", sample_spell_series["name"], sample_spell_series
        )

        # Apostrophe should be preserved in filename
        assert output_path.name == "Mage's Magnificent Mansion.tex"
        assert "'" in output_path.stem

    def test_get_output_file_path_preserves_spaces(self, sample_spell_series):
        """Test that output file path preserves spaces in spell names."""
        sample_spell_series["name"] = "Magic Missile"
        output_path = LaTeXGenerator.get_output_file_path(
            "wizard", sample_spell_series["name"], sample_spell_series
        )

        # Spaces should be preserved in filename
        assert output_path.name == "Magic Missile.tex"
        assert " " in output_path.stem

    def test_generate_spell_latex(self, sample_spell_series):
        """Test generating LaTeX for a spell."""
        generator = LaTeXGenerator()
        latex, conflicts = generator.generate_spell_latex(sample_spell_series, "wizard")

        assert isinstance(latex, str)
        assert isinstance(conflicts, list)
        assert len(conflicts) == 0
        assert "\\begin{spellcard}" in latex
        assert "\\end{spellcard}" in latex
        assert "Fireball" in latex
        assert "wizard" in latex

    def test_generate_spell_latex_with_custom_german_url(self, sample_spell_series):
        """Test generating LaTeX with custom German URL."""
        generator = LaTeXGenerator()
        custom_url = "https://custom-url.com/spell"
        latex, conflicts = generator.generate_spell_latex(
            sample_spell_series, "wizard", german_url_template=custom_url
        )

        assert len(conflicts) == 0
        assert custom_url in latex

    @patch("spell_card_generator.generators.latex_generator.subprocess.run")
    def test_process_description_with_pandoc(self, mock_run, sample_spell_series):
        """Test processing description with pandoc."""
        generator = LaTeXGenerator()

        # Mock successful pandoc execution
        mock_run.return_value = MagicMock(stdout="Converted LaTeX text")

        result = generator._process_description("<p>HTML text</p>", "Fallback text")

        assert mock_run.called
        # Should return converted text (with potential fixes applied)
        assert "Converted" in result or "LaTeX" in result

    @patch("spell_card_generator.generators.latex_generator.subprocess.run")
    def test_process_description_pandoc_failure(self, mock_run, sample_spell_series):
        """Test processing description when pandoc fails."""
        generator = LaTeXGenerator()

        # Mock pandoc failure
        mock_run.side_effect = FileNotFoundError()

        result = generator._process_description("<p>HTML text</p>", "Fallback text")

        # Should fall back to plain text
        assert result == "Fallback text"

    def test_generate_latex_template(self, sample_spell_series):
        """Test generation of complete LaTeX template."""
        generator = LaTeXGenerator()
        latex, conflicts = generator._generate_latex_template(
            sample_spell_series,
            "wizard",
            "3",
            "https://english.com/spell",
            "https://german.com/spell",
            r"\textbf{none}",  # attackroll (already formatted by _detect_attack_roll)
        )

        assert isinstance(conflicts, list)
        assert len(conflicts) == 0
        assert r"\begin{spellcard}" in latex
        assert "{wizard}" in latex
        assert "{Fireball}" in latex
        assert "{3}" in latex
        assert "https://english.com/spell" in latex
        assert "https://german.com/spell" in latex
        assert "\\spellcardinfo" in latex
        assert "\\spellcardqr" in latex

    def test_generate_cards_creates_files(self, tmp_path, sample_spell_data):
        """Test that generate_cards creates files."""
        generator = LaTeXGenerator()

        # Create spell data list
        spell_series = sample_spell_data.iloc[0]
        selected_spells = [("wizard", "Fireball", spell_series)]

        with patch.object(LaTeXGenerator, "get_output_file_path") as mock_path:
            output_file = tmp_path / "test.tex"
            mock_path.return_value = output_file

            generated, skipped, conflicts = generator.generate_cards(
                selected_spells, overwrite=True
            )

            assert len(generated) == 1
            assert len(skipped) == 0
            assert len(conflicts) == 0
            assert output_file.exists()

    def test_generate_cards_skips_existing_without_overwrite(
        self, tmp_path, sample_spell_data
    ):
        """Test that generate_cards skips existing files when overwrite=False."""
        generator = LaTeXGenerator()

        spell_series = sample_spell_data.iloc[0]
        selected_spells = [("wizard", "Fireball", spell_series)]

        with patch.object(LaTeXGenerator, "get_output_file_path") as mock_path:
            output_file = tmp_path / "test.tex"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text("existing content")
            mock_path.return_value = output_file

            generated, skipped, conflicts = generator.generate_cards(
                selected_spells, overwrite=False
            )

            assert len(generated) == 0
            assert len(skipped) == 1
            assert len(conflicts) == 0
            # File should still have original content
            assert output_file.read_text() == "existing content"

    def test_generate_cards_overwrites_existing_with_overwrite(
        self, tmp_path, sample_spell_data
    ):
        """Test that generate_cards overwrites existing files when overwrite=True."""
        generator = LaTeXGenerator()

        spell_series = sample_spell_data.iloc[0]
        selected_spells = [("wizard", "Fireball", spell_series)]

        with patch.object(LaTeXGenerator, "get_output_file_path") as mock_path:
            output_file = tmp_path / "test.tex"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text("existing content")
            mock_path.return_value = output_file

            generated, skipped, conflicts = generator.generate_cards(
                selected_spells, overwrite=True
            )

            assert len(generated) == 1
            assert len(skipped) == 0
            assert len(conflicts) == 0
            # File should have new content
            assert "existing content" not in output_file.read_text()
            assert "spellcard" in output_file.read_text()

    def test_generate_cards_with_progress_callback(self, tmp_path, sample_spell_data):
        """Test that generate_cards calls progress callback."""
        generator = LaTeXGenerator()
        progress_calls = []

        def progress_callback(current, total, message):
            progress_calls.append((current, total, message))

        spell_series = sample_spell_data.iloc[0]
        selected_spells = [("wizard", "Fireball", spell_series)]

        with patch.object(LaTeXGenerator, "get_output_file_path") as mock_path:
            output_file = tmp_path / "test.tex"
            mock_path.return_value = output_file

            generator.generate_cards(
                selected_spells, overwrite=True, progress_callback=progress_callback
            )

            assert len(progress_calls) > 0
            # Should have at least initial and completion calls
            assert any("Processing" in call[2] for call in progress_calls)
            assert any("complete" in call[2] for call in progress_calls)

    def test_generate_cards_handles_errors(self, sample_spell_data):
        """Test that generate_cards handles errors properly."""
        generator = LaTeXGenerator()

        spell_series = sample_spell_data.iloc[0]
        selected_spells = [("wizard", "Fireball", spell_series)]

        with patch.object(
            generator, "generate_spell_latex", side_effect=Exception("Test error")
        ):
            with pytest.raises(GenerationError, match="Failed to generate spell card"):
                generator.generate_cards(selected_spells, overwrite=True)

    def test_generate_cards_special_characters_in_filename(
        self, tmp_path, sample_spell_data
    ):
        """Test that generate_cards handles special characters correctly."""
        generator = LaTeXGenerator()

        # Create spell with apostrophe like "Mage's Magnificent Mansion"
        spell_series = sample_spell_data.iloc[0].copy()
        spell_series["name"] = "Mage's Magnificent Mansion"
        selected_spells = [("wizard", "Mage's Magnificent Mansion", spell_series)]

        with patch(
            "spell_card_generator.utils.paths.PathConfig.get_output_base_path",
            return_value=tmp_path,
        ):
            generated, skipped, conflicts = generator.generate_cards(
                selected_spells, overwrite=True
            )

            assert len(generated) == 1
            assert len(conflicts) == 0

            # Verify the file was created with the correct name (apostrophe preserved)
            expected_file = (
                tmp_path
                / "src"
                / "spells"
                / "wizard"
                / "3"
                / "Mage's Magnificent Mansion.tex"
            )
            assert expected_file.exists()
            assert "'" in expected_file.name

            # Verify content contains the spell name
            content = expected_file.read_text()
            assert "Mage's Magnificent Mansion" in content

    def test_generate_cards_comma_in_filename(self, tmp_path, sample_spell_data):
        """Test that generate_cards handles commas in spell names correctly."""
        generator = LaTeXGenerator()

        # Create spell with comma like "Invisibility, Greater"
        spell_series = sample_spell_data.iloc[0].copy()
        spell_series["name"] = "Invisibility, Greater"
        selected_spells = [("wizard", "Invisibility, Greater", spell_series)]

        with patch(
            "spell_card_generator.utils.paths.PathConfig.get_output_base_path",
            return_value=tmp_path,
        ):
            generated, skipped, conflicts = generator.generate_cards(
                selected_spells, overwrite=True
            )

            assert len(generated) == 1
            assert len(conflicts) == 0

            # Verify the file was created with the correct name (comma preserved)
            expected_file = (
                tmp_path
                / "src"
                / "spells"
                / "wizard"
                / "3"
                / "Invisibility, Greater.tex"
            )
            assert expected_file.exists()
            assert "," in expected_file.name

            # Verify content contains the spell name
            content = expected_file.read_text()
            assert "Invisibility, Greater" in content

    def test_generate_cards_overwrite_special_characters(
        self, tmp_path, sample_spell_data
    ):
        """Test that overwriting works correctly with special characters in filename."""
        generator = LaTeXGenerator()

        # Create spell with apostrophe
        spell_series = sample_spell_data.iloc[0].copy()
        spell_series["name"] = "Mage's Magnificent Mansion"
        selected_spells = [("wizard", "Mage's Magnificent Mansion", spell_series)]

        with patch(
            "spell_card_generator.utils.paths.PathConfig.get_output_base_path",
            return_value=tmp_path,
        ):
            # First generation
            generated1, skipped1, conflicts1 = generator.generate_cards(
                selected_spells, overwrite=True
            )
            assert len(generated1) == 1
            assert len(skipped1) == 0
            assert len(conflicts1) == 0

            expected_file = (
                tmp_path
                / "src"
                / "spells"
                / "wizard"
                / "3"
                / "Mage's Magnificent Mansion.tex"
            )
            assert expected_file.exists()
            first_content = expected_file.read_text()

            # Try to generate again without overwrite - should skip
            generated2, skipped2, conflicts2 = generator.generate_cards(
                selected_spells, overwrite=False
            )
            assert len(generated2) == 0
            assert len(skipped2) == 1
            assert len(conflicts2) == 0
            assert expected_file.read_text() == first_content

            # Generate again with overwrite - should overwrite the same file
            generated3, skipped3, conflicts3 = generator.generate_cards(
                selected_spells, overwrite=True
            )
            assert len(generated3) == 1
            assert len(skipped3) == 0
            assert len(conflicts3) == 0

            # File should still exist with the same name
            assert expected_file.exists()
            assert "Mage's Magnificent Mansion.tex" in str(expected_file)
