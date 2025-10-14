# Refactoring Plan for `spell_card_generator`

## G3. **Code Coverage and Testing Setup** ✅ *COMPLETED*
   - ✅ Added pytest and coverage.py to pyproject.toml dependencies
   - ✅ Created tests/ directory structure with proper organization
   - ✅ Set up pytest configuration and coverage settings
   - ✅ Priority test areas completed: data loading, spell filtering, LaTeX generation
   - ✅ Created mock data fixtures for testing
   - ✅ Measured code coverage and documented results (28% overall, 93-100% for core modules)
   - ✅ HTML coverage reports generated (see `htmlcov/` directory)
   - 🔜 Identify and prioritize untested code for new tests (focus on UI modules)

4. **Linting and Type Checking** 🔜 *NEXT*
   - Run linting tools (flake8, pylint, black) to ensure compliance
   - Add type hints to remaining functions
   - Set up mypy for type checking
   - Address any linting or type errorsntain code quality, readability, and maintainability
- Ensure compliance with flake8, black, and pylint
- Organize code structure and naming
- Remove dead code and unused imports
- Add/Improve docstrings and type hints
- Ensure all code passes linting and formatting checks

## Remaining Steps & Priorities

1. **Sidebar Workflow Completion** ⏸️ *ON HOLD*
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
   - 🔜 Complete Preview & Generate step (comprehensive summary and generation)
   - 🔜 Polish UI transitions and animations

2. **Testing and Validation** ✅ *COMPLETED*
   - ✅ Created comprehensive test suite with pytest
   - ✅ Added pytest, pytest-cov, and pytest-mock dependencies
   - ✅ Created pytest configuration (pytest.ini)
   - ✅ Implemented 102 unit tests with 100% pass rate
   - ✅ Achieved code coverage tracking and reporting
   - **Test Coverage:**
     - Core modules (models, data, generators, utils): 93-100% coverage
     - Overall project coverage: 28% (UI modules not yet tested)
   - **Test Files Created:**
     - `tests/conftest.py`: Shared fixtures and utilities
     - `tests/test_spell.py`: Spell model tests (5 tests)
     - `tests/test_loader.py`: Data loader tests (12 tests)
     - `tests/test_filter.py`: Spell filter tests (20 tests)
     - `tests/test_class_categorization.py`: Class categorization tests (9 tests)
     - `tests/test_validators.py`: Input validation tests (17 tests)
     - `tests/test_exceptions.py`: Exception handling tests (12 tests)
     - `tests/test_latex_generator.py`: LaTeX generation tests (27 tests)
     - `tests/README.md`: Test documentation
   - 🔜 Add UI component tests (requires tkinter mocking)
   - 🔜 Add integration tests for complete workflows

3. **Code Coverage and Testing Setup** ✅ *COMPLETED*
   - Add pytest and coverage.py to pyproject.toml dependencies
   - Create tests/ directory structure
   - Set up pytest configuration and coverage settings
   - Priority test areas: data loading, spell filtering, LaTeX generation
   - Create mock data for testing UI components
   - Measure code coverage and document results
   - Identify and prioritize untested code for new tests

4. **Linting and Type Checking** 🔜 *NEXT*
   - Run linting tools (flake8, pylint, black) to ensure compliance
   - Add type hints to remaining functions
   - Set up mypy for type checking
   - Address any linting or type errors

5. **Configuration and Dependency Management**
   - ✅ Added dev dependencies (pytest, pytest-cov, pytest-mock)
   - Review and update pyproject.toml (add missing dev dependencies like mypy)
   - Standardize configuration loading patterns
   - Review requirements.txt vs pyproject.toml consistency

6. **Documentation Update**
   - ✅ Created comprehensive test documentation (tests/README.md)
   - Update README and code comments as needed
   - Document any major changes in agent-plan.md
   - Add inline documentation for complex algorithms
   - Create developer setup guide additions if needed

## Technical Debt & Refactoring Opportunities
- Review for any remaining cell variable issues in loops (W0640)
- Consider refactoring protected member access patterns in UI (W0212)
- Continue improving type hints and docstring coverage
- Evaluate use of Enums for constants
- Further improve pathlib usage for file handling

## Next Steps
- Resume sidebar workflow completion (step 1 - on hold)
- Run linting and type checking (step 4)
- Expand test coverage to include UI components
- Finalize configuration and documentation
- Address any remaining technical debt

## Recent Progress (2024)
- ✅ **Step 2 Completed**: Created comprehensive test suite
  - 102 unit tests covering core modules
  - 100% test pass rate
  - 93-100% coverage for tested modules (models, data, generators, utils)
  - Proper test infrastructure with pytest, fixtures, and coverage reporting
  - Test documentation created

---

**Focus:**
- Only actionable, forward-looking tasks are listed above.
- Completed steps and results have been removed for clarity.
- This plan should be updated as new priorities emerge or tasks are completed.
