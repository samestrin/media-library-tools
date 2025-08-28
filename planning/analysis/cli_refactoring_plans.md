# Media Library Tools CLI Refactoring Plans

## Overview
This document provides detailed, step-by-step refactoring plans for each script to achieve CLI standardization and consistency across the media library tools project.

**Analysis Date:** 2025-08-28  
**Sprint:** 10.0 CLI Standardization and Consistency  
**Phase:** 1.2 Create Refactoring Plans

---

## Refactoring Strategy

### Script Categorization by Complexity

**Complex Scripts (Phase 2.1):**
- `plex_update_tv_years` - Reference implementation (verify compliance only)
- `sabnzbd_cleanup` - Complete structure but missing verbose/debug

**Medium Complexity Scripts (Phase 2.2):**
- `plex_correct_dirs` - Missing args + dry-run logic
- `plex_make_dirs` - Missing args + dry-run logic
- `plex_make_seasons` - Missing args + dry-run logic  
- `plex_make_years` - Missing args + dry-run logic

**Remaining Scripts (Phase 3.1):**
- `plex_move_movie_extras` - Major issues: missing global config
- `plex_movie_subdir_renamer` - Partial integration needed
- `plex_make_all_seasons` - Missing args + dry-run logic

---

## Individual Script Refactoring Plans

### 1. `plex_update_tv_years` - Reference Implementation ✅

**Status:** Complete - Verify only
**Files to Modify:** `plex/plex_update_tv_years`

**Verification Steps:**
1. Confirm all standard arguments present
2. Verify global configuration integration
3. Check mode indicator headers
4. Validate help text includes cron examples

**Expected Outcome:** No changes needed - this is the reference standard

---

### 2. `sabnzbd_cleanup` - Add Missing Arguments

**Status:** Moderate complexity
**Files to Modify:** `SABnzbd/sabnzbd_cleanup`

**Step-by-Step Refactoring:**

#### Step 1: Add Missing Standard Arguments
**Location:** Around line 400 (argument parser section)
**Before:**
```python
parser.add_argument('--version', action='version', version=f'%(prog)s v{VERSION}')
```
**After:**
```python
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Show verbose output')
parser.add_argument('--debug', action='store_true',
                    help='Show detailed debug output')
parser.add_argument('--version', action='version', version=f'%(prog)s v{VERSION}')
```

#### Step 2: Handle Debug Mode
**Location:** Around line 450 (argument validation section)
**Add:**
```python
# Handle debug mode
if args.debug:
    args.verbose = True
```

#### Step 3: Add Verbose Support to SABnzbdDetector Class
**Location:** Around line 200 (SABnzbdDetector class)
**Modify Constructor:**
```python
def __init__(self, verbose: bool = False, debug: bool = False):
    self.verbose = verbose
    self.debug = debug
```

**Add Logging Methods:**
```python
def log_verbose(self, message: str) -> None:
    """Log verbose message if verbose mode is enabled."""
    if self.verbose:
        print(f"[VERBOSE] {message}")

def log_debug(self, message: str) -> None:
    """Log debug message if debug mode is enabled."""
    if self.debug:
        print(f"[DEBUG] {message}")
```

#### Step 4: Integrate Logging in Detection Methods
**Location:** Throughout SABnzbdDetector methods
**Add logging calls:**
```python
# In analyze_directory method
self.log_debug(f"Analyzing directory: {directory}")

# In detect_sabnzbd_dir method  
self.log_verbose(f"Checking directory: {dir_path}")
```

#### Step 5: Update Main Function Call
**Location:** Around line 500 (main function)
**Before:**
```python
detector = SABnzbdDetector()
```
**After:**
```python
detector = SABnzbdDetector(verbose=args.verbose, debug=args.debug)
```

**Testing Required:** Unit tests for verbose/debug functionality

---

### 3. `plex_correct_dirs` - Standard Refactoring

**Status:** Medium complexity
**Files to Modify:** `plex/plex_correct_dirs`

**Step-by-Step Refactoring:**

