# Media Library Tools CLI Argument Pattern Analysis

## Overview
This analysis examines CLI argument patterns across 9 scripts in the media library tools project to identify inconsistencies and standardization opportunities compared to the reference implementation (`plex_update_tv_years`).

**Analysis Date:** 2025-08-28  
**Sprint:** 10.0 CLI Standardization and Consistency  
**Phase:** 1.1 Detailed Script Analysis

---

## Scripts Analyzed

1. **plex_update_tv_years** (Reference Implementation) ✅
2. **sabnzbd_cleanup** 
3. **plex_correct_dirs**
4. **plex_make_dirs** 
5. **plex_make_seasons**
6. **plex_make_years**
7. **plex_move_movie_extras**
8. **plex_movie_subdir_renamer**
9. **plex_make_all_seasons**

---

## Reference Implementation Analysis: `plex_update_tv_years`

### Standard Arguments (Complete Implementation)
```python
parser.add_argument('path', nargs='?', default='.',
                    help='Directory to process (default: current directory)')
parser.add_argument('--dry-run', action='store_true', default=True,
                    help='Show what would be renamed without making changes (default: true)')
parser.add_argument('--execute', action='store_true',
                    help='Actually perform the renaming operations (overrides --dry-run)')
parser.add_argument('-y', '--yes', action='store_true',
                    help='Skip confirmation prompts (for non-interactive use)')
parser.add_argument('--force', action='store_true',
                    help='Force execution even if another instance is running')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Show verbose output')
parser.add_argument('--debug', action='store_true',
                    help='Show detailed debug output')
parser.add_argument('--version', action='version', version=f'%(prog)s v{VERSION}')
```

### Key Standardization Features
- ✅ Complete global configuration support (`AUTO_EXECUTE`, `AUTO_CONFIRM`)
- ✅ Full `is_non_interactive()` detection
- ✅ Proper `-y`/`--yes` flag validation
- ✅ Header with mode indicators
- ✅ Comprehensive help text with cron examples
- ✅ File locking mechanism
- ✅ Dry-run as default with explicit `--execute` override

---

## Detailed Script Analysis and Issues

### 1. `sabnzbd_cleanup` - ⚠️ MODERATE ISSUES

**File Location:** `SABnzbd/sabnzbd_cleanup`

**Missing Standard Arguments:**
```python
# Missing these standard arguments:
parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
parser.add_argument('--debug', action='store_true', help='Show detailed debug output')
```

**Current Pattern:**
- ✅ Uses `--delete` flag (equivalent to `--execute`)
- ✅ Has proper global configuration support
- ✅ Includes cron examples in help text
- ❌ Missing verbose/debug support

**Specific Code Changes Needed:**
- Line ~400: Add `--verbose` and `--debug` arguments to parser
- Line ~200-300: Add verbose logging to SABnzbdDetector class methods
- Line ~500: Integrate debug output in main execution flow

### 2. `plex_correct_dirs` - ⚠️ MODERATE ISSUES

**File Location:** `plex/plex_correct_dirs`

**Missing Standard Arguments:**
```python
# Missing these standard arguments:
parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
parser.add_argument('--debug', action='store_true', help='Show detailed debug output')
```

**Dry-Run Logic Inconsistency:**
```python
# Current (INCONSISTENT):
parser.add_argument('--dry-run', action='store_true',
                    help='Show what would be done without making changes (limited to 5 items)')

# Should be (STANDARDIZED):
parser.add_argument('--dry-run', action='store_true', default=True,
                    help='Show what would be done without making changes (default: true)')
parser.add_argument('--execute', action='store_true',
                    help='Actually perform operations (overrides --dry-run)')
```

**Specific Code Changes Needed:**
- Line ~500: Add missing `--verbose` and `--debug` arguments
- Line ~550: Update dry-run logic to match reference implementation
- Line ~600: Update global configuration handling for new execute flag

### 3. `plex_make_dirs` - ⚠️ MODERATE ISSUES

**File Location:** `plex/plex_make_dirs`

**Issues Identical to `plex_correct_dirs`:**
- Missing `--verbose` and `--debug` arguments
- Inconsistent dry-run logic (uses `--dry-run` flag instead of default)

**Unique Arguments (Keep These):**
```python
parser.add_argument('--types', nargs='+', metavar='EXT',
                    help='File extensions to process (e.g., mp4 mkv avi)')
parser.add_argument('--exclude', nargs='+', metavar='EXT',
                    help='File extensions to exclude from processing')
parser.add_argument('--list-types', action='store_true',
                    help='List all supported file types and exit')
```

### 4. `plex_make_seasons` - ⚠️ MODERATE ISSUES

**File Location:** `plex/plex_make_seasons`

**Issues Identical to Previous Scripts:**
- Missing `--verbose` and `--debug` arguments
- Inconsistent dry-run logic

**Unique Arguments (Keep These):**
```python
parser.add_argument('--target', metavar='DIR',
                    help='Target directory for organized files (default: same as source)')
parser.add_argument('--list-patterns', action='store_true',
                    help='List all supported season detection patterns and exit')
```

### 5. `plex_make_years` - ⚠️ MODERATE ISSUES

**File Location:** `plex/plex_make_years`

**Issues Identical to Previous Scripts:**
- Missing `--verbose` and `--debug` arguments
- Inconsistent dry-run logic

**Unique Arguments (Keep These):**
```python
parser.add_argument('--base', metavar='DIR',
                    help='Base directory for year organization (default: same as source)')
parser.add_argument('--year-range', nargs=2, type=int, metavar=('START', 'END'),
                    default=[1900, 2030], help='Valid year range (default: 1900-2030)')
parser.add_argument('--list-patterns', action='store_true',
                    help='List all supported year detection patterns and exit')
```

