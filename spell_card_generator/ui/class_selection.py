"""Class selection UI management."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Set, Dict, Any

from config.constants import CharacterClasses, UIConfig
from models.spell import SectionData

class ClassSelectionManager:
    """Manages the character class selection UI."""
    
    def __init__(self, parent_frame: ttk.Frame, selection_callback: Callable[[Set[str]], None]):
        self.parent_frame = parent_frame
        self.selection_callback = selection_callback
        
        # State management
        self.class_vars: Dict[str, tk.BooleanVar] = {}
        self.section_vars: Dict[str, tk.BooleanVar] = {}
        self.section_frames: Dict[str, SectionData] = {}
        self.current_classes: Set[str] = set()
        
        # UI containers
        self.container_frame: ttk.Frame = None
    
    def setup_class_sections(self, character_classes: list):
        """Create collapsible sections with character classes."""
        if not character_classes:
            return
        
        # Get class categories
        categories = self._get_class_categories(character_classes)
        
        # Create main container frame for two columns
        self.container_frame = ttk.Frame(self.parent_frame)
        self.container_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E))
        self.container_frame.columnconfigure(0, weight=1)
        self.container_frame.columnconfigure(1, weight=1)
        
        # Split sections into two columns
        sections_list = list(categories.items())
        left_sections = sections_list[::2]  # Every even index (0, 2, 4, ...)
        right_sections = sections_list[1::2]  # Every odd index (1, 3, 5, ...)
        
        # Create left column
        left_frame = ttk.Frame(self.container_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        
        row = 0
        for section_name, section_data in left_sections:
            self._create_class_section_in_frame(left_frame, section_name, section_data, row)
            row += 2
        
        # Create right column
        right_frame = ttk.Frame(self.container_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        
        row = 0
        for section_name, section_data in right_sections:
            self._create_class_section_in_frame(right_frame, section_name, section_data, row)
            row += 2
        
        # Add global selection buttons at the bottom
        self._create_global_selection_buttons(
            self.container_frame, 
            max(len(left_sections), len(right_sections)) * 2
        )
    
    def _get_class_categories(self, character_classes: list) -> dict:
        """Get character classes organized by categories."""
        categories = {}
        
        # Filter categories to only include classes that exist in the data
        for category_name, class_list in CharacterClasses.CATEGORIES.items():
            existing_classes = [cls for cls in class_list if cls in character_classes]
            if existing_classes:
                categories[f"{category_name} ({len(existing_classes)})"] = {
                    'classes': existing_classes,
                    'expanded': category_name == "Core Classes"  # Only Core Classes start expanded
                }
        
        # Find unknown classes and add them to "Other"
        known_classes = set()
        for classes in CharacterClasses.CATEGORIES.values():
            known_classes.update(classes)
        
        unknown_classes = [cls for cls in character_classes if cls not in known_classes]
        if unknown_classes:
            categories[f"Other ({len(unknown_classes)})"] = {
                'classes': unknown_classes,
                'expanded': False
            }
        
        return categories
    
    def _create_class_section_in_frame(self, parent_frame: ttk.Frame, section_name: str, section_data: dict, row: int):
        """Create a single collapsible section within a specific parent frame."""
        # Create section data object
        section_obj = SectionData(
            classes=section_data['classes'],
            expanded=section_data['expanded']
        )
        
        # Section header frame
        header_frame = ttk.Frame(parent_frame)
        header_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        header_frame.columnconfigure(1, weight=1)
        
        # Section variables
        expanded_var = tk.BooleanVar(value=section_obj.expanded)
        self.section_vars[section_name] = expanded_var
        
        # Toggle button
        toggle_btn = ttk.Button(
            header_frame, 
            text=UIConfig.EXPAND_ICON if section_obj.expanded else UIConfig.COLLAPSE_ICON,
            width=3, 
            command=lambda: self._toggle_section(section_name)
        )
        toggle_btn.grid(row=0, column=0, sticky=tk.W)
        
        # Section checkbox for bulk selection
        section_select_var = tk.BooleanVar()
        section_cb = ttk.Checkbutton(
            header_frame, 
            variable=section_select_var,
            command=lambda: self._toggle_section_selection(section_name)
        )
        section_cb.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Section label
        section_label = ttk.Label(
            header_frame, 
            text=section_name, 
            font=("TkDefaultFont", 9, "bold")
        )
        section_label.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=(20, 5))
        
        # Classes frame
        classes_frame = ttk.Frame(parent_frame)
        if section_obj.expanded:
            classes_frame.grid(row=row + 1, column=0, sticky=(tk.W, tk.E), padx=15, pady=(0, 5))
        
        # Update section object
        section_obj.select_var = section_select_var
        section_obj.select_cb = section_cb
        section_obj.frame = classes_frame
        section_obj.toggle_btn = toggle_btn
        section_obj.row = row + 1
        section_obj.parent_frame = parent_frame
        
        self.section_frames[section_name] = section_obj
        
        # Add checkboxes for classes in this section
        for i, class_name in enumerate(section_obj.classes):
            display_name = self.get_display_name(class_name)
            var = tk.BooleanVar()
            self.class_vars[class_name] = var
            
            cb = ttk.Checkbutton(
                classes_frame, 
                text=display_name, 
                variable=var,
                command=lambda cn=class_name: self._on_class_selection_changed(cn)
            )
            cb.grid(row=i, column=0, sticky=tk.W, padx=5, pady=1)
        
        # Initialize the section checkbox state
        self._update_section_checkbox_state(section_obj.classes)
    
    def _create_global_selection_buttons(self, container_frame: ttk.Frame, total_rows: int):
        """Create buttons for selecting all/none classes globally."""
        button_frame = ttk.Frame(container_frame)
        button_frame.grid(row=total_rows + 1, column=0, columnspan=2, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Center the buttons
        inner_frame = ttk.Frame(button_frame)
        inner_frame.grid(row=0, column=0, columnspan=2)
        
        ttk.Button(
            inner_frame, 
            text="Select All Classes", 
            command=self.select_all_classes
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            inner_frame, 
            text="Deselect All Classes", 
            command=self.deselect_all_classes
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            inner_frame, 
            text="Core Classes Only", 
            command=self.select_core_classes
        ).pack(side=tk.LEFT, padx=5)
    
    def _toggle_section(self, section_name: str):
        """Toggle visibility of a class section."""
        if section_name not in self.section_frames:
            return
        
        section_data = self.section_frames[section_name]
        expanded = self.section_vars[section_name].get()
        
        if expanded:
            # Hide the section
            section_data.frame.grid_remove()
            section_data.toggle_btn.config(text=UIConfig.COLLAPSE_ICON)
            self.section_vars[section_name].set(False)
        else:
            # Show the section
            section_data.frame.grid(
                row=section_data.row, column=0, 
                sticky=(tk.W, tk.E), padx=15, pady=(0, 5)
            )
            section_data.toggle_btn.config(text=UIConfig.EXPAND_ICON)
            self.section_vars[section_name].set(True)
    
    def _toggle_section_selection(self, section_name: str):
        """Toggle selection state for all classes in a section."""
        if section_name not in self.section_frames:
            return
        
        section_data = self.section_frames[section_name]
        classes = section_data.classes
        
        # Check current state
        selected_count = sum(1 for cls in classes if cls in self.class_vars and self.class_vars[cls].get())
        total_count = len(classes)
        
        if selected_count == 0:
            # None selected -> select all
            self._select_section_classes(classes, True)
        elif selected_count == total_count:
            # All selected -> deselect all
            self._select_section_classes(classes, False)
        else:
            # Some selected -> select all
            self._select_section_classes(classes, True)
    
    def _select_section_classes(self, classes: list, select: bool):
        """Select or deselect all classes in a section."""
        for class_name in classes:
            if class_name in self.class_vars:
                self.class_vars[class_name].set(select)
                if select:
                    self.current_classes.add(class_name)
                else:
                    self.current_classes.discard(class_name)
        
        # Update the section's checkbox
        self._update_section_checkbox_state(classes)
        
        # Notify callback
        self.selection_callback(self.current_classes.copy())
    
    def _update_section_checkbox_state(self, classes: list):
        """Update the tri-state checkbox based on current class selections."""
        # Find which section these classes belong to
        for section_name, section_data in self.section_frames.items():
            if set(classes) == set(section_data.classes):
                selected_count = sum(1 for cls in classes if cls in self.class_vars and self.class_vars[cls].get())
                total_count = len(classes)
                
                # Use after_idle to ensure the GUI has time to process the state change
                def update_state():
                    if selected_count == 0:
                        # None selected - unchecked state
                        section_data.select_var.set(False)
                        section_data.select_cb.state(['!alternate'])
                    elif selected_count == total_count:
                        # All selected - checked state
                        section_data.select_var.set(True)
                        section_data.select_cb.state(['!alternate'])
                    else:
                        # Some selected - indeterminate state
                        section_data.select_var.set(True)
                        section_data.select_cb.state(['alternate'])
                
                if hasattr(self.parent_frame, 'after_idle'):
                    self.parent_frame.after_idle(update_state)
                break
    
    def _on_class_selection_changed(self, class_name: str):
        """Handle when a class selection changes."""
        if class_name in self.class_vars:
            if self.class_vars[class_name].get():
                self.current_classes.add(class_name)
            else:
                self.current_classes.discard(class_name)
        
        # Update the section checkbox state
        self._update_section_checkbox_for_class(class_name)
        
        # Notify callback
        self.selection_callback(self.current_classes.copy())
    
    def _update_section_checkbox_for_class(self, class_name: str):
        """Update section checkbox when an individual class selection changes."""
        # Find the section containing this class
        for section_name, section_data in self.section_frames.items():
            if class_name in section_data.classes:
                self._update_section_checkbox_state(section_data.classes)
                break
    
    def select_all_classes(self):
        """Select all character classes."""
        for class_name, var in self.class_vars.items():
            var.set(True)
            self.current_classes.add(class_name)
        
        # Update all section checkboxes
        for section_name, section_data in self.section_frames.items():
            self._update_section_checkbox_state(section_data.classes)
        
        # Notify callback
        self.selection_callback(self.current_classes.copy())
    
    def deselect_all_classes(self):
        """Deselect all character classes."""
        for class_name, var in self.class_vars.items():
            var.set(False)
        self.current_classes.clear()
        
        # Update all section checkboxes
        for section_name, section_data in self.section_frames.items():
            self._update_section_checkbox_state(section_data.classes)
        
        # Notify callback
        self.selection_callback(self.current_classes.copy())
    
    def select_core_classes(self):
        """Select only core classes, deselect others."""
        self.current_classes.clear()
        
        for class_name, var in self.class_vars.items():
            if class_name in CharacterClasses.CORE:
                var.set(True)
                self.current_classes.add(class_name)
            else:
                var.set(False)
        
        # Update all section checkboxes
        for section_name, section_data in self.section_frames.items():
            self._update_section_checkbox_state(section_data.classes)
        
        # Notify callback
        self.selection_callback(self.current_classes.copy())
    
    @staticmethod
    def get_display_name(class_name: str) -> str:
        """Get user-friendly display name for a class."""
        return CharacterClasses.DISPLAY_NAMES.get(class_name, class_name.title())
