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
