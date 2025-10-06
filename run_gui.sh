#!/bin/bash
# Launcher script for the Spell Card Generator GUI.
# This script ensures dependencies are installed and launches the GUI application.

set -euo pipefail

# Change to the script's directory
cd "$(dirname "$0")"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing poetry..."
    pip install -r requirements.txt
fi
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found after install. PATH may need to be updated (try logoff/logon)."
    exit 1
fi

# Ensure dependencies are up to date
echo "Installing dependencies..."
poetry install

# Launch the GUI application
echo "Starting Spell Card Generator..."
poetry run python src/spell_card_generator.py
