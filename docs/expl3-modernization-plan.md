# expl3 Modernization Plan for LaTeX Spell Cards

**Date**: October 25, 2025  
**Last Updated**: October 29, 2025  
**Status**: Phase 5 In Progress (Table Rendering Issue)  
**Priority**: Modern features over backwards compatibility

## Executive Summary

Migration of spell card LaTeX project to expl3 (LaTeX3) programming layer. Phases 1-4 complete. Phase 5 (integration) mostly complete but blocked on table rendering issue affecting some spells.

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

### In Progress 🚧

**Phase 5: Table Rendering** (BLOCKED - Critical Issue)
- **Problem**: Side-by-side tabularx tables render vertically stacked for some spells
- **Current approach**: LaTeX2e compatibility layer (ExplSyntaxOff/On switching)
- **Status**: Works for Teleport, fails for Mage's Magnificent Mansion
- **Width ratio 0.51**: Not a universal solution
- **Visual quality**: ✅ Horizontal rules (booktabs) now working
- **Next step**: Investigate spell-specific factors (content length, row count, etc.)

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

### Table Rendering (Phase 5 - In Progress)
**Current Implementation**:
```latex
\ExplSyntaxOff
\def\firsttablewidth{#1}%  % #1 = width ratio (default 0.51)
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

**Issue**: Width ratio 0.51 works for some spells but not others (spell-specific problem)

## Next Session Priority Tasks

1. **FIX Phase 5: Table Rendering** (HIGHEST PRIORITY - BLOCKING)
   - Investigate why 0.51 ratio works for Teleport but not Mage's Magnificent Mansion
   - Compare spell properties between working/failing cases
   - Identify spell-specific factors affecting table layout (content length, components, etc.)
   - Find universal solution that works for all spells
   - Test with multiple spell examples before claiming fix
   
2. **Full Feature Parity** (HIGH PRIORITY - BLOCKING)
   - **Missing feature**: `\spellmarkerchart` command not implemented in expl3 package
   - **Test setup**: 
     * Enable all spells in generic deck in both spellcards.tex and spellcards-legacy.tex
     * Disable other decks (combat, utility, teleport)
     * Disable cardify layout
     * Enable `\spellmarkerchart` in both versions
   - **Goal**: Identical marker chart drawing between expl3 and legacy PDFs
   - **Status**: Needs implementation
   
3. **Python Test Suite** (HIGH PRIORITY)
   - Run: `cd spell_card_generator && pytest --cov`
   - Verify: 350 tests pass, 10.00/10 pylint, ~59% coverage maintained
   
4. **URL Preservation Bug** (MEDIUM PRIORITY)
   - Issue: Re-generating spells may lose secondary URLs
   - Check: `utils/file_scanner.py` URL extraction logic
   
5. **Phase 6: Documentation** (after Phase 5 complete)
6. **Phase 7: Refactoring** (future session)

## Recent Work Sessions

### October 29, 2025 - Table Rendering Investigation ⚠️

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

**Width Ratio Problem** ⚠️
- **Issue**: Tables sometimes render vertically stacked instead of horizontally
- **Teleport**: ✅ Works with ratio 0.51 (1 page)
- **Mage's Magnificent Mansion**: ✗ Fails with ratio 0.51 (2 pages)
- **Conclusion**: Width ratio 0.51 is NOT a universal solution
- **Next**: Investigate spell-specific factors

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
