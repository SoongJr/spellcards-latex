"""
Spell Card Generator GUI

A GUI application to replace the convert.sh script for generating LaTeX spell cards
from the spell_full.tsv database.
"""

from app import SpellCardGeneratorApp
import sys
import os
import tkinter as tk

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main function to run the application."""
    root = tk.Tk()
    _ = SpellCardGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
