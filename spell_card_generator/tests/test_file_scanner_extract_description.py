"""Tests for FileScanner.extract_description method.

These tests verify that the method correctly handles indentation:
- Base indentation (at the level of "% SPELL DESCRIPTION BEGIN") should be stripped
- Additional indentation beyond the base level should be preserved
- Empty descriptions should be handled gracefully
"""

# pylint: disable=line-too-long,duplicate-code

import pytest

from spell_card_generator.utils.file_scanner import FileScanner


@pytest.mark.unit
class TestExtractDescription:
    """Test FileScanner.extract_description method."""

    def test_extract_description_empty(self, tmp_path):
        """Test extract_description with no description (empty between markers)."""
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \newcommand{\name}{Test Spell}
  \ifprintcard
    \SpellCardInfo{}
    %
    % SPELL DESCRIPTION BEGIN
    % SPELL DESCRIPTION END
    %
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        assert description == ""

    def test_extract_description_single_line_no_extra_indent(self, tmp_path):
        """Test extract_description with single line at base indentation."""
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \newcommand{\name}{Test Spell}
  \ifprintcard
    \SpellCardInfo{}
    %
    % SPELL DESCRIPTION BEGIN
    This is a single line description.
    % SPELL DESCRIPTION END
    %
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        # Should have no leading indentation
        assert description == "This is a single line description."
        assert not description.startswith(" ")

    def test_extract_description_multiple_lines_same_indent(self, tmp_path):
        """Test extract_description with multiple lines at base indentation.

        This test demonstrates the current bug: all lines after the first
        should have their base indentation stripped, but currently they don't.
        """
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \newcommand{\name}{Test Spell}
  \ifprintcard
    \SpellCardInfo{}
    %
    % SPELL DESCRIPTION BEGIN
    You fire a small orb of acid at the target.
    You must succeed on a ranged touch attack to hit your target.
    The orb deals 1d3 points of acid damage.
    This acid disappears after 1 round.
    % SPELL DESCRIPTION END
    %
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        # Expected: All lines should have no leading indentation
        expected = """You fire a small orb of acid at the target.
You must succeed on a ranged touch attack to hit your target.
The orb deals 1d3 points of acid damage.
This acid disappears after 1 round."""

        assert description == expected
        # Verify no line starts with spaces
        for line in description.split("\n"):
            assert not line.startswith(
                " "
            ), f"Line '{line}' should not start with spaces"

    def test_extract_description_varying_indentation(self, tmp_path):
        """Test extract_description with lines having additional indentation.

        Some lines have extra indentation beyond the base level.
        The base indentation should be stripped, but the extra should be preserved.
        """
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \newcommand{\name}{Test Spell}
  \ifprintcard
    \SpellCardInfo{}
    %
    % SPELL DESCRIPTION BEGIN
    You can observe magical auras.
    \ifprintlongcards
      An attended object may attempt a Will save to resist this effect if its
      holder so desires. If the save succeeds, you learn nothing about the
      object except what you can discern by looking at it.
    \fi
    This concludes the spell description.
    % SPELL DESCRIPTION END
    %
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        # Expected: base indentation stripped, extra preserved
        expected = r"""You can observe magical auras.
\ifprintlongcards
  An attended object may attempt a Will save to resist this effect if its
  holder so desires. If the save succeeds, you learn nothing about the
  object except what you can discern by looking at it.
\fi
This concludes the spell description."""

        assert description == expected

        lines = description.split("\n")
        # Lines with \if commands should have 2 extra spaces
        assert lines[2].startswith("  An attended object")
        assert lines[3].startswith("  holder so desires")
        assert lines[4].startswith("  object except what")
        # Verify non-indented lines don't start with spaces
        assert not lines[0].startswith(" ")
        assert not lines[1].startswith(" ")
        assert not lines[5].startswith(" ")
        assert not lines[6].startswith(" ")

    def test_extract_description_with_blank_lines(self, tmp_path):
        """Test extract_description preserves blank lines within description."""
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \ifprintcard
    %
    % SPELL DESCRIPTION BEGIN
    First paragraph.

    Second paragraph after blank line.

    Third paragraph.
    % SPELL DESCRIPTION END
    %
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        expected = """First paragraph.

Second paragraph after blank line.

Third paragraph."""

        assert description == expected
        # Verify there are blank lines
        assert "\n\n" in description
        # Verify blank lines are truly empty (no whitespace) - important for LaTeX
        lines = description.split("\n")
        assert lines[1] == "", f"Blank line should be empty, got: {repr(lines[1])}"
        assert lines[3] == "", f"Blank line should be empty, got: {repr(lines[3])}"
        assert len(lines[1]) == 0, "Blank line should have length 0"
        assert len(lines[3]) == 0, "Blank line should have length 0"

    def test_extract_description_different_base_indentation_levels(self, tmp_path):
        """Test extract_description with different base indentation levels.

        The base indentation is determined by the "% SPELL DESCRIPTION BEGIN" line.
        This test uses 8 spaces as the base indentation.
        """
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \ifprintcard
        %
        % SPELL DESCRIPTION BEGIN
        Line with 8 space base indentation.
        Another line at base level.
          Line with 2 extra spaces (10 total).
        Back to base.
        % SPELL DESCRIPTION END
        %
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        expected = """Line with 8 space base indentation.
Another line at base level.
  Line with 2 extra spaces (10 total).
Back to base."""

        assert description == expected
        lines = description.split("\n")
        assert not lines[0].startswith(" ")
        assert not lines[1].startswith(" ")
        assert lines[2].startswith("  Line with 2 extra")
        assert not lines[3].startswith(" ")

    def test_extract_description_two_space_base_indentation(self, tmp_path):
        """Test extract_description with 2-space base indentation."""
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  %
  % SPELL DESCRIPTION BEGIN
  First line at 2-space base.
  Second line at 2-space base.
    Line with 2 extra spaces (4 total).
  Back to base.
  % SPELL DESCRIPTION END
  %
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        expected = """First line at 2-space base.
Second line at 2-space base.
  Line with 2 extra spaces (4 total).
Back to base."""

        assert description == expected

    def test_extract_description_no_indentation(self, tmp_path):
        """Test extract_description when markers have no indentation."""
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
% SPELL DESCRIPTION BEGIN
No indentation at all.
Second line also no indentation.
  But this line has 2 spaces.
