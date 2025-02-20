# LaTeX Spell Cards Project

This project is designed to create easily printable spell cards for tabletop roleplaying games using LaTeX and KOMA Script classes for a specific character.  

Printing cards for all spells, even for just one class, could easily consume a whole stack of paper,
so we concentrate on printing the cards your character actually knows/uses.  

## Project Structure

```
spellcards-latex
├── src
│   ├── spellcards.tex        # Main LaTeX document for compiling spell cards
│   └── spells
│       └── spell1.tex  # LaTeX file for a specific spell card
├── .vscode
│   ├── extensions.json  # Recommended extensions for VS Code
│   └── settings.json    # Workspace-specific settings for LaTeX
├── .devcontainer
│   └── devcontainer.json # Configures the development environment settings
│   ├── Dockerfile        # Defines the Docker image with necessary LaTeX packages
├── .gitignore           # Files and directories to ignore by Git
└── README.md            # Documentation for the project
```

## Getting Started

### Prerequisites

- Ensure that MikTeX is installed on your system.
- Install recommended extensions in VS Code for optimal LaTeX editing.

The easiest way to do this is by using GitHub Codespaces.

### Creating spell cards
#### Import from database
The file src/spells/spell_full.tsv is a database of existing spells, exported from a [Google Doc](https://docs.google.com/spreadsheets/d/1cuwb3QSvWDD7GG5McdvyyRBpqycYuKMRsXgyrvxvLFI/edit?usp=sharing)

To create LaTeX-based spell cards from this file, run the script `convert.sh`.  
It requires that you specify the class of the character this card is intended for, as the spell-level can differ by class and is included on the card itself.  

Here are some examples:
- `./src/spells/convert.sh --class sor --source "PFRPG Core"`  
to extract all spells from the core rulebook for this class  
(not encouraged as it will create hundreds of files for you to manually adjust, but you _can_ do it)
- `./src/spells/convert.sh --class sor --source "PFRPG Core" --level 4`  
to extract all spells of the specified spell-level for this class (_not_ character level!)
- `./src/spells/convert.sh --class sor --name "Ice Storm"`  
to extract a single spell by name (must be an exact match!)

Technically, the only required parameter is `--class`, but unless you specify additional filters, the script will have to process thousands of spells and take upwards of 10 minutes to do so.  
The most common uses will probably be to either specify an exact spell name you chose for your character to use, or using at least `--level` to choose new spells from the generated files.  
But you do you.  

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

### Contributing

Feel free to add more spell cards by creating new `.tex` files in the `src/spells` directory. Follow the structure used in `spell1.tex` for consistency.

### License

This project is open-source. Contributions are welcome, but this is very much a hobby project! Do not expect PRs to be pulled in a matter of hours, or even days.  
Please ensure to follow the project's coding standards and guidelines.

If you simply wish to add your own spells, or make subjective adjustments to spells, it would be better to fork this repository and keep your changes there.
