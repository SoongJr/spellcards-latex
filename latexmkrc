# Set the default PDF viewer to VS Code
$pdf_previewer = 'code';

# Set the default DVI viewer
$dvi_previewer = 'xdvi';

# Open the PDF in default viewer without waiting for further changes in source files
# Instead using LaTeX Workshop to keep the preview up to date with changes in source
$preview_mode = 1;

# Change to the directory containing the main source file before processing it
$do_cd = 1;

# Set the number of times to run pdflatex
$pdflatex = 'pdflatex -interaction=nonstopmode -synctex=1 %O %S';

# Set output directory
$out_dir = 'out';
