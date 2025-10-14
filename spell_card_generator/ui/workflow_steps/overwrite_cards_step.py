"""Workflow step for managing overwrite decisions for existing spell cards."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import datetime

from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep
from spell_card_generator.ui.workflow_state import workflow_state
from spell_card_generator.utils.file_scanner import FileScanner


class OverwriteCardsStep(BaseWorkflowStep):
    """Step for managing overwrite decisions for existing spell cards."""

    step_name = "Overwrite Cards"
    step_description = "Manage conflicts with existing spell card files"

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        navigation_callback: Callable[[int], None],
        on_overwrite_changed: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.on_overwrite_changed = on_overwrite_changed

        # UI components
        self.conflicts_tree: Optional[ttk.Treeview] = None
        self.selection_frame: Optional[ttk.Frame] = None

    def create_step_content(self):
        """Create the overwrite management step content."""
        # Title
        title_label = ttk.Label(
            self.content_frame,
            text="Existing Spell Cards Detected",
            font=("TkDefaultFont", 12, "bold"),
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))

        # Create grid container for description and bulk actions
        top_container = ttk.Frame(self.content_frame)
        top_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # pylint: disable=duplicate-code
        # Configure grid: description on left, bulk actions on right
        top_container.grid_rowconfigure(0, weight=0)
        top_container.columnconfigure(0, weight=1)  # Description column stretches
        top_container.columnconfigure(1, weight=0)  # Bulk actions column fixed width

        # Row 0, Col 0: Description (with dynamic wrapping)
        desc_frame = ttk.Frame(top_container)
        desc_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 20))
        desc_frame.columnconfigure(0, weight=1)

        desc_label = ttk.Label(
            desc_frame,
            text=(
                "Some selected spells already have generated card files. "
                "Choose which ones to overwrite and what to preserve.\n"
                "Click checkboxes to toggle options:"
            ),
            justify=tk.LEFT,
        )
        desc_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Bind to configure event to update wraplength dynamically
        def update_wraplength(event):
            desc_label.configure(wraplength=event.width - 10)

        desc_frame.bind("<Configure>", update_wraplength)

        # Row 0, Col 1: Bulk actions
        self._create_bulk_actions(top_container)
        # pylint: enable=duplicate-code

        # Conflicts tree view spans full width below
        self._create_conflicts_tree(self.content_frame)

        # Populate the tree with current conflicts
        self._populate_conflicts()

        # Update validation
        self._update_validation()

    def _create_conflicts_tree(self, parent: ttk.Frame):
        """Create the conflicts treeview."""
        tree_frame = ttk.LabelFrame(parent, text="Conflicting Spell Cards", padding=5)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create treeview with scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Treeview - reordered columns with checkboxes on the left
        columns = (
            "overwrite",
            "preserve_desc",
            "preserve_urls",
            "spell",
            "modified",
        )
        self.conflicts_tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", selectmode="extended"
        )

        # Configure columns - checkboxes first, then spell info
        self.conflicts_tree.heading("overwrite", text="Overwrite")
        self.conflicts_tree.heading("preserve_desc", text="Preserve Description")
        self.conflicts_tree.heading("preserve_urls", text="Preserve URLs")
        self.conflicts_tree.heading("spell", text="Spell Name")
        self.conflicts_tree.heading("modified", text="Last Modified")

        # Column widths - checkboxes narrower, spell info wider
        self.conflicts_tree.column("overwrite", width=100, minwidth=80, anchor="center")
        self.conflicts_tree.column(
            "preserve_desc", width=150, minwidth=120, anchor="center"
        )
        self.conflicts_tree.column(
            "preserve_urls", width=150, minwidth=120, anchor="center"
        )
        self.conflicts_tree.column("spell", width=250, minwidth=150)
        self.conflicts_tree.column("modified", width=150, minwidth=120)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL, command=self.conflicts_tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.HORIZONTAL, command=self.conflicts_tree.xview
        )
        self.conflicts_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Pack tree and scrollbars
        self.conflicts_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Bind events - click to toggle checkboxes
        self.conflicts_tree.bind("<Button-1>", self._on_tree_click)
        self.conflicts_tree.bind("<space>", self._on_tree_space)
        self.conflicts_tree.bind("<Return>", self._on_tree_space)

    def _create_bulk_actions(self, parent: ttk.Frame):
        """Create bulk action buttons in a grid layout."""
        actions_frame = ttk.LabelFrame(parent, text="Bulk Actions", padding=10)
        actions_frame.grid(row=0, column=1, sticky=tk.NE)

        # Configure grid columns: label, button1, button2
        actions_frame.columnconfigure(0, weight=0)  # Label column (fixed width)
        actions_frame.columnconfigure(1, weight=0)  # Button columns (no stretch)
        actions_frame.columnconfigure(2, weight=0)

        # Row 0: Overwrite
        ttk.Label(actions_frame, text="Overwrite:", anchor=tk.E).grid(
            row=0, column=0, sticky=tk.E, padx=(0, 10), pady=5
        )
        ttk.Button(
            actions_frame, text="Overwrite All", command=self._select_all_overwrite
        ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            actions_frame, text="Skip All", command=self._select_none_overwrite
        ).grid(row=0, column=2, padx=5, pady=5)

        # Row 1: Description
        ttk.Label(actions_frame, text="Preserve Description:", anchor=tk.E).grid(
            row=1, column=0, sticky=tk.E, padx=(0, 10), pady=5
        )
        ttk.Button(
            actions_frame,
            text="Preserve All",
            command=self._select_all_preserve_desc,
        ).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            actions_frame,
            text="Clear All",
            command=self._clear_all_preserve_desc,
        ).grid(row=1, column=2, padx=5, pady=5)

        # Row 2: URLs
        ttk.Label(actions_frame, text="Preserve URLs:", anchor=tk.E).grid(
            row=2, column=0, sticky=tk.E, padx=(0, 10), pady=5
        )
        ttk.Button(
            actions_frame,
            text="Preserve All",
            command=self._select_all_preserve_urls,
        ).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(
            actions_frame,
            text="Clear All",
            command=self._clear_all_preserve_urls,
        ).grid(row=2, column=2, padx=5, pady=5)

    def _populate_conflicts(self):
        """Populate the conflicts tree with current data."""
        if not self.conflicts_tree:
            return

        # Clear existing items
        for item in self.conflicts_tree.get_children():
            self.conflicts_tree.delete(item)

        # Get conflicts summary for file analysis
        summary = FileScanner.get_conflicts_summary(workflow_state.existing_cards)

        # Add items to tree and cache URLs for each existing spell
        for spell_name, _file_path in workflow_state.existing_cards.items():
            analysis = summary["analyses"].get(spell_name, {})

            # Cache the URLs from existing files for potential preservation
            primary_url = analysis.get("primary_url", "")
            secondary_url = analysis.get("secondary_url", "")
            workflow_state.set_spell_data(spell_name, "primary_url", primary_url)
            workflow_state.set_spell_data(spell_name, "secondary_url", secondary_url)

            # Get current decisions with defaults
            overwrite = workflow_state.overwrite_decisions.get(spell_name, False)
            preserve_desc = workflow_state.preserve_description.get(spell_name, False)
            preserve_urls = workflow_state.preserve_urls.get(spell_name, False)

            # Format checkboxes with more visible characters
            overwrite_text = "[X]" if overwrite else "[ ]"
            preserve_desc_text = "[X]" if preserve_desc else "[ ]"
            preserve_urls_text = "[X]" if preserve_urls else "[ ]"

            # Format modification time
            modified_text = self._format_modification_time(
                analysis.get("modification_time", 0)
            )

            self.conflicts_tree.insert(
                "",
                tk.END,
                values=(
                    overwrite_text,
                    preserve_desc_text,
                    preserve_urls_text,
                    spell_name,
                    modified_text,
                ),
                tags=(spell_name,),  # Store spell_name in tags for easy lookup
            )

    def _on_tree_click(self, event):
        """Handle tree click events."""
        if not self.conflicts_tree:
            return

        # Determine what was clicked
        region = self.conflicts_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.conflicts_tree.identify("column", event.x, event.y)
            item = self.conflicts_tree.identify("item", event.x, event.y)

            if not item:
                return

            # Get spell name from tags
            tags = self.conflicts_tree.item(item, "tags")
            if not tags:
                return
            spell_name = tags[0]

            # Toggle based on column clicked (updated for new column order)
            if column == "#1":  # Overwrite column
                self._toggle_overwrite(spell_name)
            elif column == "#2":  # Preserve Description column (moved to #2)
                self._toggle_preserve_description(spell_name)
            elif column == "#3":  # Preserve URLs column (moved to #3)
                self._toggle_preserve_urls(spell_name)

    def _on_tree_space(self, event):  # pylint: disable=unused-argument
        """Handle space/enter key to toggle overwrite for selected items."""
        if not self.conflicts_tree:
            return

        selection = self.conflicts_tree.selection()
        for item in selection:
            tags = self.conflicts_tree.item(item, "tags")
            if tags:
                spell_name = tags[0]
                self._toggle_overwrite(spell_name)

    def _toggle_overwrite(self, spell_name: str):
        """Toggle overwrite decision for a specific spell."""
        current_overwrite = workflow_state.overwrite_decisions.get(spell_name, False)
        new_overwrite = not current_overwrite

        # Update state
        workflow_state.overwrite_decisions[spell_name] = new_overwrite

        # Update display
        self._populate_conflicts()

        # Notify callback
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

        # Update validation
        self._update_validation()

    def _toggle_preserve_description(self, spell_name: str):
        """Toggle preserve description decision for a specific spell."""
        current = workflow_state.preserve_description.get(spell_name, False)
        workflow_state.preserve_description[spell_name] = not current
        self._populate_conflicts()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _toggle_preserve_urls(self, spell_name: str):
        """Toggle preserve URLs decision for a specific spell."""
        current = workflow_state.preserve_urls.get(spell_name, False)
        workflow_state.preserve_urls[spell_name] = not current
        # URLs are already cached in _populate_conflicts, no need to do it again
        self._populate_conflicts()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _select_all_overwrite(self):
        """Select all conflicts for overwrite."""
        for spell_name in workflow_state.existing_cards:
            workflow_state.overwrite_decisions[spell_name] = True
        self._populate_conflicts()
        self._update_validation()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _select_none_overwrite(self):
        """Deselect all conflicts."""
        for spell_name in workflow_state.existing_cards:
            workflow_state.overwrite_decisions[spell_name] = False
        self._populate_conflicts()
        self._update_validation()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _select_all_preserve_desc(self):
        """Select preserve description for all spells."""
        for spell_name in workflow_state.existing_cards:
            workflow_state.preserve_description[spell_name] = True
        self._populate_conflicts()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _select_all_preserve_urls(self):
        """Select preserve URLs for all spells."""
        for spell_name in workflow_state.existing_cards:
            workflow_state.preserve_urls[spell_name] = True
        self._populate_conflicts()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _clear_all_preserve_desc(self):
        """Clear preserve description for all spells."""
        for spell_name in workflow_state.existing_cards:
            workflow_state.preserve_description[spell_name] = False
        self._populate_conflicts()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _clear_all_preserve_urls(self):
        """Clear preserve URLs for all spells."""
        for spell_name in workflow_state.existing_cards:
            workflow_state.preserve_urls[spell_name] = False
        self._populate_conflicts()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _update_validation(self):
        """Update step validation based on current selections."""
        # Step is valid if user has made decisions (even if all are "don't overwrite")
        has_decisions = len(workflow_state.overwrite_decisions) > 0
        workflow_state.set_step_valid(self.step_index, has_decisions)

    def _format_modification_time(self, timestamp: float) -> str:
        """Format modification time for display."""
        if timestamp <= 0:
            return "Unknown"
        try:
            dt = datetime.datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, OSError):
            return "Invalid"

    def refresh_ui(self):
        """Refresh the UI with current state."""
        self._populate_conflicts()

    def is_step_complete(self) -> bool:
        """Check if the step is complete."""
        return workflow_state.is_step_valid(self.step_index)

    def get_next_step_index(self) -> int:
        """Get the next step index after handling conflicts."""
        return 3  # Go to documentation URLs

    def get_previous_step_index(self) -> int:
        """Get the previous step index."""
        return 1  # Go back to spell selection
