"""Tests for attack roll detection functionality."""

import pytest
from spell_card_generator.generators.latex_generator import LaTeXGenerator


class TestAttackRollDetection:
    """Test cases for _detect_attack_roll method."""

    @pytest.fixture
    def generator(self):
        """Fixture to create LaTeXGenerator instance."""
        return LaTeXGenerator()

    # ===== Ranged Touch Attack Tests =====

    def test_ranged_touch_acid_arrow(self, generator):
        """Test detection for Acid Arrow (clear ranged touch)."""
        description = (
            "A magical arrow of acid springs from your hand and speeds to its target. "
            "You must succeed on a ranged touch attack to hit your target."
        )
        result = generator._detect_attack_roll(description)
        assert result == "ranged touch"

    def test_ranged_touch_scorching_ray(self, generator):
        """Test detection for Scorching Ray (multiple ranged touch)."""
        description = (
            "You blast your enemies with a searing beam of fire. "
            "You may fire one ray, plus one additional ray for every "
            "four levels beyond 3rd. Each ray requires a ranged touch "
            "attack to hit and deals 4d6 points of fire damage."
        )
        result = generator._detect_attack_roll(description)
        assert result == "ranged touch"

    # ===== Melee Touch Attack Tests =====

    def test_melee_touch_shocking_grasp(self, generator):
        """Test detection for Shocking Grasp (clear melee touch)."""
        description = (
            "Your successful melee touch attack deals 1d6 points of "
            "electricity damage per caster level (maximum 5d6). When "
            "delivering the jolt, you gain a +3 bonus on attack rolls "
            "if the opponent is wearing metal armor."
        )
        result = generator._detect_attack_roll(description)
        assert result == "melee touch"

    def test_melee_touch_vampiric_touch(self, generator):
        """Test detection for Vampiric Touch (clear melee touch)."""
        description = (
            "You must succeed on a melee touch attack. Your touch deals "
            "1d6 points of damage per two caster levels. You gain "
            "temporary hit points equal to the damage you deal."
        )
        result = generator._detect_attack_roll(description)
        assert result == "melee touch"

    def test_touch_attack_defaults_to_melee(self, generator):
        """Test that 'touch attack' without 'ranged' defaults to melee."""
        description = "You make a touch attack that deals damage."
        result = generator._detect_attack_roll(description)
        assert result == "melee touch"

    # ===== Ranged Attack (Non-Touch) Tests =====

    def test_ranged_attack_magic_stone(self, generator):
        """Test detection for Magic Stone (ranged attack, clear context)."""
        description = (
            "You transmute as many as three pebbles, which can be no "
            "larger than sling bullets, so that they strike with great "
            "force when thrown or slung. The user of the stones makes "
            "a normal ranged attack. Each stone that hits deals 1d6+1 "
            "points of damage."
        )
        result = generator._detect_attack_roll(description)
        assert result == "ranged"

    def test_ranged_attack_nauseating_dart(self, generator):
        """Test detection for Nauseating Dart (succeed at ranged attack)."""
        description = (
            "You create a dazzling lance of energy that you can use as "
            "a ranged weapon. You must succeed at a ranged attack to hit "
            "your target. The target is staggered for 1 round."
        )
        result = generator._detect_attack_roll(description)
        assert result == "ranged"

    # ===== Melee Attack (Non-Touch) Tests =====

    def test_melee_attack_resounding_blow(self, generator):
        """Test detection for Resounding Blow (on successful melee attack)."""
        description = (
            "On a successful melee attack, your weapon resounds with a "
            "thunderous clash. The target takes an additional 1d6 points "
            "of sonic damage."
        )
        result = generator._detect_attack_roll(description)
        assert result == "melee"

    def test_melee_attack_sickening_strikes(self, generator):
        """Test detection for Sickening Strikes (any creature you strike)."""
        description = (
            "Your attacks cause pain and weakness. For the duration of "
            "the spell, any creature you strike with a melee attack must "
            "make a Fortitude save or be sickened for 1 round."
        )
        result = generator._detect_attack_roll(description)
        assert result == "melee"

    # ===== Buff/Debuff (None) Tests =====

    def test_none_bulls_strength(self, generator):
        """Test detection for Bull's Strength (buff, no attack)."""
        description = (
            "The subject becomes stronger. The spell grants a +4 "
            "enhancement bonus to Strength, adding the usual benefits "
            "to melee attack rolls, melee damage rolls, and other uses "
            "of the Strength modifier."
        )
        result = generator._detect_attack_roll(description)
        assert result == r"\textbf{none}"

    def test_none_entropic_shield(self, generator):
        """Test detection for Entropic Shield (deflects attacks)."""
        description = (
            "A magical field appears around you, glowing with a chaotic "
            "blast of multicolored hues. This field deflects incoming "
            "arrows, rays, and other ranged attacks. Each ranged attack "
            "directed at you for which the attacker must make an attack "
            "roll has a 20% miss chance."
        )
        result = generator._detect_attack_roll(description)
        assert result == r"\textbf{none}"

    # ===== Inconclusive Tests =====

    def test_inconclusive_solid_fog(self, generator):
        """Test detection for Solid Fog (environmental effect on attacks)."""
        description = (
            "This spell functions like fog cloud, but in addition to "
            "obscuring sight, the solid fog is so thick that it impedes "
            "movement. Creatures moving through a solid fog take a -2 "
            "penalty on all melee attack and melee damage rolls."
        )
        result = generator._detect_attack_roll(description)
        assert result == "inconclusive"

    def test_inconclusive_cloak_of_chaos(self, generator):
        """Test detection for Cloak of Chaos (reactive defensive effect)."""
        description = (
            "A random pattern of color surrounds the subjects, protecting "
            "them from attacks. Additionally, if a lawful creature succeeds "
            "on a melee attack against a warded creature, the offending "
            "attacker takes 1d6 points of damage."
        )
        result = generator._detect_attack_roll(description)
        assert result == "inconclusive"

    # ===== Edge Cases =====

    def test_empty_description(self, generator):
        """Test with empty description - should be inconclusive."""
        result = generator._detect_attack_roll("")
        assert result == "inconclusive"

    def test_none_description(self, generator):
        """Test with None description - should be inconclusive."""
        result = generator._detect_attack_roll(None)
        assert result == "inconclusive"

    def test_no_attack_mention(self, generator):
        """Test spell with no attack mention."""
        description = "This spell creates a magical barrier that protects the caster."
        result = generator._detect_attack_roll(description)
        assert result == r"\textbf{none}"

    def test_general_attack_mention_inconclusive(self, generator):
        """Test spell that mentions 'attack' without clear context."""
        description = "This spell involves an attack somehow."
        result = generator._detect_attack_roll(description)
        assert result == "inconclusive"

    # ===== Context Pattern Tests =====

    def test_succeed_at_ranged_attack(self, generator):
        """Test 'succeed at a ranged attack' pattern."""
        description = "You succeed at a ranged attack to deal damage."
        result = generator._detect_attack_roll(description)
        assert result == "ranged"

    def test_succeed_on_melee_attack(self, generator):
        """Test 'succeed on a melee attack' pattern."""
        description = "You succeed on a melee attack to strike the target."
        result = generator._detect_attack_roll(description)
        assert result == "melee"

    def test_ranged_attack_to_hit(self, generator):
        """Test 'ranged attack to hit' pattern."""
        description = "Requires a ranged attack to hit the target."
        result = generator._detect_attack_roll(description)
        assert result == "ranged"

    def test_requires_melee_attack(self, generator):
        """Test 'requires melee attack' pattern."""
        description = "This spell requires a melee attack to activate."
        result = generator._detect_attack_roll(description)
        assert result == "melee"

    def test_make_a_ranged_attack(self, generator):
        """Test 'make a ranged attack' pattern."""
        description = "You make a ranged attack against the target."
        result = generator._detect_attack_roll(description)
        assert result == "ranged"

    # ===== Buff Pattern Tests =====

    def test_bonus_to_attack_is_none(self, generator):
        """Test that 'bonus to attack' is recognized as buff (none)."""
        description = "This spell grants a +2 bonus to attack rolls."
        result = generator._detect_attack_roll(description)
        assert result == r"\textbf{none}"

    def test_penalty_to_ranged_attack_is_none(self, generator):
        """Test that 'penalty to ranged attack' is recognized as debuff (none)."""
        description = "Enemies take a -4 penalty to ranged attack rolls."
        result = generator._detect_attack_roll(description)
        assert result == r"\textbf{none}"

    def test_affects_melee_attack_is_none(self, generator):
        """Test that 'affects melee attack' is recognized as buff (none)."""
        description = "This spell affects all melee attack rolls made by allies."
        result = generator._detect_attack_roll(description)
        assert result == r"\textbf{none}"

    def test_grants_attack_bonus_is_none(self, generator):
        """Test that 'grants attack bonus' is recognized as buff (none)."""
        description = "The caster grants a +1 bonus to attack and damage."
        result = generator._detect_attack_roll(description)
        assert result == r"\textbf{none}"

    def test_applies_to_ranged_attacks_is_none(self, generator):
        """Test that 'applies to ranged attacks' is recognized as buff (none)."""
        description = "The bonus applies to all ranged attacks for the duration."
        result = generator._detect_attack_roll(description)
        assert result == r"\textbf{none}"
