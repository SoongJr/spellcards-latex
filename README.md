# LaTeX Spell Cards Project

This project is designed to create easily printable spell cards for tabletop roleplaying games using LaTeX and KOMA Script classes for a specific character.  

Printing cards for all spells, even for just one class, could easily consume a whole stack of paper,
so we concentrate on printing the cards your character actually knows/uses.  

## Project Structure

```
spellcards-latex
├── spell_card_generator             # Folder containing a GUI tool for generating spell cards
├── src
│   ├── spellcards.tex               # Main LaTeX document for compiling spell cards
│   └── spells
│       ├── spell_full.tsv           # Database of spells in TSV format
│       ├── convert.sh               # Legacy command-line conversion script
│       └── spell1.tex               # LaTeX file for a specific spell card
├── .vscode
│   ├── extensions.json              # Recommended extensions for VS Code
│   └── settings.json                # Workspace-specific settings for LaTeX
├── .devcontainer
│   └── devcontainer.json            # Configures the development environment settings
├── Dockerfile                       # Defines the Docker image with necessary packages
├── pyproject.toml                   # Python project configuration and dependencies
├── requirements.txt                 # Python requirements (poetry)
├── .gitignore                       # Files and directories to ignore by Git
└── README.md                        # Documentation for the project
```

## Getting Started

### Prerequisites

- Ensure that MikTeX is installed on your system.
- Python 3.8+ for the GUI spell card generator
- Install recommended extensions in VS Code for optimal LaTeX editing.

The easiest way to do this is by using GitHub Codespaces or the provided Docker environment, which includes all necessary dependencies.

**Note**: The devcontainer includes `fonts-noto-color-emoji` for Unicode symbol and emoji support in the spell card generator GUI. If you encounter display issues with symbols (✓, ✗, ⚠, etc.), rebuild the devcontainer to ensure fonts are properly installed.

### Creating spell cards

