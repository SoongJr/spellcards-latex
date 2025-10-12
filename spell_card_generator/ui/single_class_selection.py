"""Single character class selection UI using treeview."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from spell_card_generator.config.constants import CharacterClasses
from spell_card_generator.utils.class_categorization import categorize_character_classes


class SingleClassSelectionManager:
    """Manages single character class selection using a treeview."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        selection_callback: Callable[[Optional[str]], None],
    ):
        self.parent_frame = parent_frame
        self.selection_callback = selection_callback

        # Current selection
        self.selected_class: Optional[str] = None

        # UI components
        self.tree: ttk.Treeview = None
        self.character_classes: list = []

    def setup_class_tree(self, character_classes: list):
        """Create treeview with character classes organized by category."""
        if not character_classes:
            return

        self.character_classes = character_classes

        # Clear existing UI
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        # Create main layout
        self._create_tree_layout()
        self._populate_tree()

    def _create_tree_layout(self):
        """Create the treeview layout."""
        # Instructions label
        instructions = ttk.Label(
            self.parent_frame,
            text="Select a character class to view and generate spell cards:",
            font=("TkDefaultFont", 10, "bold"),
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Create frame for treeview and scrollbar
        tree_frame = ttk.Frame(self.parent_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Create treeview
        self.tree = ttk.Treeview(tree_frame, show="tree", height=12)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_selection)

        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("TkDefaultFont", 9))
        style.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"))

    def _populate_tree(self):
        """Populate the treeview with character classes."""
        # Get class categories
        categories = categorize_character_classes(self.character_classes)

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add categories and classes
        for category_name, category_data in categories.items():
            # Remove count from category name for display
            display_category = category_name.split(" (")[0]

            # Add category node
            category_id = self.tree.insert("", tk.END, text=display_category, open=True)

            # Add classes under category
            for class_name in category_data["classes"]:
                display_name = self._get_display_name(class_name)
                self.tree.insert(
                    category_id, tk.END, text=display_name, tags=(class_name,)
                )

    def _on_tree_selection(self, event):  # pylint: disable=unused-argument
        """Handle treeview selection changes."""
        selection = self.tree.selection()
        if not selection:
            return

        selected_item = selection[0]

        # Get tags to identify if this is a class (not a category)
        tags = self.tree.item(selected_item, "tags")
        if tags:
            # This is a class selection
            new_class = tags[0]
            if new_class != self.selected_class:
                self.selected_class = new_class
                self.selection_callback(self.selected_class)
        else:
            # This is a category - expand/collapse it
            if self.tree.item(selected_item, "open"):
                self.tree.item(selected_item, open=False)
            else:
                self.tree.item(selected_item, open=True)
            # Clear selection since categories aren't selectable
            self.tree.selection_remove(selected_item)

    def get_selected_class(self) -> Optional[str]:
        """Get the currently selected character class."""
        return self.selected_class

    def clear_selection(self):
        """Clear the current selection."""
        self.selected_class = None
        if self.tree:
            self.tree.selection_remove(*self.tree.selection())
        self.selection_callback(None)

    @staticmethod
    def _get_display_name(class_name: str) -> str:
        """Get user-friendly display name for a class."""
        return CharacterClasses.DISPLAY_NAMES.get(class_name, class_name.title())
