"""Tests for spell_card_generator.utils.file_scanner module."""

# pylint: disable=unused-argument,protected-access,import-outside-toplevel,duplicate-code

from typing import Any

import pytest

from spell_card_generator.utils.file_scanner import FileScanner


@pytest.mark.unit
class TestFileScanner:
    """Test cases for FileScanner class."""

    def test_detect_existing_cards_empty_list(self, tmp_path):
        """Test detect_existing_cards with empty spell list."""
        selected_spells: list[tuple[str, str, Any]] = []
        existing = FileScanner.detect_existing_cards(selected_spells, tmp_path)

        assert not existing

    def test_detect_existing_cards_no_existing_files(self, tmp_path, sample_spell_data):
        """Test detect_existing_cards when no files exist."""
        spell_series = sample_spell_data.iloc[0]
        selected_spells = [("wizard", "Fireball", spell_series)]

        existing = FileScanner.detect_existing_cards(selected_spells, tmp_path)

        assert not existing

    def test_detect_existing_cards_with_existing_file(
        self, tmp_path, sample_spell_data
    ):
        """Test detect_existing_cards finds existing files."""
        spell_series = sample_spell_data.iloc[0]
        spell_name = "Fireball"
        class_name = "wizard"
        spell_level = spell_series[class_name]

        # Create the expected directory structure
        output_dir = tmp_path / "src" / "spells" / class_name / spell_level
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create a dummy spell card file with correct capitalization
        spell_file = output_dir / "Fireball.tex"
        spell_file.write_text("% Dummy spell card content")

        selected_spells = [(class_name, spell_name, spell_series)]
        existing = FileScanner.detect_existing_cards(selected_spells, tmp_path)

        assert spell_name in existing
        assert existing[spell_name] == spell_file

    def test_detect_existing_cards_multiple_spells(self, tmp_path, sample_spell_data):
        """Test detect_existing_cards with multiple spells."""
        # Create files for some spells but not others
        selected_spells = []

        for idx, class_name in enumerate(["wizard", "wizard", "cleric"]):
            spell_series = sample_spell_data.iloc[idx]
            spell_name = spell_series["name"]
            spell_level = spell_series[class_name]

            if spell_level != "NULL":
                selected_spells.append((class_name, spell_name, spell_series))

                # Only create file for first spell
                if idx == 0:
                    output_dir = tmp_path / "src" / "spells" / class_name / spell_level
                    output_dir.mkdir(parents=True, exist_ok=True)
                    # Use exact spell name as it appears (with proper capitalization)
                    safe_name = spell_name.replace(" ", "-")
                    spell_file = output_dir / f"{safe_name}.tex"
                    spell_file.write_text("% Dummy content")

        existing = FileScanner.detect_existing_cards(selected_spells, tmp_path)

        # Should only find the first spell
        assert len(existing) == 1
        assert "Fireball" in existing

    def test_get_expected_file_path(self, tmp_path, sample_spell_data):
        """Test _get_expected_file_path returns correct path."""
        spell_series = sample_spell_data.iloc[0]
        class_name = "wizard"
        spell_name = "Fireball"

        file_path = FileScanner._get_expected_file_path(
            class_name, spell_name, spell_series, tmp_path
        )

        assert file_path.parent.name == "3"  # spell level
        assert file_path.parent.parent.name == "wizard"
        assert file_path.name == "Fireball.tex"  # Preserves capitalization

    def test_get_expected_file_path_sanitizes_filename(
        self, tmp_path, sample_spell_data
    ):
        """Test _get_expected_file_path sanitizes special characters."""
        spell_series = sample_spell_data.iloc[0].copy()
        class_name = "wizard"
        spell_name = 'Test: "Spell" | Name'

        file_path = FileScanner._get_expected_file_path(
            class_name, spell_name, spell_series, tmp_path
        )

        # Filename should be sanitized
        assert ":" not in file_path.name
        assert '"' not in file_path.name
        assert "|" not in file_path.name


