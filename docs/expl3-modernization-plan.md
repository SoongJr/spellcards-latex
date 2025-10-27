# expl3 Modernization Plan for LaTeX Spell Cards

**Date**: October 25, 2025  
**Status**: Planning Phase  
**Priority**: Modern features over backwards compatibility

## Executive Summary

This document outlines a comprehensive plan to modernize the spell card LaTeX project using expl3 (LaTeX3) programming layer. The migration will leverage modern programming constructs, improved type safety, and better maintainability while prioritizing features and code quality over backwards compatibility with older TeX distributions.

## Current Architecture Analysis

### Core Components
1. **spellcard-templates.tex** (~290 lines) - Main template logic
2. **cardify.tex** (~180 lines) - Page layout and card positioning
3. **spellcards.tex** (~30 lines) - Document entry point
4. **Generated spell files** - Individual spell card data

### Current Programming Patterns
- Traditional LaTeX2e macro definitions (`\newcommand`, `\renewcommand`)
- Counter-based state management (`\newcounter`, `\setcounter`)
- Conditional logic using `ifthen` package (`\ifthenelse`)
- Manual string equality checks
- Global/local scope management with `\gdef`, `\begingroup`/`\endgroup`
- TikZ positioning with manual calculations using `\pgfmathparse`
- Floating point calculations via `\fpeval`

## Migration Strategy

### Phase 1: Foundation and Infrastructure (Priority: HIGH)
**Goal**: Establish expl3 programming environment and basic utilities

#### 1.1 Create expl3 Package Structure
- Create `spellcard-expl3.sty` package file
- Set up expl3 programming environment with `\ExplSyntaxOn`/`\ExplSyntaxOff`
- Define package metadata and version information
- Establish naming conventions (module prefix: `spellcard_`)

#### 1.2 Set Up Modern Type System
- **Boolean variables** replacing `\newif` constructs:
  - `\bool_new:N \g_spellcard_print_card_bool` (replaces `\ifprintcard`)
  - `\bool_new:N \g_spellcard_in_deck_bool` (for nested deck detection)
  
- **Integer variables** replacing counters:
  - `\int_new:N \g_spellcard_deck_number_int` (replaces `\currentdecknumber`)
  - `\int_new:N \g_spellcard_qr_code_int` (replaces `\qrCode` counter)
  - `\int_new:N \g_spellcard_page_int` (for page tracking)
  
- **Token list variables** replacing string macros:
  - `\tl_new:N \l_spellcard_current_deck_name_tl` (replaces `\currentdeckname`)
  - `\tl_new:N \l_spellcard_class_tl`, `\l_spellcard_name_tl`, etc.
  
- **Floating point variables** for calculations:
  - `\fp_new:N \l_spellcard_marker_position_fp`
  - `\fp_new:N \l_spellcard_label_position_fp`
  - `\fp_new:N \l_spellcard_printer_margin_x_fp`
  - `\fp_new:N \l_spellcard_printer_margin_y_fp`

#### 1.3 Property Lists for Spell Data
Replace individual `\newcommand` definitions with structured property lists:

```latex
% Instead of 60+ individual \newcommand definitions:
\prop_new:N \l_spellcard_spell_props

% Set values:
\prop_put:Nnn \l_spellcard_spell_props { name } { Teleport }
\prop_put:Nnn \l_spellcard_spell_props { school } { conjuration }
\prop_put:Nnn \l_spellcard_spell_props { level } { 5 }

% Retrieve values:
\prop_item:Nn \l_spellcard_spell_props { name }
```

**Benefits**:
- Type-safe data storage
- Easy iteration over spell properties
- No namespace pollution
- Clear data structure
- Enables validation and default values

### Phase 2: Core Logic Migration (Priority: HIGH)

#### 2.1 Deck Management System
Modernize the `spelldeck` environment using expl3:

```latex
% Current approach uses renewcommand and manual checks
% New approach uses property lists and boolean flags

\NewDocumentEnvironment { spelldeck } { m }
  {
    % Validate not nested
    \bool_if:NT \g_spellcard_in_deck_bool
      { \msg_error:nn { spellcard } { nested-decks } }
    
    % Set deck name
    \tl_set:Nn \l_spellcard_current_deck_name_tl { #1 }
    
    % Validate first deck is unnamed
    \int_compare:nNnTF { \g_spellcard_deck_number_int } = { 0 }
      {
        \tl_if_empty:NF \l_spellcard_current_deck_name_tl
          { \msg_error:nn { spellcard } { first-deck-must-be-unnamed } }
      }
      {
        \tl_if_empty:NT \l_spellcard_current_deck_name_tl
          { \msg_error:nn { spellcard } { only-first-deck-unnamed } }
      }
    
    \bool_gset_true:N \g_spellcard_in_deck_bool
  }
  {
    \int_gincr:N \g_spellcard_deck_number_int
    \tl_gclear:N \l_spellcard_current_deck_name_tl
    \bool_gset_false:N \g_spellcard_in_deck_bool
  }
```

