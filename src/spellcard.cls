%%
%% This is file `spellcard.cls'
%%
%% Document class for spell card generation
%% Supports draft mode (fast, single-sided) and final mode (cardified, print-ready)
%%
%% Copyright (C) 2025 SoongJr
%% License: Open Source (see LICENSE file)
%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{spellcard}[2025/10/30 v1.0.0 Spell Card Document Class]

%% ============================================================================
%% Class Options
%% ============================================================================

\newif\if@spellcard@draft
\@spellcard@draftfalse  % Default to final mode (production-ready)

\DeclareOption{draft}{\@spellcard@drafttrue}
\DeclareOption{final}{\@spellcard@draftfalse}

%% Pass unknown options to scrartcl
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{scrartcl}}

\ProcessOptions\relax

%% ============================================================================
%% Load Base Class
%% ============================================================================

% Build options list based on draft/final mode
\if@spellcard@draft
  \PassOptionsToClass{oneside,draft}{scrartcl}
\else
  \PassOptionsToClass{twoside}{scrartcl}
\fi

\LoadClass[
  a4paper,
  DIV=14,
  fontsize=12pt,
  BCOR=0mm
]{scrartcl}

%% ============================================================================
%% Required Packages
%% ============================================================================

\RequirePackage[utf8]{inputenc}  % UTF-8 support
\RequirePackage{amsmath}         % Mathematical symbols in spell descriptions (\geq, \leq)

%% ============================================================================
%% Load Spellcards Package
%% ============================================================================

\RequirePackage{spellcards}

%% ============================================================================
%% Draft vs Final Mode Setup
%% ============================================================================

\if@spellcard@draft
  % Draft mode: No special layout changes needed
\else
  % Final mode: Load cardify for A6-on-A4 layout
  % cardify redefines page layout but does NOT touch \cleardoublepage
  % scrartcl in twoside mode already makes \cleardoublepage work correctly
  \input{cardify}
\fi

\endinput
%%
%% End of file `spellcard.cls'.
%%
