"""Input validation utilities."""

import re
from config.constants import CharacterClasses


class Validators:
    """Input validation utilities."""

    @staticmethod
    def validate_class_name(class_name: str) -> bool:
        """Validate if class name is a known character class."""
        all_classes = []
        for category_classes in CharacterClasses.CATEGORIES.values():
            all_classes.extend(category_classes)
        return class_name in all_classes

    @staticmethod
    def validate_spell_level(level: str) -> bool:
        """Validate if spell level is valid."""
        if level == "All":
            return True
        try:
            level_int = int(level)
            return 0 <= level_int <= 9
        except ValueError:
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "-", filename)
        # Replace multiple dashes with single dash
        sanitized = re.sub(r"-+", "-", sanitized)
        # Remove leading/trailing dashes and whitespace
        sanitized = sanitized.strip("- ")
        return sanitized

    @staticmethod
    def validate_url(url: str) -> bool:
        """Basic URL validation."""
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return url_pattern.match(url) is not None