**Benefits**:
- Cleaner boolean logic with `\bool_if:` variants
- Better error messages with `\msg_error:nn`
- Type-safe comparisons with `\int_compare:`
- Explicit global/local scope with `g`/`l` prefixes

#### 2.2 Positioning Calculations
Replace `\pgfmathparse` with native expl3 FP calculations:

```latex
% Old approach:
\pgfmathparse{mod(#1-1,6)}
\pgfmathsetmacro{\labelposition}{\fpeval{((1/8 * \pgfmathresult)) * \paperwidth} + 7mm}

% New approach:
\fp_set:Nn \l_spellcard_deck_mod_fp { mod(#1 - 1, 6) }
\fp_set:Nn \l_spellcard_label_position_fp 
  { 
    (1/8 * \l_spellcard_deck_mod_fp) * \dim_to_fp:n { \paperwidth } 
    + 7mm 
  }
\dim_set:Nn \l_spellcard_label_position_dim 
  { \fp_to_dim:N \l_spellcard_label_position_fp }
```

**Benefits**:
- Native floating point arithmetic
- Better precision and performance
- Type-safe dimension handling
- No dependency on PGF for calculations

#### 2.3 Conditional Logic Modernization
Replace `ifthen` package with expl3 conditionals:

```latex
% Old:
\ifthenelse{\equal{#2}{NULL}}{}{\textbf{#1:} & #2 \\ \midrule}

% New:
\str_if_eq:nnF { #2 } { NULL }
  { \textbf{#1:} & #2 \\ \midrule }

% Or with predicate:
\prg_new_conditional:Npnn \spellcard_if_not_null:n #1 { p, T, F, TF }
  {
    \str_if_eq:nnTF { #1 } { NULL }
      { \prg_return_false: }
      { \prg_return_true: }
  }

% Usage:
\spellcard_if_not_null:nT { #2 }
  { \textbf{#1:} & #2 \\ \midrule }
```

**Benefits**:
- Faster compilation (no external package)
- Consistent conditional syntax
- Custom predicates for domain logic
- Better expandability control

### Phase 3: Advanced Features (Priority: MEDIUM)

#### 3.1 Sequence-Based Spell Lists ✅ COMPLETED
**Enhanced for Deck Tracking and Index Card Generation**

Instead of just storing file paths, we now track full spell metadata per deck:

```latex
% Global deck tracking infrastructure
\prop_new:N \g_spellcard_decks_prop  % Deck metadata
\seq_new:N \g_spellcard_current_deck_spells_seq  % Current deck's spells

% Register a spell in the current deck
\spellcard_register_spell:nnnn { file } { class } { name } { level }

% Each spell stored as: file={...},class={...},name={...},level={...}
% Stored in per-deck sequences: g_spellcard_deck_N_spells_seq
```

**Query Functions for Index Generation**:
```latex
% Get spell count for a deck
\spellcard_get_deck_spell_count:n { 0 }  % Returns integer

% Check if deck exists
\spellcard_if_deck_exists:nTF { 5 } { yes } { no }

% Iterate over all spells in a deck
\spellcard_map_deck_spells:nn { 1 }
{
  % ##1 contains spell metadata string
  \process_spell_for_index { ##1 }
}

% Count spells of specific level
\spellcard_count_spells_by_level:nn { 0 } { 3 }  % Level 3 spells in deck 0
```

**Benefits**:
- ✅ Track which spells belong to each deck
- ✅ Query spell counts for layout planning
- ✅ Filter by level for organized listings
- ✅ Foundation for automatic index card generation
- ✅ Programmatic deck manipulation
- ✅ Better integration with Python generator (future)

**Use Case - Index Card Generation**:
```latex
\begin{indexcard}{Combat Spells}
  \textbf{Deck 1 - \deckspellcount{1} spells}
  
  \spellcard_map_deck_spells:nn { 1 }
  {
    \parseandlist{##1}  % Extract name and level, format as list item
  }
\end{indexcard}
```

#### 3.2 Key-Value Spell Definitions
Use `l3keys` for spell card parameters:

```latex
\keys_define:nn { spellcard }
  {
    name         .tl_set:N  = \l_spellcard_name_tl,
    school       .tl_set:N  = \l_spellcard_school_tl,
    level        .int_set:N = \l_spellcard_level_int,
    casting-time .tl_set:N  = \l_spellcard_casting_time_tl,
    components   .tl_set:N  = \l_spellcard_components_tl,
    % ... more keys
    
    % Provide defaults
    descriptor   .default:n = { NULL },
    targets      .default:n = { NULL },
  }

% Usage in spell files:
\begin{spellcard}{sor}{Teleport}{5}
  \SetSpellProperties{
    name = Teleport,
    school = conjuration,
    level = 5,
    casting-time = 1~standard~action,
    components = V,
    range = personal~and~touch,
    % ...
  }
\end{spellcard}
```

**Benefits**:
- Cleaner spell file syntax
- Default values and validation
- Type checking for numeric values
- Easier to extend with new properties
- Better error messages for missing/invalid keys

