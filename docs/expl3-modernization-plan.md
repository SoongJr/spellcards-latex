# expl3 Modernization Plan for LaTeX Spell Cards

**Date**: October 25, 2025  
**Last Updated**: October 29, 2025  
**Status**: Phase 5 Complete ✅ - Ready for Feature Parity & Testing  
**Priority**: Modern features over backwards compatibility

## Executive Summary

Migration of spell card LaTeX project to expl3 (LaTeX3) programming layer. Phases 1-5 complete with full table rendering parity. Ready to implement remaining features (`\spellmarkerchart`) and run comprehensive testing.

## Architecture

### Core Components
- **spellcard-expl3.sty** (~1450 lines) - Modern expl3 package (replaces spellcard-templates.tex)
- **cardify.tex** (~180 lines) - Page layout (unchanged, integrated successfully)
- **spellcards.tex** (~30 lines) - Document entry point
- **Generated spell files** - Property-based format using `\spellprop{key}{value}`

### Modern Implementation (expl3)
- Property lists for spell data (`\prop`)
- Boolean/integer/token list variables (`\bool`, `\int`, `\tl`)
- Native FP calculations (no pgfmath dependency)
- Conditional logic with expl3 (`\bool_if:`, `\str_if_eq:`)
- Sequence-based deck tracking
- Message system for errors/warnings

## Migration Phases

### Completed Phases ✅

**Phase 1: Foundation** - expl3 package structure, type system, property lists, message system  
**Phase 2: Core Logic** - Deck management, positioning calculations, conditional logic  
**Phase 3.1: Deck Tracking** - Sequence-based spell lists, query functions for index generation  
**Phase 4: Layout** - QR code system, marker/label positioning, dimension calculations  
**Phase 5: Table Rendering** - Side-by-side tabularx tables with proper paragraph handling

### Planned 📋

**Phase 3.2: Key-Value Interface** (deferred until Phase 5 complete)
**Phase 6: Documentation** - Document solutions, create user guide  
**Phase 7: Refactoring** - Split 1450-line package into modules, code audit

## Key Implementation Details

### Deck Tracking (Phase 3.1)
```latex
% Query Functions
\spellcard_get_deck_spell_count:n { deck_number }
\spellcard_if_deck_exists:nTF { deck_number } { true } { false }
\spellcard_map_deck_spells:nn { deck_number } { code }
```

### QR Code System (Phase 4.3)
- Maximum 2 QR codes per page (validated)
- Page parity-aware positioning (odd/even pages)
- First QR: 2cm offset, opposite page number
- Second QR: 4cm offset, same side as page number

### Table Rendering (Phase 5 - Complete ✅)
**Implementation**:
```latex
% Spell card environment adds \par after title to properly end paragraph
\section*{\Huge #2 \hfill \MakeUppercase{#1}~#3}
\spellcard_draw_deck_label:nn {...}
\spellcard_draw_spell_marker:n {#3}
\par  % Critical: ensures tables start on new line

% Table rendering with LaTeX2e compatibility
\ExplSyntaxOff
\def\firsttablewidth{#1}%  % #1 = width ratio (default 0.5)
\def\secondtablewidth{\fpeval{1-#1}}%

\begin{tabularx}{\firsttablewidth\textwidth}[b]{...}
  % Left table: Casting Time, Saving Throw, Spell Resist, Attack Roll
\end{tabularx}%
\hfill%
\begin{tabularx}{\secondtablewidth\textwidth-\tabcolsep}[b]{...}
  % Right table: Duration, Range, Comp., School
\end{tabularx}%
\ExplSyntaxOn
```

**Solution**: Added `\par` after title rendering to properly end paragraph before tables. Without this, tables were treated as inline content and positioned incorrectly (left table on right, right table wrapping to next line).

## Next Session Priority Tasks

