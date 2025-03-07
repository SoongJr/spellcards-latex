#!/usr/bin/env bash

set -euo pipefail

# Function to display usage information
usage() {
  echo "Usage: $0 --class <characterClass> [--name <spellName> | --level <spellLevel>] [--source <sourceBook>] [--overwrite]"
  echo "    -c|--class=<characterClass>  The character class to convert spells for"
  echo "    -n|--name=<spellName>        The exact name of the spell to extract from spell_full.tsv"
  echo "    -l|--level=<spellLevel>      The spell level to filter by (NOT the character level!)"
  echo "    -s|--source=<sourceBook>     The source book to filter by"
  echo "    --overwrite                  Overwrite existing files"
  exit 1
}

die() {
  echo "$1" >&2
  return 1
}

# Parse command line arguments using getopt
options=$(getopt -o c:n:l:s: --long class:,name:,level:,source:,overwrite -- "$@") || usage

eval set -- "$options"

# Initialize variables
characterClass=""
spellName=""
spellLevel=""
sourceBook=""
unset overwrite

# Extract options and their arguments into variables
while true; do
  case "$1" in
  -c | --class)
    characterClass="$2"
    shift 2
    ;;
  -n | --name) # must match a spell name in column "name" exactly.
    spellName="$2"
    shift 2
    ;;
  -l | --level)
    spellLevel="$2"
    shift 2
    ;;
  -s | --source)
    sourceBook="$2"
    shift 2
    ;;
  --overwrite)
    overwrite=true
    shift
    ;;
  --)
    shift
    break
    ;;
  *)
    usage
    ;;
  esac
done

# Parameter validation:
if [[ -z "$characterClass" ]]; then
  echo "Error: --class is a mandatory parameter" >&2
  usage
fi
if [[ -n "$spellLevel" && -n "$spellName" ]]; then
  echo "Error: --name is mutually exclusive with --level" >&2
  usage
fi
if [[ -z "$spellLevel" && -z "$spellName" && -z "$sourceBook" ]]; then
  echo "Warning: Without either --name, --level, or --source provided, there may be literally thousands of spells to convert." >&2
  echo "         Working on it now, but don't expect results any time soon..." >&2
fi

# Function trying to automatically apply some best practices that chktex will complain about to a given LaTeX-formatted text.
# These actions may not be perfect, but should make them much easier to review and adjust manually.
apply_latex_fixes() {
  local latexText="$1"
  # replacing double quotes with `` and '' (nested quotes get replaced incorrectly, but aren't expected. Unmatched quotes are left unchanged.):
  latexText=$(echo "$latexText" | sed -E "s/\"([^\"]+)\"/\`\`\1''/g")
  # text fragments like "10-ft. radius" or "within 30 ft. of the target" require explicitly marking the space as inter-word spacing
  latexText=$(echo "$latexText" | sed -E "s/([0-9]+[ -]?ft\.) ([a-z])/\1\\\ \2/g")
  # text fragments like "sq. ft." on the other hand demand a non-breaking space
  latexText=$(echo "$latexText" | sed -E "s/sq\. ft\./sq.~ft./g")
  # When a new sentence starts with an emphasized word, LaTeX wants us to explicitly mark the space as inter-sentence spacing
  latexText=$(echo "$latexText" | sed -E "s/\. \\\emph\{/.\\\@ \\\emph{/g")
  # also use superscripting for "1st", "2nd", etc.:
  latexText=$(echo "$latexText" | sed -E "s/(\b[0-9]+)(st|nd|rd|th)\b/\1\\\textsuperscript{\2}/g")
  echo "$latexText"
}

inputFile="$(dirname "$0")/spell_full.tsv"
# all spells are grouped by the class using it, as the information displayed on the spell cards can vary:
outputDirBase="$(dirname "$0")/$characterClass"

# TSV has headers, extract their names so we can use them to read the file (replacing spaces with underscores, just in case)
# Prefix each header name with "tsv_" to avoid conflicts with existing variables:
mapfile -t headers < <(head -n 1 "$inputFile" | tr ' ' '_' | sed -E 's/(^|\t)/ tsv_/g')

# Read the headers as an array
declare -a headers
read -r -a headers < <(head -n 1 "$inputFile" | tr ' ' '_' | sed -E 's/(^|\t)/ tsv_/g')