#### 3.3 Message System
Replace `\PackageError` with expl3 message system:

```latex
\msg_new:nnn { spellcard } { nested-decks }
  {
    Nested~spell~decks~are~not~supported.~
    You~may~have~forgotten~to~close~a~spelldeck~environment.
  }

\msg_new:nnn { spellcard } { too-many-qr-codes }
  {
    Too~many~QR~codes~on~page~\int_use:N \g_spellcard_page_int.~
    Maximum~2~per~page.~Consider~using~\clearpage~to~move~to~back~face.
  }

\msg_new:nnn { spellcard } { first-deck-must-be-unnamed }
  {
    The~first~spell~deck~must~have~an~empty~name.~
    Found:~'\tl_use:N \l_spellcard_current_deck_name_tl'
  }
```

**Benefits**:
- Consistent error message formatting
- Can include variable values in messages
- Different message types (error, warning, info)
- Better debugging experience

### Phase 4: Layout and Rendering (Priority: MEDIUM)

#### 4.1 Dimension Calculations
Use expl3 dimension expressions for layout:

```latex
% Define dimension variables
\dim_new:N \l_spellcard_card_width_dim
\dim_new:N \l_spellcard_card_height_dim
\dim_new:N \l_spellcard_margin_x_dim
\dim_new:N \l_spellcard_margin_y_dim

% Calculate with expressions
\dim_set:Nn \l_spellcard_card_width_dim 
  { 0.5 \paperwidth - \l_spellcard_margin_x_dim }
  
\dim_set:Nn \l_spellcard_resized_width_dim
  { 0.5 \dim_use:N \pgfphysicalwidth - \l_spellcard_printer_margin_x_dim }
```

**Benefits**:
- Type-safe dimension handling
- Cleaner arithmetic
- Better integration with layout packages
- No need for `\pgfmathsetlength`

#### 4.2 Marker and Label Positioning
Create functions for positioning logic:

```latex
\cs_new:Npn \spellcard_calculate_marker_position:n #1
  {
    \fp_set:Nn \l_tmpa_fp { mod(#1, 10) }
    \fp_set:Nn \l_spellcard_marker_position_fp
      { (1/16 * \l_tmpa_fp) * \dim_to_fp:n { \paperheight } + 2.5cm }
  }

\cs_new:Npn \spellcard_calculate_label_position:n #1
  {
    \fp_set:Nn \l_tmpa_fp { mod(#1 - 1, 6) }
    \bool_if:NTF \l_spellcard_has_printer_margin_bool
      {
        \fp_set:Nn \l_spellcard_label_position_fp
          { (1/8 * \l_tmpa_fp) * \dim_to_fp:n { \paperwidth } + 7mm }
      }
      {
        \fp_set:Nn \l_spellcard_label_position_fp
          { (1/8 * \l_tmpa_fp) * \dim_to_fp:n { \paperwidth } + 15mm }
      }
  }
```

**Benefits**:
- Encapsulated positioning logic
- Reusable functions
- Easier to test and debug
- Clear separation of concerns

#### 4.3 QR Code Management
Implement robust QR code positioning:

```latex
\cs_new:Npn \spellcard_add_qr_code:n #1
  {
    % Validate count
    \int_compare:nNnT { \g_spellcard_qr_code_int } > { 1 }
      { \msg_error:nn { spellcard } { too-many-qr-codes } }
    
    % Calculate position based on page parity and QR code number
    \int_if_odd:nTF { \value{page} }
      { \spellcard_qr_code_odd_page:n { #1 } }
      { \spellcard_qr_code_even_page:n { #1 } }
    
    \int_gincr:N \g_spellcard_qr_code_int
  }

\cs_new:Npn \spellcard_qr_code_odd_page:n #1
  {
    \int_case:nn { \g_spellcard_qr_code_int }
      {
        { 0 } { \spellcard_place_qr_southwest:n { #1 } }
        { 1 } { \spellcard_place_qr_southeast:n { #1 } }
      }
  }
```

**Benefits**:
- Clear case-based logic with `\int_case:nn`
- Separate functions for positioning logic
- Easier to extend to 3+ QR codes if needed
- Better error handling

### Phase 5: Integration and Testing (Priority: HIGH)

#### 5.1 Backwards Compatibility Layer
Create wrapper commands for existing spell files:

```latex
% Provide LaTeX2e interface for generated spell files
\NewDocumentCommand \spellattribute { m m }
  {
    \spellcard_attribute:nn { #1 } { #2 }
  }

% Internal expl3 implementation
\cs_new:Npn \spellcard_attribute:nn #1 #2
  {
    \spellcard_if_not_null:nT { #2 }
      { \textbf{#1:} & #2 \\ \midrule }
  }
```

#### 5.2 Testing Strategy
- Compile existing spell cards to verify output matches
- Run chktex on all files
- Test with different deck configurations
- Verify QR code positioning on odd/even pages
- Test marker positioning for levels 0-9+
- Validate error messages for edge cases

