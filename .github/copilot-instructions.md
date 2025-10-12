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
cd ${WORKSPACE:-.}/spell_card_generator && source .venv/bin/activate && poetry run [command]
```

#### Application Execution
```bash
cd ${WORKSPACE:-.}/spell_card_generator && source .venv/bin/activate && poetry run spell-card-generator
```

#### Alternative (if needed)
```bash
cd ${WORKSPACE:-.}/spell_card_generator && source .venv/bin/activate && [command]
```

**NEVER run Python commands without:**
1. Changing to `${WORKSPACE:-.}/spell_card_generator` directory
2. Activating `.venv`
3. Using `poetry run` to start the application

### Development Guidelines

#### Code Quality Standards
- **Pylint Score**: MUST maintain 9.77/10 or higher
- **Import Style**: Use absolute imports only (`from spell_card_generator.module import ...`)
- **Type Hints**: Required for all function parameters and return values
- **Exception Handling**: Use proper exception chaining (`raise CustomError(...) from e`)
- **Formatting**: Black formatting enforced

#### UI/UX Principles
- **Single class selection**: Users select exactly one character class
- **Progressive disclosure**: Later steps only accessible after prerequisites
- **State persistence**: User input preserved when switching steps

### Common Development Tasks

#### Running the Application
```bash
cd ${WORKSPACE:-.}/spell_card_generator && poetry run spell-card-generator
```

#### Adding Dependencies
```bash
cd ${WORKSPACE:-.}/spell_card_generator && poetry add [--dev] <package-name>
```

#### Code Quality Checks
```bash
# Format code
cd ${WORKSPACE:-.}/spell_card_generator && poetry run black .

# Lint code (maintain 9.77/10 score)
cd ${WORKSPACE:-.}/spell_card_generator && poetry run pylint .
```

### Critical DO NOTs

#### Environment & Execution
- ❌ Run Python commands without proper environment setup
- ❌ Modify `.venv/` directory contents
- ❌ Use relative imports (always use absolute)

#### Architecture & Code Quality
- ❌ Reduce Pylint score below 9.77/10
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
cd ${WORKSPACE:-.}/spell_card_generator

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
poetry run pylint spell_card_generator
```

Remember: This project has reached a certain level of code quality and professional architecture.
The focus now is on completing the remaining workflow steps while maintaining the established standards and patterns.
