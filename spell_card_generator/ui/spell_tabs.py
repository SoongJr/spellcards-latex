"""Spell tabs UI management."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Set, Optional, List, Tuple
import pandas as pd

from config.constants import UIConfig, CharacterClasses
from models.spell import ClassTabState
from data.loader import SpellDataLoader
from data.filter import SpellFilter


class SpellTabManager:
    """Manages the spell list tabs UI."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        data_loader: SpellDataLoader,
        spell_filter: SpellFilter,
    ):
        self.parent_frame = parent_frame
        self.data_loader = data_loader
        self.spell_filter = spell_filter

        # State management
        self.spell_data: Dict[str, ClassTabState] = {}
        self.spell_notebook: Optional[ttk.Notebook] = None
        self.current_classes: Set[str] = set()

    def update_tabs(self, selected_classes: Set[str]):
        """Update tabs based on selected classes."""
        self.current_classes = selected_classes

        # Clear existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.spell_data.clear()

        if not selected_classes:
            # Show message when no classes selected
            no_selection_label = ttk.Label(
                self.parent_frame,
                text="Please select one or more character classes to view spell lists",
                font=("TkDefaultFont", 12),
            )
            no_selection_label.pack(expand=True)
            return

        # Create spell content for selected classes
        self._create_spell_content()

    def _create_spell_content(self):
        """Create spell list content for selected classes."""
        # Create notebook for selected classes
        self.spell_notebook = ttk.Notebook(self.parent_frame)
        self.spell_notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs for each selected class
        for class_name in sorted(self.current_classes):
            self._create_spell_tab(class_name)

    def _create_spell_tab(self, class_name: str):
        """Create a spell tab for a specific class."""
        # Create main frame for this tab
        tab_frame = ttk.Frame(self.spell_notebook)
        tab_title = CharacterClasses.DISPLAY_NAMES.get(class_name, class_name.title())
        self.spell_notebook.add(tab_frame, text=tab_title)

        # Configure grid weights
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(1, weight=1)

        # Create filter controls
        filters_frame = self._create_filters_frame(tab_frame, class_name)

        # Create spell list
        spells_tree = self._create_spells_list(tab_frame, class_name)

        # Create class tab state
        level_var, source_var, search_var = self._get_filter_variables(filters_frame)
        level_combo, source_combo, search_entry = self._get_filter_widgets(
            filters_frame
        )

        self.spell_data[class_name] = ClassTabState(
            frame=tab_frame,
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
        filters_frame.grid(
            row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
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

        # Store references in the frame for later retrieval
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
        # Content frame for spells list and buttons
        content_frame = ttk.Frame(parent_frame)
        content_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Spells list frame
        list_frame = ttk.Frame(content_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Spells treeview
        spells_tree = ttk.Treeview(
            list_frame,
            columns=UIConfig.TREE_COLUMNS,
            show="headings",
            height=UIConfig.TREE_HEIGHT,
        )

        # Configure columns
        for col in UIConfig.TREE_COLUMNS:
            spells_tree.column(
                col,
                width=UIConfig.TREE_COLUMN_WIDTHS[col],
                minwidth=UIConfig.TREE_COLUMN_MIN_WIDTHS[col],
            )
            spells_tree.heading(col, text=col)

        spells_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=spells_tree.yview
        )
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        spells_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Bind click event for spell selection
        spells_tree.bind(
            "<Button-1>", lambda e: self._toggle_spell_selection(e, spells_tree)
        )

        # Selection buttons frame
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.W))

        ttk.Button(
            buttons_frame,
            text="Select All",
            command=lambda: self._select_all_spells(class_name),
        ).grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))

        ttk.Button(
            buttons_frame,
            text="Deselect All",
            command=lambda: self._deselect_all_spells(class_name),
        ).grid(row=1, column=0, pady=(0, 5), sticky=(tk.W, tk.E))

        ttk.Button(
            buttons_frame,
            text="Preview Spell",
            command=lambda: self._preview_spell(class_name),
        ).grid(row=2, column=0, pady=(0, 20), sticky=(tk.W, tk.E))

        return spells_tree

    def _get_filter_variables(self, filters_frame: ttk.LabelFrame):
        """Get filter variables from filters frame."""
        return (
            filters_frame._level_var,
            filters_frame._source_var,
            filters_frame._search_var,
        )

    def _get_filter_widgets(self, filters_frame: ttk.LabelFrame):
        """Get filter widgets from filters frame."""
        return (
            filters_frame._level_combo,
            filters_frame._source_combo,
            filters_frame._search_entry,
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

        # Apply filters
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
            spells_tree.insert(
                "",
                "end",
                values=(
                    UIConfig.UNCHECKED_ICON,
                    spell["name"],
                    spell[class_name],
                    spell["school"],
                    spell["source"],
                ),
                tags=("unchecked",),
            )

    def _toggle_spell_selection(self, event, spells_tree: ttk.Treeview):
        """Toggle spell selection on click."""
        item = spells_tree.identify("item", event.x, event.y)
        if item:
            current_tags = spells_tree.item(item, "tags")
            if "checked" in current_tags:
                spells_tree.set(item, "Select", UIConfig.UNCHECKED_ICON)
                spells_tree.item(item, tags=("unchecked",))
            else:
                spells_tree.set(item, "Select", UIConfig.CHECKED_ICON)
                spells_tree.item(item, tags=("checked",))

    def _select_all_spells(self, class_name: str):
        """Select all visible spells for a specific class."""
        if class_name not in self.spell_data:
            return

        spells_tree = self.spell_data[class_name].spells_tree
        for item in spells_tree.get_children():
            spells_tree.set(item, "Select", UIConfig.CHECKED_ICON)
            spells_tree.item(item, tags=("checked",))

    def _deselect_all_spells(self, class_name: str):
        """Deselect all spells for a specific class."""
        if class_name not in self.spell_data:
            return

        spells_tree = self.spell_data[class_name].spells_tree
        for item in spells_tree.get_children():
            spells_tree.set(item, "Select", UIConfig.UNCHECKED_ICON)
            spells_tree.item(item, tags=("unchecked",))

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
        from tkinter import scrolledtext

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
        """Get all selected spells across all tabs."""
        selected_spells = []

        for class_name, class_data in self.spell_data.items():
            spells_tree = class_data.spells_tree
            filtered_spells = class_data.filtered_spells

            if filtered_spells is None or filtered_spells.empty:
                continue

            for item in spells_tree.get_children():
                if "checked" in spells_tree.item(item, "tags"):
                    spell_name = spells_tree.item(item)["values"][
                        1
                    ]  # Name is in column 1
                    spell_matches = filtered_spells[
                        filtered_spells["name"] == spell_name
                    ]
                    if not spell_matches.empty:
                        spell_data = spell_matches.iloc[0]
                        selected_spells.append((class_name, spell_name, spell_data))

        return selected_spells

    def get_current_class(self) -> Optional[str]:
        """Get the currently active class from the spell notebook."""
        if self.spell_notebook and hasattr(self.spell_notebook, "select"):
            try:
                selected_tab = self.spell_notebook.select()
                if selected_tab:
                    tab_index = self.spell_notebook.index(selected_tab)
                    selected_classes = sorted(self.current_classes)
                    if tab_index < len(selected_classes):
                        return selected_classes[tab_index]
            except tk.TclError:
                pass
        return next(iter(self.current_classes)) if self.current_classes else None
