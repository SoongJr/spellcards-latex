"""Icon management for the application using symbol font characters."""

# pylint: disable=global-statement,broad-exception-caught,no-else-return

import tkinter as tk
from tkinter import font


class IconFont:
    """Manages icons using symbol font characters."""

    # Icon mappings using Unicode symbols that are widely supported
    ICONS = {
        "class": "👤",  # User/person for class selection
        "spell": "🎯",  # Target for spell selection
        "settings": "⚙",  # Gear for settings/options
        "link": "🔗",  # Chain link for URLs
        "globe": "🌐",  # Globe for language/international
        "generate": "✨",  # Sparkles for generation/magic
        "expand": "▶",  # Right arrow for expand
        "collapse": "◀",  # Left arrow for collapse
        "check": "✓",  # Checkmark
        "warning": "⚠",  # Warning triangle
        "info": "ℹ",  # Information symbol
        "folder": "📁",  # Folder icon
        "file": "📄",  # Document icon
    }

    # Fallback text icons if symbols don't render
    FALLBACK_ICONS = {
        "class": "[C]",
        "spell": "[S]",
        "settings": "[O]",
        "link": "[L]",
        "globe": "[G]",
        "generate": "[P]",
        "expand": ">",
        "collapse": "<",
        "check": "√",
        "warning": "!",
        "info": "i",
        "folder": "[F]",
        "file": "[D]",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.use_symbols = True
        self._test_symbol_support()

    def _test_symbol_support(self):
        """Test if Unicode symbols are properly supported."""
        try:
            # Create a test label to check symbol rendering
            test_label = tk.Label(self.root, text="🎯")
            test_label.update_idletasks()

            # If we can measure the text, symbols are likely supported
            font_obj = font.Font(font=test_label["font"])
            width = font_obj.measure("🎯")

            # If width is very small, symbols might not render properly
            self.use_symbols = width > 5

            test_label.destroy()
        except Exception:
            # If any error occurs, fall back to text icons
            self.use_symbols = False

    def get_icon(self, icon_name: str) -> str:
        """Get icon character for the given icon name."""
        if self.use_symbols and icon_name in self.ICONS:
            return self.ICONS[icon_name]
        if icon_name in self.FALLBACK_ICONS:  # pylint: disable=no-else-return
            return self.FALLBACK_ICONS[icon_name]
        return f"[{icon_name[0].upper()}]"

    def get_icon_font(self, size: int = 12) -> font.Font:
        """Get a font optimized for displaying icons."""
        if self.use_symbols:
            # Use a font that handles Unicode symbols well
            return font.Font(family="Segoe UI Symbol", size=size, weight="bold")
        else:
            # Use standard font for text fallbacks
            return font.Font(family="TkDefaultFont", size=size, weight="bold")


# Global icon manager instance (initialized by app)
icon_manager: IconFont = None


def init_icons(root: tk.Tk):
    """Initialize the global icon manager."""
    global icon_manager
    icon_manager = IconFont(root)


def get_icon(icon_name: str) -> str:
    """Get icon character (convenience function)."""
    if icon_manager:
        return icon_manager.get_icon(icon_name)
    else:
        # Fallback if not initialized
        return f"[{icon_name[0].upper()}]"


def get_icon_font(size: int = 12) -> font.Font:
    """Get icon font (convenience function)."""
    if icon_manager:
        return icon_manager.get_icon_font(size)
    else:
        # Fallback if not initialized
        return font.Font(family="TkDefaultFont", size=size, weight="bold")
