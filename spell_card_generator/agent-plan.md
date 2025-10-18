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

3. Bug hunting and fixing
  - test the workflows thoroughly
  - review generated cards
  - fix any issues that arise:
    - description is not preserved
    - I don't think the secondary URL was preserved either, despite having been validated (probably not isnerted into the template)
    - compared to the previous generation with convert.sh, there are no explicit "NULL" values anymore. Do we need those, or just keep them empty?
    - compared to convert.sh, the spell resistance and saving throw modifications are not recreated (emphasizing "no"/"none" respectively)
    - `\spellcardqr{\urlsecondary}` needs to be uncommented if we do have that URL. Similarly, comment the primary one if that is missing. Maybe modify the \spellcardqr command to not do anything if there is no value given... Might actually already happen!
    - After generating the cards, there is a "Next" button that just leads to an empty screen. This button should not exist, that was the last step (as of now)

4. Add more functionality
  - select all spells that already have a card to be re-generated
  - provide buttons to open the generated file for each spell so they can be adjusted (manual adjustments are an expected part of the workflow!)
  - offer to add the `\input`  startements for new cards to the appropriate tex file (might have to gneerate that if missing...), and/or to open that file.

---

**Current Status:**
- ✅ **Main workflow complete:** All 6 steps implemented and functional
- ✅ **Code quality achieved:** Pylint 10.00/10, mypy 0 errors, Black compliant
- ✅ **Test coverage:** 241 tests passing, 58% coverage
- ✅ **Application verified:** GUI launches and runs without exceptions

**Next Priority:** Bug hunting and fixing (item #3)
- Test workflows thoroughly with real data
- Review generated LaTeX cards for quality
- Fix any identified issues with preservation, formatting, and navigation
- This plan should be updated as new priorities emerge or tasks are completed.
