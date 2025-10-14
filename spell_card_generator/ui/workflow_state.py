"""Central state management for multi-step workflow."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from spell_card_generator.config.constants import Config
from spell_card_generator.ui.workflow_navigation import (
    WorkflowNavigator,
    create_default_workflow,
)
from spell_card_generator.ui.step_utils import format_steps_list


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

    # Workflow navigation
    navigator: WorkflowNavigator = field(default_factory=create_default_workflow)

    # Legacy compatibility (deprecated - use navigator instead)
    current_step: int = 0
    step_validation: Dict[int, bool] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize workflow state after dataclass creation."""
        # Ensure navigator starts at first step and refreshes state
        if self.navigator and self.navigator.first_step:
            self.navigator.current_step = self.navigator.first_step
            self.navigator.refresh_step_states(
                self.selected_class, self.selected_spells, self.conflicts_detected
            )

    # Overwrite management
    existing_cards: Dict[str, Any] = field(
        default_factory=dict
    )  # spell_name -> file_path
    overwrite_decisions: Dict[str, bool] = field(
        default_factory=dict
    )  # spell_name -> overwrite
    preserve_description: Dict[str, bool] = field(
        default_factory=dict
    )  # spell_name -> preserve description
    preserve_urls: Dict[str, bool] = field(
        default_factory=dict
    )  # spell_name -> preserve URLs
    preserve_secondary_language: bool = False  # Legacy global setting
    conflicts_detected: bool = False

    # Spell-specific data (preserved when spells are re-selected)
    spell_data_cache: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Spell filtering state (preserved when navigating between steps)
    spell_filter_state: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "level_filter": "All",
            "source_filter": "All",
            "search_term": "",
        }
    )

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
        if step == 2:  # Overwrite Cards (conditional) - only if conflicts detected
            return len(self.selected_spells) > 0 and self.conflicts_detected
        # Other steps require spells to be selected
        return len(self.selected_spells) > 0

    def reset_step_data(self, step: int) -> None:
        """Reset data for a specific step to defaults."""
        if step == 1:  # Spell Selection - reset filters when step is reset
            self.reset_spell_filter_state()
        elif step == 2:  # Overwrite Cards
            self.overwrite_decisions.clear()
            self.preserve_secondary_language = False
            self.conflicts_detected = False
        elif step == 3:  # Generation Options (shifted due to overwrite step)
            self.overwrite_existing = False
            self.output_directory = None
        elif step == 4:  # Documentation URLs (shifted)
            self.german_url_template = Config.DEFAULT_GERMAN_URL
            self.custom_url_templates.clear()
        elif step == 5:  # Secondary Language (shifted)
            self.enable_secondary_language = False
            self.secondary_language_code = "de"
            self.secondary_language_urls.clear()

        self.set_step_valid(step, False)

    def update_conflicts(self, existing_cards: Dict[str, Any]) -> None:
        """Update conflict detection state."""
        self.existing_cards = existing_cards
        self.conflicts_detected = len(existing_cards) > 0

        # Initialize overwrite decisions for new conflicts
        for spell_name in existing_cards.keys():
            if spell_name not in self.overwrite_decisions:
                self.overwrite_decisions[spell_name] = False  # Default to not overwrite

    def get_next_step_after_spells(self) -> int:
        """Get the next step index after spell selection, accounting for conditional overwrite."""
        if self.conflicts_detected:
            return 2  # Go to overwrite management
        return 3  # Skip to generation options

    # New navigation methods using the workflow navigator
    def navigate_to_step(self, step_id: str) -> bool:
        """Navigate to a step by ID using the workflow navigator."""
        self.navigator.refresh_step_states(
            self.selected_class, self.selected_spells, self.conflicts_detected
        )
        result = self.navigator.go_to_step(step_id)
        if result:
            # Update legacy current_step for compatibility
            self.current_step = self.navigator.get_current_step_index()
        return result

    def navigate_next(self) -> bool:
        """Navigate to the next step using the workflow navigator."""
        self.navigator.refresh_step_states(
            self.selected_class, self.selected_spells, self.conflicts_detected
        )
        result = self.navigator.go_to_next()
        if result:
            self.current_step = self.navigator.get_current_step_index()
        return result

    def navigate_previous(self) -> bool:
        """Navigate to the previous step using the workflow navigator."""
        self.navigator.refresh_step_states(
            self.selected_class, self.selected_spells, self.conflicts_detected
        )
        result = self.navigator.go_to_previous()
        if result:
            self.current_step = self.navigator.get_current_step_index()
        return result

    def can_navigate_next(self) -> bool:
        """Check if navigation to next step is possible."""
        self.navigator.refresh_step_states(
            self.selected_class, self.selected_spells, self.conflicts_detected
        )
        return self.navigator.has_next()

    def can_navigate_previous(self) -> bool:
        """Check if navigation to previous step is possible."""
        self.navigator.refresh_step_states(
            self.selected_class, self.selected_spells, self.conflicts_detected
        )
        return self.navigator.has_previous()

    def get_current_step_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current step."""
        current = self.navigator.get_current_step()
        if not current:
            return None

        return {
            "id": current.step_id,
            "name": current.name,
            "icon": current.icon,
            "description": current.description,
            "required": current.required,
            "is_valid": current.is_valid,
            "is_accessible": current.is_accessible,
            "is_visible": current.is_visible,
        }

    def get_all_steps_info(self) -> List[Dict[str, Any]]:
        """Get information about all visible steps."""
        self.navigator.refresh_step_states(
            self.selected_class, self.selected_spells, self.conflicts_detected
        )
        visible_steps = self.navigator.get_visible_steps()

        return format_steps_list(visible_steps, self.navigator.get_current_step())

    def update_step_validity(self, step_id: str, is_valid: bool) -> None:
        """Update the validity of a step by ID."""
        step = self.navigator.get_step_by_id(step_id)
        if step:
            step.is_valid = is_valid

    def get_spell_filter_state(self, filter_key: str, default: str = "") -> str:
        """Get current spell filtering state."""
        return self.spell_filter_state.get(filter_key, default)

    def set_spell_filter_state(self, filter_key: str, value: str) -> None:
        """Set spell filtering state."""
        self.spell_filter_state[filter_key] = value

    def reset_spell_filter_state(self) -> None:
        """Reset spell filtering state to defaults."""
        self.spell_filter_state = {
            "level_filter": "All",
            "source_filter": "All",
            "search_term": "",
        }


# Global workflow state instance
workflow_state = WorkflowState()


# Create a global workflow state instance that can be imported
workflow_state = WorkflowState()
