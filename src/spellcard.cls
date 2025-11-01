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
\ProvidesClass{spellcard}[2025/11/01 v2.2.0 Spell Card Document Class]

%% ============================================================================
%% Required Packages (Early Load)
%% ============================================================================

\RequirePackage{kvoptions}  % For key-value class options

%% ============================================================================
%% Class Options
%% ============================================================================

\SetupKeyvalOptions{
  family=spellcard,
  prefix=spellcard@
}

% Draft/final mode
\DeclareBoolOption[false]{draft}
\DeclareComplementaryOption{final}{draft}

% Deck index cards (default: enabled)
\DeclareBoolOption[true]{deckindex}

% Printer margins
\DeclareStringOption{printer-margin-x}
\DeclareStringOption{printer-margin-y}
\DeclareStringOption{printer-margin}

%% Pass unknown options to scrartcl
\DeclareDefaultOption{\PassOptionsToClass{\CurrentOption}{scrartcl}}

\ProcessKeyvalOptions*

%% ============================================================================
%% Load Base Class
%% ============================================================================

% Build options list based on draft/final mode
\ifspellcard@draft
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

% Build printer margin options to pass to spellcards package
\def\@spellcard@package@options{}

% Check each printer margin option and add if non-empty
% kvoptions defines macros as empty strings by default, so we need to check:
% 1. If the macro is defined (set by user)
% 2. If it's not empty
\RequirePackage{etoolbox}

% Note: kvoptions creates macros even when not set, but they expand to empty
% So we just need to check if the expansion is non-empty
\ifdefvoid{\spellcard@printer@margin}{}{%
  \edef\@spellcard@package@options{\@spellcard@package@options,printer-margin=\spellcard@printer@margin}%
}

\ifdefvoid{\spellcard@printer@margin@x}{}{%
  \edef\@spellcard@package@options{\@spellcard@package@options,printer-margin-x=\spellcard@printer@margin@x}%
}

\ifdefvoid{\spellcard@printer@margin@y}{}{%
  \edef\@spellcard@package@options{\@spellcard@package@options,printer-margin-y=\spellcard@printer@margin@y}%
}

% Load spellcards package with options (if any)
\ifx\@spellcard@package@options\@empty
  \RequirePackage{spellcards}
\else
  % Remove leading comma
  \edef\@spellcard@package@options{\expandafter\@gobble\@spellcard@package@options}
  \expandafter\RequirePackage\expandafter[\@spellcard@package@options]{spellcards}
\fi

%% ============================================================================
%% Draft vs Final Mode Setup
%% ============================================================================

\ifspellcard@draft
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
