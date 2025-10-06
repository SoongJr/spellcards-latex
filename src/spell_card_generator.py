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
        
        # Filters frame
        filters_frame = ttk.LabelFrame(main_frame, text="Filters", padding="10")
        filters_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        filters_frame.columnconfigure(1, weight=1)
        
        # Character class filter
        ttk.Label(filters_frame, text="Character Class:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(filters_frame, textvariable=self.class_var, state="readonly")
        self.class_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.class_combo.bind('<<ComboboxSelected>>', self.on_class_changed)
        
        # Spell level filter
        ttk.Label(filters_frame, text="Spell Level:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.level_var = tk.StringVar(value="All")
        self.level_combo = ttk.Combobox(filters_frame, textvariable=self.level_var, state="readonly")
        self.level_combo.grid(row=0, column=3, sticky=(tk.W, tk.E))
        self.level_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Source book filter
        ttk.Label(filters_frame, text="Source Book:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.source_var = tk.StringVar(value="PFRPG Core")
        self.source_combo = ttk.Combobox(filters_frame, textvariable=self.source_var, state="readonly")
        self.source_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.source_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Search by name
        ttk.Label(filters_frame, text="Search Name:").grid(row=1, column=2, sticky=tk.W, padx=(10, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filters_frame, textvariable=self.search_var)
        self.search_entry.grid(row=1, column=3, sticky=(tk.W, tk.E))
        self.search_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Spells list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Spells treeview
        columns = ("Select", "Name", "Level", "School", "Source")
        self.spells_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.spells_tree.column("Select", width=50, minwidth=50)
        self.spells_tree.column("Name", width=200, minwidth=150)
        self.spells_tree.column("Level", width=60, minwidth=50)
        self.spells_tree.column("School", width=120, minwidth=100)
        self.spells_tree.column("Source", width=120, minwidth=100)
        
        # Column headings
        self.spells_tree.heading("Select", text="Select")
        self.spells_tree.heading("Name", text="Name")
        self.spells_tree.heading("Level", text="Level")
        self.spells_tree.heading("School", text="School")
        self.spells_tree.heading("Source", text="Source")
        
        self.spells_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.spells_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.spells_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Selection buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=2, sticky=(tk.N, tk.W), padx=(10, 0))
        
        ttk.Button(buttons_frame, text="Select All", command=self.select_all_spells).grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(buttons_frame, text="Deselect All", command=self.deselect_all_spells).grid(row=1, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(buttons_frame, text="Preview Spell", command=self.preview_spell).grid(row=2, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        generate_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.generate_btn = ttk.Button(generate_frame, text="Generate Spell Cards", 
                                     command=self.generate_cards, style="Accent.TButton")
        self.generate_btn.pack()
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=3)
    
    def load_spells_data(self):
        """Load spells data from TSV file"""
        try:
            tsv_path = Path(__file__).parent / "spells" / "spell_full.tsv"
            if not tsv_path.exists():
                tsv_path = Path("src/spells/spell_full.tsv")
            
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
            self.class_combo['values'] = self.character_classes
            
            # Extract spell sources
            self.spell_sources = set(self.spells_df['source'].unique())
            self.spell_sources.discard('NULL')
            
            self.status_var.set(f"Loaded {len(self.spells_df)} spells")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load spells data: {e}")
    
    def on_class_changed(self, event=None):
        """Handle character class selection change"""
        if not self.class_var.get() or self.spells_df is None:
            return
        
        # Filter spells available for selected class
        class_col = self.class_var.get()
        available_spells = self.spells_df[self.spells_df[class_col] != "NULL"]
        
        # Update level filter options
        spell_levels = sorted([level for level in available_spells[class_col].unique() 
                              if level != "NULL"])
        self.level_combo['values'] = ["All"] + spell_levels
        
        # Update source filter options
        sources = sorted(available_spells['source'].unique())
        source_options = ["All"] + [s for s in sources if s != "NULL"]
        self.source_combo['values'] = source_options
        
        # Set default to "PFRPG Core" if it exists in the sources, otherwise keep current selection
        if "PFRPG Core" in source_options and self.source_var.get() == "PFRPG Core":
            # Keep the default selection
            pass
        elif self.source_var.get() not in source_options:
            # Reset to "All" if current selection is not available
            self.source_var.set("All")
        
        self.apply_filters()
    
    def apply_filters(self, event=None):
        """Apply filters to spell list"""
        if not self.class_var.get() or self.spells_df is None:
            return
        
        class_col = self.class_var.get()
        filtered_df = self.spells_df[self.spells_df[class_col] != "NULL"].copy()
        
        # Apply level filter
        if self.level_var.get() != "All":
            filtered_df = filtered_df[filtered_df[class_col] == self.level_var.get()]
        
        # Apply source filter
        if self.source_var.get() != "All":
            filtered_df = filtered_df[filtered_df['source'] == self.source_var.get()]
        
        # Apply name search filter
        search_text = self.search_var.get().lower()
        if search_text:
            filtered_df = filtered_df[filtered_df['name'].str.lower().str.contains(search_text, na=False)]
        
        self.filtered_spells = filtered_df
        self.update_spells_list()
    
    def update_spells_list(self):
        """Update the spells treeview with filtered results"""
        # Clear existing items
        for item in self.spells_tree.get_children():
            self.spells_tree.delete(item)
        
        if self.filtered_spells is None:
            return
        
        # Add filtered spells to treeview
        class_col = self.class_var.get()
        for _, spell in self.filtered_spells.iterrows():
            self.spells_tree.insert("", "end", 
                                   values=("", 
                                          spell['name'], 
                                          spell[class_col], 
                                          spell['school'], 
                                          spell['source']),
                                   tags=("unchecked",))
        
        self.status_var.set(f"Showing {len(self.filtered_spells)} spells")
    
    def select_all_spells(self):
        """Select all visible spells"""
        for item in self.spells_tree.get_children():
            self.spells_tree.set(item, "Select", "☑")
            self.spells_tree.item(item, tags=("checked",))
    
    def deselect_all_spells(self):
        """Deselect all spells"""
        for item in self.spells_tree.get_children():
            self.spells_tree.set(item, "Select", "")
            self.spells_tree.item(item, tags=("unchecked",))
    
    def preview_spell(self):
        """Preview selected spell details"""
        selection = self.spells_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a spell to preview")
            return
        
        # Get spell name from selection
        item = selection[0]
        spell_name = self.spells_tree.item(item)['values'][1]  # Name is now in column 1
        
        # Find spell in dataframe
        spell_data = self.filtered_spells[self.filtered_spells['name'] == spell_name].iloc[0]
        
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
        preview_text += f"Level: {spell_data[self.class_var.get()]}\n"
        preview_text += f"Casting Time: {spell_data['casting_time']}\n"
        preview_text += f"Components: {spell_data['components']}\n"
        preview_text += f"Range: {spell_data['range']}\n"
        preview_text += f"Duration: {spell_data['duration']}\n"
        preview_text += f"Saving Throw: {spell_data['saving_throw']}\n"
        preview_text += f"Spell Resistance: {spell_data['spell_resistance']}\n\n"
        preview_text += f"Description:\n{spell_data['description']}\n"
        
        text_widget.insert(tk.END, preview_text)
        text_widget.config(state=tk.DISABLED)
    
    def toggle_spell_selection(self, event):
        """Toggle spell selection on click"""
        item = self.spells_tree.identify('item', event.x, event.y)
        if item:
            current_tags = self.spells_tree.item(item, 'tags')
            if 'checked' in current_tags:
                self.spells_tree.set(item, "Select", "")
                self.spells_tree.item(item, tags=("unchecked",))
            else:
                self.spells_tree.set(item, "Select", "☑")
                self.spells_tree.item(item, tags=("checked",))
    
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
        if not self.class_var.get():
            messagebox.showwarning("Warning", "Please select a character class")
            return
        
        # Get selected spells
        selected_spells = []
        for item in self.spells_tree.get_children():
            if 'checked' in self.spells_tree.item(item, 'tags'):
                spell_name = self.spells_tree.item(item)['values'][1]  # Name is now in column 1
                selected_spells.append(spell_name)
        
        if not selected_spells:
            messagebox.showwarning("Warning", "Please select at least one spell")
            return
        
        character_class = self.class_var.get()
        overwrite = self.overwrite_var.get()
        
        # Create output directory
        output_dir = Path("src/spells") / character_class
        
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
                
                # Get spell data
                spell_data = self.filtered_spells[self.filtered_spells['name'] == spell_name].iloc[0]
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
    
    # Bind click event to toggle selection
    def on_tree_click(event):
        app.toggle_spell_selection(event)
    
    app = SpellCardGenerator(root)
    app.spells_tree.bind('<Button-1>', on_tree_click)
    
    root.mainloop()


if __name__ == "__main__":
    main()
