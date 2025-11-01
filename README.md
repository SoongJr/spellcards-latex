# LaTeX Spell Cards Project

This project creates printable spell cards for Pathfinder 1e characters using LaTeX.
Cards are designed to be printed on A6 index cards (4 per A4 sheet) with QR codes linking to online references.

## Documentation

- **[User Guide](docs/user-guide.md)** - How to compile and customize spell cards
- **[Generator Guide](docs/generator-guide.md)** - Using the Python GUI to generate spell cards
- **[API Reference](docs/api-reference.md)** - Complete LaTeX command reference

## Quick Start

### Prerequisites

- LaTeX installation (MikTeX, TeX Live, or use the included Docker environment)
- Python 3.10+ for the spell card generator
- Recommended: VS Code with LaTeX Workshop extension

**Docker/Codespaces**: The easiest setup is using GitHub Codespaces or the provided devcontainer, which includes all dependencies.

### Generate Spell Cards

```bash
spell_card_generator/spell_card_generator.sh
```

Follow the GUI workflow to select your character class and spells.

### Compile PDF

```bash
latexmk -pdf src/spellcards.tex
```

Output: `src/out/spellcards.pdf` (4 A6 cards per A4 sheet)

## Project Structure

```
spellcards-latex
├── docs/                            # Documentation
│   ├── user-guide.md               # LaTeX usage guide
│   ├── generator-guide.md          # Python generator guide
│   └── api-reference.md            # Command reference
├── spell_card_generator/           # Python GUI application
│   ├── spell_full.tsv              # Spell database (TSV format)
│   └── ...                         # Generator source code
├── src/
│   ├── spellcard.cls               # Document class (draft/final modes)
│   ├── spellcards.sty              # Main package loader
│   ├── spellcards.tex              # Main document
│   ├── cardify.tex                 # A6-on-A4 layout
│   ├── spellcards/                 # Package modules
│   │   ├── core.sty                # Foundation (variables, messages)
│   │   ├── properties.sty          # Spell data management
│   │   ├── deck.sty                # Deck organization
│   │   ├── level-markers.sty       # Spell level indicators
│   │   ├── qr-code.sty             # QR code positioning
│   │   ├── info-table.sty          # Attribute table rendering
│   │   ├── deck-index.sty          # Deck index card generation
│   │   └── content-layout.sty      # Card structure
│   └── spells/                     # Generated spell cards
│       ├── sor/                    # Sorcerer spells
│       │   ├── 0/                  # Level 0 (cantrips)
│       │   │   ├── AcidSplash.tex
│       │   │   └── ...
│       │   ├── 1/                  # Level 1
│       │   └── ...
│       ├── wiz/                    # Wizard spells
│       └── sor.tex                 # Sorcerer deck definitions
├── .devcontainer/
│   └── devcontainer.json           # VS Code dev container config
├── Dockerfile                      # Docker image with dependencies
└── README.md                       # This file
```

## Compilation

### in command line:
1. Open the repository folder in a terminal.
2. Run `latexmk -pdf src/spellcards.tex`.
3. The output PDF will be generated in directory `src/out`.

### In VS Code:
1. Open any .tex file in VS Code, e.g. the root file `src/spellcards.tex`.
2. Use the LaTeX Workshop extension to compile the document. This can typically be done by pressing `Ctrl + Alt + B`, using the command palette, or opening the extension tab ("TeX" icon).
3. The output PDF will be generated in directory `src/out`, open from Explorer tab or from LaTeX Workshop extension tab for additional options.

## Printing

### Print Settings
1. **Paper**: Use A4 cardstock (200-300 gsm recommended)
2. **Print Settings**: 
   - No scaling (100% size)
   - Double-sided printing, or a manual workaround:
      - Print all odd pages first
      - Put the stack back into the printer (oriented the "right" way!)
      - Print even pages in reverse order

### Post-Processing
1. **Cutting**: Follow the thin cutting guides to get 4 roughly A6-sized cards per sheet  
   **Note**: Unless you have professional equipment, your printer may not produce tolerances necessary to cut exactly down the center into A6.
2. **Coloring**: Use highlighters to color the spell level markers on the right edge
3. **Organization**: Sort by level or create themed decks (combat, utility, etc.)


See the [User Guide](docs/user-guide.md) for detailed printing instructions.

## Contributing

Contributions are welcome! This is a hobby project, so please be patient with review times.

For major changes:
1. Open an issue to discuss the change
2. Follow existing code quality standards (pylint 10/10, zero LaTeX warnings)
3. Add tests for new functionality  
   (LaTeX code is considered passing test if spellcards.pdf loks good... Apparently that's the industry standard)
4. Update documentation

For personal customizations (subjective spell changes), consider forking the repository.

Feel free to add spells for your personal character to this repo (maybe fork, create cards, PR when you're satisfied).  
It'll be good to have a pool of existing cards to draw from, especially of other classes.

There isn't yet a good workflow for coordinating multiple characters... Maybe `src/spellcards-<char>.tex` files?  
If there's interest, please let me know and I can consider publishing the package! Then it could be used in any LaTeX project, and the spell-cards-generator from this project used to create those cards. But those cards will not be shared, so everyone would need to create their own cards from scratch...  
Anyweay, let's talk about this if there even is any interest by other people!

## License

This project is open-source. See LICENSE file for details.
