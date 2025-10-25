# Phase 5.1 Integration Test Results

**Date**: October 25, 2025  
**Test**: Compilation of 3 real spell cards (Magic Missile, Fireball, Grease) in 2 decks

## Test Files

- **expl3 version**: `test-integration.tex` → `test-integration.pdf`
- **Legacy version**: `test-legacy.tex` → `test-legacy.pdf`

Both use identical spell files and deck structure:
- Deck 0 (unnamed): Magic Missile, Fireball, Grease
- Deck 1 (damage-dealing): Magic Missile, Fireball

## Compilation Results

| Metric | expl3 | Legacy | Notes |
|--------|-------|--------|-------|
| **Compiled** | ✅ Yes | ✅ Yes | Both successful |
| **Pages** | 4 | 4 | Same page count |
| **File Size** | 87 KB | 97 KB | expl3 10KB smaller |
| **Errors** | 0 fatal | 0 fatal | Clean compilation |
| **Warnings** | Label changes | Label changes | Both have rerun warnings |

## Visual/Content Observations

### Issues Detected in expl3 Version

From text extraction, the expl3 version shows:

1. **Strange text artifacts**:
   ```
   damage-dealing
   
   e
   
   setq rcounter :
   ```
   The legacy version doesn't have these artifacts.

2. **Table layout differences**:
   - expl3 version appears to have some layout issues with the spell attribute tables
   - Text extraction shows "Area: NULL" and "Effect: NULL" being printed (should be hidden)

3. **Deck label positioning**:
   - "damage-dealing" appears in both, but with different surrounding text

### What Works in expl3 Version

1. ✅ **QR codes**: Generated successfully (2 per spell)
2. ✅ **Deck tracking**: Both decks recognized
3. ✅ **Spell markers**: Present (based on compilation success)
4. ✅ **Basic layout**: 4 pages generated as expected
5. ✅ **File size**: Slightly smaller than legacy (possibly more efficient)

## Root Causes to Investigate

### 1. "NULL" Values Being Printed
**Problem**: expl3 version shows "Area: NULL" in extracted text  
**Expected**: NULL values should be hidden (not printed)  
**Cause**: The compatibility layer's `\spellcardinfo` uses `\spellattribute` which should call expl3's NULL-checking logic, but something isn't working correctly.

**Code Location**: `spellcard-templates-compat.tex` line ~95-115

### 2. Strange Text Artifacts ("e", "setq rcounter :")
**Problem**: Text extraction shows garbage text  
**Cause**: Unclear - possibly TikZ overlay issues, font encoding, or positioning problems

### 3. Table Layout Issues
**Problem**: Text extraction shows jumbled attribute order  
**Cause**: Possibly related to how tables are rendered or extracted from PDF

## Required Fixes

### Priority 1: NULL Value Handling
The `\spellattribute` command in the compatibility layer needs to properly invoke expl3's NULL checking:

```latex
% Current (in spellcard-templates-compat.tex):
\spellattribute{Area}{\area}

% This should call: \spellcard_attribute:nn from expl3
% which has: \spellcard_if_not_null:nT { #2 } { ... }
```

**Action**: Verify that `\spellattribute` properly connects to expl3's implementation.

### Priority 2: Verify Visual Output
**Action**: Open both PDFs side-by-side to visually confirm:
- Spell marker positions
- Deck label positions
- QR code placements
- Table layouts
- Font rendering

### Priority 3: Investigate Text Artifacts
**Action**: Check if artifacts are:
- Real content in PDF (bad)
- PDF extraction artifacts (less concerning)
- TikZ overlay issues (fixable)

## Next Steps

1. **Visual inspection**: User has opened test-integration.pdf and is withholding judgment - awaiting their observations
2. **Fix NULL handling**: Update compatibility layer if needed
3. **Compare with legacy PDF**: Side-by-side visual review
4. **Document all differences**: Create comprehensive comparison
5. **Prioritize fixes**: Focus on functional issues over cosmetic ones

## Success Criteria for Phase 5.1

- [x] Compilation successful
- [x] No fatal errors
- [x] QR codes generated
- [x] Deck tracking functional
- [ ] Visual output matches legacy (pending user review)
- [ ] NULL values properly hidden
- [ ] No text artifacts in PDF
- [ ] Performance acceptable

## Conclusion

**Status**: ⚠️ PARTIALLY SUCCESSFUL

The expl3 integration compiles and produces output, but there are formatting/rendering issues that need investigation and fixes before declaring Phase 5 complete. The core functionality (deck tracking, QR codes, compilation) works, but the output quality needs improvement to match legacy behavior.

**Awaiting**: User's visual inspection feedback to prioritize fixes.
