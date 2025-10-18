"""Preview and Generate workflow step."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional

from spell_card_generator.ui.workflow_steps.base_step import BaseWorkflowStep
from spell_card_generator.ui.workflow_state import workflow_state


class PreviewGenerateStep(BaseWorkflowStep):
    """Preview and generation step - displays comprehensive summary and triggers generation."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        step_index: int,
        navigation_callback: Optional[Callable[[int], None]] = None,
        on_generate: Optional[Callable] = None,
    ):
        super().__init__(parent_frame, step_index, navigation_callback)
        self.on_generate = on_generate
        self.summary_text: Optional[scrolledtext.ScrolledText] = None
        self.generate_button: Optional[ttk.Button] = None

    def create_step_content(self):
        """Create the preview and generate content."""
        # Title
        title_label = ttk.Label(
            self.content_frame,
            text="Preview & Generate",
            font=("TkDefaultFont", 14, "bold"),
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))

        # Description
        desc_label = ttk.Label(
            self.content_frame,
            text="Review your selections and generate spell cards.",
            justify=tk.LEFT,
        )
        desc_label.pack(anchor=tk.W, pady=(0, 20))

        # Summary section
        summary_frame = ttk.LabelFrame(
            self.content_frame, text="Generation Summary", padding=10
        )
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Summary text with scrollbar
        self.summary_text = scrolledtext.ScrolledText(
            summary_frame,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("TkDefaultFont", 10),
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Configure tags for formatted text
        self.summary_text.tag_configure("heading", font=("TkDefaultFont", 11, "bold"))
        self.summary_text.tag_configure(
            "subheading", font=("TkDefaultFont", 10, "bold")
        )
        self.summary_text.tag_configure("bullet", lmargin1=20, lmargin2=40)
        self.summary_text.tag_configure("indent", lmargin1=40, lmargin2=40)
        self.summary_text.tag_configure("warning", foreground="orange")
        self.summary_text.tag_configure("success", foreground="green")

        # Action buttons frame
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Generate button (prominent on the right)
        self.generate_button = ttk.Button(
            button_frame,
            text="🎯 Generate Spell Cards",
            command=self._on_generate_clicked,
            style="Accent.TButton",
        )
        self.generate_button.pack(side=tk.RIGHT)

        # Refresh button (less prominent on the left)
        refresh_button = ttk.Button(
            button_frame,
            text="🔄 Refresh Summary",
            command=self._update_summary,
        )
        refresh_button.pack(side=tk.LEFT)

        # Initial summary update
        self._update_summary()

    def _update_summary(
        self,
    ):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """Update the generation summary with comprehensive information."""
        if not self.summary_text:
            return

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)

        # Helper function to insert formatted text
        def insert_line(text: str, *tags):
            assert self.summary_text is not None, "Summary text must be initialized"
            self.summary_text.insert(tk.END, text + "\n", tags)

        # === Character Class ===
        insert_line("CHARACTER CLASS", "heading")
        if workflow_state.selected_class:
            insert_line(f"  • {workflow_state.selected_class}", "bullet", "success")
        else:
            insert_line("  • No class selected", "bullet", "warning")
        insert_line("")

        # === Selected Spells ===
        insert_line("SELECTED SPELLS", "heading")
        if workflow_state.selected_spells:
            spell_count = len(workflow_state.selected_spells)
            plural = "s" if spell_count != 1 else ""
            insert_line(f"  Total: {spell_count} spell{plural}", "bullet", "success")

            # Group spells by level
            spells_by_level: dict[str, list[str]] = {}
            for spell_name, class_name, spell_data in workflow_state.selected_spells:
                level = spell_data.get(class_name, "?")
                if level not in spells_by_level:
                    spells_by_level[level] = []
                spells_by_level[level].append(spell_name)

            # Display by level
            for level in sorted(spells_by_level.keys(), key=lambda x: (x == "?", x)):
                spells = spells_by_level[level]
                plural = "s" if len(spells) != 1 else ""
                insert_line(f"  Level {level}: {len(spells)} spell{plural}", "indent")
        else:
            insert_line("  • No spells selected", "bullet", "warning")
        insert_line("")

        # === Conflicts & Overwrite Decisions ===
        if workflow_state.conflicts_detected and workflow_state.existing_cards:
            insert_line("FILE CONFLICTS", "heading")
            conflicts = workflow_state.existing_cards
            overwrite_count = sum(
                1
                for spell in conflicts
                if workflow_state.overwrite_decisions.get(spell, False)
            )
            skip_count = len(conflicts) - overwrite_count

            insert_line(f"  Existing files: {len(conflicts)}", "bullet")
            overwrite_tag = "success" if overwrite_count > 0 else ""
            insert_line(
                f"  • Will overwrite: {overwrite_count}", "indent", overwrite_tag
            )
            skip_tag = "success" if skip_count > 0 else ""
            insert_line(f"  • Will skip: {skip_count}", "indent", skip_tag)

            # List preservation options
            preserve_desc_count = sum(
                1
                for spell in conflicts
                if workflow_state.preserve_description.get(spell, False)
            )
            preserve_urls_count = sum(
                1
                for spell in conflicts
                if workflow_state.preserve_urls.get(spell, False)
            )

            if preserve_desc_count > 0 or preserve_urls_count > 0:
                insert_line("  Preservation options:", "bullet")
                if preserve_desc_count > 0:
                    plural = "s" if preserve_desc_count != 1 else ""
                    insert_line(
                        f"    - Preserve descriptions: "
                        f"{preserve_desc_count} spell{plural}",
                        "indent",
                    )
                if preserve_urls_count > 0:
                    plural = "s" if preserve_urls_count != 1 else ""
                    insert_line(
                        f"    - Preserve URLs: " f"{preserve_urls_count} spell{plural}",
                        "indent",
                    )
            insert_line("")

        # === Documentation URLs ===
        insert_line("DOCUMENTATION URLS", "heading")

        # Count configured URLs
        primary_configured = 0
        secondary_configured = 0

        if workflow_state.selected_spells:
            for spell_name, _, _ in workflow_state.selected_spells:
                # Check if primary URL is customized
                primary_url = workflow_state.get_spell_data(spell_name, "primary_url")
                if primary_url:
                    primary_configured += 1

                # Check secondary URL
                secondary_url = workflow_state.get_spell_data(
                    spell_name, "secondary_url"
                )
                if secondary_url:
                    secondary_configured += 1

        total_spells = (
            len(workflow_state.selected_spells) if workflow_state.selected_spells else 0
        )

        if total_spells > 0:
            insert_line(
                f"  Primary URLs: {primary_configured}/{total_spells} configured",
                "bullet",
            )
            insert_line(
                f"  Secondary URLs: {secondary_configured}/{total_spells} "
                "configured",
                "bullet",
            )

            if primary_configured < total_spells:
                remaining = total_spells - primary_configured
                plural = "s" if remaining != 1 else ""
                insert_line(
                    f"    → {remaining} spell{plural} will use "
                    "auto-generated d20pfsrd.com URLs",
                    "indent",
                )
            if secondary_configured < total_spells:
                remaining = total_spells - secondary_configured
                plural = "s" if remaining != 1 else ""
                insert_line(
                    f"    → {remaining} spell{plural} will have " "no secondary URL",
                    "indent",
                )
        else:
            insert_line("  • No URLs configured (no spells selected)", "bullet")
        insert_line("")

        # === Generation Options ===
        insert_line("GENERATION OPTIONS", "heading")

        # Output directory
        if workflow_state.output_directory:
            insert_line(
                f"  Output Directory: {workflow_state.output_directory}",
                "bullet",
            )
        else:
            insert_line("  Output Directory: Default (src/spells/)", "bullet")

        insert_line("")

        # === Ready Status ===
        insert_line("STATUS", "heading")
        ready = bool(workflow_state.selected_class and workflow_state.selected_spells)

        if ready:
            insert_line("  ✓ Ready to generate spell cards", "bullet", "success")
            assert (
                self.generate_button is not None
            ), "Generate button must be initialized"
            self.generate_button.config(state="normal")
        else:
            missing = []
            if not workflow_state.selected_class:
                missing.append("character class")
            if not workflow_state.selected_spells:
                missing.append("spells")

            insert_line(f"  ✗ Missing: {', '.join(missing)}", "bullet", "warning")
            insert_line(
                "    Please complete the previous steps before generating.",
                "indent",
                "warning",
            )
            assert (
                self.generate_button is not None
            ), "Generate button must be initialized"
            self.generate_button.config(state="disabled")

        self.summary_text.config(state=tk.DISABLED)

    def _on_generate_clicked(self):
        """Handle generate button click."""
        if self.on_generate:
            self.on_generate()

    def refresh_ui(self):
        """Refresh the UI when workflow state changes."""
        super().refresh_ui()
        if hasattr(self, "summary_text") and self.summary_text:
            self._update_summary()
