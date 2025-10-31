# expl3 Modernization Plan for LaTeX Spell Cards

**Date**: October 25, 2025  
**Last Updated**: October 29, 2025  
**Status**: **FEATURE COMPLETE** ✅ - Full parity with legacy achieved
**Priority**: Modern features over backwards compatibility

## Executive Summary

**🎉 MIGRATION COMPLETE! Full feature parity achieved with legacy version.**

Migration of spell card LaTeX project to expl3 (LaTeX3) programming layer is COMPLETE. All phases (1-6) finished and verified. Python generator fully integrated and producing correct expl3 format. Both legacy and modern versions compile to identical 91-page PDFs with zero errors/warnings.

**Status**: Production-ready for all 25 existing spells (Level 0-7). Ready for final polishing and documentation.

## Architecture

### Current State (Pre-Refactoring)
- **spellcard-expl3.sty** (~1450 lines) - Monolithic modern expl3 package
- **cardify.tex** (~180 lines) - Page layout (unchanged, integrated successfully)
- **spellcards.tex** (~30 lines) - Document entry point
- **Generated spell files** - Property-based format using `\spellprop{key}{value}`

### Target State (Post-Refactoring)
- **spellcards.sty** (~100 lines) - Main package loader (renamed from spellcard-expl3.sty)
- **spellcards/*.sty** (~1200 lines total) - 7 focused modules in subfolder
  - `core.sty` - Foundation (variables, messages, constants)
  - `properties.sty` - Spell data management
  - `deck.sty` - Deck organization and labels
  - `level-markers.sty` - Spell level indicators on right edge
  - `qrcode.sty` - QR code system
  - `info-table.sty` - Spell attribute table rendering
  - `content-layout.sty` - Card structure orchestrator
- **tests/*.tex** - Feature-specific test files (test-core.tex, test-properties.tex, etc.)
- **cardify.tex** (~180 lines) - Page layout (unchanged)
- **spellcards.tex** (~30 lines) - Document entry point (uses `\usepackage{spellcards}`)
- **Generated spell files** - Modern PascalCase format: `\SpellProp{key}{value}`, `\SpellCardQR{url}`

### Post-Cleanup State (After Phase 11)
- ❌ **Legacy files removed**: spellcard-templates-legacy.tex, spellcards-legacy.tex, spells-legacy/
- ❌ **Compatibility layer removed**: spellcard-templates-compat.tex
- ❌ **Legacy Python code removed**: Legacy format parsing in file_scanner.py, legacy tests (~40 tests)
- ✅ **Clean, modern codebase**: Only PascalCase commands, only modern format, ~320 tests

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
**Phase 6: Missing Features** - `\SpellMarkerChart` implementation (spell level reference card)  
**Phase 7: Python Generator** - Updated to output expl3 format, full GUI workflow functional  
**Phase 8: Verification** - PDF comparison confirms identical output (91 pages, 25 spells, zero warnings)  
**Phase 9: Package Refactoring** - Split monolithic package into 7 feature-based modules (completed Oct 30)  
**Phase 10: Command Naming Modernization** - PascalCase public API, version 2.1 (completed Oct 31) ✅  
**Phase 11: Remove ALL Compatibility** - Deleted legacy templates, legacy Python code, legacy tests (completed Oct 31) ✅

### Next Priority: Documentation 📚

**Phase 12: Documentation** - Comprehensive user guide for modernized package

### Optional Future Enhancements 📋

**Phase 3.2: Key-Value Interface** (deferred - nice-to-have for user customization)  
**Index Card Generation** - Deck table of contents with spell counts by level  
**Enhanced Validation** - Better error messages and spell filtering

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

### 🎯 Phase 9: Package Refactoring (HIGH PRIORITY)

**Goal**: Split monolithic `spellcard-expl3.sty` (1450 lines) into maintainable, feature-based modules

**Why Now**: 
- ✅ Full feature parity achieved - safe time to refactor
- ✅ Identical rendering verified - we have baseline to compare against
- ✅ All tests passing - refactoring won't break functionality
- 🎯 Before adding new features - clean foundation first

#### Refactoring Strategy

**Final Structure**:
```
src/
├── spellcards.sty (~100 lines) - Main package loader
├── spellcards.tex - Document entry point
├── spellcards/ - Package modules (subfolder)
│   ├── core.sty (~150 lines)
│   ├── properties.sty (~180 lines)
│   ├── deck.sty (~170 lines)
│   ├── level-markers.sty (~140 lines)
│   ├── qrcode.sty (~180 lines)
│   ├── info-table.sty (~200 lines)
│   └── content-layout.sty (~180 lines)
└── spells/ - Generated spell cards
```

**Module Breakdown**:

1. **core.sty** (~150 lines) - Foundation
   - Variable declarations (bool, int, fp, tl, seq, prop)
   - Constants and dimensions
   - ALL message definitions (centralized)
   - Utility functions (printer margin check, NULL validation)
   - Dependencies: None

2. **properties.sty** (~180 lines) - Spell Data Management
   - Property list (`\l_spellcard_spell_props`)
   - `\spellprop{key}{value}` command
   - Property getters/setters
   - Default values
   - Dependencies: core.sty

3. **deck.sty** (~170 lines) - Deck Organization
   - Deck state management (`\begin{spelldeck}`, `\end{spelldeck}`)
   - Deck registration and tracking (sequences)
   - Deck label positioning calculations
   - Deck label drawing (TikZ overlay at top edge)
   - Deck queries (count, exists, map)
   - Dependencies: core.sty, properties.sty

4. **level-markers.sty** (~140 lines) - Spell Level Indicators
   - Marker position calculation (right edge, based on spell level)
   - Marker drawing (TikZ overlay)
   - `\SpellMarkerChart` command (reference card)
   - Dependencies: core.sty

5. **qrcode.sty** (~180 lines) - QR Code System
   - QR code counter management (max 2 per page)
   - Position calculation (page parity-aware: odd/even pages)
   - QR code placement (TikZ overlay)
   - `\spellcardqr{url}` command
   - Dependencies: core.sty

6. **info-table.sty** (~200 lines) - Spell Attribute Table
   - Table width calculations
   - Side-by-side table rendering (left: Casting Time/Saving Throw, right: Duration/Range)
   - `\spellcard_render_info:n` function (WITH `\ExplSyntaxOff/On` mode switching)
   - `\renderattribute` LaTeX2e helper (for conditional rows)
   - Dependencies: core.sty, properties.sty

7. **content-layout.sty** (~180 lines) - Card Structure Orchestrator
   - `\begin{spellcard}` environment
   - Title rendering (`\section*` with spell name)
   - Body placement (description content)
   - `\includespell` command and print control
   - Card lifecycle (clearcard, counter resets)
   - Dependencies: ALL modules (orchestrator)

**Total**: ~1200 lines (down from 1450 after trimming comments)

#### Dependency Chain (Acyclic, One-Way)

```
spellcards.sty (main loader)
  → core.sty (foundation)
  → properties.sty ← core
  → deck.sty ← core, properties
  → level-markers.sty ← core
  → qrcode.sty ← core
  → info-table.sty ← core, properties
  → content-layout.sty ← ALL (orchestrator)
```

#### Implementation Phases (Safest Order)

**Phase 1: Extract Independent Features** (LOW RISK)
1. ✅ Create `spellcards/core.sty` - All variables, messages, constants
2. ✅ Create `spellcards/properties.sty` - Property list (depends on core only)
3. ✅ Create `spellcards/level-markers.sty` - Fully independent (depends on core only)
4. ✅ Create `spellcards/qrcode.sty` - Fully independent (depends on core only)

**Phase 2: Extract Single-Dependency Features** (MEDIUM RISK)
5. ⚠️ Create `spellcards/info-table.sty` - Depends on: core, properties
   - **Critical**: Keep entire `\spellcard_render_info:n` function together
   - **Critical**: Keep `\ExplSyntaxOff/On` dance intact

**Phase 3: Extract Composite Features** (MEDIUM RISK)
6. ⚠️ Create `spellcards/deck.sty` - Depends on: core, properties
   - Includes deck state management AND deck label drawing
   - Both are part of the "deck" concept

**Phase 4: Extract Orchestrator** (HIGH RISK - DO LAST)
7. ⚠️⚠️ Create `spellcards/content-layout.sty` - Depends on: ALL
   - `\begin{spellcard}` environment
   - Calls all other modules
   - **Do this LAST** after all other modules are stable

**Phase 5: Create Main Loader**
8. ✅ Refactor `src/spellcards.sty` to just load modules in correct order
9. ✅ Rename package: `spellcard-expl3.sty` → `spellcards.sty`

**Phase 6: Reorganize Test Files**
10. ✅ Create feature-specific test files in `src/tests/` subfolder:
    - `test-core.tex` - Variables, constants, messages initialization
    - `test-properties.tex` - Property list management, defaults
    - `test-deck.tex` - Deck tracking, labels, queries
    - `test-level-markers.tex` - Marker positioning, drawing, chart
    - `test-qrcode.tex` - QR code validation, positioning (page parity), max 2 per page
    - `test-info-table.tex` - Table rendering, width calculations
    - `test-content-layout.tex` - Card environment, title, body, includespell
    - `test-integration.tex` - Full spell cards (end-to-end)
11. ✅ Remove old test files from `src/` root (test-expl3.tex, test-spell.tex, etc.)
12. ✅ Update `.gitignore` for `src/tests/out/` directory

**Rationale**: 
- Feature-based tests match module structure
- Easier to identify what broke when a test fails
- Tests can use full `\usepackage{spellcards}` and only exercise specific features
- Keeps `src/` root clean (only production files: spellcards.sty, spellcards.tex, cardify.tex)
- Test outputs in dedicated `src/tests/out/` subfolder

#### Critical Interdependencies (Watch Out!)

**🔴 HIGH RISK: Info Table + LaTeX2e Mode Switching**
- Problem: `\spellcard_render_info:n` switches between expl3 and LaTeX2e modes mid-function
- Solution: Keep entire function in `info-table.sty` - DO NOT split the mode switching logic

**🟡 MEDIUM RISK: Spell Card Environment (Orchestrator)**
- Problem: `\begin{spellcard}` depends on ALL modules (deck, markers, QR, table, properties)
- Solution: Extract this LAST after all other modules are stable

**🟡 MEDIUM RISK: Deck Labels + Deck State**
- Problem: Deck labels use deck state variables
- Solution: Keep both in `deck.sty` - they're conceptually the same feature

**🟢 NO RISK: Level Markers, QR Codes, Properties**
- These are fully independent features with clean boundaries

#### Testing Strategy

**After Each Module Extraction**:
1. ✅ Compile `src/spellcards.tex` - must succeed with exit code 0
2. ✅ Compare PDF output with baseline (`spellcards.pdf` from before refactoring)
3. ✅ Verify zero warnings/errors in log file
4. ✅ Run chktex on changed files (for traditional LaTeX2e files only)

**Final Verification**:
1. ✅ Compile both `spellcards.tex` and `spellcards-legacy.tex`
2. ✅ Compare PDFs - must remain identical (91 pages, 25 spells)
3. ✅ All 359 Python tests still pass
4. ✅ Pylint 10.00/10 maintained

#### Refactoring Guidelines

**✅ DO**:
- Keep mode switches intact (`\ExplSyntaxOff` with `\ExplSyntaxOn`)
- Maintain dependency order (Core → Features → Orchestrator)
- Test after each extraction (compile after moving each module)
- Keep related positioning code together (calculation + drawing for same feature)
- Centralize messages (all in `core.sty`)
- Trim obvious/redundant comments (target: ~100-150 comment lines total)
- Remove empty lines between function definitions

**❌ DON'T**:
- Don't split info table rendering (`\spellcard_render_info:n` is atomic)
- Don't separate deck state from deck labels (they're one feature)
- Don't split orchestrator too early (do it last when other modules are stable)
- Don't create circular dependencies (always one-way: Foundation → Features → Orchestrator)
- Don't break working code without testing immediately

---

### 🎯 Phase 9.1: Document Class Creation & `\clearcard` → `\cleardoublepage` (AFTER Phase 9)

**Goal**: Create custom document class with draft/final modes and eliminate `\clearcard` abstraction in favor of standard LaTeX `\cleardoublepage`

**Motivation**: 
- The `\clearcard` command created an artificial interdependency between spellcards package and cardify.tex
- Using `\cleardoublepage` is the LaTeX-idiomatic way (mirrors how `book` vs `article` classes handle page clearing)
- Document class can control whether `\cleardoublepage` means "clear to next page" (draft/oneside) or "clear to odd page" (final/twoside)
- This eliminates the need for cardify to redefine any commands - it just provides page layout

**Architecture**:
```
src/
├── spellcard.cls              # Custom document class
│   ├── [draft] (default)     # Single-sided, \cleardoublepage = \clearpage
│   └── [final]               # Double-sided, loads cardify, \cleardoublepage works naturally
├── spellcards.sty             # Content package (uses \cleardoublepage directly)
└── cardify.tex                # Page layout ONLY (no command redefinitions)
```

**Implementation Steps**:

1. **Create `spellcard.cls`** (~30 min)
   - Draft mode (default): `\LoadClass[oneside]{scrartcl}`, `\let\cleardoublepage\clearpage`
   - Final mode: `\LoadClass[twoside]{scrartcl}`, `\input{cardify}`, use native `\cleardoublepage`
   - Load all required packages (calc, amsmath, etc.)
   - Load `\RequirePackage{spellcards}`
   - Conditional cardify loading only in final mode

2. **Update `content-layout.sty`** (~10 min)
   - Replace `\clearcard` with `\cleardoublepage` in `\spellcard_end_card:`
   - Remove `\providecommand{\clearcard}{\clearpage}`
   - Document class now controls `\cleardoublepage` semantics

3. **Update `cardify.tex`** (~5 min)
   - Remove `\renewcommand{\clearcard}{\cleardoublepage}` at end of file
   - cardify now ONLY provides page layout, no command redefinitions

4. **Update `spellcards.tex`** (~5 min)
   - Replace `\documentclass{scrartcl}` with `\documentclass[final]{spellcard}`
   - Remove all `\usepackage` statements (now in class)
   - Remove `\usepackage{spellcards}` (now in class)
   - Remove `\input{cardify}` (now conditional in class)
   - Document becomes minimal: just `\documentclass`, `\begin{document}`, content

5. **Testing** (~20 min)
   - Compile with `\documentclass{spellcard}` (draft mode, no cardify) - should be ~21 pages, single-sided
   - Compile with `\documentclass[final]{spellcard}` (cardified) - should be 42 pages, double-sided
   - Verify page counts match expected output
   - Verify zero warnings/errors
   - Compare PDF output with previous version

**Benefits**:
- ✅ **Zero interdependency**: spellcards package never mentions cardify
- ✅ **LaTeX-idiomatic**: Mirrors book/article class pattern with `\cleardoublepage`
- ✅ **Clear user intent**: `\documentclass[draft]{spellcard}` vs `[final]` is self-documenting
- ✅ **Simpler architecture**: One command (`\cleardoublepage`) instead of custom abstraction
- ✅ **Future extensibility**: Could add other modes/layouts without touching spellcards package

**Timeline**: ~1 hour 10 minutes

**Status**: ✅ **COMPLETE** (October 30, 2025)

**Implementation Summary**:

1. ✅ **Created `spellcard.cls`**:
   - Default: final mode (production-ready, cardified, `\cleardoublepage` works naturally)
   - `[draft]` option: single-sided, no cardify, `\cleardoublepage = \clearpage`
   - Minimal dependencies: only `inputenc` (UTF-8) and `amsmath` (spell descriptions)
   - Loads `spellcards` package automatically
   - Conditional `\PassOptionsToClass` for clean option handling

2. ✅ **Replaced `\clearcard` with `\cleardoublepage`**:
   - Updated `content-layout.sty`: removed `\providecommand{\clearcard}`
   - Updated `level-markers.sty`: `\SpellMarkerChart` uses `\cleardoublepage`
   - Updated `cardify.tex`: removed `\renewcommand{\clearcard}{\cleardoublepage}`
   - Document class now controls semantics via oneside/twoside mode

3. ✅ **Simplified `spellcards.tex`**:
   - From ~30 lines to 3 lines: `\documentclass{spellcard}`, `\begin{document}`, content
   - All package loading now in document class

4. ✅ **Moved dependencies to appropriate locations**:
   - `spellcard.cls`: only `inputenc`, `amsmath` (document-level needs)
   - `spellcards.sty`: added `calc` (for info-table dimension arithmetic)
   - All feature dependencies in `spellcards.sty`: `tikz`, `qrcode`, `booktabs`, `tabularx`, `ifthen`, `longtable`

**Testing Results**:
- ✅ Draft mode: single-sided, A4, no cardify - exit code 0
- ✅ Final mode: double-sided, A4, cardified - exit code 0
- ✅ Table layout correct in both modes (side-by-side rendering)
- ✅ Zero interdependency between spellcards package and cardify

**Key Achievement**: Eliminated architectural coupling while following LaTeX conventions! 🎉

---

### 🎯 Phase 10: Command Naming Modernization (AFTER Phase 9.1)

**Goal**: Modernize public API with PascalCase naming convention

**Scope**: User-facing commands only (internal functions keep snake_case)

**Examples**:
- `\begin{spellcard}` → `\begin{SpellCard}`
- `\spellprop{key}{value}` → `\SpellProp{key}{value}`
- `\spellcardqr{url}` → `\SpellCardQR{url}`
- `\includespell[options]{file}` → `\IncludeSpell[options]{file}`

**Implementation Strategy** (No Backwards Compatibility):

1. **Manual Prototype** (~1 hour)
   - Update `spellcards.sty` to provide new command names
   - Update 2-3 spell card files to use new PascalCase commands
   - Compile a test with those spells and verify PDFs render correctly

2. **Bulk Rename Existing Files** (~30 min)
   - Use `sed` to rename commands in all existing spell card files:
     ```bash
     find src/spells/sor -name "*.tex" -exec sed -i \
       -e 's/SPELL-CARD-VERSION: 2.0-expl3/SPELL-CARD-VERSION: 2.1/g' \
       -e 's/\\begin{spellcard}/\\begin{SpellCard}/g' \
       -e 's/\\end{spellcard}/\\end{SpellCard}/g' \
       -e 's/\\spellprop{/\\SpellProp{/g' \
       -e 's/\\spellcardqr{/\\SpellCardQR{/g' \
       -e 's/\\spellcardinfo{/\\SpellCardInfo{/g' \
       {} \;
     ```
   - Verify with git diff
   - Compile spellcards.tex to ensure all cards still work

3. **Update Python Generator** (~2 hours)
   - Modify `generators/file_scanner.py` to read Version "2.1" of the template  
     Simply replace 2.0 parsing and fail if input version is 2.0, no compatibility needed!
   - Modify `generators/latex_generator.py` to output new PascalCase commands
   - Update all template strings
   - Update test fixtures to expect new format
   - Run all 359 tests - must pass
   - Verify by running the generator on the spells we've already modified with sed via CLI.  
     Files should not change.

4. **Regeneration Test** (~90 min)
   - Regenerate spells via GUI
   - Verify generated files use PascalCase
   - Verify preservation features still work
   - Compile and verify spellcards.tex
   - Compare PDF with baseline (should be identical except for any DB updates)

**Timeline**: ~5 hours total

**Breaking Change**: YES - Old spell card files won't work after this phase
**Mitigation**: All existing cards will be bulk-renamed with sed before generator is updated

---

### 🎯 Phase 11: Remove ALL Compatibility Layers (AFTER Phase 10)

**Goal**: Clean up all legacy/compatibility code - we no longer need to support old formats

**Rationale**: 
- ✅ All spell cards regenerated with modern format (Phase 10)
- ✅ No old-format cards exist anymore
- ✅ No need to read/parse legacy format ever again
- 🎯 Simpler codebase, easier maintenance

**Removals**:

1. **LaTeX Files** (~3 hours)
   - ✅ Delete `src/spellcard-templates-compat.tex` (compatibility layer)
   - ✅ Delete `src/spellcard-templates-legacy.tex` (old templates)
   - ✅ Delete `src/spellcards-legacy.tex` (legacy entry point)
   - ✅ Delete `src/spells-legacy/` directory (old spell format examples)
   - ✅ Keep `src/spells-expl3/` if it contains reference examples, or remove if obsolete

2. **Python Generator - Legacy Format Reading** (~2 hours)
   - ❌ Remove legacy property extraction from `utils/file_scanner.py`
     - Delete `\newcommand{\property}{value}` parsing
     - Keep only `\SpellProp{key}{value}` parsing (new format)
   - ❌ Remove legacy URL extraction
     - Delete `\newcommand{\urlenglish}` parsing
     - Keep only `\SpellCardQR{url}` parsing
   - ❌ Update `extract_properties()` to only handle modern format
   - ✅ Simplify `analyze_existing_card()` - no format detection needed

3. **Python Tests - Legacy Test Cases** (~1 hour)
   - ❌ Delete `TestPropertyExtractionLegacy` class from `tests/test_property_extraction.py`
   - ❌ Delete `TestPropertyExtractionLegacyEdgeCases` class
   - ✅ Keep only `TestPropertyExtractionExpl3` class (rename to just `TestPropertyExtraction`)
   - ❌ Remove legacy test fixtures and sample files
   - Update test count (will drop from 359 to ~320 tests)

4. **Documentation Updates** (~30 min)
   - Update README to remove legacy format references
   - Update Python generator README
   - Mark old format as "deprecated/removed" in changelog

**Verification**:
- ✅ All Python tests pass (~320 tests, down from 359)
- ✅ Pylint 10.00/10 maintained
- ✅ All spell cards compile successfully
- ✅ No references to legacy format in codebase (grep check)

**Timeline**: ~6.5 hours total

**Benefits**:
- 🎯 Simpler codebase (~200-300 lines removed from Python)
- 🎯 No more format detection logic
- 🎯 Easier to understand and maintain
- 🎯 No confusion about which format to use

---

### 🎯 Phase 12: Documentation (FINAL)

**Goal**: Comprehensive user guide for modernized package

**Priority**: Do AFTER refactoring and command renaming are complete and stable

---

### Optional Polishing Tasks (Future Sessions)

1. **Enhanced Features** (NICE-TO-HAVE)
   - Index card generation for deck tables of contents
   - Spell filtering for deck building
   - Additional validation with better error messages
   - Custom printer margin configuration UI

2. **Performance Optimization** (IF NEEDED)
   - Profile compilation time for large spell sets
   - Optimize TikZ drawing if slow
   - Cache calculations if beneficial

## Recent Work Sessions

### October 31, 2025 - Phase 11 Complete: Remove ALL Legacy/Compatibility Code ✅

**Phase 11: Clean Modern Codebase**

**Goal**: Remove all legacy and compatibility code to create a clean, maintainable modern codebase.

**Achievements**:
1. ✅ **Removed LaTeX Legacy Files**:
   - Deleted `spellcard-templates-compat.tex` (compatibility layer)
   - Deleted `spellcard-templates-legacy.tex` (old templates)
   - Deleted `spellcards-legacy.tex` (legacy entry point)
   - Deleted entire `spells-legacy/` directory (47 old format spell files)

2. ✅ **Removed Python Legacy Format Reading**:
   - Removed `_detect_spell_file_version()` method (no longer needed)
   - Removed `_extract_properties_legacy()` method (~60 lines)
   - Removed legacy `\newcommand` parsing logic
   - Removed legacy URL extraction (`\urlenglish`, `\urlsecondary`)
   - Removed fallback to `\href` URL extraction
   - Simplified `extract_properties()` to only call `_extract_properties_expl3()`
   - Updated `analyze_existing_card()` to only extract `\SpellCardQR` URLs

3. ✅ **Removed Python Legacy Tests**:
   - Deleted `TestPropertyExtractionLegacy` class (12 test methods)
   - Deleted `TestPropertyExtractionLegacyEdgeCases` class (2 test methods)
   - Updated 3 file_scanner tests to use modern `\SpellCardQR` format
   - Test count reduced from 359 to 346 tests (13 legacy tests removed)

4. ✅ **Updated Documentation**:
   - Updated main `README.md` to show modern `\SpellProp` format
   - Removed references to legacy `\newcommand` format
   - Removed mention of legacy `convert.sh` script
   - Updated property preservation examples to version 2.1 format

**Code Quality Verification**:
- Black formatting: 1 file reformatted, 37 files unchanged
- Pylint: 10.00/10 (perfect score)
- Tests: 346/346 passing (100% pass rate)
- Coverage: 59% overall (file_scanner: 89%, latex_generator: 84%)

**Lines of Code Removed**:
- LaTeX files: ~1500+ lines (entire legacy spell directory + template files)
- Python code: ~100 lines (legacy parsing methods)
- Python tests: ~250 lines (14 legacy test methods)
- **Total cleanup**: ~1850+ lines removed

**Benefits Achieved**:
- ✅ Simpler codebase - no format detection needed
- ✅ Single source of truth - only version 2.1 modern format
- ✅ Cleaner API - no legacy command support
- ✅ Easier maintenance - less code to understand
- ✅ No confusion - one way to do things

**Result**: Clean, modern codebase with zero legacy baggage! 🎉

---

### October 31, 2025 - Phase 10 Complete: Command Naming Modernization ✅

**Phase 10: PascalCase Public API & Version 2.1**

**Goal**: Modernize user-facing commands with PascalCase naming convention, establishing clear distinction between public and internal APIs.

**Achievements**:
1. ✅ **Manual Prototype** (~1 hour):
   - Updated 7 package files with PascalCase commands
   - Renamed 3 internal commands to snake_case (`\register_spell`, `\deck_spell_count`, `\deck_count`)
   - Removed 3 deprecated/unused commands (`\noprint`, `\spellattribute`, `\spellattributelast`)
   - Compiled test spell files: 2 pages, exit code 0

2. ✅ **Bulk Rename** (~30 min):
   - Updated 47 spell card files with sed script
   - Changed version to 2.1 across all files
   - Compiled main document: 42 pages, exit code 0

3. ✅ **Update Python Generator** (~2 hours):
   - Modified `latex_generator.py` to output version 2.1 with PascalCase
   - Updated `file_scanner.py` to recognize only PascalCase (no backward compatibility)
   - Fixed test assertions
   - All 359 tests passing, pylint 10.00/10

4. ✅ **Regeneration Test** (~15 min):
   - Used GUI to regenerate all 46 spell cards
   - Only change: comments updated to reflect `\SpellProp` naming
   - Compiled successfully: 42 pages, exit code 0

**Command Mapping**:
- Public API (PascalCase): `\SpellCard`, `\SpellProp`, `\SpellCardQR`, `\SpellCardInfo`, `\IncludeSpell`, `\SpellDeck`, `\ShowDeck`, `\SpellMarkerChart`
- Internal API (snake_case): `\register_spell`, `\deck_spell_count`, `\deck_count` (reserved for future deck index cards)

**Breaking Changes**:
- Version 2.1 (from 2.0-expl3)
- No backward compatibility with lowercase commands
- All spell cards must use PascalCase

**Quality Metrics**:
- LaTeX: Exit code 0, zero warnings, 42 pages
- Python: 359/359 tests passing, pylint 10.00/10, Black compliant
- Coverage: 59% overall (latex_generator: 84%, file_scanner: 90%)

**Documentation**: Created `docs/phase10-completion-summary.md` with full details.

**Result**: Clean, modern API ready for production use! 🎉

---

### October 30, 2025 - Phase 9.1 Complete: Document Class & Architecture Cleanup ✅

**Phase 9.1: Document Class Creation & Dependency Decoupling**

**Problem**: The `\clearcard` command created an interdependency between spellcards package and cardify.tex, requiring careful load order management.

**Solution**: Created custom document class following LaTeX conventions:
- **`spellcard.cls`**: Controls draft/final modes, loads dependencies, conditionally includes cardify
- **Default mode**: Final (production-ready, cardified, double-sided)
- **Draft mode**: `\documentclass[draft]{spellcard}` for fast iteration (single-sided, no cardify)

**Key Changes**:
1. ✅ **Eliminated `\clearcard` abstraction**: 
   - Replaced with standard LaTeX `\cleardoublepage` throughout codebase
   - Document class controls semantics (draft: `\cleardoublepage = \clearpage`, final: native twoside behavior)
   - Zero coupling between spellcards package and cardify

2. ✅ **Created `spellcard.cls`**:
   - Minimal dependencies: only `inputenc` (UTF-8) and `amsmath` (user content)
   - Conditional option passing: `\PassOptionsToClass{oneside,draft}{scrartcl}` or `{twoside}`
   - Single `\LoadClass` statement (no duplication)
   - Loads `spellcards` package automatically

3. ✅ **Moved dependencies to correct locations**:
   - **Document class**: only document-level needs (`inputenc`, `amsmath`)
   - **spellcards.sty**: all feature dependencies (`calc`, `tikz`, `qrcode`, `booktabs`, `tabularx`, `ifthen`, `longtable`)
   - Fixed: `calc` package needed by `info-table.sty` for dimension arithmetic (`\firsttablewidth\textwidth`)

4. ✅ **Simplified `spellcards.tex`**:
   - From ~30 lines (with package loading) to 3 lines
   - Just: `\documentclass{spellcard}`, `\begin{document}`, content

5. ✅ **Updated cardify.tex**:
   - Removed `\renewcommand{\clearcard}{\cleardoublepage}`
   - Now ONLY provides page layout (pgfmorepages configuration)

**Testing**:
- ✅ Draft mode: Single-sided, no cardify, table layout correct - exit code 0
- ✅ Final mode: Double-sided, cardified, table layout correct - exit code 0
- ✅ Zero warnings, zero errors in both modes

**Architecture Achievement**: Clean separation of concerns following LaTeX best practices! 🎉

---

### October 29, 2025 - MIGRATION COMPLETE! 🎉 ✅

**Final Verification - PDF Comparison**:
- Compiled both `spellcards.pdf` (expl3) and `spellcards-legacy.pdf` with all 25 spells enabled
- **Result**: IDENTICAL OUTPUT - Full feature parity achieved!

**Comparison Results**:
- ✅ Page count: Both PDFs = **91 pages**
- ✅ Spell count: Both PDFs = **25 spells**
- ✅ Field completeness: Attack Roll (82), Spell Resist (82), Saving Throw (80) - all match
- ✅ Content verification: Spell names, descriptions, statistics all identical
- ✅ LaTeX compilation: **Zero warnings, zero errors** in both versions
- ✅ Formatting: Only cosmetic spacing differences (extra spaces after colons)

**Spells Verified**:
- Level 0: Acid Splash, Dancing Lights, Detect Magic, Ghost Sound, Mage Hand, Prestidigitation, Ray of Frost
- Level 1: Comprehend Languages, Expeditious Retreat, Feather Fall, Grease, Magic Missile, Shocking Grasp
- Level 2: Flaming Sphere, Glitterdust, Knock, Scorching Ray
- Level 3: Dispel Magic, Fireball, Fly, Haste
- Level 5-7: Permanency, Elemental Body II, etc.

**Conclusion**: The expl3 modernization is **PRODUCTION READY**. Both versions are functionally identical and compile cleanly.

### October 29, 2025 - Template Format Cleanup ✅

**Issue**: File scanner looking for non-existent `\qrcode` commands
- **Legacy format**: Uses `\newcommand{\urlenglish}{url}` + `\spellcardqr{\urlenglish}` (internally calls `\qrcode`)
- **Expl3 format**: Uses `\spellcardqr{https://example.com/spell}` directly
- **Bug**: Scanner searched for `\qrcode{...}` which never appears in spell files

**Solution**:
1. Removed `\qrcode` pattern from German language detection
2. Removed QR code extraction logic for `\qrcode`
3. Updated tests to use correct formats only
4. Verified against actual spell files (Magic Missile.tex)

**Results**:
- ✅ All 359 tests passing
- ✅ Pylint: 10.00/10 maintained
- ✅ File scanner now accurately reflects actual spell file formats

### October 29, 2025 - URL Extraction Bug Fix ✅

**Problem**: File scanner extracting URLs from commented `\spellcardqr` lines
- Symptom: Regenerating spells replaced secondary URLs with placeholder `<secondary-url>`
- Root cause: Regex `r"\\spellcardqr\{([^}]+)\}"` matched ALL occurrences, including commented lines
- Example: `% \spellcardqr{<secondary-url>}` was being extracted

**Solution** (TDD approach):
1. Added 5 new test cases for expl3 format in `test_property_extraction.py`:
   - `test_extract_simple_properties_expl3` - Basic `\spellprop` extraction
   - `test_extract_qr_codes_from_expl3` - Both URLs extracted
   - `test_extract_single_qr_code_from_expl3` - Single URL only
   - `test_extract_commented_secondary_qr_code` - **Failing test** exposing the bug
   - `test_extract_properties_with_original_comments_expl3` - Modified properties

2. Fixed `file_scanner.py` `_extract_properties_expl3()` method:
   - Changed from single regex `findall` to line-by-line processing
   - Skip lines starting with `%` (comments)
   - Extract `\spellcardqr{url}` only from non-commented lines

**Verification**:
- ✅ All 355 tests pass (350 existing + 5 new)
- ✅ Pylint score: 10.00/10 maintained
- ✅ Coverage: file_scanner.py improved from 88% to 90%
- ✅ Bug confirmed fixed: Commented QR codes no longer extracted

**Impact**: Users can now safely regenerate spells - secondary URLs will be preserved when present, and placeholders won't be extracted as URLs.

### October 29, 2025 - Missing Feature Implementation (Phase 6) ✅

**Feature**: `\SpellMarkerChart` - Reference card showing all spell level markers (0-9)

**Implementation**:
- Added `\spellcard_draw_marker_chart:` internal function (line ~610 in spellcard-expl3.sty)
- Uses `\int_step_inline:nn { 10 }` to loop through levels 0-9
- Reuses existing `\spellcard_draw_spell_marker:n` function for consistency
- Added `\SpellMarkerChart` document command (line ~1332)

**TikZ Overlay Spacing Fix**:
- Added `%` signs after `\begin{tikzpicture}` and `\end{tikzpicture}` lines
- Prevents spurious spaces from TikZ overlays affecting card layout

**Verification**:
- ✅ Marker chart renders on first page
- ✅ All 10 markers (0-9) displayed on right edge
- ✅ No layout disruption from TikZ overlays
- ✅ Compilation successful (exit code 0)

**Purpose**: Provides reference card users can color with highlighters to track which colors they've assigned to each spell level when printing new cards.

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

**All core features complete!** These are optional nice-to-have improvements:

1. **Index Card Generation** (enabled by Phase 3.1 deck tracking)
   - Serves as a table of contents for each deck
   - Spell counts by level
   - Preserves input order (no sorting)

2. **Additional Features**
   - Spell filtering for deck building
   - Validation with better error messages
   - Custom printer margin configuration UI

3. **Code Quality**
   - Split large package file into modules
   - Modernize command naming (PascalCase public API)
   - Comprehensive user documentation

## Summary

**🎉 The expl3 modernization is FEATURE COMPLETE and VERIFIED!**

Both legacy and modern implementations produce identical 91-page PDFs with 25 spells, zero compilation warnings, and matching content. The Python generator fully supports the expl3 format with all preservation features (descriptions, URLs, properties, width ratios). All 359 tests pass with 10.00/10 pylint score.

**Next Steps**: Package refactoring (Phase 9-12):
1. **Phase 9**: Split into 7 feature-based modules (~2 days)
2. **Phase 10**: PascalCase command names + bulk sed rename (~5 hours)
3. **Phase 11**: Remove ALL legacy/compatibility code (~6.5 hours)
4. **Phase 12**: Documentation (~ongoing)

After Phase 11, we'll have a clean, modern codebase with no legacy baggage. Total estimated time: ~3-4 days of focused work.

**Ready for production use now, and ready for refactoring!**
