"""Tests for workflow navigation system."""

from spell_card_generator.ui.workflow_navigation import (
    WorkflowNavigator,
    WorkflowStep,
    StepCondition,
    create_default_workflow,
)


class TestWorkflowStep:
    """Test WorkflowStep dataclass."""

    def test_workflow_step_initialization(self):
        """Test WorkflowStep initializes with correct attributes."""
        step = WorkflowStep(
            step_id="test_step",
            name="Test Step",
            icon="✓",
            description="A test step",
        )

        assert step.step_id == "test_step"
        assert step.name == "Test Step"
        assert step.icon == "✓"
        assert step.description == "A test step"
        assert step.previous_step is None
        assert step.next_step is None
        assert step.required is True
        assert step.condition == StepCondition.ALWAYS_VISIBLE
        assert step.is_valid is False
        assert step.is_accessible is False
        assert step.is_visible is True
        assert isinstance(step.step_data, dict)

    def test_workflow_step_with_custom_values(self):
        """Test WorkflowStep with custom values."""
        step = WorkflowStep(
            step_id="optional_step",
            name="Optional Step",
            icon="○",
            description="An optional step",
            required=False,
            condition=StepCondition.REQUIRES_SPELLS,
        )

        assert not step.required
        assert step.condition == StepCondition.REQUIRES_SPELLS

    def test_workflow_step_data_dict(self):
        """Test WorkflowStep step_data dictionary."""
        step = WorkflowStep(
            step_id="test_step",
            name="Test",
            icon="✓",
            description="Test",
        )

        # Can store arbitrary data
        step.step_data["custom_key"] = "custom_value"
        assert step.step_data["custom_key"] == "custom_value"


class TestWorkflowNavigator:
    """Test WorkflowNavigator linked list navigation."""

    def test_navigator_initialization(self):
        """Test WorkflowNavigator initializes empty."""
        navigator = WorkflowNavigator()

        assert navigator.first_step is None
        assert navigator.current_step is None
        assert len(navigator.steps_by_id) == 0

    def test_add_first_step(self):
        """Test adding first step to navigator."""
        navigator = WorkflowNavigator()
        step = WorkflowStep(
            step_id="step1",
            name="Step 1",
            icon="1",
            description="First step",
        )

        navigator.add_step(step)

        assert navigator.first_step == step
        assert navigator.current_step == step
        assert step.step_id in navigator.steps_by_id
        assert step.previous_step is None
        assert step.next_step is None

    def test_add_multiple_steps(self):
        """Test adding multiple steps creates linked list."""
        navigator = WorkflowNavigator()

        step1 = WorkflowStep(step_id="step1", name="Step 1", icon="1", description="")
        step2 = WorkflowStep(step_id="step2", name="Step 2", icon="2", description="")
        step3 = WorkflowStep(step_id="step3", name="Step 3", icon="3", description="")

        navigator.add_step(step1)
        navigator.add_step(step2)
        navigator.add_step(step3)

        # Verify linked list structure
        assert navigator.first_step == step1
        assert step1.next_step == step2
        assert step2.previous_step == step1
        assert step2.next_step == step3
        assert step3.previous_step == step2
        assert step3.next_step is None

        # Verify all steps are registered
        assert len(navigator.steps_by_id) == 3

    def test_get_step_by_id(self):
        """Test retrieving step by ID."""
        navigator = WorkflowNavigator()
        step = WorkflowStep(step_id="test", name="Test", icon="✓", description="")
        navigator.add_step(step)

        retrieved = navigator.get_step_by_id("test")
        assert retrieved == step

        # Non-existent step
        assert navigator.get_step_by_id("nonexistent") is None

    def test_go_to_next(self):
        """Test navigating to next step."""
        navigator = WorkflowNavigator()

        step1 = WorkflowStep(step_id="step1", name="Step 1", icon="1", description="")
        step2 = WorkflowStep(step_id="step2", name="Step 2", icon="2", description="")

        # Mark steps as accessible
        step1.is_accessible = True
        step2.is_accessible = True

        navigator.add_step(step1)
        navigator.add_step(step2)

        # Start at step1
        assert navigator.current_step == step1

        # Navigate to step2
        result = navigator.go_to_next()
        assert result is True
        assert navigator.current_step == step2

        # Cannot go beyond last step
        result = navigator.go_to_next()
        assert result is False
        assert navigator.current_step == step2  # Still at step2

    def test_go_to_previous(self):
        """Test navigating to previous step."""
        navigator = WorkflowNavigator()

        step1 = WorkflowStep(step_id="step1", name="Step 1", icon="1", description="")
        step2 = WorkflowStep(step_id="step2", name="Step 2", icon="2", description="")

        # Mark steps as accessible
        step1.is_accessible = True
        step2.is_accessible = True

        navigator.add_step(step1)
        navigator.add_step(step2)

        # Navigate to step2
        navigator.go_to_next()
        assert navigator.current_step == step2

        # Go back to step1
        result = navigator.go_to_previous()
        assert result is True
        assert navigator.current_step == step1

        # Cannot go before first step
        result = navigator.go_to_previous()
        assert result is False
        assert navigator.current_step == step1  # Still at step1

    def test_go_to_step_by_id(self):
        """Test navigating directly to a step by ID."""
        navigator = WorkflowNavigator()

        step1 = WorkflowStep(step_id="step1", name="Step 1", icon="1", description="")
        step2 = WorkflowStep(step_id="step2", name="Step 2", icon="2", description="")
        step3 = WorkflowStep(step_id="step3", name="Step 3", icon="3", description="")

        # Mark steps as accessible
        step1.is_accessible = True
        step2.is_accessible = True
        step3.is_accessible = True

        navigator.add_step(step1)
        navigator.add_step(step2)
        navigator.add_step(step3)

        # Jump directly to step3
        result = navigator.go_to_step("step3")
        assert result is True
        assert navigator.current_step == step3

        # Jump to step1
        result = navigator.go_to_step("step1")
        assert result is True
        assert navigator.current_step == step1

        # Non-existent step
        result = navigator.go_to_step("nonexistent")
        assert result is False

    def test_has_next(self):
        """Test checking if next step exists."""
        navigator = WorkflowNavigator()

        step1 = WorkflowStep(step_id="step1", name="Step 1", icon="1", description="")
        step2 = WorkflowStep(step_id="step2", name="Step 2", icon="2", description="")

        # Mark steps as accessible
        step1.is_accessible = True
        step2.is_accessible = True

        navigator.add_step(step1)
        navigator.add_step(step2)

        # At step1, has next
        assert navigator.has_next() is True

        # Navigate to step2
        navigator.go_to_next()
        assert navigator.has_next() is False

    def test_has_previous(self):
        """Test checking if previous step exists."""
        navigator = WorkflowNavigator()

        step1 = WorkflowStep(step_id="step1", name="Step 1", icon="1", description="")
        step2 = WorkflowStep(step_id="step2", name="Step 2", icon="2", description="")

        # Mark steps as accessible
        step1.is_accessible = True
        step2.is_accessible = True

        navigator.add_step(step1)
        navigator.add_step(step2)

        # At step1, no previous
        assert navigator.has_previous() is False

        # Navigate to step2
        navigator.go_to_next()
        assert navigator.has_previous() is True

    def test_get_current_step(self):
        """Test getting current step."""
        navigator = WorkflowNavigator()
        step = WorkflowStep(step_id="test", name="Test", icon="✓", description="")
        navigator.add_step(step)

        assert navigator.get_current_step() == step

    def test_get_visible_steps(self):
        """Test getting all visible steps."""
        navigator = WorkflowNavigator()

        step1 = WorkflowStep(step_id="step1", name="Step 1", icon="1", description="")
        step2 = WorkflowStep(
            step_id="step2", name="Step 2", icon="2", description="", is_visible=False
        )
        step3 = WorkflowStep(step_id="step3", name="Step 3", icon="3", description="")

        navigator.add_step(step1)
        navigator.add_step(step2)
        navigator.add_step(step3)

        visible = navigator.get_visible_steps()
        assert len(visible) == 2
        assert step1 in visible
        assert step3 in visible
        assert step2 not in visible


