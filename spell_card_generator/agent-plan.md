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

2. **Linting and Type Checking**
   - Run linting tools (flake8, pylint, black) to ensure compliance
   - Add type hints to remaining functions
   - Set up mypy for type checking
   - Address any linting or type errors

3. Bug hunting and fixing
  - test the workflows thoroughly
  - review generated cards
  - fix any issues that arise:
    - description is not preserved
    - I don't think the secondary URL was preserved either, despite having been validated (probably not isnerted into the template)
    - compared to the previous generation with convert.sh, there are no explicit "NULL" values anymore. Do we need those, or just keep them empty?
    - compared to convert.sh, the spell resistance and saving throw modifications are not recreated (emphasizing "no"/"none" respectively)
    - `\spellcardqr{\urlsecondary}` needs to be uncommented if we do have that URL. Similarly, comment the primary one if that is missing. Maybe modify the \spellcardqr command to not do anything if there is no value given... Might actually already happen!

4. Add more functionality
  - select all spells that already have a card to be re-generated
  - provide buttons to open the generated file for each spell so they can be adjusted (manual adjustments are an expected part of the workflow!)
  - offer to add the `\input`  startements for new cards to the appropriate tex file (might have to gneerate that if missing...), and/or to open that file.

---

**Focus:**
- The main workflow is now complete! All steps are implemented and functional.
- Next priority: Ensure code quality through linting and type checking.
- This plan should be updated as new priorities emerge or tasks are completed.