% SPELL DESCRIPTION END
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        expected = """No indentation at all.
Second line also no indentation.
  But this line has 2 spaces."""

        assert description == expected

    def test_extract_description_with_latex_commands(self, tmp_path):
        """Test extract_description preserves LaTeX commands and formatting."""
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \ifprintcard
    %
    % SPELL DESCRIPTION BEGIN
    An attended object may attempt a Will save.
    If the save succeeds, you learn nothing about the
    object except what you can discern by looking at it. An object that
    makes its save cannot be affected by any other \emph{analyze dweomer}
    spells for 24 hours.

    \emph{Analyze dweomer} does not function when used on an artifact.
    % SPELL DESCRIPTION END
    %
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        # LaTeX commands should be preserved
        assert r"\emph{analyze dweomer}" in description
        assert r"\emph{Analyze dweomer}" in description
        # But base indentation should be stripped
        assert not description.startswith(" ")
        for line in description.split("\n"):
            if line.strip():  # Non-empty lines
                assert not line.startswith(
                    " "
                ), f"Line should not start with space: '{line}'"

    def test_extract_description_nonexistent_file(self, tmp_path):
        """Test extract_description with nonexistent file."""
        file_path = tmp_path / "nonexistent.tex"

        description = FileScanner.extract_description(file_path)

        assert description == ""

    def test_extract_description_no_markers(self, tmp_path):
        """Test extract_description when file has no description markers."""
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \newcommand{\name}{Test Spell}
  \ifprintcard
    \SpellCardInfo{}
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        assert description == ""

    def test_extract_description_acid_splash_real_example(self, tmp_path):
        """Test extract_description with real Acid Splash spell card content."""
        # This is the actual content from Acid Splash.tex
        content = r"""%%%
%%% file content generated by spell_card_generator.py,
%%% meant to be fine-tuned manually (especially the description).
%%%
%
% open a new spellcards environment
\begin{SpellCard}{sor}{Acid Splash}{0}
  % make the data from TSV accessible for to the LaTeX part:
  \newcommand{\name}{Acid Splash}
  \newcommand{\school}{conjuration}
  \ifprintcard% Only print the card if the printcard flag is true
    % print the tabular information at the top of the card:
    \SpellCardInfo{}
    % draw a QR Code pointing at online resources for this spell on the front face:
    \SpellCardQR{\urlenglish}
    \SpellCardQR{\urlsecondary}
    %
    % SPELL DESCRIPTION BEGIN
    You fire a small orb of acid at the target.
    You must succeed on a ranged touch attack to hit your target.
    The orb deals 1d3 points of acid damage.
    This acid disappears after 1 round.
    % SPELL DESCRIPTION END
    %
  \fi%printcard
\end{SpellCard}
"""
        file_path = tmp_path / "Acid Splash.tex"
        file_path.write_text(content)

        description = FileScanner.extract_description(file_path)

        # Expected: base 4-space indentation stripped, extra 2-space indentation preserved
        expected = """You fire a small orb of acid at the target.
You must succeed on a ranged touch attack to hit your target.
The orb deals 1d3 points of acid damage.
This acid disappears after 1 round."""

        assert description == expected
        lines = description.split("\n")
        # All lines should have no indentation (same base level in test data)
        assert not lines[0].startswith(" ")
        assert not lines[1].startswith(" ")
        assert not lines[2].startswith(" ")
        assert not lines[3].startswith(" ")

    def test_extract_description_tabs_not_supported(self, tmp_path):
        """Test that tabs are not explicitly handled (spaces-only assumption).

        This test documents that the implementation assumes spaces, not tabs.
        If tabs are present, behavior is undefined/not tested.
        """
        # This test just documents the assumption - we assume spaces only
        # as per the user's instructions
        content = r"""
\begin{SpellCard}{sor}{Test Spell}{0}
  \ifprintcard
    % SPELL DESCRIPTION BEGIN
    Line with spaces only.
    % SPELL DESCRIPTION END
  \fi
\end{SpellCard}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        # This should work fine with spaces
        description = FileScanner.extract_description(file_path)
        assert "Line with spaces only." in description
