"""Documentation URLs workflow step with URL guessing and validation."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Union
import urllib.request
import urllib.error
import urllib.parse
import webbrowser
from deep_translator import GoogleTranslator

from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep
from spell_card_generator.ui.workflow_state import workflow_state


class URLGuessDialog(tk.Toplevel):
    """Dialog for guessing URLs based on predefined patterns."""

    def __init__(self, parent, spell_names):
        super().__init__(parent)
        self.title("Guess Secondary URLs")
        self.spell_names = spell_names
        self.result = None

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_ui()

        # Center on parent
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

    def _create_ui(self):
        """Create the dialog UI."""
        # Description
        desc_frame = ttk.Frame(self, padding=15)
        desc_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            desc_frame,
            text="URL Guessing",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(
            desc_frame,
            text=(
                "This will generate secondary URLs based on predefined patterns.\n"
                "Choose a base URL pattern below. The spell name will be appended.\n\n"
                "Note: Generated URLs will need manual adjustment!\n"
                "They will appear with a red background until validated."
            ),
            wraplength=400,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(0, 15))

        # Base URL selection
        selection_frame = ttk.LabelFrame(
            desc_frame, text="Base URL Pattern", padding=10
        )
        selection_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(selection_frame, text="Select pattern:").pack(
            anchor=tk.W, pady=(0, 5)
        )

        self.pattern_var = tk.StringVar(value="german")
        patterns = [
            ("German (5footstep.de)", "german"),
        ]

        for label, value in patterns:
            ttk.Radiobutton(
                selection_frame,
                text=label,
                variable=self.pattern_var,
                value=value,
            ).pack(anchor=tk.W, padx=(10, 0))

        # Preview
        preview_frame = ttk.LabelFrame(desc_frame, text="Example", padding=10)
        preview_frame.pack(fill=tk.X, pady=(0, 15))

        self.preview_label = ttk.Label(
            preview_frame,
            text="http://prd.5footstep.de/Grundregelwerk/Zauber/<spell-name>",
            foreground="blue",
            font=("TkDefaultFont", 9, "italic"),
        )
        self.preview_label.pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(desc_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="Generate URLs",
            command=self._on_ok,
        ).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
        ).pack(side=tk.RIGHT)

    def _on_ok(self):
        """Handle OK button click."""
        self.result = self.pattern_var.get()
        self.destroy()

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.destroy()


class DocumentationURLsStep(BaseWorkflowStep):
    """Documentation URLs configuration step."""

    step_name = "Documentation URLs"
    step_description = "Configure primary and secondary URLs for spell cards"

    # Validation states
    STATE_VALID = "valid"
    STATE_INVALID = "invalid"
    STATE_UNVALIDATED = "unvalidated"

    # Status symbols (Unicode symbols that display correctly in tkinter)
    SYMBOL_VALID = "✓"  # U+2713 Check Mark
    SYMBOL_INVALID = "✗"  # U+2717 Ballot X
    SYMBOL_UNVALIDATED = "○"  # U+25CB White Circle

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        navigation_callback: Optional[Callable[[Union[int, str]], None]] = None,
        on_urls_changed: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.on_urls_changed = on_urls_changed

        # UI components
        self.spells_tree: Optional[ttk.Treeview] = None
        self.progress_frame: Optional[ttk.Frame] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.progress_label: Optional[ttk.Label] = None

        # URL storage per spell
        self.primary_urls: Dict[str, str] = {}
        self.secondary_urls: Dict[str, str] = {}

        # URL validation status per spell
        self.primary_validation: Dict[str, str] = {}  # spell_name -> STATE_*
        self.secondary_validation: Dict[str, str] = {}  # spell_name -> STATE_*

        # Default/original URLs (for reset functionality)
        self.default_primary_urls: Dict[str, str] = {}
        self.original_secondary_urls: Dict[str, str] = {}

    def create_step_content(self):
        """Create the documentation URLs content."""
        # Title
        title_label = ttk.Label(
            self.content_frame,
            text="Documentation URLs",
            font=("TkDefaultFont", 12, "bold"),
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))

        # Create grid container for description and bulk actions
        top_container = ttk.Frame(self.content_frame)
        top_container.pack(fill=tk.X, pady=(0, 15))

        # pylint: disable=duplicate-code
        # Configure grid: description on left, bulk actions on right
        top_container.grid_rowconfigure(0, weight=0)
        top_container.columnconfigure(0, weight=1)
        top_container.columnconfigure(1, weight=0)

        # Row 0, Col 0: Description (with dynamic wrapping)
        desc_frame = ttk.Frame(top_container)
        desc_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 20)  # type: ignore[arg-type]
        )
        desc_frame.columnconfigure(0, weight=1)

        desc_label = ttk.Label(
            desc_frame,
            text=(
                "Add custom URLs for each spell card. "
                "These links are embedded in the generated cards. "
                "Primary URL defaults to online documentation. "
                "Both URLs are optional. "
                "Double-click cells to edit, click 'R' to reset, click 'V' to visit.\n"
                "Validation status: ✓ Valid (green) | ○ Unvalidated (orange) | ✗ Invalid (red)"
            ),
            justify=tk.LEFT,
        )
        desc_label.grid(row=0, column=0, sticky=(tk.W, tk.E))  # type: ignore[arg-type]

        # Bind to configure event to update wraplength dynamically
        def update_wraplength(event):
            desc_label.configure(wraplength=event.width - 10)

        desc_frame.bind("<Configure>", update_wraplength)

        # Row 0, Col 1: Bulk actions
        self._create_bulk_actions(top_container)
        # pylint: enable=duplicate-code

        # Progress indicator (initially hidden)
        assert self.content_frame is not None, "Content frame must be initialized"
        self._create_progress_indicator(self.content_frame)

        # Spell URLs table
        self._create_urls_table(self.content_frame)

        # Load data
        self._load_spell_data()

        # Step is always valid (URLs are optional)
        workflow_state.set_step_valid(self.step_index, True)

    def _create_bulk_actions(self, parent: ttk.Frame):
        """Create bulk action buttons in a grid layout."""
        actions_frame = ttk.LabelFrame(parent, text="Bulk Actions", padding=10)
        actions_frame.grid(row=0, column=1, sticky=tk.NE)

        # Configure grid columns
        actions_frame.columnconfigure(0, weight=0)
        actions_frame.columnconfigure(1, weight=0)

        # Row 0: Reset Primary URLs
        ttk.Label(actions_frame, text="Primary URLs:", anchor=tk.E).grid(
            row=0, column=0, sticky=tk.E, padx=(0, 10), pady=5
        )
        ttk.Button(
            actions_frame,
            text="Reset to Default",
            command=self._reset_all_primary,
        ).grid(row=0, column=1, padx=5, pady=5)

        # Row 1: Guess Secondary URLs
        ttk.Label(actions_frame, text="Secondary URLs:", anchor=tk.E).grid(
            row=1, column=0, sticky=tk.E, padx=(0, 10), pady=5
        )
        ttk.Button(
            actions_frame,
            text="Guess URLs...",
            command=self._guess_secondary_urls,
        ).grid(row=1, column=1, padx=5, pady=5)

    def _create_progress_indicator(self, parent: ttk.Frame):
        """Create a progress indicator for URL validation operations."""
        self.progress_frame = ttk.Frame(parent)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_label = ttk.Label(
            self.progress_frame, text="Validating URLs...", font=("TkDefaultFont", 9)
        )
        self.progress_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_bar = ttk.Progressbar(
            self.progress_frame, mode="determinate", length=300
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Initially hide the progress indicator
        self.progress_frame.pack_forget()

    def _show_progress(self, message: str = "Validating URLs...", maximum: int = 100):
        """Show the progress indicator."""
        if self.progress_frame and self.progress_bar and self.progress_label:
            self.progress_label.config(text=message)
            self.progress_bar.config(maximum=maximum, value=0)
            self.progress_frame.pack(fill=tk.X, pady=(0, 10))
            assert self.content_frame is not None, "Content frame must be initialized"
            self.content_frame.update_idletasks()

    def _update_progress(self, value: int, message: Optional[str] = None):
        """Update the progress bar value and optionally the message."""
        if self.progress_bar:
            self.progress_bar.config(value=value)
            if message and self.progress_label:
                self.progress_label.config(text=message)
            assert self.content_frame is not None, "Content frame must be initialized"
            self.content_frame.update_idletasks()

    def _hide_progress(self):
        """Hide the progress indicator."""
        if self.progress_frame:
            self.progress_frame.pack_forget()
            assert self.content_frame is not None, "Content frame must be initialized"
            self.content_frame.update_idletasks()

    def _create_urls_table(self, parent: ttk.Frame):
        """Create the editable URLs table."""
        tree_frame = ttk.LabelFrame(parent, text="Spell URLs", padding=5)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create treeview with scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Treeview columns: spell name, primary URL, reset, visit, secondary URL, reset, visit
        columns = (
            "spell",
            "primary_url",
            "reset_primary",
            "visit_primary",
            "secondary_url",
            "reset_secondary",
            "visit_secondary",
        )
        self.spells_tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", selectmode="browse"
        )

        # Configure columns
        self.spells_tree.heading("spell", text="Spell Name")
        self.spells_tree.heading("primary_url", text="Primary URL")
        self.spells_tree.heading("reset_primary", text="")
        self.spells_tree.heading("visit_primary", text="")
        self.spells_tree.heading("secondary_url", text="Secondary URL")
        self.spells_tree.heading("reset_secondary", text="")
        self.spells_tree.heading("visit_secondary", text="")

        self.spells_tree.column("spell", width=200, minwidth=150)
        self.spells_tree.column("primary_url", width=300, minwidth=200)
        self.spells_tree.column("reset_primary", width=30, minwidth=30, anchor="center")
        self.spells_tree.column("visit_primary", width=30, minwidth=30, anchor="center")
        self.spells_tree.column("secondary_url", width=300, minwidth=200)
        self.spells_tree.column(
            "reset_secondary", width=30, minwidth=30, anchor="center"
        )
        self.spells_tree.column(
            "visit_secondary", width=30, minwidth=30, anchor="center"
        )

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL, command=self.spells_tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.HORIZONTAL, command=self.spells_tree.xview
        )
        self.spells_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Pack tree and scrollbars
        self.spells_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Configure tags for colored text based on validation status
        self.spells_tree.tag_configure(self.STATE_VALID, foreground="green")
        self.spells_tree.tag_configure(self.STATE_INVALID, foreground="red")
        self.spells_tree.tag_configure(self.STATE_UNVALIDATED, foreground="orange")

        # Bind events - double-click to edit, single-click on R/V buttons
        self.spells_tree.bind("<Double-Button-1>", self._on_tree_double_click)
        self.spells_tree.bind("<Button-1>", self._on_tree_click)

    def _load_spell_data(self):  # pylint: disable=too-many-branches
        """Load selected spells into the tree, respecting preserve URLs option."""
        if not self.spells_tree:
            return

        # Clear existing items
        for item in self.spells_tree.get_children():
            self.spells_tree.delete(item)

        # Add selected spells - extract spell name from each spell data
        spell_names = sorted([spell[1] for spell in workflow_state.selected_spells])
        total_spells = len(spell_names)

        # Show progress if we have many spells to validate
        show_progress = total_spells > 5
        if show_progress:
            self._show_progress("Validating URLs...", total_spells)

        for idx, spell_name in enumerate(spell_names):
            # Update progress
            if show_progress:
                self._update_progress(idx + 1, f"Validating {spell_name}...")

            # Generate default primary URL (e.g., online documentation link)
            if spell_name not in self.default_primary_urls:
                self.default_primary_urls[spell_name] = self._generate_default_url(
                    spell_name
                )

            # If preserve URLs is set for this spell, use the original URLs from cache
            if workflow_state.preserve_urls.get(spell_name, False):
                # Try to get preserved URLs from spell_data_cache
                preserved_primary = workflow_state.get_spell_data(
                    spell_name, "primary_url", ""
                )
                preserved_secondary = workflow_state.get_spell_data(
                    spell_name, "secondary_url", ""
                )
                self.primary_urls[spell_name] = (
                    preserved_primary or self.default_primary_urls[spell_name]
                )
                self.secondary_urls[spell_name] = preserved_secondary

                # Validate the preserved URLs
                if self.primary_urls[spell_name]:
                    is_valid = self._validate_url(self.primary_urls[spell_name])
                    self.primary_validation[spell_name] = (
                        self.STATE_VALID if is_valid else self.STATE_INVALID
                    )
                else:
                    self.primary_validation[spell_name] = self.STATE_VALID

                if self.secondary_urls[spell_name]:
                    is_valid = self._validate_url(self.secondary_urls[spell_name])
                    self.secondary_validation[spell_name] = (
                        self.STATE_VALID if is_valid else self.STATE_INVALID
                    )
                else:
                    self.secondary_validation[spell_name] = self.STATE_VALID
            else:
                # Initialize URLs if not set
                if spell_name not in self.primary_urls:
                    self.primary_urls[spell_name] = self.default_primary_urls[
                        spell_name
                    ]
                    # Validate default primary URL on first load
                    if self.primary_urls[spell_name]:
                        is_valid = self._validate_url(self.primary_urls[spell_name])
                        self.primary_validation[spell_name] = (
                            self.STATE_VALID if is_valid else self.STATE_INVALID
                        )
                    else:
                        self.primary_validation[spell_name] = self.STATE_VALID
                if spell_name not in self.secondary_urls:
                    self.secondary_urls[spell_name] = self.original_secondary_urls.get(
                        spell_name, ""
                    )
                    # Empty URLs are considered valid
                    self.secondary_validation[spell_name] = (
                        self.STATE_VALID
                        if not self.secondary_urls[spell_name]
                        else self.STATE_UNVALIDATED
                    )

            self._update_tree_item(spell_name)

        # Hide progress when done
        if show_progress:
            self._hide_progress()

    def _generate_default_url(self, spell_name: str) -> str:
        """Generate default documentation URL for a spell."""
        # Generate a default URL (d20pfsrd format)
        spell_slug = spell_name.lower().replace(" ", "-").replace("'", "")
        base_url = "https://www.d20pfsrd.com/magic/all-spells"
        return f"{base_url}/{spell_slug[0]}/{spell_slug}"  # No trailing slash

    def _guess_secondary_urls(self):
        """Show dialog to guess secondary URLs."""
        spell_names = [spell[1] for spell in workflow_state.selected_spells]

        assert self.content_frame is not None, "Content frame must be initialized"
        dialog = URLGuessDialog(self.content_frame.winfo_toplevel(), spell_names)
        self.content_frame.wait_window(dialog)

        if dialog.result:
            pattern = dialog.result
            total_spells = len(spell_names)

            # Show progress for URL generation and validation
            self._show_progress("Generating and validating URLs...", total_spells)

            for idx, spell_name in enumerate(spell_names):
                # Update progress
                self._update_progress(idx + 1, f"Validating {spell_name}...")

                # Generate URL for this spell
                url = self._generate_guessed_url(spell_name, pattern)
                self.secondary_urls[spell_name] = url

                # Validate the generated URL immediately
                if url:
                    is_valid = self._validate_url(url)
                    self.secondary_validation[spell_name] = (
                        self.STATE_VALID if is_valid else self.STATE_INVALID
                    )
                else:
                    self.secondary_validation[spell_name] = self.STATE_VALID

                # Also update the cache so it persists if preserve URLs is set
                workflow_state.set_spell_data(spell_name, "secondary_url", url)

            # Hide progress
            self._hide_progress()

            self._load_spell_data()
            if self.on_urls_changed:
                self.on_urls_changed()

    def _generate_guessed_url(self, spell_name: str, pattern: str) -> str:
        """Generate a guessed URL based on pattern, with translation."""
        if pattern == "german":
            # German 5footstep.de pattern
            # Translate spell name to German using deep-translator
            target_lang = getattr(workflow_state, "secondary_language_code", "de")
            try:
                translator = GoogleTranslator(source="auto", target=target_lang)
                translated = translator.translate(spell_name)
            except (ValueError, TypeError, ConnectionError):
                # Fallback to original if translation fails
                translated = spell_name
            spell_part = translated.replace(" ", "-").replace("'", "")
            return f"http://prd.5footstep.de/Grundregelwerk/Zauber/{spell_part}"
        return ""

    def _validate_url(self, url: str) -> bool:
        """Validate if a URL exists (returns True if accessible)."""
        if not url:
            return True  # Empty URLs are considered valid

        # Only validate strings that look like URLs
        # Allow arbitrary text (not URLs) without validation
        if not url.strip().startswith(("http://", "https://")):
            return True  # Non-URL text is valid (no validation needed)

        try:
            # Encode URL properly for non-ASCII characters (e.g., German umlauts)
            # Parse the URL and encode the path component
            parsed = urllib.parse.urlparse(url)
            # Encode the path to handle special characters
            encoded_path = urllib.parse.quote(parsed.path.encode("utf-8"), safe="/:")
            # Reconstruct the URL with encoded path
            encoded_url = urllib.parse.urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    encoded_path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment,
                )
            )

            # Set a short timeout for validation
            # Add User-Agent header to avoid being blocked by anti-bot measures
            req = urllib.request.Request(encoded_url, method="HEAD")
            req.add_header(
                "User-Agent",
                "Mozilla/5.0 (Spell Card Generator) AppleWebKit/537.36",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                return bool(response.status == 200)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            return False

    def _on_tree_click(self, event):
        """Handle single click events (for reset buttons)."""
        if not self.spells_tree:
            return

        region = self.spells_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.spells_tree.identify("column", event.x, event.y)
            item = self.spells_tree.identify("item", event.x, event.y)

            if not item:
                return

            tags = self.spells_tree.item(item, "tags")
            if not tags:
                return
            spell_name = tags[0]

            # Check if clicked on reset/visit buttons
            if column == "#3":  # Reset primary
                self._reset_primary_url(spell_name)
            elif column == "#4":  # Visit primary
                url = self.primary_urls.get(spell_name, "")
                self._visit_url(url)
            elif column == "#6":  # Reset secondary
                self._reset_secondary_url(spell_name)
            elif column == "#7":  # Visit secondary
                url = self.secondary_urls.get(spell_name, "")
                self._visit_url(url)

    def _on_tree_double_click(self, event):
        """Handle double-click to edit URL."""
        if not self.spells_tree:
            return

        region = self.spells_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.spells_tree.identify("column", event.x, event.y)
        item = self.spells_tree.identify("item", event.x, event.y)

        if not item:
            return

        # Only allow editing URL columns, not spell name or reset buttons
        if column not in ("#2", "#5"):
            return

        tags = self.spells_tree.item(item, "tags")
        if not tags:
            return
        spell_name = tags[0]

        # Determine which URL to edit
        is_primary = column == "#2"
        current_value = (
            self.primary_urls.get(spell_name, "")
            if is_primary
            else self.secondary_urls.get(spell_name, "")
        )

        # Get cell position
        bbox = self.spells_tree.bbox(item, column)
        if not bbox:
            return

        # Create entry widget for editing
        self._edit_cell(spell_name, is_primary, current_value, bbox)

    def _edit_cell(self, spell_name: str, is_primary: bool, current_value: str, bbox):
        """Create an entry widget to edit a cell."""
        x, y, width, height = bbox

        # Strip status symbol if present
        url_to_edit = current_value
        for symbol in [self.SYMBOL_VALID, self.SYMBOL_INVALID, self.SYMBOL_UNVALIDATED]:
            if url_to_edit.startswith(f"{symbol} "):
                url_to_edit = url_to_edit[2:]  # Remove symbol and space
                break

        # Create entry widget
        entry = ttk.Entry(self.spells_tree)
        entry.insert(0, url_to_edit)
        entry.select_range(0, tk.END)
        entry.focus()

        # Position entry over cell
        entry.place(x=x, y=y, width=width, height=height)

        def save_and_destroy(event=None):  # pylint: disable=unused-argument
            """Save the edited value and destroy the entry."""
            new_value = entry.get().strip()

            # Update URL
            if is_primary:
                self.primary_urls[spell_name] = new_value
            else:
                self.secondary_urls[spell_name] = new_value

            # Validate URL and update state
            if not new_value:
                # Empty URL is valid
                state = self.STATE_VALID
            else:
                is_valid = self._validate_url(new_value)
                state = self.STATE_VALID if is_valid else self.STATE_INVALID

            if is_primary:
                self.primary_validation[spell_name] = state
            else:
                self.secondary_validation[spell_name] = state

            self._update_tree_item(spell_name)
            entry.destroy()

            if self.on_urls_changed:
                self.on_urls_changed()

        def cancel_edit(event=None):  # pylint: disable=unused-argument
            """Cancel editing and destroy the entry."""
            entry.destroy()

        # Bind events
        entry.bind("<Return>", save_and_destroy)
        entry.bind("<Escape>", cancel_edit)
        entry.bind("<FocusOut>", save_and_destroy)

    def _reset_primary_url(self, spell_name: str):
        """Reset primary URL to default for a specific spell."""
        self.primary_urls[spell_name] = self.default_primary_urls.get(spell_name, "")
        # Validate the reset URL
        if self.primary_urls[spell_name]:
            is_valid = self._validate_url(self.primary_urls[spell_name])
            self.primary_validation[spell_name] = (
                self.STATE_VALID if is_valid else self.STATE_INVALID
            )
        else:
            self.primary_validation[spell_name] = self.STATE_VALID
        self._update_tree_item(spell_name)
        if self.on_urls_changed:
            self.on_urls_changed()

    def _reset_secondary_url(self, spell_name: str):
        """Reset secondary URL to original for a specific spell."""
        self.secondary_urls[spell_name] = self.original_secondary_urls.get(
            spell_name, ""
        )
        self.secondary_validation[spell_name] = (
            self.STATE_VALID
            if not self.secondary_urls[spell_name]
            else self.STATE_UNVALIDATED
        )
        self._update_tree_item(spell_name)
        if self.on_urls_changed:
            self.on_urls_changed()

    def _visit_url(self, url: str):
        """Open URL in default browser."""
        if url:
            webbrowser.open(url)

    def _reset_all_primary(self):
        """Reset all primary URLs to defaults."""
        spell_names = list(self.primary_urls.keys())
        total_spells = len(spell_names)

        # Show progress if we have many spells
        show_progress = total_spells > 5
        if show_progress:
            self._show_progress("Resetting and validating URLs...", total_spells)

        for idx, spell_name in enumerate(spell_names):
            if show_progress:
                self._update_progress(idx + 1, f"Validating {spell_name}...")

            self.primary_urls[spell_name] = self.default_primary_urls.get(
                spell_name, ""
            )
            # Validate each reset URL
            if self.primary_urls[spell_name]:
                is_valid = self._validate_url(self.primary_urls[spell_name])
                self.primary_validation[spell_name] = (
                    self.STATE_VALID if is_valid else self.STATE_INVALID
                )
            else:
                self.primary_validation[spell_name] = self.STATE_VALID

        if show_progress:
            self._hide_progress()

        self._load_spell_data()
        if self.on_urls_changed:
            self.on_urls_changed()

    def _update_tree_item(self, spell_name: str):
        """Update or create tree item for a spell with colored status symbols."""
        if not self.spells_tree:
            return

        # Get URLs and validation states
        primary = self.primary_urls.get(spell_name, "")
        secondary = self.secondary_urls.get(spell_name, "")
        primary_state = self.primary_validation.get(spell_name, self.STATE_UNVALIDATED)
        secondary_state = self.secondary_validation.get(
            spell_name, self.STATE_UNVALIDATED
        )

        # Save URLs and validation status to workflow state
        workflow_state.set_spell_data(spell_name, "primary_url", primary)
        workflow_state.set_spell_data(
            spell_name, "primary_url_valid", primary_state == self.STATE_VALID
        )
        workflow_state.set_spell_data(spell_name, "secondary_url", secondary)
        workflow_state.set_spell_data(
            spell_name, "secondary_url_valid", secondary_state == self.STATE_VALID
        )

        # Format URLs with status symbols
        primary_display = self._format_url_with_status(primary, primary_state)
        secondary_display = self._format_url_with_status(secondary, secondary_state)

        # Determine overall tag for row (use worst state for coloring)
        if self.STATE_INVALID in (primary_state, secondary_state):
            row_tag = self.STATE_INVALID
        elif self.STATE_UNVALIDATED in (primary_state, secondary_state):
            row_tag = self.STATE_UNVALIDATED
        else:
            row_tag = self.STATE_VALID

        # Find existing item
        existing_item = None
        for item in self.spells_tree.get_children():
            tags = self.spells_tree.item(item, "tags")
            if tags and spell_name in tags:
                existing_item = item
                break

        if existing_item:
            # Update existing item using item() method
            # This is as close to "in-place" as Treeview allows
            self.spells_tree.item(
                existing_item,
                values=(
                    spell_name,
                    primary_display,
                    "R",
                    "V",
                    secondary_display,
                    "R",
                    "V",
                ),
                tags=(spell_name, row_tag),
            )
        else:
            # Insert new item at the end (used during initial load)
            self.spells_tree.insert(
                "",
                tk.END,
                values=(
                    spell_name,
                    primary_display,
                    "R",
                    "V",
                    secondary_display,
                    "R",
                    "V",
                ),
                tags=(spell_name, row_tag),
            )

    def _format_url_with_status(self, url: str, state: str) -> str:
        """Format URL with validation status symbol."""
        if not url:
            return ""

        symbol = {
            self.STATE_VALID: self.SYMBOL_VALID,
            self.STATE_INVALID: self.SYMBOL_INVALID,
            self.STATE_UNVALIDATED: self.SYMBOL_UNVALIDATED,
        }.get(state, self.SYMBOL_UNVALIDATED)

        return f"{symbol} {url}"

    def refresh_ui(self):
        """Refresh the UI with current state."""
        self._load_spell_data()

    def is_step_complete(self) -> bool:
        """Check if the step is complete."""
        return True  # URLs are optional

    def get_next_step_index(self) -> int:
        """Get the next step index."""
        return 4  # Go to preview & generate

    def get_previous_step_index(self) -> int:
        """Get the previous step index."""
        # Check if we should go back through overwrite step
        if workflow_state.conflicts_detected:
            return 2  # Go to overwrite cards
        return 1  # Go to spell selection
