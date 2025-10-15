# GitHub Copilot Instructions

This repository contains two main parts:
1. A LaTeX project to print spell-cards for a Pathfinder 1e character
2. A Python application in folder spell_card_generator to help
   import information from a database to create those cards.

## LaTeX project

The LaTeX project is responsible for generating the actual spell cards in PDF format.
It takes the structured data provided by the Python application
and formats it according to the LaTeX typesetting system.

There are currently no special AI instructions for the LaTeX part.  
⚠️ **MANDATORY**: If you are working on this part of the repository, stop reading this file here.

## Spell Card Generator Application

The project uses Poetry for dependency management and follows
modern Python development practices with a workflow-based GUI.  
The poetry application is to be installed into a virtual environment first (requirements.txt),
before then using poetry to install app dependencies into that same venv.

### Critical Development Environment Setup

⚠️ **MANDATORY**: Every Python/Poetry operation MUST follow this pattern:

```bash
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator && source .venv/bin/activate && poetry run [command]
```

#### Application Execution
```bash
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
source .venv/bin/activate && poetry run spell-card-generator
```

#### Alternative (if needed)
```bash
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
source .venv/bin/activate && [command]
```

**NEVER run Python commands without:**
1. Changing to `spell_card_generator` subdirectory of the repository
2. Activating `.venv`
3. Using `poetry run` to start the application

### Development Guidelines

#### Code Quality Standards
- **Pylint Score**: MUST maintain 10.00/10 and not return non-zero exit code
- **Test Coverage**: Target 60%+ overall
- **Import Style**: Use absolute imports only (`from spell_card_generator.module import ...`)
- **Type Hints**: Required for all function parameters and return values
- **Exception Handling**: Use proper exception chaining (`raise CustomError(...) from e`)
- **Formatting**: Black formatting enforced
- **Testing**: All tests must pass (142 tests, 100% pass rate)

#### UI/UX Principles
- **Single class selection**: Users select exactly one character class
- **Progressive disclosure**: Later steps only accessible after prerequisites
- **State persistence**: User input preserved when switching steps

### Common Development Tasks

#### Running the Application
```bash
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
poetry run spell-card-generator
```

#### Adding Dependencies
```bash
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
poetry add [--dev] <package-name>
```

#### Code Quality Checks
```bash
# Format code
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
poetry run black .

# Lint code (maintain 10.00/10 score)
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
poetry run pylint .

# Type checking
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
poetry run mypy .

# Run tests
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
poetry run pytest

# Run tests with coverage
[[ "$(dirname $(pwd))" != latex-spell-cards ]] && cd spell_card_generator
poetry run pytest --cov --cov-report=html

### Testing Strategy

#### Testing Approach
The project uses a **three-tier testing strategy**:

1. **Unit Tests with Mocked tkinter**
   - Mock tkinter widgets to test logic without GUI rendering
   - Test state management, validation, event handlers
   - Located in `tests/ui/` directory

2. **Integration Tests**
   - Test workflow state transitions end-to-end
   - Verify data flow between components
   - Focus on critical user paths

3. **Manual Testing Documentation**
   - Document visual behaviors in `tests/manual_testing.md`
   - List edge cases for manual verification


### Critical DO NOTs

#### Environment & Execution
- ❌ Run Python commands without proper environment setup
- ❌ Use exclamation marks in commands
- ❌ Modify `.venv/` directory contents
- ❌ Use relative imports (always use absolute)

#### Architecture & Code Quality
- ❌ Cause Pylint to exit non-zero
- ❌ Cause Pytest to exit non-zero
- ❌ Cause test coverage to decrease
- ❌ Create duplicate UI elements

#### UI/UX
- ❌ Allow multiple class selection (enforce single selection)
- ❌ Skip step validation logic
- ❌ Break the progressive disclosure pattern

### Documentation & Context Files
- **project-specific Readme**: In `spell_card_generator/README.md`
- **Entry Point**: Configured in `pyproject.toml` as `spell-card-generator`

### When Making Changes

1. **Test with actual application**: Always run `poetry run spell-card-generator` to verify
4. **Preserve code quality**: Run linting and maintain 9.77/10 score

### Quick Reference - Most Common Operations

```bash
# Navigate to project directory
cd ./spell_card_generator

# Activate virtual environment
source .venv/bin/activate # On Windows: .venv/Scripts/activate

# Install dependencies
poetry install

# Run application
poetry run spell-card-generator

# Add dependency
poetry add [package]

# Format code
poetry run black .

# Check code quality
poetry run pylint .
```

Remember: This project has reached a certain level of code quality and professional architecture.
The focus now is on completing the remaining workflow steps while maintaining the established standards and patterns.
