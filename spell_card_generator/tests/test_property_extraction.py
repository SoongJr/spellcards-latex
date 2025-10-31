"""Tests for property extraction from existing spell cards."""

# pylint: disable=duplicate-code

from spell_card_generator.utils.file_scanner import FileScanner


class TestPropertyExtractionExpl3:
    """Test extraction of \\spellprop properties from expl3 format .tex files."""

    def test_extract_simple_properties_expl3(self, tmp_path):
        """Test extraction of simple expl3 properties without comments."""
        card_file = tmp_path / "test.tex"
        content = r"""%%%
%%% SPELL-CARD-VERSION: 2.1
%%%
\begin{SpellCard}{sor}{Test}{1}
  \SpellProp{name}{Test Spell}
  \SpellProp{school}{evocation}
  \SpellProp{range}{100 ft.}
  \SpellCardInfo{}
\end{SpellCard}
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
%%% SPELL-CARD-VERSION: 2.1
%%%
\begin{SpellCard}{sor}{Test}{1}
  \SpellProp{name}{Test Spell}
  \SpellProp{range}{medium}% original: {100 ft. + 10 ft./level}
  \SpellProp{targets}{NULL}% original: {you or creature touched}
  \SpellCardInfo{}
\end{SpellCard}
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
%%% SPELL-CARD-VERSION: 2.1
%%%
\SpellProp{range}{100 ft.\ + 10 ft./level}
\SpellProp{targets}{you or creature touched}
\SpellProp{duration}{1 round/level (D)}
\SpellProp{components}{V, S, M (bat fur)}
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
%%% SPELL-CARD-VERSION: 2.1
%%%
\begin{SpellCard}{sor}{Acid Splash}{0}
  \SpellProp{name}{Acid Splash}
  \SpellProp{school}{conjuration}
  \SpellProp{spelllevel}{0}
  \SpellCardInfo{}
  \SpellCardQR{https://www.d20pfsrd.com/magic/all-spells/a/acid-splash}
  \SpellCardQR{http://prd.5footstep.de/Grundregelwerk/Zauber/Säurespritzer}
\end{SpellCard}
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
%%% SPELL-CARD-VERSION: 2.1
%%%
\begin{SpellCard}{sor}{Test}{1}
  \SpellProp{name}{Test Spell}
  \SpellCardInfo{}
  \SpellCardQR{https://www.d20pfsrd.com/magic/test}
\end{SpellCard}
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
%%% SPELL-CARD-VERSION: 2.1
%%%
\begin{SpellCard}{sor}{Acid Splash}{0}
  \SpellProp{name}{Acid Splash}
  \SpellCardInfo{}
  \SpellCardQR{https://www.d20pfsrd.com/magic/all-spells/a/acid-splash}
  % \SpellCardQR{<secondary-url>}
\end{SpellCard}
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
%%% SPELL-CARD-VERSION: 2.1
%%%
\begin{SpellCard}{sor}{Acid Splash}{0}
  \SpellProp{name}{Acid Splash}
  \SpellCardInfo{}
  \SpellCardQR{https://www.d20pfsrd.com/magic/all-spells/a/acid-splash}
  \SpellCardQR{http://prd.5footstep.de/Grundregelwerk/Zauber/Säurespritzer}
\end{SpellCard}
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
%%% SPELL-CARD-VERSION: 2.1
%%%
\begin{SpellCard}{sor}{Test}{1}
  \SpellProp{name}{Test Spell}
  \SpellCardInfo{}
  \SpellCardQR{https://www.google.com/acid-splash}
  \SpellCardQR{https://example.com/spells?level=1&class=wizard}
\end{SpellCard}
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
