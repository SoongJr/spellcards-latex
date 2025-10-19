# Refactoring Plan for `spell_card_generator`

1. **Sidebar Workflow Completion** ✅ *COMPLETED*
   - ✅ Class Selection step (single class selection with validation)
   - ✅ Spell Selection step (searchable table with filtering)
   - ✅ Overwrite Cards step (conflict resolution with bulk actions)
   - ✅ Documentation URLs step (per-spell primary and secondary URL configuration with validation)
     - **Features implemented:**
       - Primary URL: Auto-generated d20pfsrd.com links, editable, with reset button
       - Secondary URL: Optional, with "Guess URLs" dialog for German 5footstep.de pattern
       - URL validation: HTTP HEAD requests with User-Agent header to avoid bot detection
       - Visual feedback: Colored text with Unicode symbols (✓ green valid, ○ orange unvalidated, ✗ red invalid)
       - Per-URL actions: "R" reset button, "V" visit button to open in browser
       - Bulk actions: Reset all primary URLs, Guess all secondary URLs
       - Non-ASCII support: Proper URL encoding for German umlauts (ä, ö, ü)
       - Anti-bot measures: User-Agent header required for d20pfsrd.com validation
   - ✅ Preview & Generate step (comprehensive summary and generation)
     - **Features implemented:**
       - Comprehensive summary display with formatted sections
       - Character class display
       - Selected spells grouped by level with count
       - File conflicts and overwrite decisions summary
       - Preservation options display
       - Documentation URLs configuration summary
       - Generation options summary
       - Ready status indicator with missing requirements
       - Generate button with enabled/disabled state based on workflow completeness
       - Refresh summary button for manual updates
       - Automatic refresh on workflow state changes
       - Tagged text formatting (headings, bullet points, colors)

2. **Linting and Type Checking** ✅ *COMPLETED*
   - ✅ Run linting tools (pylint, black) to ensure compliance
     - **Pylint score: 10.00/10** maintained across all files
     - **Black formatting** enforced and compliant
   - ✅ Add type hints to remaining functions
     - All function parameters and return values have type hints
     - Used `Optional[]` for None defaults
     - Applied proper exception chaining patterns
   - ✅ Set up mypy for type checking
     - **mypy 1.18.2** configured with strict settings:
       - `check_untyped_defs = true`
       - `no_implicit_optional = true`
     - **0 errors** in all 58 source files (36 production + 22 tests)
   - ✅ Address any linting or type errors
     - Production code: Strategic `# type: ignore` comments for tkinter stub limitations
     - Test code: Assertions for Optional types, type ignores for mock assignments
     - All 241 tests passing (100% pass rate)
     - 58% test coverage maintained

3. **Bug Hunting and Fixing** ✅ *COMPLETED*
   - ✅ **Description preservation**: Added extraction logic to FileScanner and integrated into LaTeXGenerator
   - ✅ **Secondary URL preservation**: Extended preservation logic to extract and reuse URLs from existing files
   - ✅ **NULL value handling**: Changed to output "NULL" for empty fields (matching legacy convert.sh behavior)
   - ✅ **Saving throw & spell resistance formatting**: Updated to use `\textbf{none}` and `\textbf{no}` (matching legacy)
   - ✅ **QR code conditional commenting**: Implemented conditional commenting based on URL presence
   - ✅ **Next button removal**: Removed Next button from final step (Preview & Generate at index 4)
   - ✅ **Description marker consolidation**: 
     - Standardized on `% SPELL DESCRIPTION BEGIN` / `% SPELL DESCRIPTION END` markers
     - Updated FileScanner to handle both old and new formats (backward compatible)
     - Migrated all 46 existing spell card files to use new markers

