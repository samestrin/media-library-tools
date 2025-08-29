# Plex Make All Seasons

## Overview

A Python tool for organizing TV show episodes into season directories for optimal Plex library structure. This tool automatically processes multiple show directories simultaneously, detects season/episode patterns, and creates organized directory structures that Plex can easily parse.

## Features

- **Batch processing**: Process entire TV show libraries at once with multi-directory support
- **Parallel processing**: Configurable worker threads for faster processing with real-time progress tracking
- **Enhanced season detection**: Recognizes various season/episode naming conventions (SxxExx and 1x01 formats)
- **Smart grouping**: Automatically groups episodes by detected season numbers with pattern validation
- **Safety & reliability**: Dry-run mode, file collision handling, error recovery, and lock file protection
- **Performance optimized**: Memory efficient processing with fast pattern matching and progress feedback
- **Recursive discovery**: Find and process shows in nested directory structures
- **Self-contained**: Uses only Python standard library modules
- **Zero installation**: Download, chmod +x, and run immediately

## Installation

```bash
# Download and make executable
wget https://raw.githubusercontent.com/samestrin/media-library-tools/main/plex/plex_make_all_seasons
chmod +x plex_make_all_seasons
```

## Usage

### Basic usage
```bash
# Process all TV show directories
./plex_make_all_seasons.py "/Users/media/TV Shows"

# Preview changes first
./plex_make_all_seasons.py "/Users/media/TV Shows" --dry-run
```

### Automation
```bash
# Run daily at 3 AM
0 3 * * * /usr/local/bin/plex_make_all_seasons.py /path/to/tv/shows
```

## Command-line options

```
Usage: plex_make_all_seasons.py [OPTIONS] DIRECTORY

Arguments:
  DIRECTORY                 Base directory containing TV show subdirectories

Options:
  --dry-run                Show what would be done without making changes
  --parallel WORKERS       Number of worker threads (1-16, default: 4)
  --recursive              Process all subdirectories recursively
  --force                  Force execution even if lock file exists
  --no-banner              Suppress banner display
  --verbose, -v            Show detailed processing information
  --debug                  Show debug output for troubleshooting
  --version                Show version information
  --help, -h               Show this help message
```

## Global Configuration Support

The tool respects environment variables for default behavior:

- `AUTO_EXECUTE=true` - Default to execute mode instead of dry-run
- `AUTO_CONFIRM=true` - Skip confirmation prompts automatically
- `QUIET_MODE=true` - Suppress banner display by default

Configuration hierarchy: CLI arguments > Environment variables > Local .env > Global ~/.media-library-tools/.env

## Season detection patterns

The script recognizes multiple season/episode naming patterns:

### Standard patterns
- **S##E##**: `S01E01`, `S1E1`, `s01e01` (case-insensitive)
- **Season Episode**: `Season 1 Episode 1`, `Season 01 Episode 01`
- **##x##**: `1x01`, `01x01`, `1x1`
- **Season Only**: `S01`, `S1`, `Season 1`

### Pattern examples
```
Breaking.Bad.S01E01.Pilot.mkv          → Season 1
Game.of.Thrones.1x01.Winter.Is.Coming.mp4 → Season 1
The.Office.Season.2.Episode.1.mkv      → Season 2
Sherlock.S02E01.A.Scandal.in.Belgravia.mp4 → Season 2
```

### Pattern priority
1. **S##E##** format (highest priority)
2. **##x##** format
3. **Season ## Episode ##** format
4. **S##** format (season only)

## Supported video formats

The script processes these video file extensions:

- **High Quality**: `.mkv`, `.mp4`, `.avi`
- **Standard**: `.mov`, `.wmv`, `.flv`, `.webm`
- **Compressed**: `.m4v`, `.3gp`, `.ogv`
- **Legacy**: `.mpg`, `.mpeg`, `.divx`, `.xvid`

*Note: File extensions are case-insensitive (e.g., `.MKV`, `.Mp4` are supported)*

## Processing modes

### Sequential processing
```bash
# Process directories one at a time
./plex_make_all_seasons.py /path/to/tv/shows --parallel 1
```
- **Best for**: Debugging, low-memory systems, network storage
- **Advantages**: Lower memory usage, easier error tracking
- **Considerations**: Slower processing time

