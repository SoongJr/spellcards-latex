"""Configuration constants and settings."""


class CharacterClasses:
    """Character class definitions and categorization."""

    CORE = ["sor", "wiz", "cleric", "druid", "ranger", "bard", "paladin"]
    BASE = [
        "alchemist",
        "summoner",
        "witch",
        "inquisitor",
        "oracle",
        "antipaladin",
        "magus",
    ]
    HYBRID = [
        "bloodrager",
        "hunter",
        "investigator",
        "shaman",
        "skald",
        "summoner_unchained",
    ]
    OCCULT = ["psychic", "medium", "mesmerist", "occultist", "spiritualist"]

    DISPLAY_NAMES = {
        "sor": "Sorcerer",
        "wiz": "Wizard",
        "summoner_unchained": "Summoner (Unchained)",
        "antipaladin": "Antipaladin",
        "investigator": "Investigator",
        "spiritualist": "Spiritualist",
        "mesmerist": "Mesmerist",
        "occultist": "Occultist",
        "psychic": "Psychic",
        "medium": "Medium",
        "cleric": "Cleric",
        "druid": "Druid",
        "ranger": "Ranger",
        "bard": "Bard",
        "paladin": "Paladin",
        "alchemist": "Alchemist",
        "summoner": "Summoner",
        "witch": "Witch",
        "inquisitor": "Inquisitor",
        "oracle": "Oracle",
        "magus": "Magus",
        "bloodrager": "Bloodrager",
        "hunter": "Hunter",
        "shaman": "Shaman",
        "skald": "Skald",
    }

    CATEGORIES = {
        "Core Classes": CORE,
        "Base Classes": BASE,
        "Hybrid Classes": HYBRID,
        "Occult Classes": OCCULT,
    }


class SpellColumns:
    """Column names in the spell database."""

    NAME = "name"
    SCHOOL = "school"
    SUBSCHOOL = "subschool"
    DESCRIPTOR = "descriptor"
    SOURCE = "source"
    DESCRIPTION = "description"
    DESCRIPTION_FORMATTED = "description_formatted"
    CASTING_TIME = "casting_time"
    COMPONENTS = "components"
    COSTLY_COMPONENTS = "costly_components"
    RANGE = "range"
    AREA = "area"
    EFFECT = "effect"
    TARGETS = "targets"
    DURATION = "duration"
    DISMISSIBLE = "dismissible"
    SHAPEABLE = "shapeable"
    SAVING_THROW = "saving_throw"
    SPELL_RESISTANCE = "spell_resistance"
    VERBAL = "verbal"
    SOMATIC = "somatic"
    MATERIAL = "material"
    FOCUS = "focus"
    DIVINE_FOCUS = "divine_focus"
    DEITY = "deity"
    SLA_LEVEL = "SLA_Level"
    DOMAIN = "domain"
    LINKTEXT = "linktext"
    ID = "id"
    MATERIAL_COSTS = "material_costs"
    BLOODLINE = "bloodline"
    PATRON = "patron"
    MYTHIC_TEXT = "mythic_text"
    AUGMENTED = "augmented"
    HAUNT_STATISTICS = "haunt_statistics"
    RUSE = "ruse"
    DRACONIC = "draconic"
    MEDITATIVE = "meditative"

    # Descriptor columns
    ACID = "acid"
    AIR = "air"
    CHAOTIC = "chaotic"
    COLD = "cold"
    CURSE = "curse"
    DARKNESS = "darkness"
    DEATH = "death"
    DISEASE = "disease"
    EARTH = "earth"
    ELECTRICITY = "electricity"
    EMOTION = "emotion"
    EVIL = "evil"
    FEAR = "fear"
    FIRE = "fire"
    FORCE = "force"
    GOOD = "good"
    LANGUAGE_DEPENDENT = "language_dependent"
    LAWFUL = "lawful"
    LIGHT = "light"
    MIND_AFFECTING = "mind_affecting"
    PAIN = "pain"
    POISON = "poison"
    SHADOW = "shadow"
    SONIC = "sonic"
    WATER = "water"


class Config:
    """Application configuration constants."""

    SPELL_DATA_FILE = "spell_full.tsv"
    OUTPUT_DIR_TEMPLATE = "src/spells/{class_name}"
    DEFAULT_GERMAN_URL = (
        "http://prd.5footstep.de/Grundregelwerk/Zauber/<german-spell-name>"
    )
    ENGLISH_URL_BASE = "https://www.d20pfsrd.com/magic/all-spells"
    NULL_VALUE = "NULL"


class UIConfig:
    """UI-specific configuration."""

    WINDOW_TITLE = "Spell Card Generator"
    WINDOW_SIZE = "1200x800"
    TREE_HEIGHT = 15
    MAIN_PADDING = "10"

    # Tree view columns
    TREE_COLUMNS = ("Select", "Name", "Level", "School", "Source")
    TREE_COLUMN_WIDTHS = {
        "Select": 60,
        "Name": 200,
        "Level": 60,
        "School": 120,
        "Source": 120,
    }
    TREE_COLUMN_MIN_WIDTHS = {
        "Select": 60,
        "Name": 150,
        "Level": 50,
        "School": 100,
        "Source": 100,
    }

    # Icons
    EXPAND_ICON = "▼"
    COLLAPSE_ICON = "▶"
    CHECKED_ICON = "[X]"
    UNCHECKED_ICON = "[ ]"
