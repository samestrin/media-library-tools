# Plex Make Seasons

## Overview

A Python tool for organizing TV show episodes into season-specific directories. This script analyzes video filenames to extract season information and automatically creates proper season directory structures that are ideal for Plex media organization.

## Features

- **Intelligent season detection**: Supports various season naming conventions (S01E01, 1x01, Season 1, etc.)
- **Flexible matching**: Handles different separators, cases, and formatting styles
- **Year-based seasons**: Recognizes year-based season patterns for certain shows
- **Episode numbering**: Detects episode, part, chapter, disc, and volume patterns
- **File organization**: Automatic directory creation with smart file movement and collision handling
- **Target directory support**: Option to organize files in a different location
- **Video file filtering**: Processes only video files, ignoring other file types
- **Safety features**: File-based locking, dry-run mode, error recovery, and progress tracking
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

### Basic usage
```bash
# Organize episodes in current directory
./plex_make_seasons.py /path/to/tv/show

# Preview changes first
./plex_make_seasons.py /path/to/tv/show --dry-run
```

### Automation
```bash
# Run daily at 3 AM
0 3 * * * /usr/local/bin/plex_make_seasons.py /path/to/downloads
```

## Command-line options

```
Usage: plex_make_seasons.py [OPTIONS] [DIRECTORY]

Arguments:
  DIRECTORY                 Directory containing TV show episodes (default: current directory)

Options:
  --target TARGET          Target directory for organized files (default: same as source)
  --dry-run               Show what would be done without making changes
  --force                 Force execution even if another instance is running
  --list-patterns         Show all supported season detection patterns
  --verbose, -v           Show detailed processing information
  --debug                 Show debug information for troubleshooting
  --version               Show version information
  --help, -h              Show this help message
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