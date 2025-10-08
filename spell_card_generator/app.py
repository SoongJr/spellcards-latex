"""Main application coordinator."""

import tkinter as tk
from tkinter import ttk
from typing import Set

from ui.main_window import MainWindow
from ui.class_selection import ClassSelectionManager
from ui.spell_tabs import SpellTabManager
from ui.dialogs import DialogManager
from data.loader import SpellDataLoader
from data.filter import SpellFilter
from generators.latex_generator import LaTeXGenerator
from config.constants import Config
from utils.exceptions import SpellCardError


class SpellCardGeneratorApp:
    """Main application coordinator."""

    def __init__(self, root: tk.Tk):
        self.root = root

        # Initialize components
        self.main_window = MainWindow(root)
        self.data_loader = SpellDataLoader()
        self.spell_filter = SpellFilter()
        self.latex_generator = LaTeXGenerator()

        # Initialize UI managers
        self.class_manager = ClassSelectionManager(
            self.main_window.class_frame, self.on_class_selection_changed
        )

        self.spell_tab_manager = SpellTabManager(
            self.main_window.content_frame, self.data_loader, self.spell_filter
        )

        self.dialog_manager = DialogManager(root)

        # Initialize application
        self._setup_options_ui()
        self._setup_controls_ui()
        self._load_initial_data()

    def _setup_options_ui(self):
        """Setup the options frame."""
        # Overwrite checkbox
        self.overwrite_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.main_window.options_frame,
            text="Overwrite existing files",
            variable=self.overwrite_var,
        ).grid(row=0, column=0, sticky=tk.W)

        # German URL entry
        ttk.Label(self.main_window.options_frame, text="German URL Template:").grid(
            row=1, column=0, sticky=tk.W, pady=(10, 0)
        )

        self.german_url_var = tk.StringVar(value=Config.DEFAULT_GERMAN_URL)
        ttk.Entry(
            self.main_window.options_frame, textvariable=self.german_url_var, width=80
        ).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

    def _setup_controls_ui(self):
        """Setup control buttons and progress bar."""
        # Generate button
        self.generate_btn = ttk.Button(
            self.main_window.control_frame,
            text="Generate Spell Cards",
            command=self.generate_cards,
            style="Accent.TButton",
        )
        self.generate_btn.pack()

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_window.progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.main_window.status_frame, textvariable=self.status_var
        )
        self.status_label.pack()

    def _load_initial_data(self):
        """Load initial spell data."""
        try:
            spells_df = self.data_loader.load_data()
            self.class_manager.setup_class_sections(self.data_loader.character_classes)
            self.status_var.set(
                f"Loaded {len(spells_df)} spells across "
                f"{len(self.data_loader.character_classes)} classes"
            )
        except SpellCardError as e:
            self.dialog_manager.show_error("Error", str(e))

    def on_class_selection_changed(self, selected_classes: Set[str]):
        """Handle class selection changes."""
        self.spell_tab_manager.update_tabs(selected_classes)

        # Update status
        count = len(selected_classes)
        if count == 0:
            self.status_var.set("No classes selected")
        elif count == 1:
            class_name = next(iter(selected_classes))
            display_name = self.class_manager.get_display_name(class_name)
            self.status_var.set(f"Selected: {display_name}")
        else:
            self.status_var.set(f"Selected: {count} classes")

    def generate_cards(self):
        """Generate LaTeX spell cards."""
        try:
            selected_spells = self.spell_tab_manager.get_selected_spells()
            if not selected_spells:
                self.dialog_manager.show_warning(
                    "Warning", "Please select at least one spell"
                )
                return

            # Generate cards with progress updates
            generated_files, skipped_files = self.latex_generator.generate_cards(
                selected_spells,
                self.overwrite_var.get(),
                self.german_url_var.get(),
                progress_callback=self._update_progress,
            )

            # Show results
            result_msg = f"Generated {len(generated_files)} spell cards"
            if skipped_files:
                result_msg += f"\\nSkipped {len(skipped_files)} existing files"

            if generated_files:
                # Extract output directory from first generated file
                from pathlib import Path

                output_dir = Path(generated_files[0]).parent.parent
                result_msg += (
                    f"\n\nFiles generated in: {output_dir}"
                    "\n\nAdd \\input{} statements to "
                    "the corresponding .tex files to include them in the document."
                )

            self.dialog_manager.show_info("Success", result_msg)
            self.status_var.set("Generation complete")

        except SpellCardError as e:
            self.dialog_manager.show_error("Error", str(e))
            self.status_var.set("Error occurred")
        except Exception as e:
            self.dialog_manager.show_error(
                "Unexpected Error", f"An unexpected error occurred: {e}"
            )
            self.status_var.set("Error occurred")
        finally:
            self.progress_var.set(0)

    def _update_progress(self, current: int, total: int, message: str):
        """Update progress bar and status."""
        progress = (current / total) * 100 if total > 0 else 0
        self.progress_var.set(progress)
        self.status_var.set(message)
        self.root.update()