#### Step 1: Add Missing Standard Arguments
**Location:** Around line 500 (argument parser section)
**Add before `--version`:**
```python
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Show verbose output')
parser.add_argument('--debug', action='store_true',
                    help='Show detailed debug output')
```

#### Step 2: Modify Dry-Run Logic
**Location:** Around line 480 (current dry-run argument)
**Before:**
```python
parser.add_argument('--dry-run', action='store_true',
                    help='Show what would be done without making changes (limited to 5 items)')
```
**After:**
```python
parser.add_argument('--dry-run', action='store_true', default=True,
                    help='Show what would be done without making changes (default: true)')
parser.add_argument('--execute', action='store_true',
                    help='Actually perform operations (overrides --dry-run)')
```

#### Step 3: Update Global Configuration Handling
**Location:** Around line 600 (global configuration section)
**Before:**
```python
# Apply global configuration (CLI arguments take precedence)
if auto_execute and args.dry_run:
    args.dry_run = False  # Override dry_run if AUTO_EXECUTE is set
```
**After:**
```python
# Apply global configuration (CLI arguments take precedence)
if auto_execute and not args.execute:
    args.execute = True  # Set execute flag if AUTO_EXECUTE is set
```

#### Step 4: Update Execution Logic
**Location:** Throughout main execution flow
**Update dry-run determination:**
```python
# Handle dry-run/execute logic
if args.execute:
    dry_run_mode = False
else:
    dry_run_mode = args.dry_run  # This is True by default
```

#### Step 5: Add Mode Headers
**Location:** Early in main execution (around line 650)
**Add:**
```python
print(f"Plex Directory Corrector v{VERSION}")
print("=" * 50)

if dry_run_mode:
    print("DRY-RUN MODE: No changes will be made")
else:
    print("EXECUTE MODE: Changes will be made to directories")
```

#### Step 6: Handle Debug Mode
**Add after argument parsing:**
```python
# Handle debug mode
if args.debug:
    args.verbose = True
```

**Testing Required:** Unit tests for new execute flag behavior

---

### 4. `plex_make_dirs` - Identical Pattern to plex_correct_dirs

**Status:** Medium complexity  
**Files to Modify:** `plex/plex_make_dirs`

**Refactoring Steps:** Identical to `plex_correct_dirs` plan above

**Unique Considerations:**
- Preserve existing `--types`, `--exclude`, and `--list-types` arguments
- Ensure unique arguments work with new standardized patterns

---

### 5. `plex_make_seasons` - Identical Pattern with Unique Args

**Status:** Medium complexity
**Files to Modify:** `plex/plex_make_seasons`

**Refactoring Steps:** Follow `plex_correct_dirs` pattern with these considerations:

**Unique Arguments to Preserve:**
```python
parser.add_argument('--target', metavar='DIR',
                    help='Target directory for organized files (default: same as source)')
parser.add_argument('--list-patterns', action='store_true',
                    help='List all supported season detection patterns and exit')
```

**Special Handling:** Global configuration application should happen **after** `--list-patterns` check to avoid interference.

---

### 6. `plex_make_years` - Identical Pattern with Unique Args

**Status:** Medium complexity
**Files to Modify:** `plex/plex_make_years`

**Refactoring Steps:** Follow `plex_correct_dirs` pattern

**Unique Arguments to Preserve:**
```python
parser.add_argument('--base', metavar='DIR',
                    help='Base directory for year organization (default: same as source)')
parser.add_argument('--year-range', nargs=2, type=int, metavar=('START', 'END'),
                    default=[1900, 2030], help='Valid year range (default: 1900-2030)')
parser.add_argument('--list-patterns', action='store_true',
                    help='List all supported year detection patterns and exit')
```

---

### 7. `plex_move_movie_extras` - Major Refactoring Required

**Status:** High complexity - Missing global configuration
**Files to Modify:** `plex/plex_move_movie_extras`

**Step-by-Step Refactoring:**

