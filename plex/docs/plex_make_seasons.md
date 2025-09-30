# Plex Make Seasons v3.1.0

## Overview

A sophisticated Python tool for organizing TV show episodes into season-specific directories using a comprehensive three-phase processing system. The enhanced version includes sample file detection, configurable directory exclusions, conflict resolution, and manifest-based rollback capability.

## What's New in v3.1.0

Enhanced plex_make_seasons now provides enterprise-grade file management with three distinct processing phases:

**Phase 1: Consolidation** - Discover and analyze files without making changes
**Phase 2: Organization** - Create season directories and move files with conflict resolution
**Phase 3: Archive** - Archive sample files and create rollback manifests

### Key Enhancements

- **Three-Phase Architecture**: Consolidation → Organization → Archive workflow
- **Sample File Detection**: Configurable size threshold (default: 50MB) to identify and handle sample files
- **Directory Exclusion**: Pattern-based exclusion (e.g., "Extras", "Samples") with partial matching
- **Enhanced Conflict Resolution**: Size-based automatic resolution with user confirmation
- **Rollback Capability**: Manifest-based system to undo operations if needed
- **Tiered Dry-Run Output**: Three detail levels (basic, detailed, comprehensive)
- **System Trash Cleanup**: Automatic removal of .DS_Store, Thumbs.db, and system files
- **Advanced Configuration**: Multi-layer configuration via CLI, environment variables, and .env files
- **19 Season Detection Patterns**: Including extended season numbers (S001-S999)

## Core Features

- **Intelligent season detection**: Supports 19 season naming conventions (S01E01, 1x01, Season 1, etc.)
- **Extended season support**: Handles season numbers 1-999 for long-running shows
- **Sample file management**: Automatically detect and optionally archive small sample files
- **Directory exclusion**: Exclude specific directories from processing
- **Flexible matching**: Handles different separators, cases, and formatting styles
- **File organization**: Automatic directory creation with smart file movement and collision handling
- **Target directory support**: Option to organize files in a different location
- **Video file filtering**: Processes only video files, ignoring other file types
- **Safety features**: File-based locking, tiered dry-run modes, error recovery, and rollback capability
- **Cron-friendly**: Non-interactive operation with comprehensive logging and proper exit codes
- **Self-contained**: Uses only Python standard library modules
- **Zero installation**: Download, chmod +x, and run immediately

## Installation

```bash
# Download and make executable
wget https://raw.githubusercontent.com/samestrin/media-library-tools/main/plex/plex_make_seasons
chmod +x plex_make_seasons
```

## Usage

### Quick Start

```bash
# Preview what would be organized (dry-run mode - default)
./plex_make_seasons /path/to/tv/show

# Actually perform the organization
./plex_make_seasons --execute /path/to/tv/show

# Organize with automatic confirmation (cron-friendly)
./plex_make_seasons --execute -y /path/to/tv/show
```

### Common Scenarios

```bash
# Organize a specific season
./plex_make_seasons --execute -s 1 /path/to/show

# Exclude directories and enable sample detection
./plex_make_seasons --execute --sample-detect --ignore-dir "Extras,Samples" /path/to/show

# Comprehensive preview with all details
./plex_make_seasons --dry-run-level comprehensive /path/to/show

# Enable sample detection and archiving with cleanup
./plex_make_seasons --execute --sample-detect --archive --cleanup /path/to/show
```

### Automation

```bash
# Run daily at 3 AM with cleanup (non-interactive)
0 3 * * * /usr/local/bin/plex_make_seasons --execute -y --cleanup /path/to/downloads
```

## Command-Line Arguments

### Standard Arguments

```
--execute               Actually perform operations (default: dry-run mode)
-y, --yes              Skip confirmation prompts (for non-interactive/cron use)
--verbose, -v          Show verbose output with detailed progress
--debug                Show detailed debug output for troubleshooting
--force                Force execution even if another instance is running
--version              Show version information and exit
--no-banner            Suppress banner display
```

### Enhanced Arguments (New in v3.1.0)

```
-s, --season N         Process only specified season number
--ignore-dir DIRS      Comma-separated list of directory names to exclude
--sample-detect        Enable automatic sample file detection
--sample-threshold N   Sample file size threshold in MB (default: 50)
--archive              Enable sample file archiving with manifest
--cleanup              Clean system trash files (.DS_Store, Thumbs.db, etc.)
--depth N              Maximum directory depth for recursive processing (default: 3)
--dry-run-level LEVEL  Dry-run detail level: basic, detailed, comprehensive (default: basic)
```

### Phase Control Arguments (New in v3.1.0)

```
--consolidate-only     Execute only consolidation phase (file discovery)
--organize-only        Execute only organization phase (season creation)
--archive-only         Execute only archive phase (sample archiving)
--no-archive           Skip archive phase entirely
```

## Configuration Management

### Configuration Hierarchy

Configuration is loaded in order of priority (highest to lowest):

1. **Command-line arguments** (highest priority)
2. **Environment variables** (PLEX_*, AUTO_*)
3. **.env file** in current directory
4. **.env file** in `~/.media-library-tools/`
5. **Built-in defaults** (lowest priority)

