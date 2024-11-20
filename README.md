# Purpose

This is a tool to import Pathfinder 1e spell information from the [Spells DB](https://home.pathfindercommunity.net/home/databases/spells)
and format them as printable index/flash cards.  

Design decisions were made to hopefully ensure this will still be running, without maintainer intervention, in ten year's time,
and even when it breaks down someone can simply fork this repo and fix it,
instead of having to start from scratch when a closed-source solution inevitably breaks down.  

This sacrifices other things, like ease of use especially for customization.
You _can_ customize the output, but may need to modify LaTeX code (this is no point-and-click adventure!)

## Import/Update data from GoogleDocs
The original data is hosted in this Google Doc:
https://docs.google.com/spreadsheets/d/1cuwb3QSvWDD7GG5McdvyyRBpqycYuKMRsXgyrvxvLFI  

Importing this data automatically on demand would require setting up Google API, storing Access Tokens, worrying about rate limiting...
So the data is imported by a manuall process, as it is expected to not change very often at this point:

1. open https://docs.google.com/spreadsheets/d/1cuwb3QSvWDD7GG5McdvyyRBpqycYuKMRsXgyrvxvLFI
1. under "File" -> "Download" choose the option "Tab Separated Values (.tsv)"
   (This format is more robust than .csv, which is locale-dependant; some countries actually use semicolons instead of commas...)  
1. [optional] open the downloaded file in some other program, sort and filter to suit your needs, making sure to save as .tsv again
1. move the resulting file into the "resources" folder, replacing the file "spell_full.tsv"
1. ensure the format of the data has not changed! Moved, removed or added columns must be reflected int he list of keys hardcoded in import-data.tex  

## Create printable PDF from imported data
### Process
All of the options below basically run this command:  
```
pdflatex -halt-on-error -interaction=errorstopmode -shell-escape -synctex=1 -output-directory=output spellcards
```  

### IDE
There are many IDEs to work on LaTeX documents. This repository is focussed on using Visual Studio Code using the extension "LaTeX Workshop" and the LaTeX installation "TeX Live".  
You should be able to build the PDF with "latexmk" (the default) from the IDE.
This will refresh the preview and the actual PDF anytime you save the document.  

### Codespaces
With GitHub Codespace you can create a PDF on the Cloud, no need to set anything up locally.  
1. Open the "<> Code" button and create a Codespace  
  (texlive, chktex and LaTeX Workshop are installed and properly configured)  
1. You get a Web-IDE, open any tex file you may want to edit (e.g. cards.tex)  
1. There will be a green arrow in the top right corner to create the PDF, and a button to show a auto-refreshing preview of your current document  

### Windows Batch
The folder "misc" contains file "make.bat" you may use to create a PDF locally, provided pdflatex is installed and available in  PATH.  

### Linux/MacOS makefile
The folder "misc" contains a makefile so you can run 'make' in the repo root.  

## Using the PDF
Find the thickest cardstock your printer can handle (I decided in 200g/m²; I do have to straighten it afterwards though) and print the PDF.  
I'm German, so all my tests were performed with DIN A4 stock!
Hopefully LaTeX handles other formats well, but if you encounter issues, I'm willing to look at Pull Requests, see the Contributions section.

## Contributing
I'll be honest, this is a pet project I do not intend to keep spending effort on for decades to come
and I can't know what my life looks like when issues start coming in.
So there's a good chance I won't reply to issues or PRs.
This repo is provided as is and if you need some tweak, feel free to fork this and work on it.  

That said, if you do feel like you've got a valuable, well-tested addition, you are welcome to create a PullRequest anyway.
Just don't expect it to get attention immediately, or ever.  

## Credits
- Information about the spells is imported from the [Spells DB](https://home.pathfindercommunity.net/home/databases/spells) ([alternate link](https://www.d20pfsrd.com/magic/tools/spells-db/), [GoogleDocs link](https://docs.google.com/spreadsheets/d/1cuwb3QSvWDD7GG5McdvyyRBpqycYuKMRsXgyrvxvLFI)) table, see above for guidance on updating the imported data when the Spell DB changes.  
- The basic project structure was forked from [tammon/akad-latex-vorlage](https://github.com/tammon/akad-latex-vorlage), but modified so heavily it should barely be recognizable... But here's a shoutout anyway 😊  

