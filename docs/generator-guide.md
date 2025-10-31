# Spell Card Generator - User Guide

**Version**: 2.1  
**Date**: October 31, 2025

## Overview

The spell card generator is a Python GUI application that creates LaTeX spell card files from a database of Pathfinder 1e spells.

## Starting the Generator

```bash
cd spell_card_generator
poetry run spell-card-generator
```

The GUI opens with a multi-step workflow.

## Generating New Spell Cards

### Step 1: Select Character Class

- Choose exactly one character class (e.g., Sorcerer, Wizard, Cleric)
- Classes are organized into categories: Core, Base, Hybrid, Prestige, etc.
- Double-click a class to proceed to next step

### Step 2: Select Spells

- Filter spells by level, source book, or search term
- Check boxes next to spells you want to generate
- Click **Next** when done

### Step 3: Configure URLs

For each spell, configure QR code URLs:

**Primary URL**: Automatically generated from spell name
- Example: "Fireball" → `https://aonprd.com/SpellDisplay.aspx?ItemName=Fireball`
- Editable if the auto-generated URL is incorrect

**Secondary URL**: Optional second reference
- Leave as `<secondary-url>` placeholder, or enter a URL
- Common options: `https://pf.tools/spell/spell-name`

**URL Validation**: The generator checks if URLs are valid web addresses:
- ✅ Green checkmark: Valid URL format
- ⚠️ Warning icon: Not a valid URL (will add `FIXME` comment in generated file)
- Plain text allowed: You can use non-URL text if needed

### Step 4: Preview & Generate

- Review your selections (class, spell count, conflicts)
- Click **Generate Cards** to create `.tex` files
- Files are written to `src/spells/{class}/{level}/{SpellName}.tex`

## Handling Existing Files

If spell card files already exist, the generator detects them and offers options.

### Conflict Resolution Step

When conflicts are detected, you see a list of existing cards with:
- File path
- Last modified date
- Content preview

**For each existing card, choose**:
- ☑️ **Overwrite**: Replace file with freshly generated version
- ☐ **Preserve Description**: Keep existing description, update properties
- ☐ **Preserve URLs**: Keep existing QR codes

**Bulk Actions**:
- "Overwrite All" - Replace all existing files
- "Preserve All Descriptions" - Keep descriptions for all files
- "Preserve All URLs" - Keep URLs for all files

**Common Scenarios**:

1. **First time generating**: No conflicts, proceed directly to URL configuration
2. **Updating spell database**: Overwrite all to get latest data
3. **Custom descriptions**: Preserve descriptions to keep your notes
4. **Custom URLs**: Preserve URLs to keep your references

## Regenerating All Spells for a Class

To regenerate all existing spell cards for a class:

1. Select the same class you used previously
2. Click **Load Existing** (or similar) to select all spells with existing cards
3. Choose conflict resolution:
   - **Preserve descriptions and URLs**: Update only spell properties from database
   - **Overwrite all**: Fresh generation (lose manual edits)
4. Generate

**Why regenerate?**
- Spell database updated with errata
- Changing URL preferences
- Standardizing formatting across cards

## Property Preservation

The generator preserves manual edits to spell properties when regenerating:

### How It Works

When you check "Preserve Description" for a card:
1. Generator reads existing `.tex` file
2. Extracts property values from `\SpellProp{key}{value}` lines
3. Uses **your edited values** instead of database values
4. Writes new file with your customizations intact

### Example Workflow

**Initial generation** (from database):
```latex
\SpellProp{range}{medium (100 ft. + 10 ft./level)}
\SpellProp{duration}{instantaneous}
```

**You edit manually** (house rule):
```latex
\SpellProp{range}{long (400 ft. + 40 ft./level)}  % House rule: extended range
\SpellProp{duration}{instantaneous}
```

