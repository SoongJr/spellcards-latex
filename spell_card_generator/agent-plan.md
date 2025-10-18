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
   
   **Future Enhancement (separate commit):**
   - "Preserve Properties" checkbox: Extract and preserve spell properties (components, range, duration, etc.) from existing .tex files instead of using TSV data. This helps with updating the template or adding new derived properties without overwriting user customizations.
     Alternative: Provide a "modified properties" section before the \spellcardinfo command to override the generated properties. Easier to restore deliberately modified data.
     Consideration: on some cards the \spellcardinfo width ratio is overridden (e.g. `\spellcardinfo[0.55]{}`), which we'll also want to preserve... Maybe add the ratio to the template as a explicit value and we just always keep the value from existing card.
   
   **Technical Notes for Next Session:**
   - Button implementation is in `spell_tabs.py` (not `spell_selection_step.py`)
   - Method: `SpellTabManager._select_existing_cards(class_name: str)`
   - Uses `self.data_loader.spells_df` to access spell data (DataFrame attribute)
   - Tree view selection updated via `tree.set()` with item IDs from `_spell_items` dict
   - Filenames preserve spaces, commas, apostrophes (only sanitize `<>:"/\|?*`)

   ### 4.2 Other Functionality (TODO)
   - Provide buttons to open the generated file for each spell so they can be adjusted
   - Offer to add the `\input` statements for new cards to the appropriate tex file

---

**Current Status:**
- ✅ **Main workflow complete:** All 6 steps implemented and functional
- ✅ **Code quality achieved:** Pylint 10.00/10, mypy 0 errors, Black compliant
- ✅ **Test coverage:** 241 tests passing, 58% coverage
- ✅ **Application verified:** GUI launches and runs without exceptions

**Next Priority:** Add more functionality (item #4)
- Select all spells that already have a card to be re-generated
- Provide buttons to open the generated file for each spell
- Offer to add `\input` statements for new cards to the appropriate tex file
- This plan should be updated as new priorities emerge or tasks are completed.
