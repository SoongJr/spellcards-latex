"""Custom exceptions for the spell card generator."""


class SpellCardError(Exception):
    """Base exception for spell card operations."""

    pass


class DataLoadError(SpellCardError):
    """Raised when spell data cannot be loaded."""

    pass


class GenerationError(SpellCardError):
    """Raised when spell card generation fails."""

    pass


class FilterError(SpellCardError):
    """Raised when spell filtering fails."""

    pass