### 6. `plex_move_movie_extras` - 🚨 MAJOR ISSUES

**File Location:** `plex/plex_move_movie_extras`

**Critical Missing Features:**
- ❌ **NO global configuration support** - Missing `read_global_config_bool()` function entirely
- ❌ Missing complete integration of verbose/debug arguments
- ❌ Inconsistent confirmation logic pattern

**Specific Code Changes Needed:**
- Line ~32: Add `read_global_config_bool()` function after imports
- Line ~385: Add global configuration reading and application
- Line ~520: Standardize confirmation logic with `is_non_interactive()`
- Line ~400: Complete verbose/debug argument integration

**Code Pattern to Add:**
```python
# Read global configuration
auto_execute = read_global_config_bool('AUTO_EXECUTE', False)
auto_confirm = read_global_config_bool('AUTO_CONFIRM', False)

# Apply global configuration (CLI arguments take precedence)
if auto_execute and args.dry_run:
    args.dry_run = False  # Override dry_run if AUTO_EXECUTE is set
if auto_confirm and not args.yes:
    args.yes = True  # Set yes flag if AUTO_CONFIRM is set
```

### 7. `plex_movie_subdir_renamer` - 🚨 MAJOR ISSUES

**File Location:** `plex/plex_movie_subdir_renamer`

**Critical Missing Features:**
- ❌ Incomplete integration of existing `--verbose` and `--debug` arguments
- ❌ Different validation and confirmation patterns than reference
- ❌ Missing mode indicators in output

**Specific Code Changes Needed:**
- Line ~500: Complete verbose/debug integration throughout execution flow
- Line ~520: Standardize confirmation logic pattern
- Line ~310: Add mode indicator headers like reference implementation

### 8. `plex_make_all_seasons` - ⚠️ MODERATE ISSUES

**File Location:** `plex/plex_make_all_seasons`

**Issues Similar to Other Scripts:**
- Missing `--verbose` and `--debug` arguments
- Inconsistent dry-run logic

**Unique Arguments (Keep These):**
```python
parser.add_argument('--parallel', '--workers', type=int, default=4, metavar='N',
                    help='Number of worker threads for parallel processing (default: 4, use 1 for sequential)')
parser.add_argument('--recursive', action='store_true',
                    help='Recursively process all subdirectories (not just immediate children)')
```

---

## Standardization Comparison Matrix

| Script | Missing --verbose | Missing --debug | Wrong Dry-Run Logic | Missing Global Config | Missing Mode Headers | Help Text Issues |
|--------|-------------------|-----------------|---------------------|----------------------|---------------------|------------------|
| plex_update_tv_years | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| sabnzbd_cleanup | ❌ | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| plex_correct_dirs | ❌ | ❌ | ❌ | ✅ | ❌ | ⚠️ |
| plex_make_dirs | ❌ | ❌ | ❌ | ✅ | ❌ | ⚠️ |
| plex_make_seasons | ❌ | ❌ | ❌ | ✅ | ❌ | ⚠️ |
| plex_make_years | ❌ | ❌ | ❌ | ✅ | ❌ | ⚠️ |
| plex_move_movie_extras | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | ❌ |
| plex_movie_subdir_renamer | ⚠️ | ⚠️ | ❌ | ✅ | ❌ | ⚠️ |
| plex_make_all_seasons | ❌ | ❌ | ❌ | ✅ | ❌ | ⚠️ |

**Legend:**
- ✅ = Fully compliant
- ⚠️ = Partially compliant/needs minor fixes  
- ❌ = Missing/needs major fixes

---

## Summary of Required Changes

### Priority 1: Universal Standard Arguments (8 scripts)
Add missing `--verbose` and `--debug` arguments to:
- sabnzbd_cleanup
- plex_correct_dirs  
- plex_make_dirs
- plex_make_seasons
- plex_make_years
- plex_make_all_seasons
- Complete integration in plex_move_movie_extras
- Complete integration in plex_movie_subdir_renamer

### Priority 2: Dry-Run Logic Standardization (7 scripts)  
Convert from `--dry-run` flag to default dry-run with explicit `--execute`:
- plex_correct_dirs
- plex_make_dirs
- plex_make_seasons  
- plex_make_years
- plex_move_movie_extras
- plex_movie_subdir_renamer
- plex_make_all_seasons

### Priority 3: Complete Global Configuration (1 script)
Add full global configuration support to:
- plex_move_movie_extras (completely missing)

### Priority 4: Mode Indicators and Headers (8 scripts)
Add consistent mode indicator headers to all scripts except reference

### Priority 5: Help Text Standardization (8 scripts)  
Standardize help text formatting and add cron usage examples

---

## Code Pattern Templates

### Standard Arguments Template
```python
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Show verbose output')
parser.add_argument('--debug', action='store_true', 
                    help='Show detailed debug output')
```

### Dry-Run Logic Template
```python
parser.add_argument('--dry-run', action='store_true', default=True,
                    help='Show what would be done without making changes (default: true)')
parser.add_argument('--execute', action='store_true',
                    help='Actually perform operations (overrides --dry-run)')
```

### Mode Indicator Template
```python
print(f"Script Name v{VERSION}")
print("=" * 50)

if args.execute:
    dry_run_mode = False
else:
    dry_run_mode = args.dry_run  # This is True by default

if dry_run_mode:
    print("DRY-RUN MODE: No changes will be made")
else:
    print("EXECUTE MODE: Changes will be made")
```

This analysis provides the foundation for creating specific, actionable refactoring plans for each script to achieve complete CLI standardization.