### Parallel processing (Default)
```bash
# Process multiple directories simultaneously
./plex_make_all_seasons.py /path/to/tv/shows --parallel 8
```
- **Best for**: Large libraries, modern multi-core systems
- **Advantages**: Significantly faster processing
- **Considerations**: Higher memory usage, more complex error tracking

### Recursive processing
```bash
# Process all subdirectories recursively
./plex_make_all_seasons.py /path/to/tv/shows --recursive
```
- **Best for**: Complex directory structures, nested show directories
- **Behavior**: Finds and processes any directory containing video files
- **Use Case**: When shows are organized in multiple levels of subdirectories

## Locking mechanism

The script implements a robust file-based locking system:

- **Automatic Lock**: Creates temporary lock file to prevent concurrent execution
- **PID Tracking**: Stores process ID in lock file for debugging
- **Clean Cleanup**: Automatically removes lock file on exit
- **Force Override**: Use `--force` flag to bypass locking (use with caution)
- **Cron-Safe**: Prevents overlapping cron jobs from conflicting

## Examples

### Directory structure transformation
```
Before:
/TV Shows/
├── Breaking Bad/
│   ├── Breaking.Bad.S01E01.Pilot.mkv
│   ├── Breaking.Bad.S01E02.Cat's.in.the.Bag.mkv
│   ├── Breaking.Bad.S02E01.Seven.Thirty-Seven.mkv
│   └── Breaking.Bad.S02E02.Grilled.mkv
└── Game of Thrones/
    ├── Game.of.Thrones.1x01.Winter.Is.Coming.mp4
    ├── Game.of.Thrones.1x02.The.Kingsroad.mp4
    └── Game.of.Thrones.2x01.The.North.Remembers.mp4

After:
/TV Shows/
├── Breaking Bad/
│   ├── Season 1/
│   │   ├── Breaking.Bad.S01E01.Pilot.mkv
│   │   └── Breaking.Bad.S01E02.Cat's.in.the.Bag.mkv
│   └── Season 2/
│       ├── Breaking.Bad.S02E01.Seven.Thirty-Seven.mkv
│       └── Breaking.Bad.S02E02.Grilled.mkv
└── Game of Thrones/
    ├── Season 1/
    │   ├── Game.of.Thrones.1x01.Winter.Is.Coming.mp4
    │   └── Game.of.Thrones.1x02.The.Kingsroad.mp4
    └── Season 2/
        └── Game.of.Thrones.2x01.The.North.Remembers.mp4
```

## Safety features

- **Dry-run mode**: Test all operations safely before execution
- **File collision prevention**: Automatic unique naming for duplicates
- **Lock file protection**: Prevents concurrent execution conflicts
- **Error isolation**: Individual directory failures don't affect others
- **Reversible operations**: Directory moves can be manually reversed
- **No file deletion**: Script only moves and renames, never deletes
- **Collision resolution**: Files with duplicate names get unique suffixes
- **Error recovery**: Continue processing even if individual directories fail
- **Permission handling**: Reports directories that can't be accessed
- **Graceful degradation**: Partial success is better than complete failure

## Troubleshooting

**"Another instance is already running"**
- Another copy of the script is running
- Use `--force` flag to override (ensure no other instance is actually running)
- Check for stale lock files in system temp directory

**"No directories found to process"**
- Verify the base directory contains subdirectories
- Check if subdirectories contain video files
- Try using `--recursive` flag for nested structures

**"Files skipped (no season pattern)"**
- Files don't match any recognized season/episode pattern
- Check filename format and adjust if necessary
- Consider manual organization for non-standard files

**Performance Issues**
- Reduce worker count for network storage
- Use sequential processing (`--parallel 1`) for debugging
- Check available system resources (CPU, memory, disk I/O)

## Technical details

### Implementation
- **Python 3.6+**: Uses f-strings, pathlib, and concurrent.futures
- **Standard library only**: No external dependencies required
- **Cross-platform**: Works on macOS, Linux, and Windows
- **Parallel processing**: ThreadPoolExecutor for concurrent directory processing
- **Memory efficient**: Processes directories individually
- **Fast pattern matching**: Compiled regex patterns
- **Minimal I/O**: Only reads directory structure and moves files
- **Safe operations**: Only moves files, never deletes
- **Path validation**: Prevents directory traversal attacks
- **Lock file security**: Uses secure temporary file creation
- **Error containment**: Exceptions are caught and reported safely