"""Spell data models."""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import pandas as pd

@dataclass
class Spell:
    """Represents a single spell."""
    
    name: str
    school: str
    source: str
    description: str
    description_formatted: str
    casting_time: str
    components: str
    range: str
    duration: str
    saving_throw: str
    spell_resistance: str
    class_levels: Dict[str, str]  # class -> level mapping
    
    # Optional fields
    subschool: Optional[str] = None
    descriptor: Optional[str] = None
    area: Optional[str] = None
    effect: Optional[str] = None
    targets: Optional[str] = None
    dismissible: Optional[str] = None
    shapeable: Optional[str] = None
    
    @classmethod
    def from_series(cls, series: pd.Series, class_columns: list) -> 'Spell':
        """Create Spell from pandas Series."""
        class_levels = {
            col: series[col] for col in class_columns 
            if col in series and series[col] != "NULL"
        }
        
        return cls(
            name=series.get('name', ''),
            school=series.get('school', ''),
            source=series.get('source', ''),
            description=series.get('description', ''),
            description_formatted=series.get('description_formatted', ''),
            casting_time=series.get('casting_time', ''),
            components=series.get('components', ''),
            range=series.get('range', ''),
            duration=series.get('duration', ''),
            saving_throw=series.get('saving_throw', ''),
            spell_resistance=series.get('spell_resistance', ''),
            class_levels=class_levels,
            subschool=series.get('subschool'),
            descriptor=series.get('descriptor'),
            area=series.get('area'),
            effect=series.get('effect'),
            targets=series.get('targets'),
            dismissible=series.get('dismissible'),
            shapeable=series.get('shapeable')
        )
    
    def is_available_for_class(self, class_name: str) -> bool:
        """Check if spell is available for given class."""
        return class_name in self.class_levels
    
    def get_level_for_class(self, class_name: str) -> Optional[str]:
        """Get spell level for given class."""
        return self.class_levels.get(class_name)

@dataclass 
class ClassTabState:
    """State for a character class tab."""
    
    frame: Any  # ttk.Frame
    level_var: Any  # tk.StringVar
    source_var: Any  # tk.StringVar  
    search_var: Any  # tk.StringVar
    spells_tree: Any  # ttk.Treeview
    level_combo: Any  # ttk.Combobox
    source_combo: Any  # ttk.Combobox
    search_entry: Any  # ttk.Entry
    filtered_spells: Optional[pd.DataFrame] = None

@dataclass
class SectionData:
    """Data for a collapsible character class section."""
    
    classes: list
    expanded: bool
    select_var: Any = None  # tk.BooleanVar
    select_cb: Any = None   # ttk.Checkbutton
    frame: Any = None       # ttk.Frame
    toggle_btn: Any = None  # ttk.Button
    row: int = 0
    parent_frame: Any = None  # ttk.Frame