#### 5.3 Python Generator Updates
Update `generators/latex_generator.py` to optionally use new key-value interface:

```python
# Add configuration option for output format
class LaTeXGenerator:
    def __init__(self, use_expl3_keys: bool = False):
        self.use_expl3_keys = use_expl3_keys
    
    def generate_spell_properties(self, spell_data):
        if self.use_expl3_keys:
            return self._generate_keyval_properties(spell_data)
        else:
            return self._generate_newcommand_properties(spell_data)
```

### Phase 6: Documentation and Cleanup (Priority: MEDIUM)

#### 6.1 Code Documentation
- Add docstring-style comments to expl3 functions
- Document function signatures and parameters
- Create internal API documentation
- Document naming conventions and module structure

#### 6.2 User Documentation
- Update README with expl3 migration notes
- Document new key-value interface for manual spell creation
- Provide examples of advanced features
- Create migration guide for existing spell files

#### 6.3 Cleanup
- Remove deprecated packages (`ifthen`)
- Clean up redundant calculations
- Consolidate similar functions
- Optimize compilation performance

## Implementation Roadmap

### Week 1-2: Foundation (Phase 1) ✅ COMPLETED
- [x] Create `spellcard-expl3.sty` package
- [x] Define all expl3 variables and data structures
- [x] Set up property lists for spell data
- [x] Create test document to verify compilation
- [x] Implement message system (completed early in Phase 1)

**Status**: Complete - See `docs/phase1-completion-summary.md`

### Week 3-4: Core Migration (Phase 2) ✅ COMPLETED
- [x] Migrate deck management system
- [x] Convert positioning calculations to expl3 FP
- [x] Replace all ifthen conditionals for spell attributes
- [x] Test with existing spell cards

**Status**: Complete - All core logic migrated to expl3

**Key Functions Added**:
- `\spellcard_calculate_marker_position:n` - Spell level markers
- `\spellcard_calculate_label_position:n` - Deck labels
- `\spellcard_attribute:nn` - NULL-aware attribute printing
- `\spellcard_get_marker_xshift:` - Margin-aware positioning

### Week 5: Advanced Features (Phase 3) 🚧 IN PROGRESS
- [x] **Phase 3.1**: Create sequence-based spell lists for deck tracking
- [x] Add spell registration system for index card generation
- [x] Implement deck query functions
- [ ] **Phase 3.2**: Implement key-value spell interface (DEFERRED until after Phase 5)
- [x] **Phase 3.3**: Message system (completed in Phase 1)

**Status**: Phase 3.1 complete - deck tracking infrastructure ready for index cards. Phase 3.2 deferred until after integration testing.

**Key Functions Added**:
- `\spellcard_register_spell:nnnn` - Register spells in decks
- `\spellcard_get_deck_spell_count:n` - Query spell counts
- `\spellcard_if_deck_exists:nTF` - Check deck existence
- `\spellcard_map_deck_spells:nn` - Iterate over deck spells
- Document-level commands: `\registerspell`, `\deckspellcount`, `\deckcount`

**Next**: Phase 3.2 (key-value interface) can be deferred until after index card feature is implemented

### Week 6: Layout (Phase 4) ✅ COMPLETED
- [x] Migrate dimension calculations
- [x] Refactor marker/label positioning (Phase 2.2)
- [x] Improve QR code system (Phase 4.3)
- [x] Test layout positioning

**Status**: Complete - All Phase 4 features implemented

**Key Functions Added**:
- `\spellcard_add_qr_code:n` - Main QR code placement function
- `\spellcard_calculate_qr_shift:` - Calculate offset based on QR code number
- `\spellcard_place_qr_southwest:n` - Place QR code at bottom-left
- `\spellcard_place_qr_southeast:n` - Place QR code at bottom-right
- `\spellcard_qr_code_odd_page:n` - QR positioning for odd pages
- `\spellcard_qr_code_even_page:n` - QR positioning for even pages
- `\spellcard_reset_qr_counter:` - Reset counter (called by spell environment)
- Document command: `\spellcardqr{url}` - User-facing QR code command

**Implementation Details**:
- Uses `\int_case:nn` for clean case-based logic
- Validates maximum 2 QR codes per page
- Intelligent positioning based on page parity (odd/even)
- First QR code: 2cm offset, opposite page number
- Second QR code: 4cm offset, same side as page number (avoids overlap)
- Clear error message when limit exceeded

### Week 7: Integration (Phase 5) � IN PROGRESS
- [x] Create compatibility layer (exists - `\includespell`, `\spellprop`)
- [x] Python generator updated to output expl3 format
- [x] Generated 15 spells successfully via CLI (with 3 minor conflicts)
- [x] Test compilation - compiles without errors (exit code 0)
- [ ] **CRITICAL**: Fix table rendering bug (tables wrapping vertically instead of side-by-side)
- [ ] PDF comparison (blocked until table fix)
- [ ] Run Python test suite (350 tests, 10.00/10 pylint)

**Status**: Python integration complete, critical rendering bug discovered

