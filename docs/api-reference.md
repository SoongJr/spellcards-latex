# LaTeX Spell Cards - API Reference

**Version**: 2.1  
**Date**: October 31, 2025

## Public Commands

All user-facing commands use PascalCase naming. Internal functions use snake_case and are not documented here.

---

## Document Class

### `\documentclass{spellcard}`

Custom document class for spell card generation.

**Options**:
- `[final]` (default): Double-sided, cardified layout (4 cards per A4 sheet)
- `[draft]`: Single-sided, no cardify (1 card per page)
- `[printer-margin=<dimension>]`: Uniform printer margin adjustment (e.g., `5mm`)
- `[printer-margin-x=<dimension>]`: Horizontal printer margin only
- `[printer-margin-y=<dimension>]`: Vertical printer margin only

**Examples**:
```latex
\documentclass{spellcard}                              % Final mode (default)
\documentclass[final]{spellcard}                       % Explicit final mode
\documentclass[draft]{spellcard}                       % Draft mode for testing
\documentclass[printer-margin=3mm]{spellcard}          % Uniform 3mm margin
\documentclass[printer-margin-x=2mm,printer-margin-y=5mm]{spellcard}  % Separate x/y margins
```

**Printer Margins**:
- **Default**: No printer margins (assumes full page printing)
- **Priority**: `printer-margin` overrides `printer-margin-x` and `printer-margin-y` if both specified
- **Note**: Most users should use printer settings ("fit to page") instead of adjusting margins in LaTeX

**Loads**: `spellcards` package (with printer margin options), `inputenc` (UTF-8), `amsmath`

---

## Spell Card Environment

### `\begin{SpellCard}{class}{name}{level}...\end{SpellCard}`

Defines a spell card with properties and description.

**Parameters**:
1. `class` - Character class abbreviation (e.g., "sor", "wiz", "clr")
2. `name` - Spell name (e.g., "Fireball", "Magic Missile")
3. `level` - Spell level (0-9)

**Content**: Properties (`\SpellProp`), QR codes (`\SpellCardQR`), and description text

**Example**:
```latex
\begin{SpellCard}{sor}{Fireball}{3}
  \SpellProp{school}{Evocation [Fire]}
  \SpellProp{castingtime}{1 standard action}
  \SpellProp{range}{long (400 ft. + 40 ft./level)}
  \SpellCardQR{https://aonprd.com/SpellDisplay.aspx?ItemName=Fireball}
  
  You create a fiery explosion that deals 1d6 points of fire
  damage per caster level (maximum 10d6).
\end{SpellCard}
```

**Behavior**:
- Renders spell card with title, property table, and description
- Draws spell level marker on right edge
- Draws deck label at top (if in a deck)
- Places QR codes at bottom
- Clears to next odd page after card (final mode)

---

## Spell Properties

### `\SpellProp{key}{value}`

Defines a spell attribute (range, duration, components, etc.).

**Parameters**:
1. `key` - Property name (lowercase, no spaces)
2. `value` - Property value (text, can include LaTeX formatting)

**Standard Properties**:
- `school` - School of magic and descriptors
- `castingtime` - Time required to cast
- `components` - V, S, M, F, DF components
- `range` - Spell range
- `targets` / `area` / `effect` - What the spell affects
- `duration` - How long the spell lasts
- `savingthrow` - Saving throw type and effect
- `spellresistance` - Whether spell resistance applies
- `attackroll` - Attack roll type (melee touch, ranged touch, or none)

**Example**:
```latex
\SpellProp{school}{Evocation [Force]}
\SpellProp{castingtime}{1 standard action}
\SpellProp{components}{V, S}
\SpellProp{range}{medium (100 ft. + 10 ft./level)}
\SpellProp{targets}{up to five creatures}
\SpellProp{duration}{instantaneous}
\SpellProp{savingthrow}{none}
\SpellProp{spellresistance}{yes}
\SpellProp{attackroll}{none}
```

**Notes**:
- Properties are optional (missing properties show as "—" in table)
- Order doesn't matter (table layout is fixed)
- Values can include LaTeX commands (e.g., `\textit{`, `\textbf{`)

---

## QR Codes

### `\SpellCardQR{url}`

Adds a QR code linking to online spell reference.

**Parameters**:
1. `url` - Web URL or arbitrary text

**Maximum**: 2 QR codes per card (additional ones are ignored with warning)

**Positioning**:
- Automatically positioned at bottom of card
- First QR: 2cm from page edge, opposite page number
- Second QR: 4cm from page edge, same side as page number
- Page parity aware (odd/even pages)

**Example**:
```latex
\SpellCardQR{https://aonprd.com/SpellDisplay.aspx?ItemName=Fireball}
\SpellCardQR{https://pf.tools/spell/fireball}
```

**URL Validation**:
The generator validates URLs, but LaTeX accepts any text. For non-URLs, the QR code will encode the text literally.

---

## Table Width

### `\SpellCardInfo[ratio]`

Adjusts the width ratio of the spell attribute table columns.

**Parameters**:
1. `ratio` (optional) - Width ratio for left column (0.0 to 1.0, default 0.5)

**Example**:
```latex
\begin{SpellCard}{sor}{Fireball}{3}
  \SpellProp{school}{Evocation [Fire]}
  % ... other properties
  \SpellCardInfo[0.4]  % Left: 40%, Right: 60%
  \SpellCardQR{https://...}
  % ... description
\end{SpellCard}

% Or use default 50/50 split
\begin{SpellCard}{sor}{Magic Missile}{1}
  \SpellProp{school}{Evocation [Force]}
  % ... other properties
  \SpellCardInfo  % Default: 50/50
  \SpellCardQR{https://...}
  % ... description
\end{SpellCard}
```

