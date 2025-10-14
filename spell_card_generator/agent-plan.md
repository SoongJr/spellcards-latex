# Refactoring Plan for `spell_card_generator`

## Goals
- Maintain code quality, readability, and maintainability
- Ensure compliance with flake8, black, and pylint
- Organize code structure and naming
- Remove dead code and unused imports
- Add/Improve docstrings and type hints
- Ensure all code passes linting and formatting checks

## Remaining Steps & Priorities

1. **Sidebar Workflow Completion**
   - Finalize Documentation & Language URLs step (per-spell English and secondary language URL inputs)
   - Complete Preview & Generate step (comprehensive summary and generation)
   - Polish UI transitions and animations
   - Integrate advanced input feedback (URL validation, tooltips, help icons)

2. **Testing and Validation**
   - Ensure all existing tests pass
   - Add/Update tests for refactored code
   - Run linting and formatting tools to confirm compliance
   - Add typechecking with mypy

3. **Code Coverage and Testing Setup**
   - Add pytest and coverage.py to pyproject.toml dependencies
   - Create tests/ directory structure
   - Set up pytest configuration and coverage settings
   - Priority test areas: data loading, spell filtering, LaTeX generation
   - Create mock data for testing UI components
   - Measure code coverage and document results
   - Identify and prioritize untested code for new tests

4. **Configuration and Dependency Management**
   - Review and update pyproject.toml (add missing dev dependencies)
   - Standardize configuration loading patterns
   - Review requirements.txt vs pyproject.toml consistency

5. **Documentation Update**
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
- Complete sidebar workflow steps and polish UI
- Expand and improve test coverage
- Finalize configuration and documentation
- Address any remaining technical debt

---

**Focus:**
- Only actionable, forward-looking tasks are listed above.
- Completed steps and results have been removed for clarity.
- This plan should be updated as new priorities emerge or tasks are completed.