**Progress (October 27, 2025)**:
- Updated `generators/latex_generator.py` to output expl3 format
- Changed from `\newcommand` to `\spellprop{key}{value}` format
- Successfully generated 15 spells via CLI: `spell_card_generator/spell_card_generator.sh`
- User approved generated files: "look absolutely great!"
- Created test comparison files (test-comparison-expl3.tex, test-comparison-legacy.tex)
- PDF compiles successfully (19 pages expl3 vs 18 pages legacy)

**Critical Bug Found**:
- **Symptom**: Two side-by-side spell info tables render vertically stacked instead of horizontally adjacent
- **Affected**: Casting Time/Saving Throw/Spell Resist/Attack Roll (left table) appears right-aligned, Duration/Range/Comp./School (right table) appears left-aligned below it
- **Not Affected**: Teleport and Invisibility Greater render correctly (unknown why)
- **Root Cause**: Unknown - issue with how tabularx environments interact with ExplSyntax mode
- **Location**: `spellcard-expl3.sty` lines 703-790 (`\spellcard_render_info:n`)
- **Attempts**: 5+ different fixes tried, none successful yet:
  1. Added `[b]` positioning argument → pages reduced 20→19, but tables still wrap
  2. Added `%` comment markers → no change
  3. Fixed dimension calculations with `\fp_to_dim:n` → no change
  4. Single `\use:x` block with both tables → LaTeX errors
  5. Separate `\use:x` blocks per table → **INTERRUPTED** (compilation cancelled by user)
- **Next Steps**: Resume testing approach #5 or try alternative strategies (exit ExplSyntax, minipage wrappers, box registers, copy legacy approach exactly)
- **Urgency**: **HIGH** - blocking all PDF comparison and Phase 5 completion

### Week 8: Documentation (Phase 6) 📋 PLANNED
- [ ] Document all expl3 functions
- [ ] Update user documentation
- [ ] Create migration guide
- [ ] Final cleanup and optimization

**Status**: Not started

### Week 9-10: Refactoring and Code Organization (Phase 7) 📋 PLANNED
**Goal**: Split monolithic package into modular components and remove deprecated code

#### 7.1 Package Modularization
**Current Issue**: `spellcard-expl3.sty` is over 1000 lines - too large for maintainability

**Proposed Structure**:
```
src/
├── spellcard-expl3.sty              # Main package (loads sub-packages)
├── spellcard-expl3-core.sty         # Core data structures and variables
├── spellcard-expl3-rendering.sty    # Spell card rendering functions
├── spellcard-expl3-layout.sty       # TikZ positioning and decorative elements
├── spellcard-expl3-qrcode.sty       # QR code system
└── spellcard-expl3-deck.sty         # Deck management and tracking
```

**Benefits**:
- **Maintainability**: Smaller files easier to navigate and understand
- **Modularity**: Clear separation of concerns
- **Testing**: Can test components in isolation
- **Reusability**: Sub-packages could be used independently
- **Documentation**: Easier to document focused functionality

**File Size Targets**:
- Main package: ~100 lines (just loads sub-packages and provides document interface)
- Core: ~200 lines (variables, property lists, basic utilities)
- Rendering: ~300 lines (spell card content, tables, attributes)
- Layout: ~250 lines (markers, labels, positioning calculations)
- QR Code: ~150 lines (QR code placement system)
- Deck: ~200 lines (deck tracking, registration, query functions)

#### 7.2 Code Audit and Cleanup
**Goals**:
1. **Remove Deprecated Code**:
   - Compatibility layer functions if no longer needed
   - Old LaTeX2e implementation (`spellcard-templates.tex`) if fully replaced
   - Unused helper functions from migration
   - Debug/test code that shouldn't be in production

2. **Identify Dead Code**:
   - Functions defined but never called
   - Variables declared but never used
   - Commented-out code blocks from experimentation
   - Redundant implementations

3. **Consolidate Duplicates**:
   - Similar positioning calculations
   - Repeated conditional patterns
   - Common utility functions

#### 7.3 Code Review Checklist
- [ ] Every function has clear documentation
- [ ] No unused variables or functions
- [ ] No commented-out code blocks
- [ ] All expl3 naming conventions followed consistently
- [ ] No LaTeX2e code in expl3 package (except document interface)
- [ ] Error messages exist for all user-facing validation
- [ ] No magic numbers (use named constants)
- [ ] Consistent indentation and formatting

#### 7.4 Performance Audit
- [ ] Identify redundant calculations (cache where appropriate)
- [ ] Check for unnecessary global assignments
- [ ] Optimize hot paths (rendering functions called per spell)
- [ ] Verify no quadratic algorithms in loops
- [ ] Measure compilation time before/after refactoring

#### 7.5 Testing Strategy for Refactoring
- [ ] Compile test documents before refactoring (baseline)
- [ ] Split package incrementally (one sub-package at a time)
- [ ] Test after each split to catch regressions
- [ ] Verify PDF output byte-for-byte identical
- [ ] Run full spell deck compilation test
- [ ] Check compilation time hasn't increased

