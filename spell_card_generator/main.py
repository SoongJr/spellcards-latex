"""
Spell Card Generator - Entry Point

A tool for generating LaTeX spell cards from the spell_full.tsv database.

Usage:
    GUI mode (default):
        spell-card-generator

    CLI mode:
        spell-card-generator sor "Magic Missile"
        spell-card-generator sor "Fireball" "Lightning Bolt"
"""

import sys
import tkinter as tk
from spell_card_generator.app import SpellCardGeneratorApp
from spell_card_generator.cli import run_cli


def main():
    """Main entry point - dispatches to GUI or CLI based on arguments."""
    # If any command-line arguments provided, use CLI mode
    if len(sys.argv) > 1:
        sys.exit(run_cli())

    # Otherwise, launch GUI
    root = tk.Tk()
    SpellCardGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
