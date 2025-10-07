#!/usr/bin/env python3
"""
Spell Card Generator GUI

A GUI application to replace the convert.sh script for generating LaTeX spell cards
from the spell_full.tsv database.
"""

import os
import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Dict, List, Optional, Set
import pandas as pd


class SpellCardGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Spell Card Generator")
        self.root.geometry("1200x800")
        
        # Initialize data
        self.spells_df: Optional[pd.DataFrame] = None
        self.filtered_spells: Optional[pd.DataFrame] = None
        self.character_classes: List[str] = []
        self.spell_sources: Set[str] = set()
        
        # Initialize UI
        self.setup_ui()
        self.load_spells_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Spell Card Generator", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Character class selection frame
        self.setup_class_selection_frame(main_frame)
        
        # Spell content frame (will be populated after class selection)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)
        
        # Initialize data structures
        self.class_vars = {}  # Boolean variables for each class
        self.section_vars = {}  # Track which sections are expanded
        self.section_frames = {}  # Store section frames for show/hide
        self.current_classes = set()  # Currently selected classes
        self.spell_data = {}  # Store spell data for each selected class
        
        # Options frame (moved up since tabs will contain the spell lists)
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Overwrite checkbox
        self.overwrite_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Overwrite existing files", 
                       variable=self.overwrite_var).grid(row=0, column=0, sticky=tk.W)
        
        # German URL entry
        ttk.Label(options_frame, text="German URL Template:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.german_url_var = tk.StringVar(value="http://prd.5footstep.de/Grundregelwerk/Zauber/<german-spell-name>")
        ttk.Entry(options_frame, textvariable=self.german_url_var, width=80).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        options_frame.columnconfigure(0, weight=1)
        
        # Generate button
        generate_frame = ttk.Frame(main_frame)
        generate_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.generate_btn = ttk.Button(generate_frame, text="Generate Spell Cards", 
                                     command=self.generate_cards, style="Accent.TButton")
        self.generate_btn.pack()
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3)
    
    def setup_class_selection_frame(self, parent):
        """Create collapsible sections for class selection"""
        # Main class selection frame
        class_frame = ttk.LabelFrame(parent, text="Select Character Classes", padding="10")
        class_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        class_frame.columnconfigure(0, weight=1)
        
        self.class_selection_frame = class_frame
        # The actual sections will be created when data is loaded
    
    def get_display_name(self, class_name):
        """Get user-friendly display name for a class"""
        display_names = {
            'sor': 'Sorcerer',
            'wiz': 'Wizard',
            'summoner_unchained': 'Summoner (Unchained)',
            'antipaladin': 'Antipaladin',
            'investigator': 'Investigator',
            'spiritualist': 'Spiritualist',
            'mesmerist': 'Mesmerist',
            'occultist': 'Occultist',
            'psychic': 'Psychic',
            'medium': 'Medium'
        }
        return display_names.get(class_name, class_name.title())
    
    def create_class_sections(self):
        """Create collapsible sections with character classes in two columns"""
        if not self.character_classes:
            return
        
        # Define class categories with known classes
        known_categories = {
            "Core Classes": ['sor', 'wiz', 'cleric', 'druid', 'ranger', 'bard', 'paladin'],
            "Base Classes": ['alchemist', 'summoner', 'witch', 'inquisitor', 'oracle', 'antipaladin', 'magus'],
            "Hybrid Classes": ['bloodrager', 'hunter', 'investigator', 'shaman', 'skald', 'summoner_unchained'],
            "Occult Classes": ['psychic', 'medium', 'mesmerist', 'occultist', 'spiritualist'],
        }
        
        # Find unknown classes and add them to "Other"
        known_classes = set()
        for classes in known_categories.values():
            known_classes.update(classes)
        
        unknown_classes = [cls for cls in self.character_classes if cls not in known_classes]
        if unknown_classes:
            known_categories["Other"] = unknown_classes
        
        # Filter categories to only include classes that exist in the data
        categories = {}
        for category_name, class_list in known_categories.items():
            existing_classes = [cls for cls in class_list if cls in self.character_classes]
            if existing_classes:
                categories[f"{category_name} ({len(existing_classes)})"] = {
                    'classes': existing_classes,
                    'expanded': category_name == "Core Classes"  # Only Core Classes start expanded
                }
        
        # Create main container frame for two columns
        container_frame = ttk.Frame(self.class_selection_frame)
        container_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E))
        container_frame.columnconfigure(0, weight=1)
        container_frame.columnconfigure(1, weight=1)
        
        # Split sections into two columns
        sections_list = list(categories.items())
        left_sections = sections_list[::2]  # Every even index (0, 2, 4, ...)
        right_sections = sections_list[1::2]  # Every odd index (1, 3, 5, ...)
        
        # Create left column
        left_frame = ttk.Frame(container_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        
        row = 0
        for section_name, section_data in left_sections:
            self.create_class_section_in_frame(left_frame, section_name, section_data, row)
            row += 2
        
        # Create right column
        right_frame = ttk.Frame(container_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        
        row = 0
        for section_name, section_data in right_sections:
            self.create_class_section_in_frame(right_frame, section_name, section_data, row)
            row += 2
        
        # Add global selection buttons at the bottom (spans both columns)
        self.create_global_selection_buttons_two_column(container_frame, max(len(left_sections), len(right_sections)) * 2)
    
    def create_class_section_in_frame(self, parent_frame, section_name, section_data, row):
        """Create a single collapsible section within a specific parent frame"""
        # Section header frame
        header_frame = ttk.Frame(parent_frame)
        header_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        header_frame.columnconfigure(1, weight=1)
        
        # Expand/collapse variable
        expanded_var = tk.BooleanVar(value=section_data['expanded'])
        self.section_vars[section_name] = expanded_var
        
        # Toggle button
        toggle_btn = ttk.Button(header_frame, text="▼" if section_data['expanded'] else "▶",
                               width=3, command=lambda: self.toggle_section(section_name))
        toggle_btn.grid(row=0, column=0, sticky=tk.W)
        
        # Section label
        section_label = ttk.Label(header_frame, text=section_name, font=("TkDefaultFont", 9, "bold"))
        section_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 5))
        
        # Section selection buttons (smaller)
        ttk.Button(header_frame, text="All", width=3,
                  command=lambda: self.select_section_classes(section_data['classes'], True)).grid(row=0, column=2, padx=2)
        ttk.Button(header_frame, text="None", width=5,
                  command=lambda: self.select_section_classes(section_data['classes'], False)).grid(row=0, column=3, padx=2)
        
        # Classes frame (initially shown/hidden based on expanded state)
        classes_frame = ttk.Frame(parent_frame)
        if section_data['expanded']:
            classes_frame.grid(row=row + 1, column=0, sticky=(tk.W, tk.E), padx=15, pady=(0, 5))
        
        # Store references for toggle functionality (update to use parent_frame context)
        section_data['frame'] = classes_frame
        section_data['toggle_btn'] = toggle_btn
        section_data['row'] = row + 1
        section_data['parent_frame'] = parent_frame  # Store parent frame reference
        self.section_frames[section_name] = section_data
        
        # Add checkboxes for classes in this section (single column layout for narrower space)
        for i, class_name in enumerate(section_data['classes']):
            display_name = self.get_display_name(class_name)
            var = tk.BooleanVar()
            self.class_vars[class_name] = var
            
            cb = ttk.Checkbutton(classes_frame, text=display_name, variable=var,
                               command=lambda cn=class_name: self.on_class_selection_changed(cn))
            cb.grid(row=i, column=0, sticky=tk.W, padx=5, pady=1)
    
    def create_global_selection_buttons(self, row):
        """Create global selection buttons"""
        btn_frame = ttk.Frame(self.class_selection_frame)
        btn_frame.grid(row=row, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Select All Classes", 
                  command=self.select_all_classes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Deselect All Classes", 
                  command=self.deselect_all_classes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Core Classes Only", 
                  command=self.select_core_classes).pack(side=tk.LEFT, padx=5)

    def create_global_selection_buttons_two_column(self, container_frame, total_rows):
        """Create buttons for selecting all/none classes globally in two-column layout"""
        button_frame = ttk.Frame(container_frame)
        button_frame.grid(row=total_rows + 1, column=0, columnspan=2, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Center the buttons
        inner_frame = ttk.Frame(button_frame)
        inner_frame.grid(row=0, column=0, columnspan=2)
        
        ttk.Button(inner_frame, text="Select All Classes", 
                  command=self.select_all_classes).pack(side=tk.LEFT, padx=5)
        ttk.Button(inner_frame, text="Deselect All Classes", 
                  command=self.deselect_all_classes).pack(side=tk.LEFT, padx=5)
        ttk.Button(inner_frame, text="Core Classes Only", 
                  command=self.select_core_classes).pack(side=tk.LEFT, padx=5)
        ttk.Button(inner_frame, text="Update Spell Lists", 
                  command=self.update_spell_content).pack(side=tk.LEFT, padx=10)
    
    def toggle_section(self, section_name):
        """Toggle visibility of a class section"""
        if section_name not in self.section_frames:
            return
        
        section_data = self.section_frames[section_name]
        expanded = self.section_vars[section_name].get()
        
        if expanded:
            # Hide the section
            section_data['frame'].grid_remove()
            section_data['toggle_btn'].config(text="▶")
            self.section_vars[section_name].set(False)
        else:
            # Show the section - use appropriate grid parameters for two-column layout
            if 'parent_frame' in section_data:
                # New two-column layout
                section_data['frame'].grid(row=section_data['row'], column=0, 
                                         sticky=(tk.W, tk.E), padx=15, pady=(0, 5))
            else:
                # Old single-column layout (fallback)
                section_data['frame'].grid(row=section_data['row'], column=0, columnspan=4, 
                                         sticky=(tk.W, tk.E), padx=20, pady=(0, 5))
            section_data['toggle_btn'].config(text="▼")
            self.section_vars[section_name].set(True)
    
    def select_section_classes(self, classes, select):
        """Select or deselect all classes in a section"""
        for class_name in classes:
            if class_name in self.class_vars:
                self.class_vars[class_name].set(select)
    
    def select_all_classes(self):
        """Select all character classes"""
        for var in self.class_vars.values():
            var.set(True)
    
    def deselect_all_classes(self):
        """Deselect all character classes"""
        for var in self.class_vars.values():
            var.set(False)
    
    def select_core_classes(self):
        """Select only core classes, deselect others"""
        core_classes = ['sor', 'wiz', 'cleric', 'druid', 'ranger', 'bard', 'paladin']
        for class_name, var in self.class_vars.items():
            var.set(class_name in core_classes)
    
    def on_class_selection_changed(self, class_name):
        """Handle when a class selection changes"""
        if class_name in self.class_vars:
            if self.class_vars[class_name].get():
                self.current_classes.add(class_name)
            else:
                self.current_classes.discard(class_name)
        
        # Update status
        count = len(self.current_classes)
        if count == 0:
            self.status_var.set("No classes selected")
        elif count == 1:
            selected_class = next(iter(self.current_classes))
            self.status_var.set(f"Selected: {self.get_display_name(selected_class)}")
        else:
            self.status_var.set(f"Selected: {count} classes")
    
    def update_spell_content(self):
        """Update the spell content area based on selected classes"""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if not self.current_classes:
            # Show message when no classes selected
            no_selection_label = ttk.Label(self.content_frame, 
                                         text="Please select one or more character classes above, then click 'Update Spell Lists'",
                                         font=("TkDefaultFont", 12))
            no_selection_label.pack(expand=True)
            return
        
        # Create spell content for selected classes
        self.create_spell_content()
    
    def create_spell_content(self):
        """Create spell list content for selected classes"""
        # Create notebook for selected classes
        self.spell_notebook = ttk.Notebook(self.content_frame)
        self.spell_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each selected class
        for class_name in sorted(self.current_classes):
            self.create_spell_tab(class_name)
    
    def create_spell_tab(self, class_name):
        """Create a spell tab for a specific class"""
        # Create main frame for this tab
        tab_frame = ttk.Frame(self.spell_notebook)
        tab_title = self.get_display_name(class_name)
        self.spell_notebook.add(tab_frame, text=tab_title)
        
        # Configure grid weights
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(1, weight=1)
        
        # Filters frame for this class
        filters_frame = ttk.LabelFrame(tab_frame, text="Filters", padding="10")
        filters_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        filters_frame.columnconfigure(1, weight=1)
        
        # Create variables specific to this class
        level_var = tk.StringVar(value="All")
        source_var = tk.StringVar(value="PFRPG Core")
        search_var = tk.StringVar()
        
        # Spell level filter
        ttk.Label(filters_frame, text="Spell Level:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        level_combo = ttk.Combobox(filters_frame, textvariable=level_var, state="readonly")
        level_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        level_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters(class_name))
        
        # Source book filter
        ttk.Label(filters_frame, text="Source Book:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        source_combo = ttk.Combobox(filters_frame, textvariable=source_var, state="readonly")
        source_combo.grid(row=0, column=3, sticky=(tk.W, tk.E))
        source_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters(class_name))
        
        # Search by name
        ttk.Label(filters_frame, text="Search Name:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        search_entry = ttk.Entry(filters_frame, textvariable=search_var)
        search_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<KeyRelease>', lambda e: self.apply_filters(class_name))
        
        # Content frame for spells list and buttons
        content_frame = ttk.Frame(tab_frame)
        content_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Spells list frame
        list_frame = ttk.Frame(content_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Spells treeview
        columns = ("Select", "Name", "Level", "School", "Source")
        spells_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        spells_tree.column("Select", width=50, minwidth=50)
        spells_tree.column("Name", width=200, minwidth=150)
        spells_tree.column("Level", width=60, minwidth=50)
        spells_tree.column("School", width=120, minwidth=100)
        spells_tree.column("Source", width=120, minwidth=100)
        
        # Column headings
        spells_tree.heading("Select", text="Select")
        spells_tree.heading("Name", text="Name")
        spells_tree.heading("Level", text="Level")
        spells_tree.heading("School", text="School")
        spells_tree.heading("Source", text="Source")
        
        spells_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=spells_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        spells_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Bind click event for spell selection
        def on_tree_click(event):
            self.toggle_spell_selection(event, spells_tree)
        spells_tree.bind('<Button-1>', on_tree_click)
        
        # Selection buttons frame
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.W))
        
        ttk.Button(buttons_frame, text="Select All", 
                  command=lambda: self.select_all_spells(class_name)).grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(buttons_frame, text="Deselect All", 
                  command=lambda: self.deselect_all_spells(class_name)).grid(row=1, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(buttons_frame, text="Preview Spell", 
                  command=lambda: self.preview_spell(class_name)).grid(row=2, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Store spell data for this class
        self.spell_data[class_name] = {
            'frame': tab_frame,
            'level_var': level_var,
            'level_combo': level_combo,
            'source_var': source_var,
            'source_combo': source_combo,
            'search_var': search_var,
            'search_entry': search_entry,
            'spells_tree': spells_tree,
            'filtered_spells': None
        }
        
        # Setup filters for this class
        self.setup_class_filters(class_name)
    

    def load_spells_data(self):
        """Load spells data from TSV file"""
        try:
            tsv_path = Path(__file__).parent / "spell_full.tsv"
            if not tsv_path.exists():
                messagebox.showerror("Error", f"Could not find spell_full.tsv file at {tsv_path}")
                return
            
            self.spells_df = pd.read_csv(tsv_path, sep='\t', dtype=str)
            self.spells_df = self.spells_df.fillna("NULL")
            
            # Extract character classes from columns
            class_columns = ['sor', 'wiz', 'cleric', 'druid', 'ranger', 'bard', 'paladin', 
                           'alchemist', 'summoner', 'witch', 'inquisitor', 'oracle', 
                           'antipaladin', 'magus', 'adept', 'bloodrager', 'shaman', 
                           'psychic', 'medium', 'mesmerist', 'occultist', 'spiritualist', 
                           'skald', 'investigator', 'hunter', 'summoner_unchained']
            
            self.character_classes = [col for col in class_columns if col in self.spells_df.columns]
            
            # Extract spell sources
            self.spell_sources = set(self.spells_df['source'].unique())
            self.spell_sources.discard('NULL')
            
            # Create collapsible sections for character classes
            if self.character_classes:
                self.create_class_sections()
                self.status_var.set(f"Loaded {len(self.spells_df)} spells across {len(self.character_classes)} classes")
            else:
                self.status_var.set("No character classes found in spell data")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load spells data: {e}")
    
    def setup_class_filters(self, class_name):
        """Setup filters for a specific character class"""
        if self.spells_df is None or class_name not in self.spell_data:
            return
        
        # Get spell data
        class_data = self.spell_data[class_name]
        
        # Filter spells available for selected class
        available_spells = self.spells_df[self.spells_df[class_name] != "NULL"]
        
        # Update level filter options
        spell_levels = sorted([level for level in available_spells[class_name].unique() 
                              if level != "NULL"])
        class_data['level_combo']['values'] = ["All"] + spell_levels
        
        # Update source filter options
        sources = sorted(available_spells['source'].unique())
        source_options = ["All"] + [s for s in sources if s != "NULL"]
        class_data['source_combo']['values'] = source_options
        
        # Apply initial filters
        self.apply_filters(class_name)
    
    def get_current_class(self):
        """Get the currently active class from the spell notebook"""
        if hasattr(self, 'spell_notebook') and self.spell_notebook.winfo_exists():
            try:
                selected_tab = self.spell_notebook.select()
                tab_index = self.spell_notebook.index(selected_tab)
                selected_classes = sorted(self.current_classes)
                if tab_index < len(selected_classes):
                    return selected_classes[tab_index]
            except tk.TclError:
                pass
        return next(iter(self.current_classes)) if self.current_classes else None

    def apply_filters(self, class_name=None):
        """Apply filters to spell list for a specific class"""
        if class_name is None:
            class_name = self.get_current_class()
            
        if not class_name or self.spells_df is None or class_name not in self.spell_data:
            return
        
        class_data = self.spell_data[class_name]
        filtered_df = self.spells_df[self.spells_df[class_name] != "NULL"].copy()
        
        # Apply level filter
        if class_data['level_var'].get() != "All":
            filtered_df = filtered_df[filtered_df[class_name] == class_data['level_var'].get()]
        
        # Apply source filter
        if class_data['source_var'].get() != "All":
            filtered_df = filtered_df[filtered_df['source'] == class_data['source_var'].get()]
        
        # Apply name search filter
        search_text = class_data['search_var'].get().lower()
        if search_text:
            filtered_df = filtered_df[filtered_df['name'].str.lower().str.contains(search_text, na=False)]
        
        class_data['filtered_spells'] = filtered_df
        self.update_spells_list(class_name)
    
    def update_spells_list(self, class_name=None):
        """Update the spells treeview with filtered results for a specific class"""
        if class_name is None:
            class_name = self.get_current_class()
            
        if not class_name or class_name not in self.spell_data:
            return
            
        class_data = self.spell_data[class_name]
        spells_tree = class_data['spells_tree']
        filtered_spells = class_data['filtered_spells']
        
        # Clear existing items
        for item in spells_tree.get_children():
            spells_tree.delete(item)
        
        if filtered_spells is None:
            return
        
        # Add filtered spells to treeview
        for _, spell in filtered_spells.iterrows():
            spells_tree.insert("", "end", 
                              values=("", 
                                     spell['name'], 
                                     spell[class_name], 
                                     spell['school'], 
                                     spell['source']),
                              tags=("unchecked",))
        
        # Update status
        current_class = self.get_current_class()
        if class_name == current_class:
            display_name = self.get_display_name(class_name)
            self.status_var.set(f"Showing {len(filtered_spells)} {display_name} spells")
    
    def select_all_spells(self, class_name=None):
        """Select all visible spells for a specific class"""
        if class_name is None:
            class_name = self.get_current_class()
            
        if not class_name or class_name not in self.spell_data:
            return
            
        spells_tree = self.spell_data[class_name]['spells_tree']
        for item in spells_tree.get_children():
            spells_tree.set(item, "Select", "☑")
            spells_tree.item(item, tags=("checked",))
    
    def deselect_all_spells(self, class_name=None):
        """Deselect all spells for a specific class"""
        if class_name is None:
            class_name = self.get_current_class()
            
        if not class_name or class_name not in self.spell_data:
            return
            
        spells_tree = self.spell_data[class_name]['spells_tree']
        for item in spells_tree.get_children():
            spells_tree.set(item, "Select", "")
            spells_tree.item(item, tags=("unchecked",))
    
    def preview_spell(self, class_name=None):
        """Preview selected spell details for a specific class"""
        if class_name is None:
            class_name = self.get_current_class()
            
        if not class_name or class_name not in self.spell_data:
            return
            
        class_data = self.spell_data[class_name]
        spells_tree = class_data['spells_tree']
        filtered_spells = class_data['filtered_spells']
        
        selection = spells_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a spell to preview")
            return
        
        # Get spell name from selection
        item = selection[0]
        spell_name = spells_tree.item(item)['values'][1]  # Name is now in column 1
        
        # Find spell in dataframe
        spell_data = filtered_spells[filtered_spells['name'] == spell_name].iloc[0]
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Preview: {spell_name}")
        preview_window.geometry("600x400")
        
        # Create scrolled text widget
        text_widget = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Format spell information
        preview_text = f"Name: {spell_data['name']}\n"
        preview_text += f"School: {spell_data['school']}\n"
        preview_text += f"Level: {spell_data[class_name]}\n"
        preview_text += f"Casting Time: {spell_data['casting_time']}\n"
        preview_text += f"Components: {spell_data['components']}\n"
        preview_text += f"Range: {spell_data['range']}\n"
        preview_text += f"Duration: {spell_data['duration']}\n"
        preview_text += f"Saving Throw: {spell_data['saving_throw']}\n"
        preview_text += f"Spell Resistance: {spell_data['spell_resistance']}\n\n"
        preview_text += f"Description:\n{spell_data['description']}\n"
        
        text_widget.insert(tk.END, preview_text)
        text_widget.config(state=tk.DISABLED)
    
    def toggle_spell_selection(self, event, spells_tree):
        """Toggle spell selection on click for a specific tree"""
        item = spells_tree.identify('item', event.x, event.y)
        if item:
            current_tags = spells_tree.item(item, 'tags')
            if 'checked' in current_tags:
                spells_tree.set(item, "Select", "")
                spells_tree.item(item, tags=("unchecked",))
            else:
                spells_tree.set(item, "Select", "☑")
                spells_tree.item(item, tags=("checked",))
    
    def apply_latex_fixes(self, text: str) -> str:
        """Apply LaTeX formatting fixes"""
        if not text or text == "NULL":
            return text
        
        # Replace double quotes with LaTeX quotes
        text = re.sub(r'"([^"]+)"', r'``\1\'\'', text)
        
        # Fix spacing for measurements
        text = re.sub(r'(\d+[ -]?ft\.) ([a-z])', r'\1\\ \2', text)
        text = re.sub(r'sq\. ft\.', r'sq.~ft.', text)
        
        # Fix spacing after periods before emphasized text
        text = re.sub(r'\. \\emph\{', r'.\@ \\emph{', text)
        
        # Superscript ordinals
        text = re.sub(r'(\b\d+)(st|nd|rd|th)\b', r'\1\\textsuperscript{\2}', text)
        
        return text
    
    def generate_english_url(self, spell_name: str) -> str:
        """Generate English D20PFSRD URL for spell"""
        base_url = "https://www.d20pfsrd.com/magic/all-spells"
        first_char = spell_name[0].lower()
        
        # Clean spell name for URL
        clean_name = re.sub(r'(, Greater| [IVX]+)$', '', spell_name)
        clean_name = clean_name.lower()
        clean_name = re.sub(r'[^a-z0-9]', '-', clean_name)
        
        return f"{base_url}/{first_char}/{clean_name}/"
    
    def generate_spell_latex(self, spell_data: pd.Series, character_class: str) -> str:
        """Generate LaTeX code for a single spell"""
        # Get spell level for the selected class
        spell_level = spell_data[character_class]
        
        # Apply LaTeX fixes to relevant fields
        fields_to_fix = ['effect', 'range', 'area', 'targets', 'mythic_text']
        for field in fields_to_fix:
            if field in spell_data and spell_data[field] != "NULL":
                spell_data[field] = self.apply_latex_fixes(spell_data[field])
        
        # Fix saving throw and spell resistance formatting
        saving_throw = spell_data['saving_throw']
        if saving_throw != "NULL":
            saving_throw = re.sub(r'\bnone\b', r'\\textbf{none}', saving_throw)
        else:
            saving_throw = "\\emph{N/A}"
        
        spell_resistance = spell_data['spell_resistance']
        if spell_resistance != "NULL":
            spell_resistance = re.sub(r'\bno\b', r'\\textbf{no}', spell_resistance)
        else:
            spell_resistance = "\\emph{N/A}"
        
        # Convert HTML description to LaTeX using pandoc
        description_formatted = spell_data['description_formatted']
        if description_formatted != "NULL":
            try:
                # Use pandoc to convert HTML to LaTeX
                process = subprocess.run(
                    ['pandoc', '-f', 'html', '-t', 'latex'],
                    input=description_formatted,
                    capture_output=True,
                    text=True,
                    check=True
                )
                description_formatted = process.stdout
                description_formatted = self.apply_latex_fixes(description_formatted)
            except subprocess.CalledProcessError:
                # Fallback to plain text description
                description_formatted = spell_data['description']
        
        # Generate URLs
        english_url = self.generate_english_url(spell_data['name'])
        german_url = self.german_url_var.get()
        
        # Generate LaTeX content
        latex_content = f"""% file content generated by spell_card_generator.py, meant to be fine-tuned manually (especially the description).

% open a new spellcards environment
\\begin{{spellcard}}{{{character_class}}}{{{spell_data['name']}}}{{{spell_level}}}
  % make the data from TSV accessible for to the LaTeX part:
  \\newcommand{{\\name}}{{{spell_data['name']}}}
  \\newcommand{{\\school}}{{{spell_data['school']}}}
  \\newcommand{{\\subschool}}{{{spell_data['subschool']}}}
  \\newcommand{{\\descriptor}}{{{spell_data['descriptor']}}}
  \\newcommand{{\\spelllevel}}{{{spell_level}}}
  \\newcommand{{\\castingtime}}{{{spell_data['casting_time']}}}
  \\newcommand{{\\components}}{{{spell_data['components']}}}
  \\newcommand{{\\costlycomponents}}{{{spell_data['costly_components']}}}
  \\newcommand{{\\range}}{{{spell_data['range']}}}
  \\newcommand{{\\area}}{{{spell_data['area']}}}
  \\newcommand{{\\effect}}{{{spell_data['effect']}}}
  \\newcommand{{\\targets}}{{{spell_data['targets']}}}
  \\newcommand{{\\duration}}{{{spell_data['duration']}}}
  \\newcommand{{\\dismissible}}{{{spell_data['dismissible']}}}
  \\newcommand{{\\shapeable}}{{{spell_data['shapeable']}}}
  \\newcommand{{\\savingthrow}}{{{saving_throw}}}
  \\newcommand{{\\spellresistance}}{{{spell_resistance}}}
  \\newcommand{{\\source}}{{{spell_data['source']}}}
  \\newcommand{{\\verbal}}{{{spell_data['verbal']}}}
  \\newcommand{{\\somatic}}{{{spell_data['somatic']}}}
  \\newcommand{{\\material}}{{{spell_data['material']}}}
  \\newcommand{{\\focus}}{{{spell_data['focus']}}}
  \\newcommand{{\\divinefocus}}{{{spell_data['divine_focus']}}}
  \\newcommand{{\\deity}}{{{spell_data['deity']}}}
  \\newcommand{{\\SLALevel}}{{{spell_data['SLA_Level']}}}
  \\newcommand{{\\domain}}{{{spell_data['domain']}}}
  \\newcommand{{\\acid}}{{{spell_data['acid']}}}
  \\newcommand{{\\air}}{{{spell_data['air']}}}
  \\newcommand{{\\chaotic}}{{{spell_data['chaotic']}}}
  \\newcommand{{\\cold}}{{{spell_data['cold']}}}
  \\newcommand{{\\curse}}{{{spell_data['curse']}}}
  \\newcommand{{\\darkness}}{{{spell_data['darkness']}}}
  \\newcommand{{\\death}}{{{spell_data['death']}}}
  \\newcommand{{\\disease}}{{{spell_data['disease']}}}
  \\newcommand{{\\earth}}{{{spell_data['earth']}}}
  \\newcommand{{\\electricity}}{{{spell_data['electricity']}}}
  \\newcommand{{\\emotion}}{{{spell_data['emotion']}}}
  \\newcommand{{\\evil}}{{{spell_data['evil']}}}
  \\newcommand{{\\fear}}{{{spell_data['fear']}}}
  \\newcommand{{\\fire}}{{{spell_data['fire']}}}
  \\newcommand{{\\force}}{{{spell_data['force']}}}
  \\newcommand{{\\good}}{{{spell_data['good']}}}
  \\newcommand{{\\languagedependent}}{{{spell_data['language_dependent']}}}
  \\newcommand{{\\lawful}}{{{spell_data['lawful']}}}
  \\newcommand{{\\light}}{{{spell_data['light']}}}
  \\newcommand{{\\mindaffecting}}{{{spell_data['mind_affecting']}}}
  \\newcommand{{\\pain}}{{{spell_data['pain']}}}
  \\newcommand{{\\poison}}{{{spell_data['poison']}}}
  \\newcommand{{\\shadow}}{{{spell_data['shadow']}}}
  \\newcommand{{\\sonic}}{{{spell_data['sonic']}}}
  \\newcommand{{\\water}}{{{spell_data['water']}}}
  \\newcommand{{\\linktext}}{{{spell_data['linktext']}}}
  \\newcommand{{\\id}}{{{spell_data['id']}}}
  \\newcommand{{\\materialcosts}}{{{spell_data['material_costs']}}}
  \\newcommand{{\\bloodline}}{{{spell_data['bloodline']}}}
  \\newcommand{{\\patron}}{{{spell_data['patron']}}}
  \\newcommand{{\\mythictext}}{{{spell_data['mythic_text']}}}
  \\newcommand{{\\augmented}}{{{spell_data['augmented']}}}
  \\newcommand{{\\hauntstatistics}}{{{spell_data['haunt_statistics']}}}
  \\newcommand{{\\ruse}}{{{spell_data['ruse']}}}
  \\newcommand{{\\draconic}}{{{spell_data['draconic']}}}
  \\newcommand{{\\meditative}}{{{spell_data['meditative']}}}
  \\newcommand{{\\urlenglish}}{{{english_url}}}
  \\newcommand{{\\urlgerman}}{{{german_url}}}
  % print the tabular information at the top of the card:
  \\spellcardinfo{{}}
  % draw a QR Code pointing at online resources for this spell on the front face:
  \\spellcardqr{{\\urlenglish}}
  % ATTENTION: URLs for foreign languages cannot be generated and must be provided by you!
  %            Set \\urlgerman above and activate this line if you want to have it: \\spellcardqr{{\\urlgerman}}
  % LaTeX-formatted description of the spell, generated from the HTML-formatted description_formatted column:
  {description_formatted}

\\end{{spellcard}}
"""
        
        return latex_content
    
    def generate_cards(self):
        """Generate LaTeX files for selected spells"""
        current_class = self.get_current_class()
        if not current_class:
            messagebox.showwarning("Warning", "No character class is selected")
            return
        
        if current_class not in self.spell_data:
            messagebox.showerror("Error", f"Spell data for {current_class} not found")
            return
        
        # Get selected spells from current class
        class_data = self.spell_data[current_class]
        spells_tree = class_data['spells_tree']
        
        selected_spells = []
        for item in spells_tree.get_children():
            if 'checked' in spells_tree.item(item, 'tags'):
                spell_name = spells_tree.item(item)['values'][1]  # Name is now in column 1
                selected_spells.append(spell_name)
        
        if not selected_spells:
            messagebox.showwarning("Warning", "Please select at least one spell")
            return
        
        character_class = current_class
        overwrite = self.overwrite_var.get()
        
        # Create output directory
        output_dir = Path(__file__).parent.parent / "src/spells" / character_class
        
        generated_files = []
        skipped_files = []
        
        # Initialize progress bar
        self.progress_var.set(0)
        total_spells = len(selected_spells)
        
        try:
            for i, spell_name in enumerate(selected_spells):
                # Update progress
                progress = (i / total_spells) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Processing {spell_name}...")
                self.root.update()
                
                # Get spell data from current class's filtered spells
                filtered_spells = self.spell_data[character_class]['filtered_spells']
                spell_data = filtered_spells[filtered_spells['name'] == spell_name].iloc[0]
                spell_level = spell_data[character_class]
                
                # Create output file path
                safe_name = spell_name.replace('/', '-')
                output_file = output_dir / spell_level / f"{safe_name}.tex"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if file exists
                if output_file.exists() and not overwrite:
                    skipped_files.append(str(output_file))
                    continue
                
                # Generate LaTeX content
                latex_content = self.generate_spell_latex(spell_data, character_class)
                
                # Write file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                
                generated_files.append(str(output_file))
            
            # Complete progress bar
            self.progress_var.set(100)
            
            # Show results
            result_msg = f"Generated {len(generated_files)} spell cards"
            if skipped_files:
                result_msg += f"\nSkipped {len(skipped_files)} existing files"
            
            result_msg += f"\n\nFiles generated in: {output_dir}"
            result_msg += f"\n\nAdd \\input{{}} statements to src/spells/{character_class}.tex to include them in the document."
            
            messagebox.showinfo("Success", result_msg)
            self.status_var.set("Generation complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate spell cards: {e}")
            self.status_var.set("Error occurred")
        
        finally:
            self.progress_var.set(0)


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = SpellCardGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