**Default**: 0.5 (50% left, 50% right)

**When to use**:
- Left column has very short entries but right column has long text that wraps awkwardly (use smaller ratio like 0.4)

**Note**: The generator preserves custom ratios when regenerating cards.

---

## Deck Organization

### `\begin{SpellDeck}{name}...\end{SpellDeck}`

Groups spells into a named deck with visual label.

**Parameters**:
1. `name` - Deck name (e.g., "Combat", "Utility", "Social")
   - Use empty braces `{}` for unnamed first deck (e.g. full list of known spells for arcane spellcasters)
   - Use descriptive names for subsequent decks

**Alternative Syntax**: `\begin{SpellDeck}[name]` with square brackets also works

**Example**:
```latex
% First deck: unnamed (all spells)
\begin{SpellDeck}{}
  \IncludeSpell{spells/sor/0/AcidSplash.tex}
  \IncludeSpell{spells/sor/1/MagicMissile.tex}
  \IncludeSpell{spells/sor/3/Fireball.tex}
\end{SpellDeck}

% Named decks
\begin{SpellDeck}{Combat Spells}
  \IncludeSpell{spells/sor/1/MagicMissile.tex}
  \IncludeSpell{spells/sor/3/Fireball.tex}
\end{SpellDeck}

\begin{SpellDeck}[Utility Spells]  % Alternative syntax with brackets
  \IncludeSpell{spells/sor/0/DetectMagic.tex}
  \IncludeSpell{spells/sor/2/Knock.tex}
\end{SpellDeck}
```

**Behavior**:
- Deck name displayed at top of each card in italics (as entered)
- Deck tracking for future index card generation

**Restrictions**:
- First deck must be unnamed (empty braces or brackets)
- Consecutive decks must be provided a name
- Decks cannot be nested

---

## Including Spells

### `\IncludeSpell[options]{filepath}`

Includes a spell card file and optionally prints it.

**Parameters**:
1. `options` (optional) - Key-value options
2. `filepath` - Relative path to spell `.tex` file

**Options**:
- `print=true` (default): Print the spell card
- `print=false` / `noprint`: Include but don't print (for deck tracking)

**Examples**:
```latex
% Standard inclusion (prints card)
\IncludeSpell{spells/sor/1/MagicMissile.tex}

% Include but don't print
\IncludeSpell[noprint]{spells/sor/1/Shield.tex}
\IncludeSpell[print=false]{spells/sor/2/Invisibility.tex}

% Explicit print (unnecessary, this is default)
\IncludeSpell[print=true]{spells/sor/3/Fireball.tex}
```

**File Checking**: Verifies file exists and emits error if not found

**Use Cases**:
- `print=false` for spells your character knows but you don't wish to print
- Temporarily disable cards without removing from source
- Track spells in deck without printing

---

## Utility Commands

### `\SpellMarkerChart`

Generates a reference card showing all spell level markers (0-9).

**Parameters**: None

**Example**:
```latex
\documentclass{spellcard}
\begin{document}

\SpellMarkerChart  % Reference card on first page

% Regular spell cards follow
\IncludeSpell{spells/sor/0/AcidSplash.tex}
\IncludeSpell{spells/sor/1/MagicMissile.tex}

\end{document}
```

**Use Case**: Print this card once and color the markers with highlighters to indicate which colors represent which spell levels for your physical card deck.

**Appearance**: Shows markers on right edge identical to how they appear on actual spell cards

---

### `\ShowDeck{deck_number}`

Displays deck information to console (debugging utility).

**Parameters**:
1. `deck_number` - Deck number to query (0 = first deck, 1 = second deck, etc.)

**Example**:
```latex
\begin{SpellDeck}{}  % First deck (number 0)
  \IncludeSpell{spells/sor/1/MagicMissile.tex}
\end{SpellDeck}

\begin{SpellDeck}{Combat}  % Second deck (number 1)
  \IncludeSpell{spells/sor/3/Fireball.tex}
\end{SpellDeck}

\ShowDeck{0}  % Shows: "Deck 0 contains 1 spells" + spell metadata
\ShowDeck{1}  % Shows: "Deck 1 contains 1 spells" + spell metadata
```

**Output**: Writes deck information to console/log file (not to PDF)

**Use Case**: 
- Debugging deck organization
- Verifying spell counts before generating index cards
- Checking deck registration worked correctly

**Note**: Deck numbers are assigned in order: first `\begin{SpellDeck}` is 0, second is 1, etc.

---

## Package Options

The `spellcards` package is loaded automatically by the `spellcard` document class.

**Printer Margin Options**: Configure via document class options (see `\documentclass{spellcard}` above)

**Direct Package Usage**: Not recommended - use the document class instead for proper configuration

---

## Internal Functions

The following are internal functions (snake_case) not intended for direct use:

- `\spellcard_*` - Internal card rendering functions
- `\register_spell` - Spell registration (used by `\begin{SpellCard}`)
- `\deck_spell_count`, `\deck_count` - Deck query functions (reserved for future index cards)

**Do not use these directly** - they may change without notice.

---

## Version History

### Version 2.1 (October 31, 2025)
- PascalCase public API
- Removed legacy compatibility
- Clean, modern command names

### Version 2.0-expl3 (October 2025)
- Full expl3 implementation
- Modular package structure
- Document class with draft/final modes

### Version 1.x (Legacy)
- Original LaTeX2e implementation
- Compatibility layer
- `\newcommand` based properties
