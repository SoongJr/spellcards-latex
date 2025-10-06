# LaTeX Spell Cards Project

This project is designed to create easily printable spell cards for tabletop roleplaying games using LaTeX and KOMA Script classes for a specific character.  

Printing cards for all spells, even for just one class, could easily consume a whole stack of paper,
so we concentrate on printing the cards your character actually knows/uses.  

## Project Structure

```
spellcards-latex
├── src
│   ├── spellcards.tex               # Main LaTeX document for compiling spell cards
│   ├── spell_card_generator.py      # GUI tool for generating spell cards
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

### Creating spell cards

The file src/spells/spell_full.tsv is a database of existing spells, exported from a [Google Doc](https://docs.google.com/spreadsheets/d/1cuwb3QSvWDD7GG5McdvyyRBpqycYuKMRsXgyrvxvLFI/edit?usp=sharing)  
Creating LaTeX-formatted spell cards from this information is supported by tools, but still requires manual modification afterwards.

#### Using the GUI Tool (Recommended)

We provide a user-friendly GUI application for generating spell cards from the spell database. This tool makes it easy to browse, filter, and select spells for your character.

**Run the GUI application:**
   ```bash
   # Option 1: Use the launcher script (recommended)
   ./run_gui.sh
   
   # Option 2: Run directly with poetry
   pip install -r requirements.txt
   poetry install
   poetry run python src/spell_card_generator.py
   ```

**Using the GUI Tool:**

1. **Select Character Class:** Choose your character's class from the dropdown menu. This will filter the available spells and determine spell levels.

2. **Apply Filters (Optional):**
   - **Spell Level:** Filter by specific spell level (0-9)
   - **Source Book:** Filter by source book (e.g., "PFRPG Core")
   - **Search Name:** Type to search for specific spell names

3. **Select Spells:** Click on spells in the list to select/deselect them. Use the "Select All" and "Deselect All" buttons for bulk operations.

4. **Preview Spells:** Select a spell and click "Preview Spell" to see detailed information before generating the card.

5. **Configure Options:**
   - **Overwrite existing files:** Check this to replace existing spell card files
   - **German URL Template:** Customize the German language URL template if needed

6. **Generate Cards:** Click "Generate Spell Cards" to create LaTeX files for your selected spells.

The generated files will be placed in `src/spells/<class>/<level>/` directories and can be manually fine-tuned before including them in your document.

#### Command Line Tool (Legacy)

You can also use the legacy command-line script `convert.sh` if you prefer:

```bash
# Extract all spells from core rulebook for sorcerer
./src/spells/convert.sh --class sor --source "PFRPG Core"

# Extract level 4 spells for sorcerer from core rulebook  
./src/spells/convert.sh --class sor --source "PFRPG Core" --level 4

# Extract a single spell by exact name
./src/spells/convert.sh --class sor --name "Ice Storm"
```

The GUI tool is recommended as it provides better usability and prevents common mistakes.  

#### Include and adjust the generated result
Follow the instructions of the script and this general workflow:  
1. To actually include the generated card in the PDF it needs an `\input{}` statement in spellcards.tex
1. Once thus included, take a look at linter violations and address them.  
If pandoc created code that needs additional packages to render the description, you will notice this here.
1. Finally, take a look at the PDF:
   1. Some parts of the pandoc-generated description, particularly tables, might not be well-formatted
   1. If the text only barely spills onto the back of the card, consider altering the description so everything is on the front
   1. Try to keep spells on a single card.  
   It is better to heavily abridge the description and have to look up details when needed, than having to juggle four cards for a single spell (cf. Teleport or Permanency)
   1. Fix hyphenation and under-/overfull boxes

#### Re-creating spells
This might be required if either the spell_full.tsv or convert.sh have changed.  
Use this command to recreate all spells for a given class:  
```bash
class=sor # short-hand for the class you want to re-recreate for (sor, wiz, etc.)
while IFS= read -r spell; do src/spells/convert.sh --overwrite -c $class -n "$spell"; done < <(find src/spells/$class -name "*.tex" -exec bash -c 'filename=$(basename "{}"); echo ${filename%.*}' \;)
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
