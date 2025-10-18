"""Main application coordinator."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Optional

# UI is now managed by the workflow coordinator
from spell_card_generator.ui.workflow_coordinator import WorkflowCoordinator
from spell_card_generator.ui.dialogs import DialogManager
from spell_card_generator.data.loader import SpellDataLoader
from spell_card_generator.data.filter import SpellFilter
from spell_card_generator.generators.latex_generator import LaTeXGenerator
from spell_card_generator.utils.exceptions import SpellCardError


class SpellCardGeneratorApp:
    """Main application coordinator."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Spell Card Generator")

        # Set reasonable default window size to prevent startup sizing issues
        self.root.geometry("900x600")  # Good default size for the application
        self.root.minsize(900, 600)  # Minimum size to ensure usability

        # Initialize components (main window layout is now handled by workflow coordinator)
        self.data_loader = SpellDataLoader()
        self.spell_filter = SpellFilter()
        self.latex_generator = LaTeXGenerator()

        # Create main content frame (before status bar)
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create status bar at bottom
        self._setup_status_bar()

        self.dialog_manager = DialogManager(root)

        # Track current application state
        self.current_selected_class: Optional[str] = None

        # Initialize application - LOAD DATA FIRST
        self._load_initial_data()

        # Initialize workflow coordinator AFTER data is loaded
        # Class selection is now part of the workflow
        self.workflow_coordinator = WorkflowCoordinator(
            self.main_frame,  # Use main_frame instead of root
            self.data_loader,
            self.spell_filter,
            on_generate_callback=self.generate_cards,
        )

    def _setup_status_bar(self):
        """Setup status bar at bottom of window."""
        # Status frame at bottom
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame, variable=self.progress_var, maximum=100, length=200
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT)

    def _load_initial_data(self):
        """Load initial spell data."""
        try:
            spells_df = self.data_loader.load_data()

            # Workflow coordinator handles class setup internally
            self.status_var.set(
                f"Loaded {len(spells_df)} spells across "
                f"{len(self.data_loader.character_classes)} classes - Begin with class selection"
            )
        except SpellCardError as e:
            self.dialog_manager.show_error("Error", str(e))

    def on_class_selection_changed(self, selected_class: Optional[str] = None):
        """Handle class selection changes (legacy method - now handled by workflow)."""
        # Class selection is now handled within the workflow coordinator
        # Keep this for backward compatibility but it's not used
        self.current_selected_class = selected_class

    def on_spell_selection_changed(self):
        """Handle spell selection changes (legacy method - workflow now handles this)."""
        # This method is kept for compatibility but workflow coordinator handles the logic

    def generate_cards(self):
        """Generate LaTeX spell cards."""
        try:
            # Get selected class from workflow state
            selected_class = self.workflow_coordinator.workflow_state.selected_class
            if not selected_class:
                self.dialog_manager.show_warning(
                    "Warning", "Please select a character class first"
                )
                return

            # Get selected spells from workflow coordinator
            selected_spells = self.workflow_coordinator.get_selected_spells()
            if not selected_spells:
                self.dialog_manager.show_warning(
                    "Warning", "Please select at least one spell"
                )
                return

            # Determine overwrite strategy from workflow state
            # If we have overwrite decisions, respect them per-spell
            # Otherwise, use the global overwrite_existing setting
            workflow_state = self.workflow_coordinator.workflow_state

            # For now, use simple overwrite logic:
            # - If conflicts were detected and resolved, allow overwrite
            # - Otherwise, use the overwrite_existing flag
            overwrite = (
                workflow_state.overwrite_existing or workflow_state.conflicts_detected
            )

            # Build URL configuration from workflow state
            # URLs are stored separately: custom_url_templates (primary),
            # secondary_language_urls (secondary)
            url_config = {}
            for spell_name in [name for _, name, _ in selected_spells]:
                primary = workflow_state.custom_url_templates.get(spell_name)
                secondary = workflow_state.secondary_language_urls.get(spell_name)
                url_config[spell_name] = (primary, secondary)

            # Generate cards with workflow state options
            generated_files, skipped_files = self.latex_generator.generate_cards(
                selected_spells,
                overwrite=overwrite,
                german_url_template=workflow_state.german_url_template,
                progress_callback=self._update_progress,
                preserve_description=workflow_state.preserve_description,
                preserve_urls=workflow_state.preserve_urls,
                url_configuration=url_config,
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