1. **Implement Missing Feature: `\spellmarkerchart`** (HIGHEST PRIORITY - BLOCKING FEATURE PARITY)
   - Currently missing from expl3 package
   - **Test setup**: 
     * Enable all spells in generic deck in both spellcards.tex and spellcards-legacy.tex
     * Disable other decks (combat, utility, teleport)
     * Disable cardify layout
     * Enable `\spellmarkerchart` in both versions
   - **Goal**: Identical marker chart drawing between expl3 and legacy PDFs
   - **Status**: Needs implementation
   
2. **Python Test Suite** (HIGH PRIORITY)
   - Run: `cd spell_card_generator && pytest --cov`
   - Verify: 350 tests pass, 10.00/10 pylint, ~59% coverage maintained
   
3. **URL Preservation Bug** (MEDIUM PRIORITY)
   - Issue: Re-generating spells may lose secondary URLs
   - Check: `utils/file_scanner.py` URL extraction logic

## Recent Work Sessions

### October 29, 2025 - Phase 5 Complete: Table Rendering ✅

**Problem Identified**: Side-by-side tables rendering in wrong positions
- Left table (Casting Time) appeared on the right side and higher than expected
- Right table (Duration) wrapped to the left on the next line
- Visual inspection confirmed tables themselves rendered correctly (pixel-perfect match)
- Issue was POSITIONING, not table width calculation

**Root Cause**: Missing paragraph break after `\section*` title
- Tables were being treated as inline content following the title
- Without proper paragraph ending, LaTeX positioned them as if part of the title line

**Solution**: Added `\par` after title rendering in `spellcard` environment
```latex
\section*{\Huge #2 \hfill \MakeUppercase{#1}~#3}
\spellcard_draw_deck_label:nn {...}
\spellcard_draw_spell_marker:n {#3}
\par  % Critical fix: end paragraph before tables
```

**Verification**:
- ✅ pdftotext output matches legacy formatting exactly
- ✅ Exit code 0 (no errors, no warnings)
- ✅ Visual comparison: pixel-perfect table positioning
- ✅ All 22-page test document compiles successfully
- ✅ Tables now side-by-side: "Casting Time" left, "Duration" right

**Phase 5 Status**: COMPLETE - Full table rendering parity achieved

### October 29, 2025 - Table Rendering Investigation (Earlier Session)

**Table Implementation - LaTeX2e Compatibility Layer** ✅
- Successfully implemented side-by-side tabularx tables using ExplSyntaxOff/On switching
- Property values exported to LaTeX2e macros for use in tables
- Tables render with proper booktabs formatting (toprule/midrule/bottomrule)
- Created `\renderattribute` LaTeX2e helper for conditional row rendering

**Benefits**:
- ✅ Visual improvement: Horizontal rules (booktabs style)
- ✅ Code clarity: Clean separation between expl3 and LaTeX2e syntax
- ✅ Maintainability: Straightforward table structure
- ✅ No sacrifices: All features preserved, visual quality improved

### October 28, 2025 - Python Generator Integration ✅
- Updated `generators/latex_generator.py` to output expl3 format
- Changed from `\newcommand` to `\spellprop{key}{value}` format
- Successfully generated 15 spells via CLI
- Full workflow functional: TSV → Python → expl3 .tex → PDF
- Exit code 0, no errors or warnings

### October 27, 2025 - Cardify Integration ✅
**Problems Fixed**:
1. Cards rendering on same page instead of odd/even pages
   - **Fix**: Changed `\clearpage` to `\clearcard` (line 1338)
2. `\includespell` state persistence bug
   - **Fix**: Reset `\l_spellcard_include_print_bool` before processing keys (line 1153)
3. `\includespell[noprint]` not suppressing output
   - **Fix**: Changed environment to use `+b` argument type (line 1320)

**Results**: test-spell.pdf and test-legacy.pdf produce identical layout

## Future Enhancements

Once Phase 5 complete and table rendering resolved:

1. **Index Card Generation** (enabled by Phase 3.1 deck tracking)
   - Serves as a table of contents for each deck
   - Spell counts by level
   - No sorting, same order they have been entered into the deck in

2. **Additional Features**
   - Spell filtering for deck building
   - Validation with better error messages
