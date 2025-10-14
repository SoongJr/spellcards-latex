# Test Suite for Spell Card Generator

## Overview
This directory contains comprehensive unit tests for the spell card generator application. The tests are organized by module and use pytest as the testing framework.

## Test Structure

### Test Files
- **`conftest.py`**: Shared fixtures and test utilities
- **`test_spell.py`**: Tests for spell data models
- **`test_loader.py`**: Tests for spell data loading functionality
- **`test_filter.py`**: Tests for spell filtering operations
- **`test_class_categorization.py`**: Tests for character class categorization
- **`test_validators.py`**: Tests for input validation utilities
- **`test_exceptions.py`**: Tests for custom exception classes
- **`test_latex_generator.py`**: Tests for LaTeX generation functionality

## Running Tests

### Run all tests:
```bash
poetry run pytest
```

### Run with coverage report:
```bash
poetry run pytest --cov=spell_card_generator --cov-report=html
```

### Run specific test file:
```bash
poetry run pytest tests/test_filter.py
```

### Run tests with specific marker:
```bash
poetry run pytest -m unit
```

### Run tests in verbose mode:
```bash
poetry run pytest -v
```

## Test Coverage

Current coverage statistics:
- **Total Tests**: 102
- **Pass Rate**: 100%
- **Code Coverage**: 28% overall

### Module Coverage Breakdown:
- `models/spell.py`: 100%
- `data/filter.py`: 100%
- `data/loader.py`: 93%
- `generators/latex_generator.py`: 96%
- `utils/validators.py`: 100%
- `utils/class_categorization.py`: 100%
- `utils/exceptions.py`: 100%

UI modules (0% coverage) - these require integration tests with tkinter mocking.

## Test Fixtures

### Available Fixtures (in conftest.py):
- `sample_spell_data`: DataFrame with sample spell data for testing
- `temp_spell_file`: Temporary TSV file with spell data
- `sample_spell_series`: Single spell as a pandas Series
- `mock_spell_classes`: List of character classes for testing

## Writing New Tests

### Example Test:
```python
import pytest
from spell_card_generator.data.filter import SpellFilter

@pytest.mark.unit
class TestSpellFilter:
    def test_filter_by_class(self, sample_spell_data):
        """Test filtering spells by character class."""
        filtered = SpellFilter.filter_spells(sample_spell_data, "wizard")
        assert not filtered.empty
        assert all(filtered["wizard"] != "NULL")
```

### Best Practices:
1. Use descriptive test names starting with `test_`
2. Group related tests in classes
3. Use pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
4. Leverage fixtures for common test data
5. Test both success and failure cases
6. Include edge cases and boundary conditions

## Test Markers

- `@pytest.mark.unit`: Unit tests for individual functions
- `@pytest.mark.integration`: Integration tests for module interactions
- `@pytest.mark.slow`: Tests that take significant time to run

## Coverage Reports

HTML coverage reports are generated in `htmlcov/` directory. Open `htmlcov/index.html` in a browser to view detailed coverage information.

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:
```yaml
# Example GitHub Actions
- name: Run tests
  run: poetry run pytest --cov=spell_card_generator --cov-report=xml
```

## Future Test Additions

Priority areas for additional testing:
1. **UI Components**: Mock tkinter for UI testing
2. **Integration Tests**: Test complete workflows
3. **File I/O**: Test actual file generation and reading
4. **Error Handling**: More comprehensive error scenarios
5. **Performance Tests**: Test with large datasets
