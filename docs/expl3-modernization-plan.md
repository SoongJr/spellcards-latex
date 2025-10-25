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

#### 3.1 Sequence-Based Spell Lists
Use sequences instead of manual file inclusion:

```latex
% Define sequence for spell list
\seq_new:N \g_spellcard_spell_list_seq

% Add spells to sequence
\seq_gput_right:Nn \g_spellcard_spell_list_seq 
  { spells/sor/0/Acid~Splash }

% Process all spells
\seq_map_inline:Nn \g_spellcard_spell_list_seq
  {
    \bool_if:NTF \g_spellcard_print_card_bool
      { \input { #1 } }
      { \spellcard_noprint:n { #1 } }
  }
```

**Benefits**:
- Programmatic spell list manipulation
- Easy filtering and sorting
- Can implement search/filter functions
- Better integration with Python generator

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

### Week 1-2: Foundation (Phase 1)
- [ ] Create `spellcard-expl3.sty` package
- [ ] Define all expl3 variables and data structures
- [ ] Set up property lists for spell data
- [ ] Create test document to verify compilation

### Week 3-4: Core Migration (Phase 2)
- [ ] Migrate deck management system
- [ ] Convert positioning calculations to expl3 FP
- [ ] Replace all ifthen conditionals
- [ ] Implement message system
- [ ] Test with existing spell cards

### Week 5: Advanced Features (Phase 3)
- [ ] Implement key-value spell interface
- [ ] Create sequence-based spell lists
- [ ] Add validation and defaults
- [ ] Update one spell file to test new interface

### Week 6: Layout (Phase 4)
- [ ] Migrate dimension calculations
- [ ] Refactor marker/label positioning
- [ ] Improve QR code system
- [ ] Test layout with cardify

### Week 7: Integration (Phase 5)
- [ ] Create compatibility layer
- [ ] Run comprehensive tests
- [ ] Update Python generator
- [ ] Fix any compilation issues

### Week 8: Documentation (Phase 6)
- [ ] Document all expl3 functions
- [ ] Update user documentation
- [ ] Create migration guide
- [ ] Final cleanup and optimization

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
- ✅ chktex passes without warnings
- ✅ Compilation time same or faster
- ✅ Code is more readable and maintainable
- ✅ Python generator produces valid expl3 code
- ✅ Error messages are clearer and more helpful
- ✅ New features (key-value interface) are documented and working

## Future Enhancements (Post-Migration)

Once expl3 migration is complete, these features become possible:

1. **Smart Spell Sorting**: Automatically sort spells by level, school, name
2. **Conditional Rendering**: Only include certain properties if non-NULL
3. **Template Variants**: Different card layouts selectable via keys
4. **Spell Filtering**: Programmatically filter spells for deck building
5. **Batch Processing**: Generate multiple deck variants from one source
6. **Statistics**: Count spells by level, school, etc.
7. **Validation**: Check for required fields, warn on missing data
8. **Cross-References**: Link related spells automatically

## Conclusion

This migration to expl3 represents a significant modernization of the spell card project. By prioritizing modern features and clean code over backwards compatibility, we can create a more maintainable, extensible, and feature-rich system. The phased approach allows for incremental progress with continuous testing, minimizing risk while maximizing benefits.

The investment in expl3 will pay dividends in:
- Easier maintenance and debugging
- Better integration with the Python generator
- More powerful features for users
- Cleaner, more professional codebase
- Foundation for future enhancements

**Recommendation**: Proceed with Phase 1 (Foundation) immediately, establishing the expl3 infrastructure while maintaining full backwards compatibility. This allows testing and validation before committing to deeper changes.
