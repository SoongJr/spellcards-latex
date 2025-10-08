"""Spell filtering functionality."""

from typing import Optional, List
import pandas as pd

from config.constants import Config
from utils.exceptions import FilterError

class SpellFilter:
    """Handles filtering of spell data."""
    
    @staticmethod
    def filter_spells(
        spells_df: pd.DataFrame,
        class_name: str,
        level: Optional[str] = None,
        source: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> pd.DataFrame:
        """Filter spells based on criteria."""
        try:
            # Start with spells available for the class
            if class_name not in spells_df.columns:
                raise FilterError(f"Class {class_name} not found in data")
            
            filtered = spells_df[spells_df[class_name] != Config.NULL_VALUE].copy()
            
            # Apply level filter
            if level and level != "All":
                filtered = filtered[filtered[class_name] == level]
            
            # Apply source filter
            if source and source != "All":
                filtered = filtered[filtered['source'] == source]
            
            # Apply search filter
            if search_term and search_term.strip():
                search_lower = search_term.lower().strip()
                filtered = filtered[
                    filtered['name'].str.lower().str.contains(
                        search_lower, na=False, regex=False
                    )
                ]
            
            return filtered
        
        except Exception as e:
            raise FilterError(f"Failed to filter spells: {e}")
    
    @staticmethod
    def get_available_levels(spells_df: pd.DataFrame, class_name: str) -> List[str]:
        """Get available spell levels for a class."""
        try:
            if class_name not in spells_df.columns:
                return ["All"]
            
            class_spells = spells_df[spells_df[class_name] != Config.NULL_VALUE]
            levels = sorted(
                [level for level in class_spells[class_name].unique() 
                 if level != Config.NULL_VALUE]
            )
            return ["All"] + levels
        
        except Exception as e:
            raise FilterError(f"Failed to get available levels: {e}")
    
    @staticmethod
    def get_available_sources(spells_df: pd.DataFrame, class_name: str) -> List[str]:
        """Get available sources for a class's spells."""
        try:
            if class_name not in spells_df.columns:
                return ["All"]
            
            class_spells = spells_df[spells_df[class_name] != Config.NULL_VALUE]
            sources = sorted(
                [source for source in class_spells['source'].unique() 
                 if source != Config.NULL_VALUE]
            )
            return ["All"] + sources
        
        except Exception as e:
            raise FilterError(f"Failed to get available sources: {e}")