The file spell_card_generator/spell_full.tsv is a database of existing spells, exported from a [Google Doc](https://docs.google.com/spreadsheets/d/1cuwb3QSvWDD7GG5McdvyyRBpqycYuKMRsXgyrvxvLFI/edit?usp=sharing)  
Creating LaTeX-formatted spell cards from this information is supported by tooling, but still requires manual modification afterwards.

#### spell card generator

Folder `spell_card_generator` contains a GUI application for generating spell cards from the spell database.  
Start it by executing `spell_card_generator/spell_card_generator.sh` from the repository root.

The generated files will be placed in `src/spells/<class>/<level>/` directories and need to be manually fine-tuned before including them in your document.

#### Include and adjust the generated result
Follow the instructions of the tool and this general workflow:  
1. To actually include the generated card in the PDF it needs an `\input{}` statement in spellcards.tex (or one of its included files)
1. Once thus included, take a look at linter violations and address them.  
   If pandoc created code that needs additional packages to render the description, you will notice this here.
1. Finally, take a look at the PDF:
   1. Some parts of the pandoc-generated description, particularly tables, might not be well-formatted
   1. If the text only barely spills onto the back of the card, consider altering the description so everything is on the front
   1. Try to keep spells on a single card.  
      It is better to heavily abridge the description and have to look up details when needed, than having to juggle four cards for a single spell (cf. Teleport or Permanency)
   1. Fix hyphenation and under-/overfull boxes

#### Re-creating spells
This might be required if either `spell_full.tsv` or `spell_card_generator` have changed.

The spell card generator GUI includes a "Select Existing" button, allowing users to re-import and update previously generated spell cards.  
You will be asked to confirm the overwrite and whether you wish to preserve URLs,
descriptions, and **property modifications**.

**Property Preservation Feature**: When you customize spell properties
(e.g. fix chktex warnings, clarify targets, simplify components...) in the generated `.tex` files,
the generator can preserve your modifications even when regenerating from an updated database.

**⚠️ Critical Requirement**: To preserve your modifications, you must first make a copy of the value
and comment it with `% original: {value}` so the generator knows that you've modified this value
and can detect changes in the database when they happen.

**Note**: This preservation logic applies to spell properties (like `\targets`, `\castingtime`, etc.),
but **not to URLs** (`\urlenglish`, `\urlsecondary`). URLs are either preserved entirely from the
existing card or generated fresh - there's no comparison or conflict detection for URL values.

Example:
```latex
% Line generated by spell_card_generator:
\newcommand{\targets}{one object or 10-ft. square}

% ✅ Your modification to address chktex warning:
\newcommand{\targets}{one object or 10-ft.\ square}% original: {one object or 10-ft. square}

% ❌ This would be interpreted as a generated value an overwritten by next generator run:
\newcommand{\targets}{one object or 10-ft.\ square}
```

### Recommended Extensions

- **LaTeX Workshop**: Provides a rich editing experience for LaTeX documents, including syntax highlighting, preview, and compilation.

### Compiling the LaTeX Files

#### in command line:
1. Open the repository folder in a terminal.
2. Run `latexmk -pdf src/spellcards.tex`.
3. The output PDF will be generated in directory `src/out` and opened in VS Code, refreshing when .tex files change (refresh is performed by LaTeX Workshop extension on save of files).

#### in VS Code:
1. Open any .tex file in VS Code, e.g. the root file `src/spellcards.tex`.
2. Use the LaTeX Workshop extension to compile the document. This can typically be done by pressing `Ctrl + Alt + B`, using the command palette, or opening the extension tab ("TeX" icon).
3. The output PDF will be generated in directory `src/out`, open from Explorer tab or from LaTeX Workshop extension tab for additional options.

### Printing and post-processing
1. In `src/spellcards.tex` ensure you're out of drafting mode and "cardify" is included before creating the PDF
1. Print the PDF double-sided:
   - If your printer supports double-sided printing and can deal with the card-stock you use, just use that.
   - Otherwise, print all odd pages first, then put the stack of print-outs back into the printer so the next print goes onto the backside.  
     Now print the even pages _in reverse order_
1. Cut the DIN A4 pages into cards (somewhere between DIN A6/B7):  
   Unless you have professional equipment, your printer will not be able to produce the tolerances
   that would be necessary to just cut the printed pages down the center into DIN A6.  
   For this reason, there are faint guides printed for you to cut along, both through the middle and along the margins.  
   If you do not see the outer margins, increase the value for `\printermarginx` in [src/cardify.tex](src/cardify.tex).  
   Tipps for best results:
   - If your printer's in-tray is open to the environment, try to help it pull in the sheets as straight as possible.
   - Use a cutting-mat, straight-edge and sharp craft knife. Using scissors will shift the pages if you cut multiple at a time.
   - Take multiple, light cutting passes instead of a single heavy one. Heavy cuts will also move the papers.
   - Ensure your blade's tip is still sharp. Consider using a fresh blade even if it seems wasteful. Paper is harsh on metal edges and dulls them quickly.
1. Sort your cards (at least for spell-level).  
   (The cards were supposed to be re-ordered so they would line up sorted after cutting, but that does not appear to work, so you have to sort manually.)
1. Each spell's front face has a marker on the right-hand edge at a specific height for that level.  
   Take a highlighter/textmarker or similar and color this in to make it easy to flip through a stack of these cards.  
   Maybe get three different colors and alternate between them.

You may wish to consider printing multiple copies of each card to build "decks", e.g.:  
All spells that deal damage without allowing spell resistance, all spells that give an advantage in social interactions, spells that are good against physically tough enemies, or against large numbers, or fire-resistant ones.  
You'll probably end up with one deck of "misc" or seldom-used spells just to keep your "main deck" handleable.

### Contributing

Feel free to add more spell cards by creating new `.tex` files in the `src/spells` directory. Follow the structure used in `spell1.tex` for consistency.

### License

This project is open-source. Contributions are welcome, but this is very much a hobby project! Do not expect PRs to be pulled in a matter of hours, or even days.  
Please ensure to follow the project's coding standards and guidelines.

If you simply wish to add your own spells, or make subjective adjustments to spells, it would be better to fork this repository and keep your changes there.