### Environment Variables

```bash
# Global execution settings
AUTO_EXECUTE=true        # Automatically execute without --execute flag
AUTO_CONFIRM=true        # Automatically confirm without -y flag

# Sample detection settings
PLEX_SAMPLE_DETECTION=true   # Enable sample detection by default
PLEX_SAMPLE_THRESHOLD=50     # Default sample threshold in MB
```

### Example .env File

Create `~/.media-library-tools/.env` for global defaults:

```bash
# Execution settings
AUTO_EXECUTE=false
AUTO_CONFIRM=false

# Sample detection
PLEX_SAMPLE_DETECTION=true
PLEX_SAMPLE_THRESHOLD=50

# Directory exclusions (comma-separated)
PLEX_IGNORE_DIRS=Extras,Samples,Bonus,Behind the Scenes
```

## Season detection patterns

The tool recognizes multiple season naming conventions:

### Standard TV patterns
- **S01E01 format**: `S01E01`, `S1E1`, `s01e01` (most common)
- **Season X format**: `Season 1`, `Season.01`, `Season_1`
- **1x01 format**: `1x01`, `01x01` (alternative numbering)
- **S1 format**: `S1`, `S01` (season only)

### Alternative patterns
- **Year format**: `2023`, `(2023)`, `[2023]` (for year-based seasons)
- **Episode format**: `Episode 1`, `Ep 1`, `Ep.01`
- **Part format**: `Part 1`, `Part.01`
- **Chapter format**: `Chapter 1`, `Chapter.01`
- **Disc format**: `Disc 1`, `D1`
- **Volume format**: `Vol 1`, `V1`

### Pattern Examples

```
Show.S01E01.Episode.Name.mkv        → Season 01/
Show.1x01.Episode.Name.mp4          → Season 01/
Show.Season.1.Episode.1.avi         → Season 01/
Show.2023.Episode.Name.mp4          → Season 2023/
Show.Episode.01.mkv                 → Season 01/
Show.Part.1.mp4                     → Season 01/
```

## Supported video formats

The tool processes the following video file types:

### Common formats
- **MP4**: `.mp4`, `.m4v`, `.m4p`
- **MKV**: `.mkv`
- **AVI**: `.avi`
- **MOV**: `.mov`
- **WMV**: `.wmv`

### Streaming formats
- **Web**: `.webm`, `.flv`
- **MPEG**: `.mpg`, `.mpeg`, `.3gp`
- **Transport**: `.ts`, `.m2ts`

### Legacy formats
- **DVD**: `.vob`
- **Codec**: `.divx`, `.xvid`
- **RealMedia**: `.rm`, `.rmvb`
- **Windows**: `.asf`, `.f4v`
- **Other**: `.ogv`

## Processing logic

### Season detection process
1. **File analysis**: Scans video files for season patterns
2. **Pattern matching**: Applies regex patterns in order of specificity
3. **Season extraction**: Extracts season number from matched pattern
4. **Validation**: Ensures reasonable season numbers (1-50 for most patterns)
5. **Directory naming**: Generates appropriate season directory name

### File organization process
1. **Directory creation**: Creates season directory if it doesn't exist
2. **Collision detection**: Checks for existing files with same name
3. **Unique naming**: Generates unique names for conflicting files
4. **File movement**: Moves episode to season directory
5. **Statistics tracking**: Records processing results

### Collision handling
- **No conflict**: File moved directly to season directory
- **Name conflict**: Appends `_1`, `_2`, etc. to create unique names
- **Directory reuse**: Uses existing season directories when appropriate

## Examples

### Basic organization
```bash
# Organize episodes in current directory
./plex_make_seasons.py /path/to/tv/show

# Preview changes first
./plex_make_seasons.py /path/to/tv/show --dry-run

# Organize to different location
./plex_make_seasons.py /downloads/show --target /media/tv/show
```

### Pattern analysis
```bash
# List all supported patterns
./plex_make_seasons.py --list-patterns

# Test pattern detection
./plex_make_seasons.py /path/to/show --dry-run
```

### Directory structure transformation

**Before:**
```
/tv/Breaking.Bad/
├── Breaking.Bad.S01E01.Pilot.mkv
├── Breaking.Bad.S01E02.Cat.in.the.Bag.mkv
├── Breaking.Bad.S02E01.Seven.Thirty.Seven.mkv
├── Breaking.Bad.S02E02.Grilled.mkv
└── Breaking.Bad.S03E01.No.Mas.mkv
```

**After:**
```
/tv/Breaking.Bad/
├── Season 01/
│   ├── Breaking.Bad.S01E01.Pilot.mkv
│   └── Breaking.Bad.S01E02.Cat.in.the.Bag.mkv
├── Season 02/
│   ├── Breaking.Bad.S02E01.Seven.Thirty.Seven.mkv
│   └── Breaking.Bad.S02E02.Grilled.mkv
└── Season 03/
    └── Breaking.Bad.S03E01.No.Mas.mkv
```