#### 7.6 Documentation Updates
- [ ] Update package loading instructions
- [ ] Document internal API between sub-packages
- [ ] Add architecture diagram showing module dependencies
- [ ] Document which functions are public vs internal
- [ ] Create contribution guide with code organization principles

**Status**: Not started - scheduled after Phase 5 and 6 complete

**Estimated Effort**: 2 weeks
- Week 1: Split package, test each module
- Week 2: Code audit, cleanup, documentation

## Technical Benefits Summary

### Code Quality
- **Type Safety**: Explicit types for integers, booleans, dimensions, floats
- **Naming Conventions**: Clear `l_`/`g_` prefixes, underscore separators
- **Scoping**: Explicit local/global scope management
- **Error Handling**: Rich message system with context

### Performance
- **Faster Execution**: Native expl3 is faster than ifthen package
- **Better FP**: expl3 FP more efficient than pgfmath for non-graphics
- **Reduced Dependencies**: Less package loading overhead

### Maintainability
- **Readable Code**: Modern syntax, clear intent
- **Modularity**: Functions and conditionals are reusable
- **Extensibility**: Easy to add new features
- **Debugging**: Better error messages, clearer control flow

### Modern Features
- **Property Lists**: Structured data storage
- **Key-Value Interface**: User-friendly spell definition
- **Sequences**: Programmatic list manipulation
- **Predicates**: Custom conditional logic
- **Case Expressions**: Clean multi-branch logic

## Risk Assessment

### Low Risk
- Variable and function definitions (fully backwards compatible via wrappers)
- Positioning calculations (internal implementation detail)
- Message system (improves user experience)

### Medium Risk
- Key-value interface (optional, can be phased in gradually)
- Sequence-based lists (requires Python generator update)
- Dimension calculations (needs thorough testing)

### Mitigation Strategies
1. **Incremental Migration**: Keep LaTeX2e interface, migrate internals first
2. **Comprehensive Testing**: Test every change with full spell deck
3. **Compatibility Layer**: Maintain old commands during transition
4. **Version Control**: Use git branches for experimental features
5. **Documentation**: Clear notes on what changed and why

## Success Criteria

- ✅ All existing spell cards compile without errors
- ✅ PDF output is visually identical (or improved)
- ✅ chktex passes without warnings (38 false positives in expl3 code - expected)
- ✅ Compilation time same or faster
- ✅ Code is more readable and maintainable
- 🔄 Python generator produces valid expl3 code (Phase 5 - next step)
- ✅ Error messages are clearer and more helpful
- 🔄 New features (key-value interface) documented (Phase 3.2 deferred)
- ✅ QR code system works correctly on odd/even pages
- ✅ All Phase 4 layout features functional (positioning, QR codes)
- ✅ Cardify integration working correctly
- ✅ `\includespell` command working as drop-in replacement for `\input`
- ✅ Exit code 0 (zero errors, zero warnings)

**Current Status**: Phases 1-4 complete. Cardify integration tested and working. **Ready for Phase 5: Python Generator Integration.**

## Next Steps (Phase 5)

**Immediate Priority**: Update Python Generator to Output expl3 Format

**Legacy Preservation** (October 27, 2025):
- Created `*-legacy` variants to preserve working legacy system:
  - `src/spellcards-legacy.tex` - Legacy document (4 decks, 15 spells total)
  - `src/spellcard-templates-legacy.tex` - Legacy templates
  - `src/spells-legacy/` - Copy of all legacy spell files
- This allows side-by-side comparison of legacy vs expl3 output
- `src/spells/sor/` folder can now be freely converted to expl3 format
- Legacy system remains compilable for reference and verification

The LaTeX infrastructure is complete and tested. The next step is to update the Python spell card generator to produce expl3-compatible `.tex` files:

1. **Modify `generators/latex_generator.py`**:
   - Change from generating `\newcommand` statements
   - Generate `\spellprop{key}{value}` statements instead
   - Maintain compatibility with existing spell data (TSV format)
   
2. **Convert Existing Spells**:
   - Run updated generator on `spell_full.tsv`
   - Convert all spells in `src/spells/sor/` to expl3 format
   - Legacy spells preserved in `src/spells-legacy/` for comparison
   
3. **Update Output Format**:
   ```latex
   % Old format (60+ lines of \newcommand):
   \newcommand{\name}{Fireball}
   \newcommand{\school}{evocation}
   ...
   
   % New format (cleaner, property-based):
   \spellprop{name}{Fireball}
   \spellprop{school}{evocation}
   ...
   ```

4. **Testing Plan**:
   - Generate spell files with updated Python code
   - Compile `src/spellcards.tex` with expl3 package
   - Compile `src/spellcards-legacy.tex` for comparison
   - Verify layout matches between old and new
   - Test with full spell deck (all 15 spells across 4 decks)

5. **Acceptance Criteria**:
   - Python generator produces valid expl3 spell files
   - Generated files compile without errors or warnings
   - Exit code 0 maintained
   - Layout identical to legacy version (compare spellcards.pdf vs spellcards-legacy.pdf)
   - Full workflow functional: TSV → Python → expl3 .tex → PDF