@pytest.mark.unit
class TestFileScannerAnalyze:
    """Test analyze_existing_card functionality."""

    def test_analyze_existing_card_nonexistent_file(self, tmp_path):
        """Test analyze_existing_card with nonexistent file."""
        file_path = tmp_path / "nonexistent.tex"
        analysis = FileScanner.analyze_existing_card(file_path)

        assert not analysis

    def test_analyze_existing_card_basic(self, tmp_path):
        """Test analyze_existing_card with basic file."""
        content = r"""
\begin{spellcard}
\newcommand{\urlenglish}{https://example.com/spell}
\newcommand{\urlsecondary}{https://example.de/spell}
\spellcardname{Fireball}
\end{spellcard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        analysis = FileScanner.analyze_existing_card(file_path)

        assert "file_size" in analysis
        assert "modification_time" in analysis
        assert analysis["file_size"] > 0
        assert analysis["modification_time"] > 0
        assert analysis["primary_url"] == "https://example.com/spell"
        assert analysis["secondary_url"] == "https://example.de/spell"

    def test_analyze_existing_card_with_secondary_language(self, tmp_path):
        """Test analyze_existing_card detects secondary language."""
        content = r"""
\begin{spellcard}
\newcommand{\urlenglish}{https://example.com/spell}
\newcommand{\urlsecondary}{https://example.de/spell}
\href{https://example.de/spell}{German Link}
\end{spellcard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        analysis = FileScanner.analyze_existing_card(file_path)

        assert analysis["has_secondary_language"] is True
        assert "example.de" in analysis["secondary_url"]

    def test_analyze_existing_card_without_secondary_language(self, tmp_path):
        """Test analyze_existing_card when no secondary language."""
        content = r"""
\begin{spellcard}
\newcommand{\urlenglish}{https://example.com/spell}
\spellcardname{Fireball}
\end{spellcard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        analysis = FileScanner.analyze_existing_card(file_path)

        assert analysis["has_secondary_language"] is False
        assert analysis["secondary_url"] == ""

    def test_analyze_existing_card_extracts_qr_codes(self, tmp_path):
        """Test analyze_existing_card extracts QR codes."""
        content = r"""
\begin{spellcard}
\newcommand{\urlenglish}{https://example.com/spell}
\qrcode{https://example.com/spell}
\qrcode{https://example.de/spell}
\end{spellcard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        analysis = FileScanner.analyze_existing_card(file_path)

        assert len(analysis["qr_codes"]) == 2
        assert "https://example.com/spell" in analysis["qr_codes"]
        assert "https://example.de/spell" in analysis["qr_codes"]

    def test_analyze_existing_card_fallback_to_href(self, tmp_path):
        """Test analyze_existing_card falls back to href for URLs."""
        content = r"""
\begin{spellcard}
\href{https://primary.com/spell}{Primary}
\href{https://secondary.de/spell}{Secondary}
\end{spellcard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        analysis = FileScanner.analyze_existing_card(file_path)

        # Should fall back to href URLs
        assert "primary.com" in analysis["primary_url"]
        assert "secondary.de" in analysis["secondary_url"]

    def test_analyze_existing_card_content_preview(self, tmp_path):
        """Test analyze_existing_card includes content preview."""
        content = "A" * 300  # Content longer than 200 chars
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        analysis = FileScanner.analyze_existing_card(file_path)

        assert "content_preview" in analysis
        assert len(analysis["content_preview"]) == 203  # 200 + "..."
        assert analysis["content_preview"].endswith("...")

    def test_analyze_existing_card_short_content_no_ellipsis(self, tmp_path):
        """Test analyze_existing_card without ellipsis for short content."""
        content = "Short content"
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        analysis = FileScanner.analyze_existing_card(file_path)

        assert analysis["content_preview"] == content
        assert not analysis["content_preview"].endswith("...")

    def test_analyze_existing_card_handles_unicode_error(self, tmp_path):
        """Test analyze_existing_card handles file read errors gracefully."""
        file_path = tmp_path / "test.tex"
        # Write binary content that will cause UnicodeDecodeError
        file_path.write_bytes(b"\x80\x81\x82\x83")

        analysis = FileScanner.analyze_existing_card(file_path)

        # Should return error dict with error key
        assert "error" in analysis
        assert analysis["file_size"] == 0
        assert analysis["modification_time"] == 0

    def test_analyze_existing_card_detects_german_patterns(self, tmp_path):
        """Test analyze_existing_card detects various German patterns."""
        patterns_to_test = [
            (r"\href{https://example.de/spell}{Link}", True),
            (r"\qrcode{https://example.de/spell}", True),
            (r"% German spell description", True),
            (r"% Deutsch spell description", True),
            (r"% English only content", False),
        ]

        for content, should_detect_german in patterns_to_test:
            file_path = tmp_path / f"test_{should_detect_german}.tex"
            file_path.write_text(content)

            analysis = FileScanner.analyze_existing_card(file_path)

            assert analysis["has_secondary_language"] == should_detect_german


@pytest.mark.unit
class TestFileScannerConflictsSummary:
    """Test get_conflicts_summary functionality."""

    def test_get_conflicts_summary_empty(self):
        """Test get_conflicts_summary with no conflicts."""
        existing_cards: dict[str, Any] = {}
        summary = FileScanner.get_conflicts_summary(existing_cards)

        assert summary["total_conflicts"] == 0
        assert summary["has_secondary_language"] == 0
        assert summary["total_size"] == 0
        assert summary["newest_modification"] == 0
        assert summary["oldest_modification"] == 0

    def test_get_conflicts_summary_single_file(self, tmp_path):
        """Test get_conflicts_summary with one conflict."""
        file_path = tmp_path / "test.tex"
        file_path.write_text("% Test content")

        existing_cards = {"Fireball": file_path}
        summary = FileScanner.get_conflicts_summary(existing_cards)

        assert summary["total_conflicts"] == 1
        assert summary["total_size"] > 0
        assert summary["newest_modification"] > 0
        assert "analyses" in summary
        assert "Fireball" in summary["analyses"]

    def test_get_conflicts_summary_multiple_files(self, tmp_path):
        """Test get_conflicts_summary with multiple conflicts."""
        # Create multiple files
        file1 = tmp_path / "test1.tex"
        file1.write_text("% First spell" * 10)

        file2 = tmp_path / "test2.tex"
        file2.write_text(
            r"\href{https://example.de/spell}{German}" + "% Second spell" * 10
        )

        existing_cards = {"Fireball": file1, "Magic Missile": file2}
        summary = FileScanner.get_conflicts_summary(existing_cards)

        assert summary["total_conflicts"] == 2
        assert summary["has_secondary_language"] >= 1  # file2 has German
        assert summary["total_size"] > 0
        assert len(summary["analyses"]) == 2

    def test_get_conflicts_summary_modification_times(self, tmp_path):
        """Test get_conflicts_summary tracks modification times correctly."""
        # Create files with different modification times
        import time

        file1 = tmp_path / "test1.tex"
        file1.write_text("% First")
        time.sleep(0.01)  # Ensure different timestamps

        file2 = tmp_path / "test2.tex"
        file2.write_text("% Second")

        existing_cards = {"Spell1": file1, "Spell2": file2}
        summary = FileScanner.get_conflicts_summary(existing_cards)

        assert summary["newest_modification"] > 0
        assert summary["oldest_modification"] > 0
        assert summary["newest_modification"] >= summary["oldest_modification"]

    def test_get_conflicts_summary_calculates_totals(self, tmp_path):
        """Test get_conflicts_summary calculates summary statistics."""
        # Create files with known sizes
        file1 = tmp_path / "test1.tex"
        file1.write_text("A" * 100)

        file2 = tmp_path / "test2.tex"
        file2.write_text("B" * 200)

        existing_cards = {"Spell1": file1, "Spell2": file2}
        summary = FileScanner.get_conflicts_summary(existing_cards)

        assert summary["total_size"] == 300
        assert summary["total_conflicts"] == 2
