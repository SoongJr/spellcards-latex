@echo off
setlocal EnableDelayedExpansion

REM set some variables
set "filename=spellcards"
set "pdflatex=pdflatex"
REM add MikTeX path to PATH in case it's not in there yet:
set "PATH=C:\Program Files (x86)\MiKTeX 2.9\miktex\bin;!PATH!"
where "!pdflatex!"
if errorlevel 1 exit /B !errorlevel!
REM prevent pdflatex from wrapping output lines as per https://tex.stackexchange.com/a/52994 (unless the user specified some values explicitly themselves)
if not defined max_print_line set "max_print_line=100000"
if not defined error_line set "error_line=254"
if not defined half_error_line set "half_error_line=238"

REM run LaTeX commands
"!pdflatex!" -halt-on-error -interaction=nonstopmode -shell-escape -synctex=1 -output-directory="%~dp0\..\output" "%~dp0\..\!filename!"
if errorlevel 1 echo Error: pdflatex step failed. >&2 & exit /B %errorlevel%
REM Note: usually you would run this three times to ensure page references are up to date,
REM but spellcards have no references, so running once is fine.
exit /B 0
