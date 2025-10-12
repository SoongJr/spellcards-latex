"""Custom exceptions for the spell card generator."""


class SpellCardError(Exception):
    """Base exception for spell card operations."""


class DataLoadError(SpellCardError):
    """Raised when spell data cannot be loaded."""


class GenerationError(SpellCardError):
    """Raised when spell card generation fails."""


class FilterError(SpellCardError):
    """Raised when spell filtering fails."""