# Read the TSV file and process each line
declare -a generatedFiles=() # store the generated files in an array to print them afterwards
# Explicitly assign NULL values to empty cells so `read` will work correctly, and skip the first line (the header):
inputData="$(awk 'BEGIN {FS=OFS="\t"} NR>1 {for (i=1; i<=NF; i++) if ($i == "") $i="NULL"; print}' "$inputFile")"
while IFS=$'\t' read -r "${headers[@]}"; do
  # Fail if any of the expected columns is missing (this also satisfies the shellcheck SC2154 warning)
  characterClassSpellLevelColumn=tsv_$characterClass
  [[ -z "${tsv_name:-}" ]] && die "Error: Missing 'name' column in TSV file '$inputFile'"
  [[ -z "${tsv_saving_throw:-}" ]] && die "Error: Missing 'saving_throw' column in TSV file '$inputFile'"
  [[ -z "${tsv_spell_resistance:-}" ]] && die "Error: Missing 'spell_resistance' column in TSV file '$inputFile'"
  [[ -z "${tsv_source:-}" ]] && die "Error: Missing 'source' column in TSV file '$inputFile'"
  [[ -z "${!characterClassSpellLevelColumn:-}" ]] && die "Error: Missing '${characterClass}' column in TSV file '$inputFile'"
  # double-checking the columns we know is last in the file to ensure all data is assigned correctly:
  [[ -z "${tsv_summoner_unchained:-}" ]] && die "Error: Missing column in TSV file '$inputFile', not all columns for spell ${tsv_name} have a value"

  # the spell_level values from the input are no use to us, calculate the one for the desired class instead:
  tsv_spell_level="${!characterClassSpellLevelColumn}"

  # if tsv_spell_level has the value "NULL", the class does not have access to this spell from the database
  [[ "$tsv_spell_level" != "NULL" ]] || continue

  # Skip spells that do not match the filter requirements specified by the user (either name, level, or source book)
  if [[ 
    (-n "${spellName:-}" && "$spellName" != "$tsv_name") ||
    (-n "${spellLevel:-}" && "$spellLevel" != "$tsv_spell_level") ||
    (-n "${sourceBook:-}" && "$sourceBook" != "$tsv_source") ]]; then
    continue
  fi

  # Create a file path from the spell's level and name. The only problematic character is the slash, so replace it with a dash:
  outputFile="$outputDirBase/${tsv_spell_level}/$(echo "$tsv_name" | tr '/' '-')".tex
  mkdir -p "$(dirname "$outputFile")"

  # Only overwrite existing file if the --overwrite flag is set
  if [[ -z "${overwrite:-}" && -e "$outputFile" ]]; then
    echo "File '$outputFile' already exists, skipping spell '${tsv_name}' (use --overwrite to replace existing files)"
    continue
  fi

  # Modify some of the columns' content:

  # in saving_throw and spell_resistance, highlight the words "none" and "no" respectively with LaTeX commands
  tsv_saving_throw=$(echo "$tsv_saving_throw" | sed -E 's/\bnone\b/\\textbf{none}/g')
  tsv_spell_resistance=$(echo "$tsv_spell_resistance" | sed -E 's/\bno\b/\\textbf{no}/g')

  # a missing value ("NULL") in saving_throw or spell_resistance means it is not applicable
  [[ "$tsv_saving_throw" != "NULL" ]] || tsv_saving_throw="\\emph{N/A}"
  [[ "$tsv_spell_resistance" != "NULL" ]] || tsv_spell_resistance="\\emph{N/A}"

  # Convert HTML to LaTeX using pandoc and replace the content of tsv_description_formatted
  if ! tsv_description_formatted=$(echo "$tsv_description_formatted" | pandoc -f html -t latex); then
    die "Error: Failed to convert HTML to LaTeX for spell '${tsv_name}'" || continue
  fi

  # Apply LaTeX formatting to some specific fields we know to contain common issues:
  tsv_effect=$(apply_latex_fixes "$tsv_effect")
  tsv_range=$(apply_latex_fixes "$tsv_range")
  tsv_area=$(apply_latex_fixes "$tsv_area")
  tsv_targets=$(apply_latex_fixes "$tsv_targets")
  tsv_mythic_text=$(apply_latex_fixes "$tsv_mythic_text")
  tsv_description_formatted=$(apply_latex_fixes "$tsv_description_formatted")

  # Create additional "columns" with generated content:

  # Create a guess at a URL to the English online rules for this spell from the name. The user will have to check whether it's correct:
  # base URL is `https://www.d20pfsrd.com/magic/all-spells/`, followed by the first character of the spell's name,
  # then the entire name with lower-cased and non-alphebethical charatcers replaced with dashes.
  englishBaseUrl="https://www.d20pfsrd.com/magic/all-spells"
  # shellcheck disable=SC2034 # variable used by dynamically constructing variable name, so spellcheck can't know
  tsv_url_english="${englishBaseUrl}/$(
    printf "%s" "${tsv_name:0:1}" | tr '[:upper:]' '[:lower:]'
  )/$(
    # The "Greater" variants of spells do not have their own pages and are instead included in the base spell's page, so we remove that and hope for the best.
    # The same goes for "levels" of spells, like "Summon Monster III", which needs to direct to the base page.
    printf "%s" "${tsv_name}" | sed -E 's/(, Greater| [IVX]+)$//' | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9' '-'
  )/"
  # We cannot determine the same for other languages, but we can at least provide the user with a template:
  germanBaseUrl="http://prd.5footstep.de/Grundregelwerk/Zauber"
  # shellcheck disable=SC2034 # variable used by dynamically constructing variable name, so spellcheck can't know
  tsv_url_german="${germanBaseUrl}/<german-spell-name>"

  # Write the LaTeX content to the output file
  (
    printf '%% file content generated by %s, meant to be fine-tuned manually (especially the description).\n' "$(basename "$0")"
    printf '\n'
    printf '%% open a new spellcards environment\n'
    printf '\\begin{spellcard}{%s}{%s}{%s}\n' "${characterClass}" "${tsv_name}" "${tsv_spell_level}"
    printf '  %% make the data from TSV accessible for to the LaTeX part:\n'
    for headerVar in "${headers[@]}" "tsv_url_english" "tsv_url_german"; do
      headerName="${headerVar#tsv_}"
      # black-list some columns from being included as they contain LaTeX commands that would be difficult to use in \newcommand
      # or are just plain too long to be usefully included
      blacklisted=(
        description description_formatted full_text short_description
        # also ignoring the data for class-specific spell-levels as only the current class is of interest, and that data is now in tsv_spell_level:
        sor wiz cleric druid ranger bard paladin alchemist summoner witch inquisitor oracle antipaladin magus adept mythic bloodrager shaman psychic medium mesmerist occultist spiritualist skald investigator hunter summoner_unchained
      )
      if [[ ! " ${blacklisted[*]} " =~ [[:space:]]${headerName}[[:space:]] ]]; then
        # Note: LaTeX macro names may only be a-zA-Z, no numbers or special characters so remove them
        printf '  \\newcommand{\\%s}{%s}\n' "$(echo "$headerName" | tr -cd 'a-zA-Z')" "${!headerVar}"
      fi
    done
    printf '  %% print the tabular information at the top of the card:\n'
    printf '  \\spellcardinfo{}\n'
    printf '  %% draw a QR Code pointing at online resources for this spell on the front face:\n'
    printf '  \\spellcardqr{\\urlenglish}\n'
    printf '  %% ATTENTION: URLs for foreign languages cannot be generated and must be provided by you!\n'
    printf '  %%            Set \\urlgerman above and activate this line if you want to have it: \\spellcardqr{\\urlgerman}\n'
    printf '  %% LaTeX-formatted description of the spell, generated from the HTML-formatted description_formatted column:\n'
    printf '%s\n\n' "${tsv_description_formatted}" # will be indented/formatted properly later
    printf '\\end{spellcard}\n'
  ) >"$outputFile"

  # Now auto-format the resulting file (warn about failures but continue; stderr gets discarded because of excessive warnings)
  if ! latexindent --cruft="$(dirname "$0")/out/" --local="$(dirname "$0")/../.latexindent.yaml" \
    --overwrite "$outputFile" --silent 2>/dev/null; then
    echo "Warning: Failed to auto-format LaTeX file '$outputFile'" >&2
  fi

  # Now that this file has been created, add it to the list of generated files
  generatedFiles+=("$outputFile")