class TestCreateDefaultWorkflow:
    """Test the default workflow creation function."""

    def test_create_default_workflow(self):
        """Test that default workflow is created correctly."""
        navigator = create_default_workflow()

        # Verify navigator is created
        assert navigator is not None
        assert navigator.first_step is not None

        # Verify expected steps exist
        assert navigator.get_step_by_id("class_selection") is not None
        assert navigator.get_step_by_id("spell_selection") is not None
        assert navigator.get_step_by_id("overwrite_cards") is not None
        assert navigator.get_step_by_id("documentation_urls") is not None
        assert navigator.get_step_by_id("preview_generate") is not None

        # Verify first step is class selection
        assert navigator.first_step.step_id == "class_selection"

    def test_default_workflow_step_conditions(self):
        """Test that default workflow steps have correct conditions."""
        navigator = create_default_workflow()

        class_step = navigator.get_step_by_id("class_selection")
        spell_step = navigator.get_step_by_id("spell_selection")
        overwrite_step = navigator.get_step_by_id("overwrite_cards")

        # Class selection always visible
        assert class_step.condition == StepCondition.ALWAYS_VISIBLE

        # Spell selection requires class
        assert spell_step.condition == StepCondition.REQUIRES_CLASS

        # Overwrite requires conflicts
        assert overwrite_step.condition == StepCondition.REQUIRES_CONFLICTS

    def test_default_workflow_navigation(self):
        """Test navigating through default workflow."""
        navigator = create_default_workflow()

        # Refresh with all conditions met to make all steps accessible
        navigator.refresh_step_states(
            selected_class="wizard",
            selected_spells=[("Fireball", "3", None)],
            conflicts_detected=True,
        )

        # Start at class selection
        assert navigator.current_step.step_id == "class_selection"

        # Can navigate to next
        assert navigator.has_next()

        # Navigate through workflow
        navigator.go_to_next()
        assert navigator.current_step.step_id == "spell_selection"

        navigator.go_to_next()
        assert navigator.current_step.step_id == "overwrite_cards"

        # Can go back
        navigator.go_to_previous()
        assert navigator.current_step.step_id == "spell_selection"
