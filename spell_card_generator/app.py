"""Main application coordinator."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Optional

from spell_card_generator.ui.main_window import MainWindow
from spell_card_generator.ui.single_class_selection import SingleClassSelectionManager
from spell_card_generator.ui.class_placeholder import ClassSelectionPlaceholder
from spell_card_generator.ui.spell_tabs import SpellTabManager
from spell_card_generator.ui.dialogs import DialogManager
from spell_card_generator.data.loader import SpellDataLoader
from spell_card_generator.data.filter import SpellFilter
from spell_card_generator.generators.latex_generator import LaTeXGenerator
from spell_card_generator.config.constants import Config
from spell_card_generator.utils.exceptions import SpellCardError


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
        self.class_manager = SingleClassSelectionManager(
            self.main_window.class_frame, self.on_class_selection_changed
        )

        # Placeholder for when no class is selected
        self.class_placeholder = ClassSelectionPlaceholder(
            self.main_window.content_frame
        )

        self.spell_tab_manager = SpellTabManager(
            self.main_window.content_frame,
            self.data_loader,
            self.spell_filter,
            spell_selection_callback=self.on_spell_selection_changed,
        )

        self.dialog_manager = DialogManager(root)

        # Track current application state
        self.current_selected_class: Optional[str] = None

        # Initialize application
        self._setup_controls_ui()
        self._load_initial_data()

    def _setup_controls_ui(self):
        """Setup control buttons and progress bar."""
        # Generate button - initially hidden
        self.generate_btn = ttk.Button(
            self.main_window.control_frame,
            text="Generate Spell Cards",
            command=self.generate_cards,
            style="Accent.TButton",
            state="disabled",
        )
        # Don't pack initially - will be shown when class is selected

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
            self.class_manager.setup_class_tree(self.data_loader.character_classes)

            # Show placeholder initially since no class is selected
            self.class_placeholder.show()

            self.status_var.set(
                f"Loaded {len(spells_df)} spells across "
                f"{len(self.data_loader.character_classes)} classes - Please select a class"
            )
        except SpellCardError as e:
            self.dialog_manager.show_error("Error", str(e))

    def on_class_selection_changed(self, selected_class: Optional[str] = None):
        """Handle class selection changes."""
        self.current_selected_class = selected_class

        if selected_class:
            # Show spell tabs for the selected class
            self.class_placeholder.hide()
            self.spell_tab_manager.update_tabs({selected_class})

            # Show Generate button when class is selected
            self.generate_btn.pack(pady=(10, 0))
            # Start disabled until spells are selected
            self.generate_btn.configure(state="disabled")

            # Update status
            display_name = self.class_manager._get_display_name(selected_class)
            self.status_var.set(
                f"Selected: {display_name} - Select spells to generate cards"
            )
        else:
            # No class selected - show placeholder and hide Generate button
            self.spell_tab_manager.update_tabs(set())
            self.class_placeholder.show()
            self.generate_btn.pack_forget()
            self.status_var.set("No class selected")

    def on_spell_selection_changed(self):
        """Handle spell selection changes to enable/disable Generate button."""
        if not self.current_selected_class:
            return

        selected_spells = self.spell_tab_manager.get_selected_spells()
        if selected_spells:
            self.generate_btn.configure(state="normal")
            self.status_var.set(
                f"Selected: {len(selected_spells)} spells - Ready to generate"
            )
        else:
            self.generate_btn.configure(state="disabled")
            display_name = self.class_manager._get_display_name(
                self.current_selected_class
            )
            self.status_var.set(
                f"Selected: {display_name} - Select spells to generate cards"
            )

    def generate_cards(self):
        """Generate LaTeX spell cards."""
        try:
            if not self.current_selected_class:
                self.dialog_manager.show_warning(
                    "Warning", "Please select a character class first"
                )
                return

            selected_spells = self.spell_tab_manager.get_selected_spells()
            if not selected_spells:
                self.dialog_manager.show_warning(
                    "Warning", "Please select at least one spell"
                )
                return

            # Generate cards with progress updates - use default options for now
            generated_files, skipped_files = self.latex_generator.generate_cards(
                selected_spells,
                overwrite=False,  # Will be configurable in the sidebar wizard
                german_url_template=Config.DEFAULT_GERMAN_URL,
                progress_callback=self._update_progress,
            )

            # Show results
            result_msg = f"Generated {len(generated_files)} spell cards"
            if skipped_files:
                result_msg += f"\\nSkipped {len(skipped_files)} existing files"

            if generated_files:
                # Extract output directory from first generated file
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
        except (OSError, IOError, MemoryError) as e:
            self.dialog_manager.show_error(
                "System Error", f"A system error occurred: {e}"
            )
            self.status_var.set("System error occurred")
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Final safety net to prevent GUI crashes
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