#### Step 1: Add Missing Global Configuration Function
**Location:** After imports (around line 32)
**Add complete `read_global_config_bool()` function:**
```python
def read_global_config_bool(var_name: str, default: bool = False) -> bool:
    """Read a boolean environment variable with support for .env files.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if not found
        
    Returns:
        Boolean value of the environment variable
    """
    # Check environment variable directly
    value = os.environ.get(var_name)
    if value is not None:
        return value.lower() in ('true', '1', 'yes', 'on')
    
    # Check local .env file
    env_file = '.env'
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f'{var_name}='):
                        value = line.split('=', 1)[1].strip()
                        return value.lower() in ('true', '1', 'yes', 'on')
        except (IOError, OSError):
            pass
    
    # Check global .env file
    global_env_path = Path.home() / '.media-library-tools' / '.env'
    if global_env_path.exists():
        try:
            with open(global_env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f'{var_name}='):
                        value = line.split('=', 1)[1].strip()
                        return value.lower() in ('true', '1', 'yes', 'on')
        except (IOError, OSError):
            pass
    
    return default
```

#### Step 2: Standardize Dry-Run Arguments
**Location:** Argument parser section (around line 450)
**Replace existing dry-run argument with standard pattern:**
```python
parser.add_argument('--dry-run', action='store_true', default=True,
                    help='Show what would be done without making changes (default: true)')
parser.add_argument('--execute', action='store_true',
                    help='Actually perform operations (overrides --dry-run)')
```

#### Step 3: Add Global Configuration Integration
**Location:** After argument parsing (around line 385)
**Add:**
```python
# Read global configuration
auto_execute = read_global_config_bool('AUTO_EXECUTE', False)
auto_confirm = read_global_config_bool('AUTO_CONFIRM', False)

# Apply global configuration (CLI arguments take precedence)
if auto_execute and not args.execute:
    args.execute = True  # Set execute flag if AUTO_EXECUTE is set
if auto_confirm and not args.yes:
    args.yes = True  # Set yes flag if AUTO_CONFIRM is set
```

#### Step 4: Update Confirmation Logic
**Location:** Around line 520 (confirmation section)
**Standardize to use `is_non_interactive()` pattern:**
```python
# Confirmation logic for non-interactive environments
if not args.execute:
    dry_run_mode = args.dry_run  # True by default
else:
    dry_run_mode = False

if not dry_run_mode:
    if not args.yes and not is_non_interactive():
        response = input(f"\nMove extras from '{args.sub_dir}' for '{args.main_file}'? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    elif args.yes or is_non_interactive():
        print("Proceeding with move operation...")
```

#### Step 5: Add Mode Indicators
**Location:** Early in execution flow
**Add:**
```python
print(f"Plex Movie Extras Mover v{VERSION}")
print("=" * 50)

if dry_run_mode:
    print("DRY-RUN MODE: No changes will be made")
else:
    print("EXECUTE MODE: Files will be moved")
```

#### Step 6: Complete Verbose/Debug Integration
**Location:** Throughout execution flow
**Add verbose/debug output where appropriate:**
```python
if args.verbose:
    print(f"[VERBOSE] Processing main file: {args.main_file}")
if args.debug:
    print(f"[DEBUG] Sub directory: {args.sub_dir}")
```

**Testing Required:** Complete unit tests for global configuration integration

---

### 8. `plex_movie_subdir_renamer` - Complete Integration

**Status:** Medium-High complexity
**Files to Modify:** `plex/plex_movie_subdir_renamer`

**Step-by-Step Refactoring:**

#### Step 1: Standardize Dry-Run Arguments  
**Location:** Argument parser section
**Replace existing pattern with standardized approach:**
```python
parser.add_argument('--dry-run', action='store_true', default=True,
                    help='Show what would be done without making changes (default: true)')
parser.add_argument('--execute', action='store_true',
                    help='Actually perform operations (overrides --dry-run)')
```