**Regenerate with "Preserve Description"**:
- Generator reads: `range = long (400 ft. + 40 ft./level)`
- Writes new file with your custom range value
- Description also preserved (everything after `\SpellCardQR` lines)

### What Gets Preserved

✅ **Preserved**:
- `\SpellProp{key}{value}` values **with `% original:` comment** (see below)
- Description text (between `% SPELL DESCRIPTION BEGIN/END` markers)
- QR code URLs (if "Preserve URLs" checked)
- Table width ratio (if you added `\SpellCardInfo[ratio]`)

❌ **Not preserved** (regenerated from database):
- Spell level
- Spell name
- Character class
- Property values **without `% original:` comment** (assumed to be from database)

### Property Preservation Requirements

**Critical**: To preserve property modifications, you **must** add a `% original: {value}` comment:

```latex
\SpellProp{range}{long (400 ft. + 40 ft./level)}% original: {medium (100 ft. + 10 ft./level)}
```

**How it works**:
1. Generator sees modified value has `% original:` comment
2. Preserves your modified value when regenerating
3. Updates comment if database changes, allowing you to review conflicts

**Without the comment**: Generator assumes value came from database and will overwrite it.

### Best Practices

1. **Always add `% original:` comment** when modifying properties:
   ```latex
   \SpellProp{components}{NULL}% original: {V, S, M (diamond dust worth 500 gp)}
   ```

2. **Use preserve options** when:
   - You've written custom descriptions
   - You've adjusted properties for house rules
   - You've configured specific URLs

3. **Overwrite** when:
   - You want fresh data from updated spell database
   - You haven't made manual edits
   - You're standardizing formatting

## URL Validation Feature

The generator validates URLs before writing to files:

### Valid URLs
- Start with `http://` or `https://`
- Contain a domain name
- Result: Written as-is, no warnings

### Invalid URLs
- Start with `http://` or `https://` but not reachable
- Example: A generated URL that was guessed incorrectly
- Result: User is meant to catch and fix this, but if ignored, will be written to file with LaTeX package warning message

**Example output for invalid URL**:
```latex
\SpellCardQR{https://broken-url}
  \msg_warning:nnn { spellcard } { invalid-url } { https://broken-url }
```

### Non-URL Text

If you enter text that doesn't start with `http://` or `https://`:
- **Result**: Accepted as-is, no validation or warnings
- **Example**: `#0123ABC`, "page 42 in core rule book", or any custom text
- **Use case**: Placeholder text, notes, custom identifiers

**Example output for non-URL text**:
```latex
\SpellCardQR{See page 42}
```

The LaTeX package will render whatever text you provide as QR code content.

## Output Files

Generated files are written to:
```
src/spells/{class}/{level}/{SpellName}.tex
```

Examples:
- `src/spells/sor/0/Acid Splash.tex`
- `src/spells/sor/3/Fireball.tex`
- `src/spells/sor/4/Invisibility, Greater.tex`

**Note**: File names preserve the exact spell name from the database, including spaces and commas.

**File format**: Version 2.1 with PascalCase commands (`\SpellProp`, `\SpellCardQR`)

## Troubleshooting

### "No spells found for this class"
- Database might not have spells for that class
- Check `spell_full.tsv` exists and contains data

### "Failed to write file"
- Check file permissions
- Verify `src/spells/{class}/` directories exist
- Check disk space

### Generated URLs are wrong
- Edit them in the URL configuration step
- Or manually edit the `.tex` file after generation

### Properties not preserved
- Ensure you checked "Preserve Description" in conflict resolution
- Verify `.tex` file uses version 2.1 format
- Check property name matches exactly (case-sensitive)

## Tips

- **Preview before generating**: Use the summary in Step 4
- **Bulk operations**: Use "Preserve All" buttons for consistent behavior
- **Test with one spell**: Generate a single card first to verify settings
- **Keep backups**: Use git to track changes to spell card files
- **URL shorteners**: Use for very long URLs to make QR codes more scannable
