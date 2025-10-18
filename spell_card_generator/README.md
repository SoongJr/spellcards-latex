# Spell Card Generator

A GUI application for generating LaTeX spell cards from spell database files
with a user-friendly interface.

## Start the application

There is a helper script to just start the GUI to create spell cards:
```bash
spell_card_generator/spell_card_generator.sh
```

## Development Setup

If you wish to modify the spell card generator, maybe add new features,
maybe update dependencies, you'll need a development setup.

### Prerequisites

- Python 3.10+

### Setup Workflow

1. **Create and activate a Python virtual environment:**
   ```bash
   cd spell_card_generator
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv/Scripts/activate
   ```

2. **Install Poetry into the virtual environment:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install project dependencies (also go into the same virtual environment):**
   ```bash
   poetry install
   ```

### Development Workflow

1. **Activate your virtual environment** (if not already active):
   ```bash
   source spell_card_generator/.venv/bin/activate
   # On Windows: spell_card_generator/.venv\Scripts\activate
   ```

2. **Make your code changes** - no reinstallation needed! The package is installed in editable mode.

3. **Run the application**  
  `poetry run spell-card-generator`

4. **Run tests and linting:**
   ```bash
   cd spell_card_generator
   # Code formatting
   black .
   # Linting
   pylint .
   # Type checking
   mypy .
   # Run tests
   pytest
   ```

### When to Reinstall

You only need to run `poetry -C spell_card_generator install` again when:
- Dependencies change in `pyproject.toml`
- Entry points are modified in `pyproject.toml`
- Major structural changes occur (rare)

## Project Structure

```
spell_card_generator/
├── __init__.py                # Package initialization
├── main.py                    # Main entry point
├── app.py                     # Application coordinator
├── pyproject.toml             # Project configuration and dependencies
├── requirements.txt           # Legacy requirements file
├── spell_full.tsv             # Spell database
├── config/                    # Configuration constants
├── data/                      # Data loading and filtering
├── generators/                # LaTeX generation logic  
├── models/                    # Data models
├── ui/                        # User interface components
└── utils/                     # Utilities and validators
```

## Configuration

The application uses configuration constants defined in `config/constants.py`:

- **Character Classes**: Organized by categories (Core, Base, Hybrid, Occult)
- **Spell Database Columns**: Column mappings for the TSV file
- **UI Settings**: Window dimensions, tree view configurations
- **File Paths**: Output directory templates and default URLs

## Output

Generated LaTeX files are placed in:
```
src/spells/{class_name}/{spell_level}/{Spell Name}.tex
```

These files can be included in your main LaTeX document using `\input{}` statements.

## Contributing

1. Format code with Black
1. Ensure all code passes linting (pylint) and type checking (mypy)
1. Add test coverage for new functionality
1. Update documentation as needed

## License

See the LICENSE file in the project root.
