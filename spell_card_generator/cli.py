"""Command-line interface for spell card generation."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from spell_card_generator.data.loader import SpellDataLoader
from spell_card_generator.generators.latex_generator import (
    LaTeXGenerator,
    PreservationOptions,
)
from spell_card_generator.config.constants import Config
from spell_card_generator.utils.exceptions import SpellCardError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="spell-card-generator",
        description="Generate LaTeX spell cards in expl3 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a single spell card
  spell-card-generator sor "Magic Missile"

  # Generate multiple spell cards
  spell-card-generator sor "Magic Missile" "Fireball" "Teleport"

Defaults:
  - Overwrite: ON (existing files will be updated)
  - Preserve descriptions: ON (keep manual edits in description section)
  - Preserve URLs: ON (keep custom URLs)
  - Preserve properties: ON (keep manual property modifications with % original comments)
""",
    )

    parser.add_argument(
        "class_name", help="Character class (e.g., sor, wiz, clr)", metavar="CLASS"
    )

    parser.add_argument(
        "spell_names",
        nargs="+",
        help="One or more spell names to generate (quote names with spaces)",
        metavar="SPELL",
    )

    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Skip existing files instead of updating them",
    )

    parser.add_argument(
        "--no-preserve",
        action="store_true",
        help="Don't preserve descriptions, URLs, or properties from existing files",
    )

    parser.add_argument(
        "--tsv",
        type=Path,
        default=None,
        help="Path to spell_full.tsv (default: spell_full.tsv in package directory)",
    )

    return parser


def run_cli(args: Optional[List[str]] = None) -> int:
    """
    Run the command-line interface.

    Args:
        args: Command-line arguments (for testing). Uses sys.argv if None.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    try:
        # Determine TSV path
        if parsed_args.tsv:
            tsv_path = parsed_args.tsv
        else:
            # Use default location relative to this file
            tsv_path = Path(__file__).parent / "spell_full.tsv"

        if not tsv_path.exists():
            print(f"Error: Spell data file not found: {tsv_path}", file=sys.stderr)
            return 1

        # Load spell data
        print(f"Loading spell data from {tsv_path}...")
        loader = SpellDataLoader(tsv_path)
        df = loader.load_data()

        # Validate class
        class_name = parsed_args.class_name.lower()
        if class_name not in df.columns:
            available = [
                col
                for col in df.columns
                if col not in ["name", "school", "description"]
            ]
            print(f"Error: Unknown class '{class_name}'", file=sys.stderr)
            print(f"Available classes: {', '.join(available[:10])}", file=sys.stderr)
            return 1

        # Determine which spells to generate
        spell_names = parsed_args.spell_names

        # Validate spell names and collect spell data
        selected_spells = []
        for spell_name in spell_names:
            matching = df[df["name"] == spell_name]
            if matching.empty:
                print(
                    f"Warning: Spell '{spell_name}' not found, skipping...",
                    file=sys.stderr,
                )
                continue

            spell_data = matching.iloc[0]

            # Check if spell is available for this class
            if spell_data[class_name] == "NULL":
                print(
                    f"Warning: '{spell_name}' not available for {class_name}, skipping...",
                    file=sys.stderr,
                )
                continue

            selected_spells.append((class_name, spell_name, spell_data))

        if not selected_spells:
            print("Error: No valid spells to generate", file=sys.stderr)
            return 1

        # Set up preservation options
        preservation_options = None
        if not parsed_args.no_preserve:
            # Enable preservation for all spells
            preservation_options = PreservationOptions()
            preservation_options.preserve_properties = True

            # Check which spells have existing files to preserve from
            for class_name, spell_name, spell_data in selected_spells:
                output_file = LaTeXGenerator.get_output_file_path(
                    class_name, spell_name, spell_data
                )
                if output_file.exists():
                    preservation_options.preserve_description[spell_name] = True
                    preservation_options.preserve_urls[spell_name] = True

        # Generate spell cards
        print(f"\nGenerating {len(selected_spells)} spell card(s)...")
        generator = LaTeXGenerator()

        def progress_callback(current: int, total: int, message: str) -> None:
            print(f"[{current}/{total}] {message}")

        generated, skipped, conflicts = generator.generate_cards(
            selected_spells,
            overwrite=not parsed_args.no_overwrite,
            german_url_template=Config.DEFAULT_GERMAN_URL,
            progress_callback=progress_callback,
            preservation_options=preservation_options,
        )

        # Report results
        print(f"\n✓ Generated {len(generated)} spell card(s)")
        if skipped:
            print(
                f"  Skipped {len(skipped)} existing file(s) (use without --no-overwrite to update)"
            )
        if conflicts:
            print(f"\n⚠ Found {len(conflicts)} conflict(s):")
            for conflict in conflicts[:5]:  # Show first 5
                print(
                    f"  - {conflict.spell_name}: {conflict.property_name} "
                    f"(DB: {conflict.old_db_value!r} → {conflict.new_db_value!r})"
                )
            if len(conflicts) > 5:
                print(f"  ... and {len(conflicts) - 5} more")
            print("  Check generated files for '% original:' comments")

        return 0

    except SpellCardError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # pylint: disable=broad-except
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback  # pylint: disable=import-outside-toplevel

        traceback.print_exc()
        return 1
