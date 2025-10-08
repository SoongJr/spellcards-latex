#!/bin/bash
# Launcher script for the Spell Card Generator GUI.
# This script ensures dependencies are installed and launches the GUI application.

set -euo pipefail

# Change to the script's directory
scriptFolder="$(dirname "$0")"

# Create virtual environment if it doesn't exist
venvFolder="${scriptFolder}/.venv"
if [ ! -d "${venvFolder}" ]; then
    echo "Creating virtual environment..."
    python -m venv "${venvFolder}"
fi
# Activate the virtual environment (accounting for platform-specific paths)
[[ -f "${venvFolder}/bin/activate" ]] && source "${venvFolder}/bin/activate"
[[ -f "${venvFolder}/Scripts/activate" ]] && source "${venvFolder}/Scripts/activate"
# Verify the virtual environment is activated
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo "Failed to activate virtual environment. Please check your setup." >&2
    exit 1
fi

# Ensure poetry is installed
echo "Installing/updating Poetry..."
pip install -r "${scriptFolder}/requirements.txt"
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found in virtual environment." >&2
    exit 1
fi

# Ensure dependencies are up to date
echo "Installing/updating dependencies..."
poetry -C "${scriptFolder}" install --no-root

# Launch the GUI application
echo "Starting Spell Card Generator..."
bash -cx '$@' -- poetry -C "${scriptFolder}" run python main.py