### Automation examples
```bash
# Cron job - daily at 3 AM
0 3 * * * /usr/local/bin/plex_make_seasons.py /path/to/downloads

# Force execution (bypass lock)
./plex_make_seasons.py /path/to/show --force

# Organize multiple shows
for show in /downloads/tv/*/; do
    plex_make_seasons.py "$show"
done
```

## Safety features

- **File locking**: Creates temporary lock file to prevent concurrent runs with PID tracking
- **Clean cleanup**: Automatically removes lock file on exit
- **Force override**: `--force` flag bypasses lock for emergency situations
- **Graceful failures**: Continues processing other files if one fails
- **Detailed logging**: Reports specific errors for troubleshooting
- **Pattern validation**: Ensures extracted season numbers are reasonable
- **File safety**: Original files remain intact if operations fail
- **Dry-run mode**: Shows exactly what would be done without making changes
- **Pattern analysis**: Displays which patterns would be matched
- **Collision preview**: Shows how naming conflicts would be resolved
- **Statistics**: Provides counts of files that would be processed

## Troubleshooting

### Common issues

**"Another instance is already running"**
- Another copy of the script is running
- Use `--force` to override if you're sure no other instance exists
- Check for stale lock files in `/tmp/`

**"No season pattern found"**
- Filename doesn't match any supported patterns
- Use `--list-patterns` to see all supported formats
- Consider renaming files to match standard patterns
- Check if files are actually video files

**"Permission denied"**
- Ensure you have write permissions to the target directory
- Check that files aren't in use by other applications
- Verify the script has execute permissions

**Files not being processed**
- Check that files have video extensions
- Ensure filenames contain recognizable season patterns
- Use `--dry-run` to see what would be processed

### Debug information

```bash
# Check supported patterns
./plex_make_seasons.py --list-patterns

# Preview processing with detailed output
./plex_make_seasons.py /path/to/show --dry-run

# Test specific directory
./plex_make_seasons.py /path/to/test --dry-run
```

### Pattern debugging

If files aren't being recognized:

1. **Check filename format**: Ensure it contains season information
2. **Use dry-run mode**: See which patterns are being matched
3. **Review pattern list**: Compare your filenames to supported patterns
4. **Consider renaming**: Adjust filenames to match standard conventions

### Performance considerations

- **Large directories**: Processing hundreds of files may take time
- **Network storage**: Operations on network drives will be slower
- **Pattern complexity**: More complex patterns take longer to match
- **File locks**: Some media players may lock files during playback

## Technical details

- **Python 3.6+**: Required for pathlib and f-string support
- **Standard library only**: No external dependencies required
- **Cross-platform**: Works on Linux, macOS, and Windows
- **Regex engine**: Uses Python's `re` module for pattern matching
- **Case insensitive**: Patterns match regardless of case
- **Ordered matching**: Patterns are tried in order of specificity
- **Validation**: Extracted numbers are validated for reasonableness
- **Atomic moves**: Uses `shutil.move()` for safe file operations
- **Path handling**: Leverages `pathlib` for robust path operations
- **Lock management**: Uses `fcntl` for file locking (Unix/Linux/macOS)

### Implementation

- **Path validation**: Prevents directory traversal attacks
- **Permission checks**: Validates access before operations
- **Temporary files**: Secure lock file creation in system temp directory
- **Error isolation**: Failures in one file don't affect others

## Version History

### Version 3.1.0 (Current - Sprint 9.0)
- **Three-Phase Processing Architecture**: Consolidation → Organization → Archive
- **Sample File Detection**: Configurable size threshold with automatic identification
- **Directory Exclusion**: Pattern-based exclusion with partial matching
- **Enhanced Conflict Resolution**: Size-based automatic resolution with user confirmation
- **Rollback Capability**: Manifest-based system for operation recovery
- **Tiered Dry-Run Output**: Three levels (basic, detailed, comprehensive)
- **System Trash Cleanup**: Automatic removal of OS-specific junk files
- **Advanced Configuration**: Multi-layer hierarchy with .env support
- **Extended Season Support**: Season numbers 1-999 for long-running shows
- **19 Season Detection Patterns**: Including extended formats and validation
- **Phase Control**: Run individual phases independently
- **Archive System**: Sample file archiving with JSON manifests
- **Enhanced CLI**: New arguments for sample detection, exclusions, and phase control
- **Improved Error Handling**: Comprehensive validation and user feedback
- **Performance Optimization**: Configurable depth control and efficient traversal

### Version 2.0.0
- Complete rewrite in Python from bash
- Added comprehensive season pattern detection
- Implemented file-based locking mechanism
- Added collision detection and handling
- Enhanced error reporting and statistics
- Added dry-run mode and force flag
- Improved cron-friendly operation
- Added target directory support
- Added pattern analysis and debugging tools

### Version 1.0.0 (bash)
- Basic season detection (S01E01 format only)
- Simple file moving
- Limited error handling
- Basic dry-run support

---

*Part of the Media Library Tools project - A collection of utilities for managing and organizing media libraries.*