4. **Add more functionality** 🔄 *IN PROGRESS*

   ### 4.1 "Select All Existing Cards" Feature ✅ *COMPLETED*
   
   **Goal:** Allow users to quickly select all spells that already have generated .tex files for regeneration, respecting the current class selection and active filters.
   
   **Use Cases:**
   1. **Template update**: User modified LaTeX template, wants to regenerate all cards while preserving customizations (Description/URLs)
   2. **Database update**: TSV was updated, user wants to regenerate cards with new data (optionally preserving URLs)
   3. **Selective regeneration**: User filters to "Level 3 spells" and regenerates only those existing cards
   
   **Design Principles:**
   - Maintain single-class workflow (select class first)
   - Respect existing UI filters (level, source, search term)
   - Simple button - user manually chooses preservation options in Overwrite Cards step
   
   **Implementation Completed:**
   
   1. ✅ **Added `PathConfig` utility module**
      - Created `utils/paths.py` to centralize path management
      - Resolves circular import between FileScanner ↔ LaTeXGenerator
      - Methods: `get_output_base_path()`, `get_spells_output_dir()`, `get_class_spells_dir()`
   
   2. ✅ **Added `FileScanner.find_all_existing_cards()` utility method**
      - Signature: `find_all_existing_cards(spell_dataframe, class_name, level_filter, source_filter, search_term)`
      - Scans `src/spells/{class_name}/**/*.tex` for the specified class only
      - Applies same filters as spell selection UI (level, source, search)
      - Matches filenames to spell database using sanitized name matching
      - Returns `List[Tuple[str, str, pd.Series]]` (class_name, spell_name, spell_data)
      - Example: For class="wizard", level="3", finds only existing Level 3 wizard cards
      - **Important:** Uses `SpellDataLoader.spells_df` attribute (not `spell_data`)
   
   3. ✅ **Added "Select Existing" button to Spell Selection step**
      - **Location:** In `spell_tabs.py` buttons frame, between "Select All" and "Deselect All" buttons
      - Button text: `"Select\nExisting"` (multi-line to fit space)
      - Only functional when a class is selected (reads from `workflow_state.selected_class`)
      - Reads current filters from `workflow_state.spell_filter_state`
      - Calls `FileScanner.find_all_existing_cards()` with class + filters
      - Updates spell selection checkboxes via tree view item IDs
      - Shows status message: "Selected X existing cards" or "No existing cards found"
   
   4. ✅ **UI improvements**
      - Increased window size by 10%: `900x600` → `990x660` (in `app.py`)
      - Button positioned for optimal workflow (grouped with selection actions)
      - Multi-line text accommodates space constraints
   
   5. ✅ **Test coverage**
      - Created `tests/test_file_scanner_find_existing.py` with 12 comprehensive tests
      - Added 6 special character tests to `tests/test_latex_generator.py` (commas, apostrophes, spaces)
      - Total: 278 tests passing, all green
      - Coverage: 58% maintained
      - **Verified:**
        - Class filter works (only scans specified class directory)
        - Level filter respected (only loads cards of filtered level)
        - Source filter respected
        - Search term filter respected (case-insensitive)
        - Combined filters work together
        - Filename matching handles special characters (spaces, commas, apostrophes)
        - Non-existent directories handled gracefully
        - Invalid filenames ignored
   
   6. ✅ **Code quality maintained**
      - Pylint: 10.00/10 score
      - mypy: 0 errors
      - Black: Properly formatted
      - All 278 tests passing
   
   **Workflow Example:**
   1. User selects "Wizard" class in Class Selection step
   2. User navigates to Spell Selection step
   3. User sets filter to "Level: 3" (optional)
   4. User clicks **"Select\nExisting"** button (between "Select All" and "Deselect All")
   5. All existing Level 3 wizard spell cards are auto-selected in the table
   6. User proceeds to Overwrite Cards step
   7. User manually chooses preservation options (Description ✓, URLs ✓) per existing UI
   8. Cards are regenerated with chosen preservation settings
   
   **Remaining Work:**
   - ⏳ UI integration tests for button functionality
   
   **Verified via Manual Testing:**
   - ✅ Button appears correctly after class selection
   - ✅ Button positioned between "Select All" and "Deselect All"
   - ✅ Various filter combinations work as expected
   - ✅ Spell checkboxes update correctly
   - ✅ Proceeding to Overwrite Cards step works
   - ✅ Preservation options function as expected
   - ✅ Real spell data tested successfully
   
   **Technical Notes for Next Session:**
   - Button implementation is in `spell_tabs.py` (not `spell_selection_step.py`)
   - Method: `SpellTabManager._select_existing_cards(class_name: str)`
   - Uses `self.data_loader.spells_df` to access spell data (DataFrame attribute)
   - Tree view selection updated via `tree.set()` with item IDs from `_spell_items` dict
   - Filenames preserve spaces, commas, apostrophes (only sanitize `<>:"/\|?*`)

   ### 4.2 "Preserve Properties & Customizations" Feature ✅ *COMPLETED*
   
   **Goal:** Preserve user customizations in existing spell cards when regenerating, including modified property values and LaTeX formatting overrides.
   
   **Status:** Both Phase 1 (Width Ratio) and Phase 2 (Property Preservation) are complete and tested.
   
   **Problem Statement:**
   Users may manually customize spell cards after generation:
   - Correct errors in TSV data (e.g., wrong range, incorrect components)
   - Adjust formatting (e.g., `\spellcardinfo[0.55]{}` width ratio for long text)
   - Fine-tune property values for specific use cases
   - Currently: Regeneration overwrites ALL customizations (except Description/URLs)
   - Needed: Selective preservation of user modifications
   
   **Design Approaches Analysis:**
   
   | Approach | Pros | Cons | Complexity |
   |----------|------|------|------------|
   | **A: Extract & preserve all properties** | • Complete preservation<br>• No template changes | • Hard to distinguish intentional edits from TSV updates<br>• All-or-nothing per spell | Medium |
   | **B: Modified properties section** | • Clear separation of customizations<br>• Easy to identify user changes<br>• Survives regeneration automatically | • Requires template modification<br>• Users must manually move customizations | Low |
   | **C: Width ratio preservation** | • Solves most common customization<br>• Simple to implement<br>• No template changes | • Only handles one specific case<br>• Doesn't address property value changes | Very Low |
   
   **Recommended Solution: Hybrid Approach (B + C)**
   
   Combine approaches B and C for maximum benefit:
   1. **Width ratio preservation** (Approach C) - implement immediately as it's simple and common
   2. **Modified properties section** (Approach B) - update template and generator to support overrides
   
   This provides:
   - ✅ Immediate value (width ratio preservation)
   - ✅ Future-proof solution (property override section)
   - ✅ Clear user intent (explicit override section)
   - ✅ Maintainable code (no complex extraction logic)
   
   **Implementation Plan:**
   
   **Phase 1: Width Ratio Preservation (Quick Win)** ✅ *COMPLETED*
   
   1. ✅ **Updated `FileScanner.analyze_existing_card()`**
      - Added extraction pattern for `\spellcardinfo[RATIO]{}` format
      - Returns `width_ratio: Optional[str]` in analysis dict
      - Handles both `\spellcardinfo{}` (default) and `\spellcardinfo[0.55]{}` (custom) formats
      - Tested with various ratio values (0.50, 0.55, 0.60, etc.)
   
   2. ✅ **Updated `LaTeXGenerator._generate_latex_template()`**
      - Added `preserved_width_ratio: Optional[str] = None` parameter
      - Generates `\spellcardinfo[RATIO]{}` if ratio provided, else `\spellcardinfo{}`
      - Passes through from `generate_spell_latex()` → `_generate_latex_template()`
   
   3. ✅ **Updated `LaTeXGenerator.generate_cards()`**
      - Extracts width ratio from existing cards when overwriting
      - Passes to `generate_spell_latex()` alongside preserved description/URLs
      - Applies automatically when `overwrite=True` (no UI needed)
   
   4. ✅ **Added test coverage**
      - Created `tests/test_width_ratio_preservation.py` with 10 tests
      - Tests extraction of various width ratios
      - Tests generation with custom ratio
      - Tests preservation during regeneration
      - Tests fallback to default when no custom ratio exists
      - All tests passing (301 total)
   
   **Phase 2: Property Value Preservation with Original Tracking** ✅ *COMPLETED*
   
   1. ✅ **Updated `FileScanner.extract_properties()`**
      - New method to extract all `\newcommand{...}{...}` property definitions
      - Parses property name, current value, and `% original:` comment if present
      - Returns: `Dict[str, Tuple[str, Optional[str]]]` format: `{property_name: (current_value, original_comment)}`
      - Handles both formats: with and without `% original:` comment
      - Preserves exact LaTeX formatting and escaping
      - Created `tests/test_property_extraction.py` with 13 comprehensive tests
   
   2. ✅ **Updated `LaTeXGenerator._generate_latex_template()`**
      - Added `preserved_properties: Optional[Dict[str, Tuple[str, Optional[str]]]] = None` parameter
      - Added `conflicts: List[PropertyConflict]` return value for conflict tracking
      - Implemented 4-case decision logic:
        - **Case 1:** Unmodified (user == DB) → No comment
        - **Case 2:** No marker (no original comment) → Use DB value
        - **Case 3:** User modified, DB stable (original == DB) → Preserve user value with comment
        - **Case 4:** CONFLICT (original ≠ DB, user modified) → Preserve user value, update comment, track conflict
   
   3. ✅ **Created `PropertyConflict` NamedTuple**
      - Tracks conflicts: `(spell_name, property_name, old_db_value, new_db_value)`
      - Returned from generation methods for user notification
      - Logged in generation results (non-blocking)
   
   4. ✅ **Updated `LaTeXGenerator.generate_cards()`**
      - Always extracts properties from existing cards when overwriting
      - Passes to `generate_spell_latex()` → `_generate_latex_template()`
      - Collects conflicts from all generated cards
      - Returns: `Tuple[List[str], List[str], List[PropertyConflict]]`
      - Automatic preservation - no UI changes needed
   
   5. ✅ **Fixed TSV column name bug**
      - **Problem:** TSV columns use underscores (`casting_time`) but LaTeX properties don't (`castingtime`)
      - **Root cause:** Properties were being emptied because column lookup failed
      - **Solution:** Modified `SpellDataLoader.load_data()` to remove underscores from column names during loading
      - **Benefit:** Cleaner code - no need for 70+ line mapping dictionary
      - **Command:** `self.spells_df.columns = self.spells_df.columns.str.replace("_", "")`
   
   6. ✅ **Refactored with `PreservationOptions` dataclass**
      - **Problem:** Adding `preserve_properties` parameter would violate pylint's too-many-arguments rule
      - **Solution:** Created `PreservationOptions` dataclass to encapsulate all preservation settings
      - **Benefits:**
        - Reduced `generate_cards()` from 9 parameters to 5
        - Groups related preservation settings logically
        - Easier to extend in the future
        - Better code organization
      - **Structure:**
        ```python
        @dataclass
        class PreservationOptions:
            preserve_description: Dict[str, bool] = field(default_factory=dict)
            preserve_urls: Dict[str, bool] = field(default_factory=dict)
            url_configuration: Dict[str, Tuple[Optional[str], Optional[str]]] = field(default_factory=dict)
            preserve_properties: bool = True  # Global toggle
        ```
   
   7. ✅ **Added global UI toggle**
      - Added "Preserve modified properties (global)" checkbox to Overwrite Cards step
      - Located in Row 3 of bulk actions frame (after URLs row)
      - Default state: ✅ Enabled (preserve_properties=True)
      - Updates `workflow_state.preserve_properties` in real-time
      - When disabled: All properties use fresh database values (no preservation, no comments)
      - When enabled: 4-case decision logic applies
   
   8. ✅ **Updated app.py integration**
      - Constructs `PreservationOptions` from `workflow_state`
      - Passes to `LaTeXGenerator.generate_cards()`
      - Displays conflict count in results dialog if any detected
   
   9. ✅ **Added comprehensive test coverage**
      - **Property extraction tests:** 13 tests covering all edge cases
      - **Width ratio tests:** 10 tests for extraction and generation
      - **All 301 tests passing** (100% pass rate maintained)
      - **Coverage: 59%** (increased from 58%)
      - **Pylint: 10.00/10** (perfect score maintained)
      - Tested all 4 decision cases
      - Tested special characters and complex values
      - Tested custom properties (preserved as-is)
      - Tested new properties (added normally)
   
   10. ✅ **Updated documentation**
       - Added comprehensive "Property Preservation Feature" section to main project README
       - Documented the critical `% original:` comment requirement with warnings
       - Included examples showing correct vs. incorrect usage
       - Added workflow examples and best practices
       - Linked detailed documentation from main README to spell_card_generator README
   
   **Manual Testing Results:** ✅ *VERIFIED*
   - ✅ Checkbox appears correctly in Overwrite Cards step
   - ✅ Properties preserved when checkbox enabled (with `% original:` comments)
   - ✅ Properties NOT preserved when checkbox disabled (DB values only)
   - ✅ State persists across step navigation
   - ✅ Git diff shows expected behavior
   - ✅ Width ratio preservation working automatically
   
   **Implementation Summary:**
   - **Total changes:** 9 files modified, 1 new test file created
   - **Code quality:** 10.00/10 pylint score maintained
   - **Test coverage:** 59% (301 tests passing)
   - **Lines of code:** ~500 lines added (including tests and docs)
   - **Implementation time:** Completed over multiple sessions
   - **Key innovation:** `PreservationOptions` dataclass for cleaner API design
   
   **Files Modified:**
   - `data/loader.py` - Column name transformation
   - `generators/latex_generator.py` - PropertyConflict NamedTuple, PreservationOptions dataclass, 4-case logic
   - `ui/workflow_state.py` - Added preserve_properties flag
   - `ui/workflow_steps/overwrite_cards_step.py` - Added global checkbox
   - `app.py` - PreservationOptions integration
   - `utils/file_scanner.py` - Property extraction logic
   - `tests/test_property_extraction.py` - NEW: 13 comprehensive tests
   - `tests/test_width_ratio_preservation.py` - 10 tests
   - `tests/test_latex_generator.py` - Updated for new signatures
   - `README.md` - Property preservation documentation
   
   **User Documentation:**
   - ✅ Main README updated with overview and critical warnings
   - ✅ Detailed workflow examples and best practices documented
   - ✅ 4-case decision logic explained with examples
   - ✅ Emphasis on `% original:` comment requirement
   - ✅ Examples of correct vs. incorrect usage
   
   **Phase 3: UI Enhancement** ⏳ *DEFERRED*
   
   Optional visual indicators in Overwrite Cards step showing which cards have customizations.
   - Deferred - current functionality is complete and sufficient
   - Can be added later if user feedback indicates it would be helpful

   ### 4.3 Other Functionality (TODO)
   - Provide buttons to open the generated file for each spell so they can be adjusted
   - Offer to add the `\input` statements for new cards to the appropriate tex file

---

**Current Status:**
- ✅ **Main workflow complete:** All 6 steps implemented and functional
- ✅ **Code quality achieved:** Pylint 10.00/10, mypy 0 errors, Black compliant
- ✅ **Test coverage:** 301 tests passing, 59% coverage
- ✅ **Application verified:** GUI launches and runs without exceptions
- ✅ **"Select Existing Cards" feature complete:** Button functional with comprehensive testing
- ✅ **"Preserve Properties & Customizations" feature complete:** 
  - Phase 1 (Width Ratio Preservation) ✅
  - Phase 2 (Property Value Preservation with Conflict Detection) ✅
  - Global UI toggle for property preservation ✅
  - Comprehensive documentation in README ✅
  - All tests passing (301/301) ✅
  - `PreservationOptions` dataclass for clean API design ✅

**Next Priority:** Item #4.3 - Other Functionality
- Provide buttons to open generated files for editing
- Offer to add `\input` statements for new cards to appropriate .tex files
- This plan should be updated as new priorities emerge or tasks are completed.
