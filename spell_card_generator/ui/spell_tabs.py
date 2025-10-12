"""Spell tabs UI management."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Set, Optional, List, Tuple
import pandas as pd

from spell_card_generator.config.constants import UIConfig
from spell_card_generator.models.spell import ClassTabState
from spell_card_generator.data.loader import SpellDataLoader
from spell_card_generator.data.filter import SpellFilter


class SpellTabManager:
    """Manages the spell list tabs UI."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        data_loader: SpellDataLoader,
        spell_filter: SpellFilter,
        spell_selection_callback=None,
        double_click_callback=None,
    ):
        self.parent_frame = parent_frame
        self.data_loader = data_loader
        self.spell_filter = spell_filter
        self.spell_selection_callback = spell_selection_callback
        self.double_click_callback = double_click_callback

        # State management
        self.spell_data: Dict[str, ClassTabState] = {}
        self.current_classes: Set[str] = set()

        # Persistent spell selection state (spell_name -> is_selected)
        self.selected_spells_state: Dict[str, bool] = {}

    def update_tabs(self, selected_classes: Set[str]):
        """Update tabs based on selected classes."""
        self.current_classes = selected_classes

        # Clear existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.spell_data.clear()

        if not selected_classes:
            # This shouldn't happen with the new single-class selection UI
            # but we keep it as a fallback
            return

        # Create content for single class (get the first and only class)
        selected_class = next(iter(selected_classes))
        self._create_spell_content_for_class(selected_class)

    def _create_spell_content_for_class(self, class_name: str):
        """Create spell content for a specific class."""
        # Configure parent frame to expand properly
        self.parent_frame.rowconfigure(0, weight=1)
        self.parent_frame.columnconfigure(0, weight=1)

        # Create main frame directly in parent frame using pack for better resizing
        content_frame = ttk.Frame(self.parent_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Create filter controls (fixed height at top)
        filters_frame = self._create_filters_frame(content_frame, class_name)

        # Create spell list (expandable area below filters)
        spells_tree = self._create_spells_list(content_frame, class_name)

        # Create class tab state
        level_var, source_var, search_var = self._get_filter_variables(filters_frame)
        level_combo, source_combo, search_entry = self._get_filter_widgets(
            filters_frame
        )

        self.spell_data[class_name] = ClassTabState(
            frame=content_frame,
            level_var=level_var,
            source_var=source_var,
            search_var=search_var,
            spells_tree=spells_tree,
            level_combo=level_combo,
            source_combo=source_combo,
            search_entry=search_entry,
            filtered_spells=None,
        )

        # Setup filters for this class
        self._setup_class_filters(class_name)

    def _create_filters_frame(
        self, parent_frame: ttk.Frame, class_name: str
    ) -> ttk.LabelFrame:
        """Create filters frame for a class tab."""
        filters_frame = ttk.LabelFrame(
            parent_frame, text="Filters", padding=UIConfig.MAIN_PADDING
        )
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        filters_frame.columnconfigure(1, weight=1)

        # Create variables
        level_var = tk.StringVar(value="All")
        source_var = tk.StringVar(value="All")
        search_var = tk.StringVar()

        # Spell level filter
        ttk.Label(filters_frame, text="Spell Level:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        level_combo = ttk.Combobox(
            filters_frame, textvariable=level_var, state="readonly"
        )
        level_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        level_combo.bind(
            "<<ComboboxSelected>>", lambda e: self._apply_filters(class_name)
        )

        # Source book filter
        ttk.Label(filters_frame, text="Source Book:").grid(
            row=0, column=2, sticky=tk.W, padx=(10, 5)
        )
        source_combo = ttk.Combobox(
            filters_frame, textvariable=source_var, state="readonly"
        )
        source_combo.grid(row=0, column=3, sticky=(tk.W, tk.E))
        source_combo.bind(
            "<<ComboboxSelected>>", lambda e: self._apply_filters(class_name)
        )

        # Search by name
        ttk.Label(filters_frame, text="Search Name:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5)
        )
        search_entry = ttk.Entry(filters_frame, textvariable=search_var)
        search_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self._apply_filters(class_name))

        # Store references in the frame for later retrieval  # pylint: disable=protected-access
        filters_frame._level_var = level_var
        filters_frame._source_var = source_var
        filters_frame._search_var = search_var
        filters_frame._level_combo = level_combo
        filters_frame._source_combo = source_combo
        filters_frame._search_entry = search_entry

        return filters_frame

    def _create_spells_list(
        self, parent_frame: ttk.Frame, class_name: str
    ) -> ttk.Treeview:
        """Create spells list for a class tab."""
        # Content frame for spells list and buttons - this should expand
        content_frame = ttk.Frame(parent_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Spells list frame (left side, expandable)
        list_frame = ttk.Frame(content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        # Spells treeview
        spells_tree = ttk.Treeview(
            list_frame,
            columns=UIConfig.TREE_COLUMNS,
            show="headings",
            height=UIConfig.TREE_HEIGHT,
        )

        # Configure columns
        for col in UIConfig.TREE_COLUMNS:
            # Center align the Select column for better checkbox visibility
            anchor = "center" if col == "Select" else "w"
            spells_tree.column(
                col,
                width=UIConfig.TREE_COLUMN_WIDTHS[col],
                minwidth=UIConfig.TREE_COLUMN_MIN_WIDTHS[col],
                anchor=anchor,
            )
            spells_tree.heading(col, text=col)

        spells_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=spells_tree.yview
        )
        tree_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        spells_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Bind click event for spell selection (only in Select column)
        spells_tree.bind("<Button-1>", lambda e: self._on_tree_click(e, spells_tree))

        # Bind keyboard events
        spells_tree.bind(
            "<KeyPress-space>", lambda e: self._toggle_selected_spells(spells_tree)
        )
        spells_tree.bind(
            "<Return>", lambda e: self._toggle_selected_spells(spells_tree)
        )

        # Allow the treeview to get focus for keyboard events
        spells_tree.bind("<Button-1>", lambda e: spells_tree.focus_set(), add="+")

        # Enable extended selection mode for multi-row selection
        spells_tree.configure(selectmode="extended")

        # Bind double-click event to toggle selection instead of navigation
        spells_tree.bind(
            "<Double-1>", lambda e: self._on_double_click_toggle(e, spells_tree)
        )

        # Selection buttons frame (right side, fixed width)
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=tk.Y, side=tk.RIGHT, anchor=tk.N)

        ttk.Button(
            buttons_frame,
            text="Select All",
            command=lambda: self._select_all_spells(class_name),
        ).pack(pady=(0, 5), fill=tk.X)

        ttk.Button(
            buttons_frame,
            text="Deselect All",
            command=lambda: self._deselect_all_spells(class_name),
        ).pack(pady=(0, 5), fill=tk.X)

        ttk.Button(
            buttons_frame,
            text="Preview Spell",
            command=lambda: self._preview_spell(class_name),
        ).pack(pady=(0, 20), fill=tk.X)

        return spells_tree

    def _get_filter_variables(self, filters_frame: ttk.LabelFrame):
        """Get filter variables from filters frame."""
        return (
            filters_frame._level_var,  # pylint: disable=protected-access
            filters_frame._source_var,  # pylint: disable=protected-access
            filters_frame._search_var,  # pylint: disable=protected-access
        )

    def _get_filter_widgets(self, filters_frame: ttk.LabelFrame):
        """Get filter widgets from filters frame."""
        return (
            filters_frame._level_combo,  # pylint: disable=protected-access
            filters_frame._source_combo,  # pylint: disable=protected-access
            filters_frame._search_entry,  # pylint: disable=protected-access
        )

    def _setup_class_filters(self, class_name: str):
        """Setup filters for a specific character class."""
        if self.data_loader.spells_df is None or class_name not in self.spell_data:
            return

        class_data = self.spell_data[class_name]

        # Update level filter options
        levels = self.spell_filter.get_available_levels(
            self.data_loader.spells_df, class_name
        )
        class_data.level_combo["values"] = levels

        # Update source filter options
        # pylint: disable=protected-access
        sources = self.spell_filter.get_available_sources(
            self.data_loader.spells_df, class_name
        )
        class_data.source_combo["values"] = sources

        # Apply initial filters
        self._apply_filters(class_name)

    def _apply_filters(self, class_name: str):
        """Apply filters to spell list for a specific class."""
        if self.data_loader.spells_df is None or class_name not in self.spell_data:
            return

        class_data = self.spell_data[class_name]

        # Apply filters  # pylint: disable=protected-access
        filtered_df = self.spell_filter.filter_spells(
            self.data_loader.spells_df,
            class_name,
            level=(
                class_data.level_var.get()
                if class_data.level_var.get() != "All"
                else None
            ),
            source=(
                class_data.source_var.get()
                if class_data.source_var.get() != "All"
                else None
            ),
            search_term=class_data.search_var.get(),
        )

        class_data.filtered_spells = filtered_df
        self._update_spells_list(class_name)

    def _update_spells_list(self, class_name: str):
        """Update the spells treeview with filtered results."""
        if class_name not in self.spell_data:
            return

        class_data = self.spell_data[class_name]
        spells_tree = class_data.spells_tree
        filtered_spells = class_data.filtered_spells

        # Clear existing items
        for item in spells_tree.get_children():
            spells_tree.delete(item)

        if filtered_spells is None or filtered_spells.empty:
            return

        # Add filtered spells to treeview
        for _, spell in filtered_spells.iterrows():
            spell_name = spell["name"]

            # Check if this spell was previously selected
            is_selected = self.selected_spells_state.get(spell_name, False)

            item = spells_tree.insert(
                "",
                "end",
                values=(
                    UIConfig.CHECKED_ICON if is_selected else UIConfig.UNCHECKED_ICON,
                    spell_name,
                    spell[class_name],
                    spell["school"],
                    spell["source"],
                ),
                tags=("checked" if is_selected else "unchecked",),
            )

    def _on_tree_click(self, event, spells_tree: ttk.Treeview):
        """Handle tree click - only toggle selection if clicking in Select column."""
        item = spells_tree.identify("item", event.x, event.y)
        column = spells_tree.identify("column", event.x, event.y)

        if item and column == "#1":  # Select column is #1
            self._toggle_spell_selection_for_item(item, spells_tree)
        # Other clicks just select the row for highlighting

    def _toggle_spell_selection_for_item(self, item, spells_tree: ttk.Treeview):
        """Toggle spell selection for a specific item."""
        spell_name = spells_tree.item(item)["values"][1]  # Name is in column 1

        # Update persistent state
        current_state = self.selected_spells_state.get(spell_name, False)
        self.selected_spells_state[spell_name] = not current_state

        # Update UI
        if self.selected_spells_state[spell_name]:
            spells_tree.set(item, "Select", UIConfig.CHECKED_ICON)
            spells_tree.item(item, tags=("checked",))
        else:
            spells_tree.set(item, "Select", UIConfig.UNCHECKED_ICON)
            spells_tree.item(item, tags=("unchecked",))

        # Notify callback about selection change
        if self.spell_selection_callback:
            self.spell_selection_callback()

    def _toggle_selected_spells(self, spells_tree: ttk.Treeview):
        """Toggle selection for all highlighted/selected items (Space/Enter key)."""
        selection = spells_tree.selection()
        if not selection:
            # If no items are selected, try to select the item with focus
            focus_item = spells_tree.focus()
            if focus_item:
                selection = (focus_item,)
            else:
                return

        for item in selection:
            self._toggle_spell_selection_for_item(item, spells_tree)

    def _on_double_click_toggle(self, event, spells_tree: ttk.Treeview):
        """Handle double-click to toggle spell selection."""
        item = spells_tree.identify("item", event.x, event.y)
        if item:
            self._toggle_spell_selection_for_item(item, spells_tree)

    def _on_double_click(self, event):  # pylint: disable=unused-argument
        """Handle double-click on spell list (legacy method for navigation)."""
        if self.double_click_callback:
            self.double_click_callback()

    def _select_all_spells(self, class_name: str):
        """Select all visible spells for a specific class."""
        if class_name not in self.spell_data:
            return

        spells_tree = self.spell_data[class_name].spells_tree
        for item in spells_tree.get_children():
            spell_name = spells_tree.item(item)["values"][1]
            self.selected_spells_state[spell_name] = True
            spells_tree.set(item, "Select", UIConfig.CHECKED_ICON)
            spells_tree.item(item, tags=("checked",))

        # Notify callback about selection change
        if self.spell_selection_callback:
            self.spell_selection_callback()

    def _deselect_all_spells(self, class_name: str):
        """Deselect all spells for a specific class."""
        if class_name not in self.spell_data:
            return

        spells_tree = self.spell_data[class_name].spells_tree
        for item in spells_tree.get_children():
            spell_name = spells_tree.item(item)["values"][1]
            self.selected_spells_state[spell_name] = False
            spells_tree.set(item, "Select", UIConfig.UNCHECKED_ICON)
            spells_tree.item(item, tags=("unchecked",))

        # Notify callback about selection change
        if self.spell_selection_callback:
            self.spell_selection_callback()

    def _preview_spell(self, class_name: str):
        """Preview selected spell details."""
        if class_name not in self.spell_data:
            return

        class_data = self.spell_data[class_name]
        spells_tree = class_data.spells_tree
        filtered_spells = class_data.filtered_spells

        selection = spells_tree.selection()
        if not selection:
            # Show warning - we'll need to import this from dialogs
            return

        # Get spell name from selection
        item = selection[0]
        spell_name = spells_tree.item(item)["values"][1]  # Name is in column 1

        # Find spell in dataframe
        if filtered_spells is not None and not filtered_spells.empty:
            spell_matches = filtered_spells[filtered_spells["name"] == spell_name]
            if not spell_matches.empty:
                spell_data = spell_matches.iloc[0]
                self._show_spell_preview(spell_name, spell_data, class_name)

    def _show_spell_preview(
        self, spell_name: str, spell_data: pd.Series, class_name: str
    ):
        """Show spell preview window."""
        # Create preview window
        preview_window = tk.Toplevel()
        preview_window.title(f"Preview: {spell_name}")
        preview_window.geometry("600x400")

        # Create scrolled text widget
        text_widget = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format spell information
        preview_text = f"Name: {spell_data['name']}\\n"
        preview_text += f"School: {spell_data['school']}\\n"
        preview_text += f"Level: {spell_data[class_name]}\\n"
        preview_text += f"Casting Time: {spell_data['casting_time']}\\n"
        preview_text += f"Components: {spell_data['components']}\\n"
        preview_text += f"Range: {spell_data['range']}\\n"
        preview_text += f"Duration: {spell_data['duration']}\\n"
        preview_text += f"Saving Throw: {spell_data['saving_throw']}\\n"
        preview_text += f"Spell Resistance: {spell_data['spell_resistance']}\\n\\n"
        preview_text += f"Description:\\n{spell_data['description']}\\n"

        text_widget.insert(tk.END, preview_text)
        text_widget.config(state=tk.DISABLED)

    def get_selected_spells(self) -> List[Tuple[str, str, pd.Series]]:
        """Get all selected spells based on persistent selection state."""
        selected_spells = []

        # Get the current class (we're using single class selection now)
        current_class = self.get_current_class()
        if not current_class:
            return selected_spells

        # Get all spells for this class from the data loader
        all_spells = self.data_loader.get_spells_for_class(current_class)

        # Filter based on persistent selection state
        for spell_name, is_selected in self.selected_spells_state.items():
            if is_selected:
                spell_matches = all_spells[all_spells["name"] == spell_name]
                if not spell_matches.empty:
                    spell_data = spell_matches.iloc[0]
                    selected_spells.append((current_class, spell_name, spell_data))

        return selected_spells

    def get_current_class(self) -> Optional[str]:
        """Get the currently selected class."""
        return next(iter(self.current_classes)) if self.current_classes else None
