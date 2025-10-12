"""Central state management for multi-step workflow."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from spell_card_generator.config.constants import Config


@dataclass
class WorkflowState:
    """Central state for the multi-step spell card generation workflow."""

    # Current selection state
    selected_class: Optional[str] = None
    selected_spells: List[Tuple[str, str, pd.Series]] = field(default_factory=list)

    # Generation options
    overwrite_existing: bool = False
    output_directory: Optional[str] = None

    # Documentation URLs
    german_url_template: str = Config.DEFAULT_GERMAN_URL
    custom_url_templates: Dict[str, str] = field(default_factory=dict)

    # Secondary language settings
    enable_secondary_language: bool = False
    secondary_language_code: str = "de"
    secondary_language_urls: Dict[str, str] = field(default_factory=dict)

    # Validation state
    current_step: int = 0
    step_validation: Dict[int, bool] = field(default_factory=dict)

    # Spell-specific data (preserved when spells are re-selected)
    spell_data_cache: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def get_spell_data(self, spell_name: str, key: str, default: Any = None) -> Any:
        """Get cached data for a specific spell."""
        return self.spell_data_cache.get(spell_name, {}).get(key, default)

    def set_spell_data(self, spell_name: str, key: str, value: Any) -> None:
        """Set cached data for a specific spell."""
        if spell_name not in self.spell_data_cache:
            self.spell_data_cache[spell_name] = {}
        self.spell_data_cache[spell_name][key] = value

    def remove_spell_data(self, spell_name: str) -> None:
        """Remove cached data for a deselected spell."""
        self.spell_data_cache.pop(spell_name, None)

    def is_step_valid(self, step: int) -> bool:
        """Check if a step has valid data."""
        return self.step_validation.get(step, False)

    def set_step_valid(self, step: int, valid: bool) -> None:
        """Set validation state for a step."""
        self.step_validation[step] = valid

    def can_navigate_to_step(self, step: int) -> bool:
        """Check if user can navigate to a specific step."""
        if step == 0:  # Class Selection is always accessible
            return True
        if step == 1:  # Spell Selection requires class selection
            return self.selected_class is not None
        # Other steps require spells to be selected
        return len(self.selected_spells) > 0

    def reset_step_data(self, step: int) -> None:
        """Reset data for a specific step to defaults."""
        if step == 1:  # Generation Options
            self.overwrite_existing = False
            self.output_directory = None
        elif step == 2:  # Documentation URLs
            self.german_url_template = Config.DEFAULT_GERMAN_URL
            self.custom_url_templates.clear()
        elif step == 3:  # Secondary Language
            self.enable_secondary_language = False
            self.secondary_language_code = "de"
            self.secondary_language_urls.clear()

        self.set_step_valid(step, False)


# Create a global workflow state instance that can be imported
workflow_state = WorkflowState()
