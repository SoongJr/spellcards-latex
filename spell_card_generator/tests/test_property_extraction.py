"""Tests for property extraction from existing spell cards."""

# pylint: disable=duplicate-code

from spell_card_generator.utils.file_scanner import FileScanner


class TestPropertyExtractionLegacy:
    """Test extraction of \\newcommand properties from legacy format .tex files."""

    def test_extract_simple_properties(self, tmp_path):
        """Test extraction of simple properties without comments."""
        card_file = tmp_path / "test.tex"
        content = r"""
\begin{spellcard}{sor}{Test}{1}
  \newcommand{\name}{Test Spell}
  \newcommand{\school}{evocation}
  \newcommand{\range}{100 ft.}
  \spellcardinfo{}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties == {
            "name": ("Test Spell", None),
            "school": ("evocation", None),
            "range": ("100 ft.", None),
        }

    def test_extract_properties_with_original_comments(self, tmp_path):
        """Test extraction of properties with % original: comments."""
        card_file = tmp_path / "test.tex"
        content = r"""
\begin{spellcard}{sor}{Test}{1}
  \newcommand{\name}{Test Spell}
  \newcommand{\range}{medium}% original: {100 ft. + 10 ft./level}
  \newcommand{\targets}{NULL}% original: {you or creature touched}
  \spellcardinfo{}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties == {
            "name": ("Test Spell", None),
            "range": ("medium", "100 ft. + 10 ft./level"),
            "targets": ("NULL", "you or creature touched"),
        }

    def test_extract_properties_mixed(self, tmp_path):
        """Test extraction with mix of commented and uncommented properties."""
        card_file = tmp_path / "test.tex"
        content = r"""
\begin{spellcard}{sor}{Test}{1}
  \newcommand{\name}{Test Spell}
  \newcommand{\school}{evocation}
  \newcommand{\range}{medium}% original: {100 ft.}
  \newcommand{\targets}{one creature}
  \newcommand{\duration}{instantaneous}% original: {1 round}
  \spellcardinfo{}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert len(properties) == 5
        assert properties["name"] == ("Test Spell", None)
        assert properties["school"] == ("evocation", None)
        assert properties["range"] == ("medium", "100 ft.")
        assert properties["targets"] == ("one creature", None)
        assert properties["duration"] == ("instantaneous", "1 round")

    def test_extract_properties_with_special_characters(self, tmp_path):
        """Test extraction of properties with special LaTeX characters."""
        card_file = tmp_path / "test.tex"
        content = r"""
\newcommand{\range}{100 ft.\ + 10 ft./level}
\newcommand{\targets}{you or creature touched}
\newcommand{\duration}{1 round/level (D)}
\newcommand{\components}{V, S, M (bat fur)}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties["range"] == (r"100 ft.\ + 10 ft./level", None)
        assert properties["targets"] == ("you or creature touched", None)
        assert properties["duration"] == ("1 round/level (D)", None)
        assert properties["components"] == ("V, S, M (bat fur)", None)

    def test_extract_null_values(self, tmp_path):
        """Test extraction of NULL values."""
        card_file = tmp_path / "test.tex"
        content = r"""
\newcommand{\area}{NULL}
\newcommand{\effect}{NULL}
\newcommand{\targets}{NULL}% original: {one creature}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties["area"] == ("NULL", None)
        assert properties["effect"] == ("NULL", None)
        assert properties["targets"] == ("NULL", "one creature")

    def test_extract_numeric_properties(self, tmp_path):
        """Test extraction of numeric/boolean properties."""
        card_file = tmp_path / "test.tex"
        content = r"""
