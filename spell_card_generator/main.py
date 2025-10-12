"""
Spell Card Generator GUI

A GUI application to replace the convert.sh script for generating LaTeX spell cards
from the spell_full.tsv database.
"""

import tkinter as tk

from spell_card_generator.app import SpellCardGeneratorApp


def main():
    """Main function to run the application."""
    root = tk.Tk()
    _ = SpellCardGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
