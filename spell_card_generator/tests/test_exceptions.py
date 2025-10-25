"""Tests for spell_card_generator.utils.exceptions module."""

# pylint: disable=duplicate-code

import pytest

from spell_card_generator.utils.exceptions import (
    SpellCardError,
    DataLoadError,
    FilterError,
    GenerationError,
)


@pytest.mark.unit
class TestExceptions:
    """Test cases for custom exception classes."""

    def test_spell_card_error_basic(self):
        """Test basic SpellCardError."""
        error = SpellCardError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_spell_card_error_with_cause(self):
        """Test SpellCardError with cause."""
        cause = ValueError("Original error")
        try:
            raise SpellCardError("Wrapped error") from cause
        except SpellCardError as error:
            assert str(error) == "Wrapped error"
            assert error.__cause__ is cause

    def test_data_load_error_basic(self):
        """Test basic DataLoadError."""
        error = DataLoadError("Failed to load data")
        assert str(error) == "Failed to load data"
        assert isinstance(error, SpellCardError)
        assert isinstance(error, Exception)

    def test_data_load_error_raise_and_catch(self):
        """Test raising and catching DataLoadError."""
        with pytest.raises(DataLoadError, match="Test error"):
            raise DataLoadError("Test error")

    def test_filter_error_basic(self):
        """Test basic FilterError."""
        error = FilterError("Filter failed")
        assert str(error) == "Filter failed"
        assert isinstance(error, SpellCardError)

    def test_filter_error_raise_and_catch(self):
        """Test raising and catching FilterError."""
        with pytest.raises(FilterError, match="Invalid filter"):
            raise FilterError("Invalid filter")

    def test_generation_error_basic(self):
        """Test basic GenerationError."""
        error = GenerationError("Generation failed")
        assert str(error) == "Generation failed"
        assert isinstance(error, SpellCardError)

    def test_generation_error_raise_and_catch(self):
        """Test raising and catching GenerationError."""
        with pytest.raises(GenerationError, match="LaTeX generation failed"):
            raise GenerationError("LaTeX generation failed")

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from SpellCardError."""
        assert issubclass(DataLoadError, SpellCardError)
        assert issubclass(FilterError, SpellCardError)
        assert issubclass(GenerationError, SpellCardError)

    def test_catch_as_base_exception(self):
        """Test catching custom exceptions as base SpellCardError."""
        with pytest.raises(SpellCardError):
            raise DataLoadError("Data error")

        with pytest.raises(SpellCardError):
            raise FilterError("Filter error")

        with pytest.raises(SpellCardError):
            raise GenerationError("Generation error")

    def test_exception_with_formatting(self):
        """Test exception messages with string formatting."""
        file_path = "/path/to/file.txt"
        error = DataLoadError(f"Could not find file at {file_path}")
        assert "/path/to/file.txt" in str(error)

    def test_exception_chaining(self):
        """Test exception chaining with 'from' syntax."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise DataLoadError("Wrapped error") from e
        except DataLoadError as e:
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "Original error"
