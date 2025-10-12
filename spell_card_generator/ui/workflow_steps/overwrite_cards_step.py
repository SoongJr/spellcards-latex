"""Workflow step for managing overwrite decisions for existing spell cards."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import datetime
from pathlib import Path

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
        self.preserve_secondary_var: Optional[tk.BooleanVar] = None
        self.summary_label: Optional[ttk.Label] = None
        self.selection_frame: Optional[ttk.Frame] = None

    def create_ui(self):
        """Create the overwrite management UI."""
        super().create_ui()

        # Main content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Title and description
        title_label = ttk.Label(
            content_frame,
            text="Existing Spell Cards Detected",
            font=("TkDefaultFont", 12, "bold"),
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))

        desc_label = ttk.Label(
            content_frame,
            text="Some selected spells already have generated card files. "
            "Choose which ones to overwrite:",
            wraplength=600,
        )
        desc_label.pack(anchor=tk.W, pady=(0, 15))

        # Summary information
        self._create_summary_section(content_frame)

        # Conflicts tree view
        self._create_conflicts_tree(content_frame)

        # Bulk actions
        self._create_bulk_actions(content_frame)

        # Secondary language preservation
        self._create_preservation_options(content_frame)

        # Populate the tree with current conflicts
        self._populate_conflicts()

        # Update validation
        self._update_validation()

    def create_step_content(self):
        """Create the overwrite management step content."""
        # This method is implemented via create_ui() which calls the specific UI creation methods

    def _create_summary_section(self, parent: ttk.Frame):
        """Create summary information section."""
        summary_frame = ttk.LabelFrame(parent, text="Conflict Summary", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 15))

        self.summary_label = ttk.Label(summary_frame, text="")
        self.summary_label.pack(anchor=tk.W)

    def _create_conflicts_tree(self, parent: ttk.Frame):
        """Create the conflicts treeview."""
        tree_frame = ttk.LabelFrame(parent, text="Conflicting Spell Cards", padding=5)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create treeview with scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Treeview
        columns = (
            "overwrite",
            "spell",
            "file_path",
            "size",
            "modified",
            "secondary_lang",
        )
        self.conflicts_tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", selectmode="extended"
        )

        # Configure columns
        self.conflicts_tree.heading("overwrite", text="Overwrite")
        self.conflicts_tree.heading("spell", text="Spell Name")
        self.conflicts_tree.heading("file_path", text="File Path")
        self.conflicts_tree.heading("size", text="Size")
        self.conflicts_tree.heading("modified", text="Modified")
        self.conflicts_tree.heading("secondary_lang", text="Has German")

        # Column widths
        self.conflicts_tree.column("overwrite", width=80, minwidth=60)
        self.conflicts_tree.column("spell", width=200, minwidth=150)
        self.conflicts_tree.column("file_path", width=300, minwidth=200)
        self.conflicts_tree.column("size", width=80, minwidth=60)
        self.conflicts_tree.column("modified", width=120, minwidth=100)
        self.conflicts_tree.column("secondary_lang", width=100, minwidth=80)

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

        # Bind events
        self.conflicts_tree.bind("<Double-1>", self._on_tree_double_click)
        self.conflicts_tree.bind("<Button-1>", self._on_tree_click)

    def _create_bulk_actions(self, parent: ttk.Frame):
        """Create bulk action buttons."""
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(actions_frame, text="Bulk Actions:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(actions_frame, text="Select All", command=self._select_all).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(actions_frame, text="Select None", command=self._select_none).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(
            actions_frame, text="Invert Selection", command=self._invert_selection
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            actions_frame, text="Preview File", command=self._preview_selected_file
        ).pack(side=tk.RIGHT)

    def _create_preservation_options(self, parent: ttk.Frame):
        """Create secondary language preservation options."""
        preserve_frame = ttk.LabelFrame(
            parent, text="Secondary Language Options", padding=10
        )
        preserve_frame.pack(fill=tk.X)

        self.preserve_secondary_var = tk.BooleanVar(
            value=workflow_state.preserve_secondary_language
        )

        preserve_check = ttk.Checkbutton(
            preserve_frame,
            text="Preserve existing secondary language configuration (German URLs, QR codes)",
            variable=self.preserve_secondary_var,
            command=self._on_preserve_changed,
        )
        preserve_check.pack(anchor=tk.W)

        help_label = ttk.Label(
            preserve_frame,
            text="When enabled, existing German documentation and QR codes "
            "will be preserved for overwritten cards.",
            font=("TkDefaultFont", 8),
            foreground="gray50",
        )
        help_label.pack(anchor=tk.W, pady=(5, 0))

    def _populate_conflicts(self):
        """Populate the conflicts tree with current data."""
        if not self.conflicts_tree:
            return

        # Clear existing items
        for item in self.conflicts_tree.get_children():
            self.conflicts_tree.delete(item)

        # Get conflicts summary
        summary = FileScanner.get_conflicts_summary(workflow_state.existing_cards)

        # Update summary label
        if self.summary_label:
            summary_text = (
                f"Total conflicts: {summary['total_conflicts']} | "
                f"With German content: {summary['has_secondary_language']} | "
                f"Total size: {self._format_file_size(summary['total_size'])}"
            )
            self.summary_label.config(text=summary_text)

        # Add items to tree
        for spell_name, file_path in workflow_state.existing_cards.items():
            analysis = summary["analyses"].get(spell_name, {})
            overwrite = workflow_state.overwrite_decisions.get(spell_name, False)

            # Format data for display
            overwrite_text = "☑" if overwrite else "☐"
            size_text = self._format_file_size(analysis.get("file_size", 0))
            modified_text = self._format_modification_time(
                analysis.get("modification_time", 0)
            )
            has_german = (
                "Yes" if analysis.get("has_secondary_language", False) else "No"
            )

            # Relative path for display
            try:
                relative_path = Path(file_path).relative_to(Path.cwd())
            except (ValueError, OSError):
                relative_path = Path(file_path).name

            self.conflicts_tree.insert(
                "",
                tk.END,
                values=(
                    overwrite_text,
                    spell_name,
                    str(relative_path),
                    size_text,
                    modified_text,
                    has_german,
                ),
                tags=("overwrite" if overwrite else "skip",),
            )

        # Configure tags for visual feedback
        self.conflicts_tree.tag_configure("overwrite", background="#ffe6e6")
        self.conflicts_tree.tag_configure("skip", background="#e6ffe6")

    def _on_tree_click(self, event):
        """Handle tree click events."""
        if not self.conflicts_tree:
            return

        # Determine what was clicked
        region = self.conflicts_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.conflicts_tree.identify("column", event.x, event.y)
            if column == "#1":  # Overwrite column
                item = self.conflicts_tree.identify("item", event.x, event.y)
                if item:
                    self._toggle_overwrite(item)

    def _on_tree_double_click(self, _event):
        """Handle double-click to preview file."""
        self._preview_selected_file()

    def _toggle_overwrite(self, item_id: str):
        """Toggle overwrite decision for a specific item."""
        if not self.conflicts_tree:
            return

        values = self.conflicts_tree.item(item_id, "values")
        if len(values) >= 2:
            spell_name = values[1]
            current_overwrite = workflow_state.overwrite_decisions.get(
                spell_name, False
            )
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

    def _select_all(self):
        """Select all conflicts for overwrite."""
        for spell_name in workflow_state.existing_cards:
            workflow_state.overwrite_decisions[spell_name] = True
        self._populate_conflicts()
        self._update_validation()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _select_none(self):
        """Deselect all conflicts."""
        for spell_name in workflow_state.existing_cards:
            workflow_state.overwrite_decisions[spell_name] = False
        self._populate_conflicts()
        self._update_validation()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _invert_selection(self):
        """Invert current selection."""
        for spell_name in workflow_state.existing_cards:
            current = workflow_state.overwrite_decisions.get(spell_name, False)
            workflow_state.overwrite_decisions[spell_name] = not current
        self._populate_conflicts()
        self._update_validation()
        if self.on_overwrite_changed:
            self.on_overwrite_changed()

    def _preview_selected_file(self):
        """Preview the content of the selected file."""
        if not self.conflicts_tree:
            return

        selection = self.conflicts_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a file to preview.")
            return

        item = selection[0]
        values = self.conflicts_tree.item(item, "values")
        if len(values) >= 2:
            spell_name = values[1]
            file_path = workflow_state.existing_cards.get(spell_name)

            if file_path and Path(file_path).exists():
                self._show_file_preview(spell_name, Path(file_path))
            else:
                messagebox.showerror(
                    "File Not Found", f"Could not find file for {spell_name}"
                )

    def _show_file_preview(self, spell_name: str, file_path: Path):
        """Show file preview dialog."""
        preview_window = tk.Toplevel(self.main_frame)
        preview_window.title(f"Preview: {spell_name}")
        preview_window.geometry("600x400")
        preview_window.transient(self.main_frame.winfo_toplevel())
        preview_window.grab_set()

        # File info
        info_frame = ttk.Frame(preview_window)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(
            info_frame, text=f"File: {file_path}", font=("TkDefaultFont", 10, "bold")
        ).pack(anchor=tk.W)

        # Content
        content_frame = ttk.Frame(preview_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        text_widget = tk.Text(content_frame, wrap=tk.WORD, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(
            content_frame, orient=tk.VERTICAL, command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        try:
            content = file_path.read_text(encoding="utf-8")
            text_widget.insert("1.0", content)
            text_widget.config(state=tk.DISABLED)
        except (OSError, UnicodeDecodeError, PermissionError) as e:
            text_widget.insert("1.0", f"Error reading file: {e}")
            text_widget.config(state=tk.DISABLED)

        # Close button
        ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(
            pady=10
        )

    def _on_preserve_changed(self):
        """Handle preserve secondary language change."""
        if self.preserve_secondary_var:
            workflow_state.preserve_secondary_language = (
                self.preserve_secondary_var.get()
            )
            if self.on_overwrite_changed:
                self.on_overwrite_changed()

    def _update_validation(self):
        """Update step validation based on current selections."""
        # Step is valid if user has made decisions (even if all are "don't overwrite")
        has_decisions = len(workflow_state.overwrite_decisions) > 0
        workflow_state.set_step_valid(self.step_index, has_decisions)

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

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
        if self.preserve_secondary_var:
            self.preserve_secondary_var.set(workflow_state.preserve_secondary_language)

    def is_step_complete(self) -> bool:
        """Check if the step is complete."""
        return workflow_state.is_step_valid(self.step_index)

    def get_next_step_index(self) -> int:
        """Get the next step index after handling conflicts."""
        return 3  # Go to generation options (accounting for inserted overwrite step)

    def get_previous_step_index(self) -> int:
        """Get the previous step index."""
        return 1  # Go back to spell selection
