"""Utility functions for workflow step management."""

from typing import Dict, Any, List
from spell_card_generator.ui.workflow_navigation import WorkflowStep


def format_step_info(step: WorkflowStep, is_current: bool = False) -> Dict[str, Any]:
    """Format a WorkflowStep into a dictionary for UI consumption."""
    return {
        "id": step.step_id,
        "name": step.name,
        "icon": step.icon,
        "description": step.description,
        "required": step.required,
        "is_valid": step.is_valid,
        "is_accessible": step.is_accessible,
        "is_visible": step.is_visible,
        "is_current": is_current,
    }


def format_steps_list(
    steps: List[WorkflowStep], current_step: WorkflowStep = None
) -> List[Dict[str, Any]]:
    """Format a list of WorkflowSteps into dictionaries for UI consumption."""
    return [format_step_info(step, step == current_step) for step in steps]