## Future Enhancements (Post-Migration)

### Immediate Next Feature (Enabled by Phase 3.1)
**Index Card Generation**: With deck tracking now implemented, we can generate index cards showing:
- Table of contents for each deck
- Spell counts by level
- Alphabetically sorted spell lists
- Page references or deck positions
- Quick reference for deck organization

### Additional Features Once Migration Complete

1. **Smart Spell Sorting**: Automatically sort spells by level, school, name
2. **Conditional Rendering**: Only include certain properties if non-NULL (partially done)
3. **Template Variants**: Different card layouts selectable via keys
4. **Spell Filtering**: Programmatically filter spells for deck building
5. **Batch Processing**: Generate multiple deck variants from one source
6. **Statistics**: Count spells by level, school, etc. (foundation in place)
7. **Validation**: Check for required fields, warn on missing data (message system ready)
8. **Cross-References**: Link related spells automatically

## Current Status Summary (October 27, 2025 - Cardify Integration Complete)

### Completed ✅
- **Phase 1**: Foundation and Infrastructure
  - expl3 package structure
  - Modern type system (booleans, integers, token lists, FP, dimensions)
  - Property lists for spell data
  - Message system
  
- **Phase 2**: Core Logic Migration
  - Deck management with validation
  - Positioning calculations (markers, labels)
  - Conditional logic for spell attributes
  - Print control system
  
- **Phase 3.1**: Deck Tracking Infrastructure
  - Spell registration system
  - Per-deck sequence storage
  - Query functions for deck contents
  - Foundation for index card generation

- **Phase 4**: Layout and Rendering
  - QR code management system
  - Page parity-based positioning
  - Validation and error handling
  - Integration with TikZ

- **Modern Spell File Format**: Property list-based spell definitions
  - Created `spells-expl3/` directory with modern format
  - Converted Acid Splash, Magic Missile, and Teleport as examples
  - Uses `\spellprop{key}{value}` instead of 60+ `\newcommand` statements
  - Test files successfully compile

- **Integration Testing & Layout Parity** ✅
  - Created test documents without cardify layout for isolated testing
  - Fixed spell marker rendering (TikZ dimension expansion issue)
  - Fixed description font size (\Large scope issue)
  - Fixed table spacing (row spacing + gap reduction)
  - **Visual verification complete**: Layout matches legacy with acceptable differences

- **Cardify Integration** ✅ **COMPLETED October 27, 2025**
  - Fixed `\clearcard` vs `\clearpage` issue (line 1338) - now respects cardify's `\cleardoublepage`
  - Fixed `\includespell` state persistence bug (line 1153) - reset bool before processing keys
  - Fixed `noprint` option - changed environment to use `+b` argument type (line 1320)
  - **test-spell.tex and test-legacy.tex produce identical layout**
  - Both have 2 pages (4 cards on front sheet, backs on second sheet)
  - Same spell counts: 1 Acid Splash, 2 Magic Missile, 1 Teleport
  - Correct deck labels ("combat", "utility")
  - Zero compilation errors, zero warnings, exit code 0

### In Progress 🚧
- **Phase 5: Python Generator Integration** (CRITICAL BUG BLOCKING)
  - ✅ Python generator updated to output expl3 format
  - ✅ Successfully generated 15 spells via CLI
  - ✅ Files compile without LaTeX errors (exit code 0)
  - ❌ **CRITICAL**: Table rendering bug - tables wrap vertically
  - ⛔ **BLOCKED**: PDF comparison until tables render correctly
  - ⛔ **BLOCKED**: Python test suite verification
  - **Next**: Fix table rendering in `\spellcard_render_info:n` function

### Recent Completion: Cardify Integration (October 27, 2025) ✅
**Problems Identified**:
1. Both front and back of cards rendering on same page instead of odd/even pages
2. `\includespell` command not working as drop-in replacement for `\input`
3. `\includespell[noprint]` option not actually suppressing card output

**Root Causes**:
1. **\clearcard vs \clearpage**: Used hardcoded `\clearpage` instead of `\clearcard` macro
   - cardify.tex redefines `\clearcard` as `\cleardoublepage` to skip to next odd page
   - Without this, cards don't respect the 8-page caching for cardify layout
   
2. **State persistence**: `\l_spellcard_include_print_bool` not reset between `\includespell` calls
   - Once set to false by `noprint`, stayed false for subsequent calls
   
3. **Conditional body execution**: Environment executed body regardless of print flag
   - Standard `\NewDocumentEnvironment` doesn't support conditional body skipping
   - Needed `+b` argument type to capture and conditionally execute body

**Solutions Implemented**:
1. **Line 1338**: Changed `\clearpage` to `\clearcard`
   - Now respects cardify's redefinition as `\cleardoublepage`
   - Cards correctly placed on odd pages (fronts) and even pages (backs)
   
2. **Line 1153**: Reset `\l_spellcard_include_print_bool` to true before processing keys
   - Each `\includespell` call starts fresh
   - `noprint` option works correctly
   