#### Step 2: Complete Verbose/Debug Integration
**Location:** Throughout PlexMovieSubdirRenamer class
**Ensure all methods use verbose/debug properly:**
```python
def rename_featurettes(self, directory_path: str, movie_name: Optional[str] = None) -> bool:
    if self.verbose:
        print(f"[VERBOSE] Starting rename process for: {directory_path}")
    if self.debug:
        print(f"[DEBUG] Movie name parameter: {movie_name}")
    # ... rest of method
```

#### Step 3: Update Global Configuration Handling
**Location:** In `validate_args` function
**Update to handle new execute flag:**
```python
if auto_execute and not args.execute:
    args.execute = True  # Set execute flag if AUTO_EXECUTE is set
```

#### Step 4: Fix Execution Logic
**Location:** In main() function
**Update dry-run determination:**
```python
# Handle dry-run/execute logic
if args.execute:
    dry_run_mode = False
else:
    dry_run_mode = args.dry_run  # This is True by default

renamer = PlexMovieSubdirRenamer(
    dry_run=dry_run_mode,
    force=args.force,
    verbose=args.verbose
)
```

#### Step 5: Add Mode Indicators
**Location:** Early in main execution
**Add standardized headers:**
```python
print(f"Plex Movie Subdirectory Renamer v{VERSION}")
print("=" * 50)

if dry_run_mode:
    print("DRY-RUN MODE: No changes will be made")  
else:
    print("EXECUTE MODE: Files will be renamed")
```

**Testing Required:** Integration tests for complete verbose/debug functionality

---

### 9. `plex_make_all_seasons` - Standard Refactoring

**Status:** Medium complexity
**Files to Modify:** `plex/plex_make_all_seasons`

**Refactoring Steps:** Follow `plex_correct_dirs` pattern

**Unique Arguments to Preserve:**
```python
parser.add_argument('--parallel', '--workers', type=int, default=4, metavar='N',
                    help='Number of worker threads for parallel processing (default: 4, use 1 for sequential)')
parser.add_argument('--recursive', action='store_true',
                    help='Recursively process all subdirectories (not just immediate children)')
```

**Special Considerations:** 
- Ensure parallel processing works correctly with new verbose/debug output
- Coordinate verbose output across multiple worker threads

---

## Implementation Order and Dependencies

### Phase 2.1: Complex Scripts
1. **plex_update_tv_years** - Verification only
2. **sabnzbd_cleanup** - Add missing arguments

### Phase 2.2: Medium Complexity Scripts  
3. **plex_correct_dirs** - Full standardization
4. **plex_make_dirs** - Follow plex_correct_dirs pattern
5. **plex_make_seasons** - Follow pattern + preserve unique args
6. **plex_make_years** - Follow pattern + preserve unique args

### Phase 3.1: Remaining Scripts
7. **plex_move_movie_extras** - Major refactoring (global config)
8. **plex_movie_subdir_renamer** - Complete integration
9. **plex_make_all_seasons** - Standard + parallel considerations

---

## Testing Strategy per Script

### Unit Tests Required
- **All Scripts:** Test verbose/debug flag functionality
- **7 Scripts:** Test new execute flag behavior vs old dry-run pattern
- **plex_move_movie_extras:** Test global configuration integration
- **All Scripts:** Test mode indicator display

### Integration Tests Required
- **All Scripts:** Test CLI argument precedence
- **All Scripts:** Test non-interactive mode detection
- **Scripts with unique args:** Test argument combinations

### Backward Compatibility Tests
- **All Scripts:** Verify existing usage patterns still work
- **Scripts with dry-run changes:** Test migration path

---

## Rollback Strategy

### Individual Script Rollback
- Each script refactoring should be atomic (one commit per script)
- Keep original patterns in comments during development
- Maintain backup copies of original argument patterns

### Global Rollback Plan
- Feature branch allows complete rollback via git reset
- Individual script commits allow selective rollback
- Test failures should trigger immediate rollback of failing script

### Risk Mitigation
- Test each script immediately after refactoring
- Validate existing functionality before adding new features
- Document all changes for easy reversion

This refactoring plan provides specific, actionable steps for achieving complete CLI standardization while maintaining backward compatibility and minimizing risk.