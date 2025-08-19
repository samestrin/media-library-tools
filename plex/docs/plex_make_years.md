# Plex Year Organizer

A Python tool for organizing media directories by year. This script analyzes directory names to extract year information and automatically creates year-based directory structures that are ideal for organizing movies and TV shows by release year.

## Overview

This tool provides intelligent year detection and directory organization for media libraries. It analyzes directory names using multiple pattern recognition techniques to extract year information and automatically creates year-based directory structures.

## Features

- **Self-contained**: Single Python script using only standard library modules
- **Zero installation**: Download, make executable, and run immediately
- **Intelligent year detection**: Multiple pattern recognition with configurable year ranges
- **Safe operations**: Dry-run mode, file locking, and comprehensive error handling
- **Automation ready**: Non-interactive operation with proper exit codes
- **Flexible organization**: Customizable base directories and collision handling

## Installation

No installation required. Download the script and make it executable:

```bash
# Download and make executable
curl -O https://raw.githubusercontent.com/your-repo/media-library-tools/main/plex/plex_make_years.py
chmod +x plex_make_years.py

# Run immediately
./plex_make_years.py /path/to/media
```

## Usage

### Basic usage
```bash
# Organize directories by year
./plex_make_years.py /path/to/movies

# Preview changes first
./plex_make_years.py /path/to/movies --dry-run
```

### Automation
```bash
# Cron job - daily at 2 AM
0 2 * * * /usr/local/bin/plex_make_years.py /path/to/downloads

# Force execution (bypass lock)
./plex_make_years.py /path/to/media --force
```

## Command-line options

| Option | Description |
|--------|-------------|
| `directory` | Directory containing directories to organize by year (required) |
| `--base DIR` | Base directory for year organization (default: same as source) |
| `--dry-run` | Show what would be done without making changes |
| `--force` | Force execution even if another instance is running |
| `--year-range START END` | Valid year range (default: 1900-2030) |
| `--list-patterns` | List all supported year detection patterns and exit |
| `--version` | Show version information |
| `--help` | Show help message |

## Year detection patterns

The tool recognizes multiple year naming conventions:

**Enclosed patterns (highest priority)**
- Parentheses: `(2023)`, `(1999)`
- Brackets: `[2023]`, `[1999]`

**Separator patterns**
- Dot separated: `.2023.`, `.1999.`
- Space separated: ` 2023 `, ` 1999 `
- Dash separated: `-2023-`, `-1999-`
- Underscore separated: `_2023_`, `_1999_`

**Position-based patterns**
- End patterns: `.2023`, ` 2023`, `-2023`, `_2023`
- Beginning patterns: `2023.`, `2023 `, `2023-`, `2023_`
- Standalone: `2023` (lowest priority to avoid false positives)

### Pattern Examples

```
Movie.Title.(2023)              → 2023/
Another.Movie.[2022]            → 2022/
Show.2021.Season.1              → 2021/
Film.Title.2020.1080p           → 2020/
2019.Movie.Title                → 2019/
Movie_2018_BluRay               → 2018/
Classic.Film-1995-Remastered    → 1995/
```

## Processing logic

**Year detection process**
1. Directory analysis: Scans directory names for year patterns
2. Pattern matching: Applies regex patterns in order of specificity
3. Year extraction: Extracts year from matched pattern
4. Range validation: Ensures year falls within specified range
5. Directory planning: Determines target year directory

**Directory organization process**
1. Year directory creation: Creates year directory if it doesn't exist
2. Collision detection: Checks for existing directories with same name
3. Merge analysis: Determines if directories can be safely merged
4. Conflict resolution: Handles naming conflicts with unique names
5. Directory movement: Moves or merges directories as appropriate

**Collision handling**
- No conflict: Directory moved directly to year directory
- Safe merge: Compatible directories merged automatically
- Name conflict: Creates unique names with numeric suffixes
- File conflicts: Renames conflicting files with `_backup` suffix
- Type conflicts: Handles file vs directory conflicts

## Examples

**Basic organization**
```bash
# Organize directories by year
./plex_make_years.py /path/to/movies

# Organize to different location
./plex_make_years.py /downloads/movies --base /media/movies
```

**Custom configuration**
```bash
# Custom year range (for older content)
./plex_make_years.py /path/to/classics --year-range 1920 1990

# List supported patterns
./plex_make_years.py --list-patterns
```

**Directory structure transformation**

Before:
```
/movies/
├── The.Matrix.(1999)/
├── Inception.(2010)/
├── Blade.Runner.(1982)/
├── Interstellar.(2014)/
└── Casablanca.(1942)/
```

After:
```
/movies/
├── 1942/
│   └── Casablanca.(1942)/
├── 1982/
│   └── Blade.Runner.(1982)/
├── 1999/
│   └── The.Matrix.(1999)/
├── 2010/
│   └── Inception.(2010)/
└── 2014/
    └── Interstellar.(2014)/
```

**Automation examples**
```bash
# Organize multiple directories
for dir in /downloads/*/; do
    plex_make_years.py "$dir"
done
```

## Safety features

The tool implements comprehensive safety measures:

- **File locking**: Prevents concurrent executions with automatic cleanup
- **Error recovery**: Continues processing if individual directories fail
- **Dry-run mode**: Preview all changes before execution
- **Collision resolution**: Smart merging and conflict handling
- **Permission handling**: Graceful handling of access restrictions

## Troubleshooting

**Common issues**

- "Another instance is already running": Use `--force` to override or check for stale lock files
- "No year pattern found": Directory name doesn't contain recognizable year pattern
- "Permission denied": Ensure write permissions to target directory
- Directories not processed: Check that items are directories with year information

**Debug information**

```bash
# Check supported patterns
./plex_make_years.py --list-patterns

# Preview processing
./plex_make_years.py /path/to/media --dry-run
```

**Pattern debugging**

1. Check directory names contain year information
2. Use dry-run mode to see pattern matching
3. Review pattern list for supported formats
4. Adjust year range if needed
5. Consider renaming with years in parentheses

## Technical details

**Implementation**
- Python 3.6+ with standard library only
- Regex-based pattern matching with ordered processing
- Atomic directory operations using `shutil.move()`
- File locking for concurrent execution prevention

**Dependencies**
- Python standard library modules only
- Cross-platform compatibility (Linux, macOS, Windows)
- No external package requirements

**Security**
- Path validation prevents directory traversal
- Permission checks before operations
- Secure temporary file handling
- Error isolation between directories

## Version History

### Version 2.0.0
- Complete rewrite in Python from bash
- Added comprehensive year pattern detection
- Implemented file-based locking mechanism
- Added intelligent collision detection and merging
- Enhanced error reporting and statistics
- Added dry-run mode and force flag
- Improved cron-friendly operation
- Added base directory support
- Added configurable year range validation
- Added pattern analysis and debugging tools

### Version 1.0.0 (bash)
- Basic year detection (parentheses format only)
- Simple directory moving
- Limited error handling
- Basic dry-run support

---

*Part of the Media Library Tools project - A collection of utilities for managing and organizing media libraries.*