done < <(printf "%s" "${inputData}")
# (explicitly unset variables defined in the loop to prevent accidentally using them outside)
unset "${!tsv_@}" characterClassSpellLevelColumn outputFile

# Warn if there were no files generated for the parameters provided
if [[ "${#generatedFiles[@]}" -eq 0 ]]; then
  echo "Warning: No spells found to convert that did not already exist as files. Please review the parameters given." >&2
  if [[ -n "$spellName" ]]; then
    echo "Note: Spell names must match exactly, including case and special characters." >&2
  fi
  exit 1
fi

printf "\nPlease review the generated files, delete the ones you don't want, and fine-tune the rest manually:\n"
for file in "${generatedFiles[@]}"; do
  printf '  - "%s"\n' "$file"
  # some new spells might already have been converted for one or more other classes, and probably already optimized for displaying on a spellcard.
  # notify the user that they should consider using one of those
  # Determine whether there already exist files for this spell for other classes and remember their paths to print later
  while IFS= read -r existingFile; do
    if [[ "$existingFile" != "$file" ]]; then
      printf '    (see also previously-converted file "%s")\n' "${existingFile}"
    fi
  done < <(find "$(dirname "${outputDirBase}")" -type f -name "$(basename "${file}")")
done
printf "Once they look good, add an \input{} statement to src/spells/%s.tex to actually include them in the document.\n" "${characterClass}"
# It is rare that the user wants to print all cards at once, usually they print a couple spells for their level-up.
# So automatically adding these to the tex file seems like a good idea at first, but will mostly be a pain to deal with.
printf "If you wish to include all currently available spells for this class, you can use the following command:\n"
printf "( cd src && find spells/%s -name '*.tex' | sed 's/\.tex$//' | xargs -I{} --delimiter='\\\n' printf '\input{%%s}\\\n' {} ) > src/spells/%s.tex\n" "${characterClass}" "${characterClass}"