\newcommand{\spelllevel}{3}
\newcommand{\verbal}{1}
\newcommand{\somatic}{1}
\newcommand{\material}{0}
\newcommand{\dismissible}{1}
\newcommand{\shapeable}{0}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties["spelllevel"] == ("3", None)
        assert properties["verbal"] == ("1", None)
        assert properties["somatic"] == ("1", None)
        assert properties["material"] == ("0", None)
        assert properties["dismissible"] == ("1", None)
        assert properties["shapeable"] == ("0", None)

    def test_extract_empty_file(self, tmp_path):
        """Test extraction from empty file."""
        card_file = tmp_path / "empty.tex"
        card_file.write_text("", encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert not properties

    def test_extract_nonexistent_file(self, tmp_path):
        """Test extraction from nonexistent file."""
        nonexistent = tmp_path / "nonexistent.tex"

        properties = FileScanner.extract_properties(nonexistent)

        assert not properties

    def test_extract_ignores_non_newcommand_lines(self, tmp_path):
        """Test that non-\\newcommand lines are ignored."""
        card_file = tmp_path / "test.tex"
        content = r"""
% This is a comment
\begin{spellcard}{sor}{Test}{1}
  % Another comment
  \newcommand{\name}{Test Spell}
  \spellcardinfo{}
  % More comments
  \spellcardqr{\urlenglish}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties == {"name": ("Test Spell", None)}

    def test_extract_real_spell_card(self, tmp_path):
        """Test extraction from a realistic spell card."""
        card_file = tmp_path / "Magic Missile.tex"
        content = r"""%%%
%%% file content generated by spell_card_generator.py
%%%
\begin{spellcard}{sor}{Magic Missile}{1}
  \newcommand{\name}{Magic Missile}
  \newcommand{\school}{evocation}
  \newcommand{\descriptor}{force}
  \newcommand{\spelllevel}{1}
  \newcommand{\range}{medium (100 ft. + 10 ft./level)}
  \newcommand{\targets}{up to five creatures}
  \newcommand{\duration}{instantaneous}
  \newcommand{\savingthrow}{\textbf{none}}
  \newcommand{\spellresistance}{yes}
  \spellcardinfo{}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert len(properties) == 9
        assert properties["name"] == ("Magic Missile", None)
        assert properties["school"] == ("evocation", None)
        assert properties["descriptor"] == ("force", None)
        assert properties["range"] == ("medium (100 ft. + 10 ft./level)", None)
        assert properties["savingthrow"] == (r"\textbf{none}", None)

    def test_extract_modified_spell_card(self, tmp_path):
        """Test extraction from modified spell card with original comments."""
        card_file = tmp_path / "Invisibility, Greater.tex"
        content = r"""%%%
%%% file content generated by spell_card_generator.py
%%%
\begin{spellcard}{sor}{Invisibility, Greater}{4}
  \newcommand{\name}{Invisibility, Greater}
  \newcommand{\school}{illusion}
  \newcommand{\range}{personal or touch}
  \newcommand{\targets}{NULL}% original: {you or creature touched}
  \newcommand{\duration}{1 round/level}
  \newcommand{\savingthrow}{Will negates (harmless)}
  \spellcardinfo[0.55]{}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties["name"] == ("Invisibility, Greater", None)
        assert properties["school"] == ("illusion", None)
        assert properties["range"] == ("personal or touch", None)
        assert properties["targets"] == ("NULL", "you or creature touched")
        assert properties["duration"] == ("1 round/level", None)
        assert properties["savingthrow"] == ("Will negates (harmless)", None)


class TestPropertyExtractionLegacyEdgeCases:
    """Test edge cases in legacy property extraction."""

    def test_extract_property_with_spaces_in_comment(self, tmp_path):
        """Test extraction with extra spaces in original comment."""
        card_file = tmp_path / "test.tex"
        content = r"""
\newcommand{\range}{medium}%   original:   {100 ft.}
\newcommand{\targets}{NULL}%original:{one creature}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        # Should handle varying whitespace
        assert properties["range"] == ("medium", "100 ft.")
        assert properties["targets"] == ("NULL", "one creature")

    def test_extract_property_with_comma_in_value(self, tmp_path):
        """Test extraction of values containing commas."""
        card_file = tmp_path / "test.tex"
        content = r"""
\newcommand{\name}{Invisibility, Greater}
\newcommand{\components}{V, S, M}
\newcommand{\targets}{you, or one creature}% original: {you or one creature}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties["name"] == ("Invisibility, Greater", None)
        assert properties["components"] == ("V, S, M", None)
        assert properties["targets"] == ("you, or one creature", "you or one creature")


class TestPropertyExtractionExpl3:
    """Test extraction of \\spellprop properties from expl3 format .tex files."""

    def test_extract_simple_properties_expl3(self, tmp_path):
        """Test extraction of simple expl3 properties without comments."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.0-expl3
%%%
\begin{spellcard}{sor}{Test}{1}
  \spellprop{name}{Test Spell}
  \spellprop{school}{evocation}
  \spellprop{range}{100 ft.}
  \spellcardinfo{}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties == {
            "name": ("Test Spell", None),
            "school": ("evocation", None),
            "range": ("100 ft.", None),
        }

    def test_extract_properties_with_original_comments_expl3(self, tmp_path):
        """Test extraction of expl3 properties with % original: comments."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.0-expl3
%%%
\begin{spellcard}{sor}{Test}{1}
  \spellprop{name}{Test Spell}
  \spellprop{range}{medium}% original: {100 ft. + 10 ft./level}
  \spellprop{targets}{NULL}% original: {you or creature touched}
  \spellcardinfo{}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties == {
            "name": ("Test Spell", None),
            "range": ("medium", "100 ft. + 10 ft./level"),
            "targets": ("NULL", "you or creature touched"),
        }

    def test_extract_properties_with_special_characters_expl3(self, tmp_path):
        """Test extraction of properties with special LaTeX characters."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.0-expl3
%%%
\spellprop{range}{100 ft.\ + 10 ft./level}
\spellprop{targets}{you or creature touched}
\spellprop{duration}{1 round/level (D)}
\spellprop{components}{V, S, M (bat fur)}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        assert properties["range"] == (r"100 ft.\ + 10 ft./level", None)
        assert properties["targets"] == ("you or creature touched", None)
        assert properties["duration"] == ("1 round/level (D)", None)
        assert properties["components"] == ("V, S, M (bat fur)", None)

    def test_extract_qr_codes_from_expl3(self, tmp_path):
        """Test extraction of QR codes from \\spellcardqr commands in expl3 format."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.0-expl3
%%%
\begin{spellcard}{sor}{Acid Splash}{0}
  \spellprop{name}{Acid Splash}
  \spellprop{school}{conjuration}
  \spellprop{spelllevel}{0}
  \spellcardinfo{}
  \spellcardqr{https://www.d20pfsrd.com/magic/all-spells/a/acid-splash}
  \spellcardqr{http://prd.5footstep.de/Grundregelwerk/Zauber/Säurespritzer}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        # Should extract URLs as urlenglish and urlsecondary
        assert "urlenglish" in properties
        assert properties["urlenglish"] == (
            "https://www.d20pfsrd.com/magic/all-spells/a/acid-splash",
            None,
        )
        assert "urlsecondary" in properties
        assert properties["urlsecondary"] == (
            "http://prd.5footstep.de/Grundregelwerk/Zauber/Säurespritzer",
            None,
        )

    def test_extract_single_qr_code_from_expl3(self, tmp_path):
        """Test extraction of single QR code from expl3 format."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.0-expl3
%%%
\begin{spellcard}{sor}{Test}{1}
  \spellprop{name}{Test Spell}
  \spellcardinfo{}
  \spellcardqr{https://www.d20pfsrd.com/magic/test}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        # Should extract only primary URL
        assert "urlenglish" in properties
        assert properties["urlenglish"] == ("https://www.d20pfsrd.com/magic/test", None)
        assert "urlsecondary" not in properties

    def test_extract_commented_secondary_qr_code(self, tmp_path):
        """Test that commented QR codes are ignored."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.0-expl3
%%%
\begin{spellcard}{sor}{Acid Splash}{0}
  \spellprop{name}{Acid Splash}
  \spellcardinfo{}
  \spellcardqr{https://www.d20pfsrd.com/magic/all-spells/a/acid-splash}
  % \spellcardqr{<secondary-url>}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        # Should extract only primary URL, secondary is commented out
        assert "urlenglish" in properties
        assert properties["urlenglish"] == (
            "https://www.d20pfsrd.com/magic/all-spells/a/acid-splash",
            None,
        )
        # Secondary URL should NOT be extracted because it's commented
        assert "urlsecondary" not in properties

    def test_extract_qr_code_with_non_ascii_characters(self, tmp_path):
        """Test extraction of QR codes with non-ASCII characters (e.g., German umlauts)."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.0-expl3
%%%
\begin{spellcard}{sor}{Acid Splash}{0}
  \spellprop{name}{Acid Splash}
  \spellcardinfo{}
  \spellcardqr{https://www.d20pfsrd.com/magic/all-spells/a/acid-splash}
  \spellcardqr{http://prd.5footstep.de/Grundregelwerk/Zauber/Säurespritzer}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        # Should extract both URLs including the one with German characters
        assert "urlenglish" in properties
        assert properties["urlenglish"] == (
            "https://www.d20pfsrd.com/magic/all-spells/a/acid-splash",
            None,
        )
        assert "urlsecondary" in properties
        assert properties["urlsecondary"] == (
            "http://prd.5footstep.de/Grundregelwerk/Zauber/Säurespritzer",
            None,
        )

    def test_extract_qr_code_with_special_url_characters(self, tmp_path):
        """Test extraction of QR codes with various URL characters."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.0-expl3
%%%
\begin{spellcard}{sor}{Test}{1}
  \spellprop{name}{Test Spell}
  \spellcardinfo{}
  \spellcardqr{https://www.google.com/acid-splash}
  \spellcardqr{https://example.com/spells?level=1&class=wizard}
\end{spellcard}
"""
        card_file.write_text(content, encoding="utf-8")

        properties = FileScanner.extract_properties(card_file)

        # Should extract both URLs with hyphens, query parameters, etc.
        assert "urlenglish" in properties
        assert properties["urlenglish"] == ("https://www.google.com/acid-splash", None)
        assert "urlsecondary" in properties
        assert properties["urlsecondary"] == (
            "https://example.com/spells?level=1&class=wizard",
            None,
        )