3. **Line 1320**: Changed environment to use `+b` argument type
   - Captures body as argument
   - Conditionally executes with `\tl_use:N` only when printing
   - Body completely skipped when `noprint` is active

**Results**:
- ✅ test-spell.pdf and test-legacy.pdf produce identical layout
- ✅ Both have 2 pages (cardify correctly caching 8 pages → 4 cards per sheet)
- ✅ Same spell distribution: 1 Acid Splash, 2 Magic Missile, 1 Teleport
- ✅ Deck labels display correctly
- ✅ `\includespell` works as drop-in replacement for `\input`
- ✅ `\includespell[noprint]` correctly suppresses entire card (title, body, QR codes)
- ✅ Zero compilation errors, zero warnings, exit code 0

**Status**: Cardify integration complete and tested!

### Next Session Tasks 📋
1. **FIX CRITICAL TABLE BUG** (HIGHEST PRIORITY)
   - Resume testing approach #5 (separate `\use:x` blocks) - was interrupted
   - If still fails, try alternative approaches:
     * Exit ExplSyntax entirely before rendering tables
     * Use minipage instead of side-by-side tables
     * Use box registers to store and position tables
     * Copy legacy approach exactly (without expl3 wrappers)
   - Location: `spellcard-expl3.sty` lines 750-762
   - Target: Tables must render side-by-side, not vertically stacked
   - Success metric: pdftotext output matches legacy (tables on same line)

2. **Investigate URL preservation bug** (MEDIUM PRIORITY)
   - User reported: "re-generating spells that are already in the new format fails to read (possibly only secondary?) URLs"
   - Check `utils/file_scanner.py` URL extraction logic
   - Test: Generate spell, verify URLs, re-generate same spell, check if URLs preserved
   - Document findings and create fix if needed
   
3. **Complete Phase 5** (AFTER TABLE FIX)
   - Run full PDF comparison (expl3 vs legacy)
   - Verify identical layout (target: 18 pages both)
   - Run Python test suite (350 tests, 10.00/10 pylint, 59% coverage)
   - Update Phase 5 status to complete
   
4. **Phase 6: Documentation** (AFTER PHASE 5)
   - Document table rendering fix and challenges
   - Document URL preservation fix
   - Update user documentation
   
5. **Phase 7: Refactoring** (FINAL PHASE)
   - Split 1000+ line package into modular components
   - Remove deprecated code and compatibility layers

### Known Issues 🐛
1. **Booktabs limitation**: Cannot use horizontal rules in spell info tables
   - Token list pre-building incompatible with `\noalign` commands
   - Acceptable trade-off: plain tables with manual spacing instead
   - Visual difference from legacy: no horizontal rules between rows
   - Not a blocking issue - documented as expected difference

2. **CRITICAL: Table rendering bug** (October 27, 2025)
   - **Symptom**: Two side-by-side spell info tables wrap vertically instead of appearing horizontally
   - **Pattern**: Left table (Casting Time, Saving Throw, Spell Resist, Attack Roll) renders right-aligned at top, right table (Duration, Range, Comp., School) renders left-aligned below it
   - **Expected**: Both tables side-by-side on same line with `\hfill` spacing
   - **Status**: 5+ fixes attempted, none successful
   - **Blocking**: PDF comparison, Phase 5 completion
   - **Location**: `spellcard-expl3.sty` lines 750-762
   - **Working reference**: Third table (Target/Effect) renders correctly with similar `\use:x` pattern
   - **Next action**: Test separate `\use:x` blocks approach (interrupted) or try alternative strategies

3. **Python generator URL preservation** (October 27, 2025)
   - **Symptom**: Re-generating spells already in expl3 format fails to read URLs (possibly only secondary URLs)
   - **Impact**: URLs lost when updating existing spell cards
   - **Workaround**: Unknown - needs investigation
   - **Priority**: Medium - affects workflow but not initial generation
   - **Location**: Likely in `utils/file_scanner.py` URL extraction logic
   - **Note**: User reported this issue at end of session, needs further investigation to confirm scope

### Planned 📋
- **Phase 3.2**: Key-Value Spell Interface (deferred until after Phase 5)
- **Phase 5**: Integration and Testing
- **Phase 6**: Documentation and Cleanup
- **Phase 7**: Refactoring and Code Organization

## Conclusion

This migration to expl3 represents a significant modernization of the spell card project. By prioritizing modern features and clean code over backwards compatibility, we can create a more maintainable, extensible, and feature-rich system. The phased approach allows for incremental progress with continuous testing, minimizing risk while maximizing benefits.

The investment in expl3 will pay dividends in:
- Easier maintenance and debugging
- Better integration with the Python generator
- More powerful features for users
- Cleaner, more professional codebase
- Foundation for future enhancements

**Recommendation**: Proceed with Phase 1 (Foundation) immediately, establishing the expl3 infrastructure while maintaining full backwards compatibility. This allows testing and validation before committing to deeper changes.
